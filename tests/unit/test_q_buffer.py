import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.engine._q_buffer import ArtifactValidationError, build_musical_state_stream, normalize_fft_levels


def _write_json(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content), encoding="utf-8")


def test_normalize_fft_levels_reduces_seven_bands_to_five() -> None:
    values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
    normalized = normalize_fft_levels(values)

    assert normalized.shape == (5,)
    assert list(normalized) == [0.1, 0.2, 0.3, 0.4, 0.5]


def test_rejects_fft_frames_with_too_few_bands() -> None:
    with pytest.raises(ArtifactValidationError):
        normalize_fft_levels([0.1, 0.2, 0.3])


def test_section_progress_and_label_propagation() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        artifact_dir = root / "Cinderella - Ella Lee"
        _write_json(
            artifact_dir / "essentia" / "beats.json",
            {"duration": 10.0, "beats": []},
        )
        _write_json(
            artifact_dir / "essentia" / "fft_bands.json",
            {
                "frames": [
                    {"time": 0.0, "levels": [0.1, 0.1, 0.1, 0.1, 0.1], "transient_strength": 0.0},
                    {"time": 5.0, "levels": [0.1, 0.1, 0.1, 0.1, 0.1], "transient_strength": 0.0},
                ]
            },
        )
        _write_json(
            artifact_dir / "section_segmentation" / "sections.json",
            {
                "sections": [
                    {"start": 0.0, "end": 2.5, "label": "intro"},
                    {"start": 2.5, "end": 10.0, "label": "verse"},
                ]
            },
        )

        states = build_musical_state_stream(artifact_dir)
        assert states[0]["section_label"] == "intro"
        assert states[0]["section_progress"] == 0.0
        assert states[1]["section_label"] == "verse"
        assert 0.0 < states[1]["section_progress"] <= 1.0


def test_invalid_lighting_events_are_ignored() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        artifact_dir = root / "Cinderella - Ella Lee"
        _write_json(
            artifact_dir / "essentia" / "beats.json",
            {"duration": 10.0, "beats": []},
        )
        _write_json(
            artifact_dir / "essentia" / "fft_bands.json",
            {
                "frames": [
                    {"time": 0.0, "levels": [0.1, 0.1, 0.1, 0.1, 0.1], "transient_strength": 0.5},
                ]
            },
        )
        _write_json(
            artifact_dir / "section_segmentation" / "sections.json",
            {"sections": [{"start": 0.0, "end": 10.0, "label": "ambient"}]},
        )
        _write_json(
            artifact_dir / "lighting_events.json",
            {
                "lighting_events": [
                    {"time_s": 5.0, "type": "accent", "strength": 1.0},
                    {"time_s": 4.0, "type": "accent", "strength": 1.0},
                ]
            },
        )

        states = build_musical_state_stream(artifact_dir)
        assert all(state["cue_trigger"] >= 0.0 for state in states)
        assert states[0]["cue_trigger"] == 0.5
