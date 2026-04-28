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
    if len(levels) > 5:
        return np.asarray(levels[:5], dtype=float)
    raise ArtifactValidationError(
        f"FFT frame contains {len(levels)} bands; expected exactly 5 canonical values."
    )


def _find_section(sections: list[dict[str, Any]], time: float) -> dict[str, Any]:
    for section in sections:
        if section.get("start", 0.0) <= time < section.get("end", 0.0):
            return section
    return sections[-1] if sections else {"label": "unknown", "start": 0.0, "end": time or 1.0}


def _validate_cues(cues: list[dict[str, Any]], duration: float) -> bool:
    last_time = -1.0
    for item in cues:
        time = item.get("time_s") if item.get("time_s") is not None else item.get("time")
        if not isinstance(time, (int, float)):
            return False
        if time < 0 or time > duration or time < last_time:
            return False
        if not item.get("type"):
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

    cues = data.get("lighting_events")
    if not isinstance(cues, list):
        return []

    if not _validate_cues(cues, duration):
        return []

    return [
        {
            "time": float(item.get("time_s", item.get("time", 0.0))),
            "strength": float(item.get("strength", 1.0)) if item.get("strength") is not None else 1.0,
            "type": item.get("type", "accent"),
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

    duration = float(beats.get("duration", beats.get("tempo", 0.0)))
    frames = fft.get("frames", [])
    section_list = sections.get("sections", [])
    cues = _load_event_cues(song_artifact_dir, duration)

    smoothed_bands = np.zeros(5, dtype=float)
    previous_intensity = 0.0
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
        previous_intensity = intensity_hit

    if not states:
        raise ArtifactValidationError("No FFT frames found for song artifact.")

    return states
