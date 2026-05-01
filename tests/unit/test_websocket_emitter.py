import asyncio

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