from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from src.engine._q_buffer import build_musical_state_stream
from src.engine.evaluator import Evaluator
from src.io.dmx_writer import DmxWriter


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def compile_dmx_show(
    song_path: Path,
    show_name: str,
    artifact_root: Path | None = None,
    fixture_path: Path | None = None,
    poi_path: Path | None = None,
    stage_virtual_canvas_path: Path | None = None,
    shows_root: Path | None = None,
    max_frames: int | None = None,
) -> Path:
    song_path = Path(song_path)
    artifact_root = artifact_root or Path("data/artifacts")
    fixture_path = fixture_path or Path("data/fixtures/fixtures.json")
    poi_path = poi_path or Path("data/fixtures/pois.json")
    stage_virtual_canvas_path = stage_virtual_canvas_path or Path("src/config/stage_virtual_canvas.json")
    shows_root = shows_root or Path("data/shows")

    if not song_path.is_file():
        raise FileNotFoundError(f"Song path does not exist: {song_path}")

    song_name = song_path.stem
    song_artifact_dir = artifact_root / song_name
    if not song_artifact_dir.is_dir():
        raise FileNotFoundError(f"Missing artifact directory for {song_name}")

    stage_data = _load_json(stage_virtual_canvas_path)
    canvas = stage_data.get("canvas", {})
    fixtures = stage_data.get("fixtures", [])
    if not fixtures:
        raise ValueError("Stage virtual canvas does not define any fixtures.")

    pois = _load_json(poi_path)
    pois_map = {poi["id"]: poi for poi in pois}
    evaluator = Evaluator(
        canvas_width=float(canvas.get("width", 10.0)),
        canvas_height=float(canvas.get("height", 5.0)),
        fixtures=fixtures,
        pois=pois_map,
    )

    musical_state_stream = build_musical_state_stream(song_artifact_dir)
    if max_frames is not None:
        musical_state_stream = musical_state_stream[:max_frames]

    shows_root.mkdir(parents=True, exist_ok=True)
    output_path = shows_root / f"{song_name}.{show_name}.dmx"

    with DmxWriter(output_path, fixture_path, poi_path, frame_rate=50) as writer:
        writer.write_header(len(musical_state_stream))
        for state in musical_state_stream:
            render_states = evaluator.evaluate_frame(state)
            writer.write_frame(int(state["time"] * 1000), render_states)

    return output_path
