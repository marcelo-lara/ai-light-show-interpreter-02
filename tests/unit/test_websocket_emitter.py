import asyncio
import time

from src.io.websocket_emitter import EngineWebSocketServer


def test_select_song_event_invokes_handler_and_broadcasts_loading() -> None:
    server = EngineWebSocketServer(evaluator=None, song_name="")
    seen: list[str] = []
    payloads: list[dict] = []

    async def fake_broadcast(payload: dict) -> None:
        payloads.append(payload)

    server._broadcast = fake_broadcast  # type: ignore[method-assign]
    server.set_song_selection_handler(lambda song_name: seen.append(song_name))

    asyncio.run(server._handle_event({"type": "select_song", "data": {"song_name": "Chimera - Hana"}}))

    assert seen == ["Chimera - Hana"]
    assert payloads[0] == {"type": "end"}
    assert payloads[1] == {"type": "loading", "data": {"song_name": "Chimera - Hana"}}


def test_select_song_event_broadcasts_error() -> None:
    server = EngineWebSocketServer(evaluator=None, song_name="")
    payloads: list[dict] = []

    async def fake_broadcast(payload: dict) -> None:
        payloads.append(payload)

    server._broadcast = fake_broadcast  # type: ignore[method-assign]
    server.set_song_selection_handler(lambda _song_name: (_ for _ in ()).throw(ValueError("bad song")))

    asyncio.run(server._handle_event({"type": "select_song", "data": {"song_name": "missing"}}))

    assert payloads[-1] == {"type": "error", "data": {"message": "bad song"}}


def test_playback_loop_overhead_stays_under_two_ms_per_frame(monkeypatch) -> None:
    server = EngineWebSocketServer(evaluator=None, song_name="")
    frame_count = 100
    server.cache_states([{"time": index * 0.02} for index in range(frame_count)])

    async def fake_broadcast(_payload: dict) -> None:
        return None

    async def fake_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(server, "_broadcast", fake_broadcast)
    monkeypatch.setattr(server, "_build_frame_payload", lambda state: {"time": state["time"]})
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    started = time.perf_counter()
    asyncio.run(server._playback_loop())
    elapsed = time.perf_counter() - started

    assert elapsed / frame_count < 0.002