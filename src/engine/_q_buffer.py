from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


class MusicalStateBuffer(dict):
    """A dictionary-like container for per-frame musical render state."""

    time: float
    bands: np.ndarray
    intensity_hit: float
    cumulative_rotation: float
    mid_warp: float
    section_label: str
    section_progress: float
    cue_trigger: float


class ArtifactValidationError(ValueError):
    pass


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_fft_levels(levels: list[float]) -> np.ndarray:
    if len(levels) == 5:
        return np.asarray(levels, dtype=float)
    if len(levels) == 7:
        source = np.asarray(levels, dtype=float)
        return np.asarray(
            [
                source[0],
                source[1],
                (source[2] + source[3]) * 0.5,
                (source[4] + source[5]) * 0.5,
                source[6],
            ],
            dtype=float,
        )
    raise ArtifactValidationError(
        f"FFT frame contains {len(levels)} bands; expected 5 canonical values or 7 upstream values."
    )


def _find_section(sections: list[dict[str, Any]], time: float) -> dict[str, Any]:
    for section in sections:
        if section.get("start", 0.0) <= time < section.get("end", 0.0):
            return section
    return sections[-1] if sections else {"label": "unknown", "start": 0.0, "end": time or 1.0}


def _validate_beats_metadata(beats: dict[str, Any]) -> float:
    duration = beats.get("duration")
    if not isinstance(duration, (int, float)) or duration <= 0:
        raise ArtifactValidationError("beats.json must define a positive numeric duration.")

    beat_grid = beats.get("beats")
    if not isinstance(beat_grid, list) or not beat_grid:
        raise ArtifactValidationError("beats.json must define a non-empty beats list.")

    previous_time = -1.0
    for beat in beat_grid:
        if not isinstance(beat, dict):
            raise ArtifactValidationError("Each beat entry must be an object.")

        time = beat.get("time")
        bar = beat.get("bar")
        beat_in_bar = beat.get("beat_in_bar")
        if not isinstance(time, (int, float)):
            raise ArtifactValidationError("Each beat entry must include a numeric time.")
        if time < 0 or time > duration or time < previous_time:
            raise ArtifactValidationError("Beat times must be monotonically increasing within song duration.")
        if not isinstance(bar, int) or bar < 1:
            raise ArtifactValidationError("Each beat entry must include a positive integer bar number.")
        if not isinstance(beat_in_bar, int) or beat_in_bar < 1:
            raise ArtifactValidationError("Each beat entry must include a positive integer beat_in_bar value.")
        previous_time = float(time)

    return float(duration)


def _event_time(item: dict[str, Any]) -> Any:
    if item.get("time_s") is not None:
        return item.get("time_s")
    return item.get("time")


def _anchor_matches(anchor: dict[str, Any], refs: dict[str, Any]) -> bool:
    section_id = refs.get("section_id")
    phrase_window_id = refs.get("phrase_window_id")

    if section_id is not None and anchor.get("section_id") != section_id:
        return False
    if phrase_window_id is not None and anchor.get("phrase_window_id") != phrase_window_id:
        return False

    return section_id is not None or phrase_window_id is not None


def _has_resolvable_anchor_reference(
    item: dict[str, Any],
    anchors_by_id: dict[str, dict[str, Any]],
    anchors: list[dict[str, Any]],
) -> bool:
    anchor_id = item.get("anchor_id")
    if isinstance(anchor_id, str) and anchor_id in anchors_by_id:
        return True

    anchor_refs = item.get("anchor_refs")
    if not isinstance(anchor_refs, dict):
        return False

    cue_anchor_ids = anchor_refs.get("cue_anchor_ids")
    if isinstance(cue_anchor_ids, list) and cue_anchor_ids:
        return all(isinstance(anchor_ref, str) and anchor_ref in anchors_by_id for anchor_ref in cue_anchor_ids)

    return any(_anchor_matches(anchor, anchor_refs) for anchor in anchors)


def _validate_cues(
    cues: list[dict[str, Any]],
    duration: float,
    anchors_by_id: dict[str, dict[str, Any]],
    anchors: list[dict[str, Any]],
) -> bool:
    last_time = -1.0
    for item in cues:
        time = _event_time(item)
        if not isinstance(time, (int, float)):
            return False
        if time < 0 or time > duration or time < last_time:
            return False
        if not item.get("type") and not item.get("event_type"):
            return False
        if not _has_resolvable_anchor_reference(item, anchors_by_id, anchors):
            return False
        last_time = float(time)
    return True


