from __future__ import annotations

import asyncio
import json
import threading
from typing import Any, Callable, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.engine.evaluator import Evaluator
from src.engine._q_buffer import MusicalStateBuffer


class EngineWebSocketServer:
    def __init__(self, evaluator: Optional[Evaluator], song_name: str, port: int = 3301):
        self.evaluator = evaluator
        self.song_name = song_name
        self.port = int(port)
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._clients: List[WebSocket] = []
        self._client_lock = threading.Lock()
        self._state_cache: list[MusicalStateBuffer] = []
        self._ready = threading.Event()
        self._play_task: Optional[asyncio.Task[Any]] = None
        self._song_selection_handler: Optional[Callable[[str], None]] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._playback_started = threading.Event()
        self._playback_finished = threading.Event()
        self._server_thread = threading.Thread(target=self._run, daemon=True)
        self._register_routes()

    def _register_routes(self) -> None:
        @self.app.websocket("/ws/canvas")
        async def websocket_endpoint(websocket: WebSocket) -> None:
            await websocket.accept()
            self._add_client(websocket)
            try:
                if self._ready.is_set():
                    await self._send_ready(websocket)
                    await self._send_init(websocket)
                while True:
                    message = await websocket.receive_text()
                    event = json.loads(message)
                    await self._handle_event(event)
            except WebSocketDisconnect:
                pass
            finally:
                self._remove_client(websocket)

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        event_type = event.get("type")
        payload = event.get("data", {})
        if event_type == "play":
            start_time = float(payload.get("start_time", 0.0))
            await self._start_playback(start_time)
        elif event_type == "select_song":
            song_name = str(payload.get("song_name", "")).strip()
            if song_name:
                await self._select_song(song_name)

    def _add_client(self, websocket: WebSocket) -> None:
        with self._client_lock:
            self._clients.append(websocket)

    def _remove_client(self, websocket: WebSocket) -> None:
        with self._client_lock:
            if websocket in self._clients:
                self._clients.remove(websocket)

    def _run(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port, log_level="warning")
        server = uvicorn.Server(config)
        self._loop.run_until_complete(server.serve())

    def start(self) -> None:
        if not self._server_thread.is_alive():
            self._server_thread.start()

    def cache_states(self, states: list[MusicalStateBuffer]) -> None:
        self._state_cache = list(states)

    def set_evaluator(self, evaluator: Evaluator) -> None:
        self.evaluator = evaluator

    def set_song_name(self, song_name: str) -> None:
        self.song_name = song_name

    def set_song_selection_handler(self, handler: Callable[[str], None]) -> None:
        self._song_selection_handler = handler

    def clear_ready(self) -> None:
        self._ready.clear()

    def notify_error(self, message: str) -> None:
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast_error(message), self._loop)

    async def _broadcast_error(self, message: str) -> None:
        await self._broadcast({"type": "error", "data": {"message": message}})

    def notify_ready(self) -> None:
        self._ready.set()
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self._broadcast_ready_state(), self._loop)

    async def _send_ready(self, websocket: WebSocket) -> None:
        await websocket.send_json({"type": "ready"})

    async def _send_init(self, websocket: WebSocket) -> None:
        await websocket.send_json({"type": "init", "data": self._build_init_payload()})

    async def _broadcast_ready_state(self) -> None:
        await self._broadcast({"type": "ready"})
        await self._broadcast({"type": "init", "data": self._build_init_payload()})

    async def _broadcast(self, payload: Dict[str, Any]) -> None:
        dead_clients: list[WebSocket] = []
        with self._client_lock:
            clients = list(self._clients)
        for client in clients:
            try:
                await client.send_json(payload)
            except WebSocketDisconnect:
                dead_clients.append(client)
            except Exception:
                dead_clients.append(client)
        with self._client_lock:
            for client in dead_clients:
                if client in self._clients:
                    self._clients.remove(client)

    async def _start_playback(self, start_time: float = 0.0) -> None:
        if self._play_task and not self._play_task.done():
            return
        if not self._state_cache:
            return
        self._playback_started.set()
        self._playback_finished.clear()
        await self._broadcast({"type": "init", "data": self._build_init_payload()})
        self._play_task = asyncio.create_task(self._playback_loop(start_time))

    async def _playback_loop(self, start_time: float = 0.0) -> None:
        index = 0
        while index < len(self._state_cache) and self._state_cache[index].get("time", 0.0) < start_time:
            index += 1
        start = self._state_cache[index].get("time", 0.0) if index < len(self._state_cache) else 0.0
        last_time = None
        while index < len(self._state_cache):
            state = self._state_cache[index]
            payload = self._build_frame_payload(state)
            await self._broadcast({"type": "frame", "data": payload})
            elapsed = float(state.get("time", 0.0)) - start
            if last_time is None:
                last_time = elapsed
            else:
                delay = max(0.0, elapsed - last_time)
                await asyncio.sleep(delay if delay > 0 else 0.02)
                last_time = elapsed
            index += 1
        await self._broadcast({"type": "end"})
        self._playback_finished.set()

    async def _stop_playback(self) -> None:
        if self._play_task and not self._play_task.done():
            self._play_task.cancel()
            try:
                await self._play_task
            except asyncio.CancelledError:
                pass
        self._play_task = None
        self._playback_started.clear()
        self._playback_finished.clear()
        await self._broadcast({"type": "end"})

    async def _select_song(self, song_name: str) -> None:
        if self._song_selection_handler is None:
            return
        await self._stop_playback()
        self.clear_ready()
        await self._broadcast({"type": "loading", "data": {"song_name": song_name}})
        try:
            await asyncio.to_thread(self._song_selection_handler, song_name)
        except Exception as exc:
            await self._broadcast_error(str(exc))

    def wait_for_playback(self, timeout: float | None = None) -> bool:
        if not self._playback_started.wait(timeout=timeout):
            return False
        return self._playback_finished.wait(timeout=timeout)

    def wait_forever(self, poll_interval: float = 0.5) -> None:
        sentinel = threading.Event()
        while True:
            sentinel.wait(timeout=poll_interval)

    def _build_init_payload(self) -> Dict[str, Any]:
        if self.evaluator is None:
            raise RuntimeError("WebSocket server requires an Evaluator before sending init payloads.")
        duration = float(self._state_cache[-1].get("time", 0.0)) if self._state_cache else 0.0
        return {
            "song_name": self.song_name,
            "duration": duration,
            "canvas": {
                "width": float(self.evaluator.canvas_width),
                "height": float(self.evaluator.canvas_height),
            },
            "fixtures": [
                {
                    "id": fixture.get("id"),
                    "position": fixture.get("position"),
                    "type": fixture.get("type"),
                }
                for fixture in self.evaluator.fixtures
            ],
        }

    def _build_frame_payload(self, state: MusicalStateBuffer) -> Dict[str, Any]:
        if self.evaluator is None:
            raise RuntimeError("WebSocket server requires an Evaluator before building frame payloads.")
        fixture_states = self.evaluator.evaluate_frame(state)
        return {
            "time": float(state.get("time", 0.0)),
            "q_buffer": {
                "bands": [float(value) for value in state.get("bands", [])],
                "intensity_hit": float(state.get("intensity_hit", 0.0)),
                "cumulative_rotation": float(state.get("cumulative_rotation", 0.0)),
                "mid_warp": float(state.get("mid_warp", 0.0)),
                "section_label": str(state.get("section_label", "unknown")),
                "section_progress": float(state.get("section_progress", 0.0)),
                "cue_trigger": float(state.get("cue_trigger", 0.0)),
            },
            "fixtures": [
                {
                    "id": render_state.get("fixture_id"),
                    "dimmer": render_state.get("dimmer"),
                    "color_rgb": render_state.get("color_rgb"),
                }
                for render_state in fixture_states
            ],
            "canvas_mesh": self.evaluator.render_canvas_mesh(state),
        }


def create_websocket_server(evaluator: Evaluator, song_name: str, port: int = 3301) -> EngineWebSocketServer:
    return EngineWebSocketServer(evaluator=evaluator, song_name=song_name, port=port)
