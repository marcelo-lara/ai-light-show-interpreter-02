import tempfile
from pathlib import Path

import pytest

from src.io.show_compiler import compile_dmx_show


def test_missing_artifact_directory_raises_error() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        song_path = root / "data" / "songs" / "missing.mp3"
        song_path.parent.mkdir(parents=True)
        song_path.write_text("dummy", encoding="utf-8")

        with pytest.raises(FileNotFoundError):
            compile_dmx_show(
                song_path,
                "demo",
                artifact_root=root / "data" / "artifacts",
                fixture_path=root / "data" / "fixtures" / "fixtures.json",
                poi_path=root / "data" / "fixtures" / "pois.json",
                stage_virtual_canvas_path=root / "src" / "config" / "stage_virtual_canvas.json",
                shows_root=root / "data" / "shows",
            )


def test_invalid_show_name_is_rejected_by_main_invalid_path() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        with pytest.raises(FileNotFoundError):
            compile_dmx_show(
                root / "missing_song.mp3",
                "demo",
                artifact_root=root / "data" / "artifacts",
                fixture_path=root / "data" / "fixtures" / "fixtures.json",
                poi_path=root / "data" / "fixtures" / "pois.json",
                stage_virtual_canvas_path=root / "src" / "config" / "stage_virtual_canvas.json",
                shows_root=root / "data" / "shows",
            )