def _load_event_cues(song_artifact_dir: Path, duration: float) -> list[dict[str, Any]]:
    event_path = song_artifact_dir / "lighting_events.json"
    if not event_path.exists():
        return []

    data = _load_json(event_path)
    if not isinstance(data, dict):
        return []

    anchors = data.get("cue_anchors")
    if not isinstance(anchors, list):
        return []
    anchors_by_id = {
        anchor["id"]: anchor
        for anchor in anchors
        if isinstance(anchor, dict) and isinstance(anchor.get("id"), str)
    }

    cues = data.get("lighting_events")
    if not isinstance(cues, list):
        return []

    if not _validate_cues(cues, duration, anchors_by_id, anchors):
        return []

    return [
        {
            "time": float(_event_time(item)),
            "strength": float(item.get("strength", item.get("intensity", 1.0))),
            "type": item.get("type", item.get("event_type", "accent")),
        }
        for item in cues
    ]


def _map_cues_to_frame_time(time: float, cues: list[dict[str, Any]], window: float = 0.05) -> float:
    for cue in cues:
        if abs(cue["time"] - time) <= window:
            return min(1.0, max(0.0, cue["strength"]))
    return 0.0


def _build_section_progress(section: dict[str, Any], time: float) -> float:
    start = float(section.get("start", 0.0))
    end = float(section.get("end", start + 1.0))
    if end <= start:
        return 0.0
    return min(1.0, max(0.0, (time - start) / (end - start)))


def build_musical_state_stream(
    song_artifact_dir: Path,
    attack: float = 0.3,
    release: float = 0.6,
) -> list[MusicalStateBuffer]:
    beats_path = song_artifact_dir / "essentia" / "beats.json"
    fft_path = song_artifact_dir / "essentia" / "fft_bands.json"
    sections_path = song_artifact_dir / "section_segmentation" / "sections.json"

    beats = _load_json(beats_path)
    fft = _load_json(fft_path)
    sections = _load_json(sections_path)

    if not isinstance(beats, dict):
        raise ArtifactValidationError("beats.json must contain a JSON object.")
    if not isinstance(fft, dict):
        raise ArtifactValidationError("fft_bands.json must contain a JSON object.")
    if not isinstance(sections, dict):
        raise ArtifactValidationError("sections.json must contain a JSON object.")

    duration = _validate_beats_metadata(beats)
    frames = fft.get("frames", [])
    section_list = sections.get("sections", [])
    cues = _load_event_cues(song_artifact_dir, duration)

    smoothed_bands = np.zeros(5, dtype=float)
    states: list[MusicalStateBuffer] = []
    cumulative_rotation = 0.0

    for frame in frames:
        time = float(frame.get("time", 0.0))
        levels = frame.get("levels")
        if not isinstance(levels, list):
            raise ArtifactValidationError("FFT frames must contain a levels list.")

        bands = normalize_fft_levels(levels)
        alpha = attack if bands.mean() >= smoothed_bands.mean() else release
        smoothed_bands = smoothed_bands * (1.0 - alpha) + bands * alpha

        intensity_hit = float(frame.get("transient_strength", 0.0))
        intensity_hit = max(intensity_hit, float(np.max(bands)) * 0.25)
        cumulative_rotation += float(smoothed_bands[2]) * 0.02
        mid_warp = float(smoothed_bands[2] * 0.4 + smoothed_bands[3] * 0.25)

        section = _find_section(section_list, time)
        cue_trigger = _map_cues_to_frame_time(time, cues) if cues else float(frame.get("transient_strength", 0.0))

        state = MusicalStateBuffer(
            time=time,
            bands=smoothed_bands.copy(),
            intensity_hit=float(intensity_hit),
            cumulative_rotation=float(cumulative_rotation),
            mid_warp=float(mid_warp),
            section_label=str(section.get("label", "unknown")),
            section_progress=_build_section_progress(section, time),
            cue_trigger=cue_trigger,
        )
        states.append(state)

    if not states:
        raise ArtifactValidationError("No FFT frames found for song artifact.")

    return states
