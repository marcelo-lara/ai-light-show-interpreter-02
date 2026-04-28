from pathlib import Path

from src.io.show_compiler import compile_dmx_show


def test_deterministic_dmx_byte_output(tmp_path: Path) -> None:
    song_path = Path("data/songs/Cinderella - Ella Lee.mp3")
    out1 = tmp_path / "shows" / "run1"
    out2 = tmp_path / "shows" / "run2"
    out1.mkdir(parents=True)
    out2.mkdir(parents=True)

    result_1 = compile_dmx_show(song_path, "deterministic", shows_root=out1, max_frames=3)
    result_2 = compile_dmx_show(song_path, "deterministic", shows_root=out2, max_frames=3)

    assert result_1.exists()
    assert result_2.exists()
    assert result_1.read_bytes() == result_2.read_bytes()


def test_dmx_header_structure_matches_spec(tmp_path: Path) -> None:
    song_path = Path("data/songs/Cinderella - Ella Lee.mp3")
    output_dir = tmp_path / "shows"
    output_dir.mkdir(parents=True)

    output_path = compile_dmx_show(song_path, "contract", shows_root=output_dir, max_frames=2)
    assert output_path.exists()

    blob = output_path.read_bytes()
    assert blob[:4] == b"DMXP"
    assert int.from_bytes(blob[4:6], "little") == 1
    assert int.from_bytes(blob[6:8], "little") == 1
    assert int.from_bytes(blob[12:16], "little") == 50
    assert len(blob) == 32 + 2 * 516
