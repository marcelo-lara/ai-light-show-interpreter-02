from pathlib import Path

import pytest

from src.main import validate_show_name, list_song_choices


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
