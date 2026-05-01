from __future__ import annotations

import argparse
import curses
import re
import sys
from pathlib import Path
from typing import Iterable

from src.io.layout_debug import export_stage_layout_svg
from src.io.show_compiler import compile_dmx_show
from src.io.websocket_emitter import EngineWebSocketServer

SONG_DIRECTORY = Path("data/songs")
SHOW_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def validate_show_name(value: str) -> str:
    if not value:
        return "main-show"
    if not SHOW_NAME_PATTERN.fullmatch(value):
        raise ValueError(
            "Invalid show name. Only letters, numbers, underscores, and hyphens are allowed."
        )
    return value


def list_song_choices(song_dir: Path = SONG_DIRECTORY) -> list[Path]:
    if not song_dir.is_dir():
        return []
    return sorted(
        [p for p in song_dir.iterdir() if p.is_file() and p.suffix.lower() == ".mp3"],
        key=lambda path: path.name.lower(),
    )


def artifact_dir_for_song(song_path: Path) -> Path:
    return Path("data/artifacts") / song_path.stem


def artifact_missing(song_path: Path) -> bool:
    return not artifact_dir_for_song(song_path).is_dir()


def resolve_song_choice(song_value: str, songs: list[Path]) -> Path:
    normalized = song_value.strip()
    if not normalized:
        raise ValueError("Song name cannot be empty.")

    candidates = {song.name.lower(): song for song in songs}
    candidates.update({song.stem.lower(): song for song in songs})
    match = candidates.get(normalized.lower())
    if match is None:
        raise ValueError(f"Song not found: {song_value}")
    if artifact_missing(match):
        raise ValueError(f"Selected song is missing artifacts: {match.stem}")
    return match


def run_curses_selector(stdscr: "curses._CursesWindow", songs: list[Path]) -> Path:
    curses.curs_set(0)
    stdscr.keypad(True)
    selected_index = 0
    missing_status = [artifact_missing(song) for song in songs]

    while True:
        stdscr.erase()
        height, width = stdscr.getmaxyx()
        if height < 5 or width < 30:
            stdscr.addstr(0, 0, "Terminal too small for the song selector.")
            stdscr.refresh()
            key = stdscr.getch()
            if key == 27:
                raise KeyboardInterrupt
            continue

        headline = "Select a song with arrow keys and ENTER. Press ESC to cancel."
        stdscr.addnstr(0, 0, headline, width - 1)
        for index, path in enumerate(songs):
            row = index + 2
            if row >= height - 1:
                break
            prefix = "▶" if index == selected_index else " "
            line = f"{prefix} {path.stem}"
            stdscr.addnstr(row, 0, line, width - 1)

        stdscr.refresh()

        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            selected_index = max(0, selected_index - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            selected_index = min(len(songs) - 1, selected_index + 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            if missing_status[selected_index]:
                warning = "Selected song cannot be rendered because its artifact directory is missing."
                stdscr.addnstr(height - 2, 0, warning, width - 1)
                stdscr.refresh()
                stdscr.getch()
                continue
            return songs[selected_index]
        elif key == 27:
            raise KeyboardInterrupt


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a DMX show from a selected song.")
    parser.add_argument(
        "--show-name",
        default="main-show",
        help="Optional show name. Valid characters: A-Z a-z 0-9 _ -.",
    )
    parser.add_argument(
        "--export-layout",
        action="store_true",
        help="Export an SVG debug view of the stage layout to data/shows/ and exit.",
    )
    parser.add_argument(
        "--song",
        help="Optional song file or stem to render without opening the selector.",
    )
    parser.add_argument(
        "--ui-playback",
        action="store_true",
        help="Keep the WebSocket server alive after baking so the UI can request playback.",
    )
    parser.add_argument(
        "--layout-output",
        default="data/shows/stage-layout.svg",
        help="Output path for --export-layout.",
    )
    args = parser.parse_args()

    try:
        show_name = validate_show_name(args.show_name)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    if args.export_layout:
        try:
            output_path = export_stage_layout_svg(Path(args.layout_output))
            print(f"Layout written to: {output_path}")
            return 0
        except Exception as exc:
            print(f"Failed to export layout: {exc}")
            return 1

    songs = list_song_choices()
    if not songs:
        print("No songs found in data/songs/. Please add .mp3 files to the directory.")
        return 1

    if args.ui_playback:
        websocket_server = EngineWebSocketServer(evaluator=None, song_name="")

        def compile_selected_song(song_value: str) -> None:
            selected_path = resolve_song_choice(song_value, songs)
            websocket_server.set_song_name(selected_path.stem)
            output_path = compile_dmx_show(selected_path, show_name, websocket_server=websocket_server)
            websocket_server.notify_ready()
            print(f"Show written to: {output_path}", flush=True)

        websocket_server.set_song_selection_handler(compile_selected_song)
        websocket_server.start()
        print("Waiting for a UI client to select a song on ws://0.0.0.0:3301/ws/canvas")

        if args.song:
            try:
                compile_selected_song(args.song)
            except ValueError as exc:
                print(f"Error: {exc}", file=sys.stderr)
                websocket_server.notify_error(str(exc))
            except Exception as exc:
                print(f"Failed to compile show: {exc}", file=sys.stderr)
                websocket_server.notify_error(str(exc))

        try:
            websocket_server.wait_forever()
            return 0
        except KeyboardInterrupt:
            print("Interrupted before rendering began.")
            return 1

    try:
        if args.song:
            selected_path = resolve_song_choice(args.song, songs)
        else:
            selected_path = curses.wrapper(run_curses_selector, songs)
    except KeyboardInterrupt:
        print("Interrupted before rendering began.")
        return 1
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    websocket_server = None
    if args.ui_playback:
        websocket_server = EngineWebSocketServer(evaluator=None, song_name=selected_path.stem)
        websocket_server.start()

    try:
        if websocket_server is None:
            output_path = compile_dmx_show(selected_path, show_name)
        else:
            output_path = compile_dmx_show(selected_path, show_name, websocket_server=websocket_server)
        if websocket_server is not None:
            websocket_server.notify_ready()
        print(f"Show written to: {output_path}")
        if websocket_server is not None:
            print("Waiting for a UI client to start playback on ws://0.0.0.0:3301/ws/canvas")
            websocket_server.wait_for_playback()
        return 0
    except Exception as exc:
        print(f"Failed to compile show: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
