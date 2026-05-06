import subprocess
import sys
from pathlib import Path

import pytest

import src.main as cli_main
from src.main import list_song_choices, run_curses_selector, validate_show_name


class FakeScreen:
    def __init__(self, keys: list[int]):
        self.keys = list(keys)
        self.frames: list[list[str]] = []
        self.current_lines: list[str] = []

    def keypad(self, _enabled: bool) -> None:
        return None

    def erase(self) -> None:
        self.current_lines = []

    def getmaxyx(self) -> tuple[int, int]:
        return (20, 80)

    def addstr(self, _y: int, _x: int, text: str) -> None:
        self.current_lines.append(text)

    def addnstr(self, _y: int, _x: int, text: str, _limit: int) -> None:
        self.current_lines.append(text)

    def refresh(self) -> None:
        self.frames.append(list(self.current_lines))

    def getch(self) -> int:
        if not self.keys:
            raise AssertionError("No more keys available for fake screen.")
        return self.keys.pop(0)


def test_validate_show_name_accepts_safe_values() -> None:
    assert validate_show_name("main-show") == "main-show"
    assert validate_show_name("Show_01") == "Show_01"


def test_validate_show_name_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        validate_show_name("bad name")
    with pytest.raises(ValueError):
        validate_show_name("show!name")


def test_list_song_choices_finds_mp3_files(tmp_path: Path) -> None:
    songs_dir = tmp_path / "data" / "songs"
    songs_dir.mkdir(parents=True)
    (songs_dir / "track_a.mp3").write_text("dummy")
    (songs_dir / "track_b.txt").write_text("ignore")

    choices = list_song_choices(song_dir=songs_dir)
    assert [choice.name for choice in choices] == ["track_a.mp3"]


def test_run_curses_selector_moves_indicator_and_selects_song(monkeypatch: pytest.MonkeyPatch) -> None:
    songs = [Path("alpha.mp3"), Path("beta.mp3")]
    screen = FakeScreen(keys=[cli_main.curses.KEY_DOWN, 10])

    monkeypatch.setattr(cli_main.curses, "curs_set", lambda _value: None)
    monkeypatch.setattr(cli_main, "artifact_missing", lambda _song: False)

    selected = run_curses_selector(screen, songs)

    assert selected == songs[1]
    assert any("▶ alpha" in line for line in screen.frames[0])
    assert any("▶ beta" in line for line in screen.frames[1])


def test_missing_artifact_is_reported_only_after_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    songs = [Path("missing.mp3"), Path("ready.mp3")]
    screen = FakeScreen(keys=[10, ord("x"), cli_main.curses.KEY_DOWN, 10])

    monkeypatch.setattr(cli_main.curses, "curs_set", lambda _value: None)
    monkeypatch.setattr(cli_main, "artifact_missing", lambda song: song.stem == "missing")

    selected = run_curses_selector(screen, songs)

    assert selected == songs[1]
    assert all("MISSING ARTIFACT" not in "\n".join(frame) for frame in screen.frames[:1])
    assert any("artifact directory is missing" in line for line in screen.frames[1])


def test_main_defaults_to_main_show_when_omitted(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    song = Path("data/songs/Cinderella - Ella Lee.mp3")
    captured: dict[str, str] = {}

    def fake_compile(selected_song: Path, show_name: str) -> Path:
        captured["song"] = str(selected_song)
        captured["show_name"] = show_name
        return Path("data/shows/Cinderella - Ella Lee.main-show.dmx")

    monkeypatch.setattr(cli_main, "list_song_choices", lambda: [song])
    monkeypatch.setattr(cli_main.curses, "wrapper", lambda _func, songs: songs[0])
    monkeypatch.setattr(cli_main, "compile_dmx_show", fake_compile)
    monkeypatch.setattr(sys, "argv", ["main.py"])

    exit_code = cli_main.main()

    assert exit_code == 0
    assert captured["song"] == str(song)
    assert captured["show_name"] == "main-show"
    assert "main-show.dmx" in capsys.readouterr().out


def test_export_layout_defaults_outside_data_shows(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    captured: dict[str, Path] = {}

    def fake_export(output_path: Path) -> Path:
        captured["output_path"] = output_path
        return output_path

    monkeypatch.setattr(cli_main, "export_stage_layout_svg", fake_export)
    monkeypatch.setattr(sys, "argv", ["main.py", "--export-layout"])

    exit_code = cli_main.main()

    assert exit_code == 0
    assert captured["output_path"] == Path("stage-layout.svg")
    assert "data/shows" not in str(captured["output_path"])
    assert "stage-layout.svg" in capsys.readouterr().out


def test_cli_menu_renders_within_one_second() -> None:
    script = """
from pathlib import Path
import time
import src.main as cli_main

class FakeScreen:
    def keypad(self, _enabled):
        pass
    def erase(self):
        pass
    def getmaxyx(self):
        return (20, 80)
    def addstr(self, *_args):
        pass
    def addnstr(self, *_args):
        pass
    def refresh(self):
        pass
    def getch(self):
        return 10

cli_main.curses.curs_set = lambda _value: None
cli_main.artifact_missing = lambda _song: False
cli_main.run_curses_selector(FakeScreen(), [Path('timing.mp3')])
"""

    start = __import__("time").perf_counter()
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )
    elapsed = __import__("time").perf_counter() - start

    assert completed.returncode == 0
    assert elapsed < 1.0
