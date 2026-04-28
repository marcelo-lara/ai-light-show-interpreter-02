import json
from pathlib import Path

from src.engine.evaluator import Evaluator
from src.io.show_compiler import compile_dmx_show


def test_evaluator_produces_states_for_all_canvas_fixtures() -> None:
    canvas_path = Path("src/config/stage_virtual_canvas.json")
    pois_path = Path("data/fixtures/pois.json")

    canvas_data = json.loads(canvas_path.read_text(encoding="utf-8"))
    fixtures = canvas_data["fixtures"]
    pois = {poi["id"]: poi for poi in json.loads(pois_path.read_text(encoding="utf-8"))}
    evaluator = Evaluator(
        canvas_width=float(canvas_data["canvas"]["width"]),
        canvas_height=float(canvas_data["canvas"]["height"]),
        fixtures=fixtures,
        pois=pois,
    )

    sample_song = Path("data/songs/Cinderella - Ella Lee.mp3")
    assert sample_song.exists()

    output_path = Path("data/artifacts/Cinderella - Ella Lee/essentia/fft_bands.json")
    assert output_path.exists()

    state = {
        "time": 0.0,
        "bands": __import__("numpy").array([0.1, 0.2, 0.3, 0.4, 0.5]),
        "intensity_hit": 0.2,
        "cumulative_rotation": 0.0,
        "mid_warp": 0.1,
        "section_label": "intro",
        "section_progress": 0.0,
        "cue_trigger": 0.0,
    }
    render_states = evaluator.evaluate_frame(state)

    assert len(render_states) == len(fixtures)
    for fixture_state in render_states:
        assert "fixture_id" in fixture_state
        assert 0 <= fixture_state["dimmer"] <= 255
        assert len(fixture_state["color_rgb"]) == 3


def test_compile_dmx_show_returns_expected_path(tmp_path: Path) -> None:
    song_path = Path("data/songs/Cinderella - Ella Lee.mp3")
    output_dir = tmp_path / "shows"
    output_dir.mkdir(parents=True)

    output_path = compile_dmx_show(
        song_path,
        "test-show",
        shows_root=output_dir,
        max_frames=2,
    )

    assert output_path.exists()
    assert output_path.name == "Cinderella - Ella Lee.test-show.dmx"
