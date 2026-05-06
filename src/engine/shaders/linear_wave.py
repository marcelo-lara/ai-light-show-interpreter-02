from __future__ import annotations

import numpy as np


def linear_wave(coords: np.ndarray, state: dict, wavelength: float = 4.0, speed: float = 0.3) -> np.ndarray:
    axis = coords[:, 0]
    phase = axis * (2.0 * np.pi / wavelength) - float(state.get("time", 0.0)) * speed
    base = 0.5 + 0.5 * np.sin(phase)
    reaction = float(state["bands"][2]) * 0.9 + float(state.get("cue_trigger", 0.0)) * 0.3
    return np.clip(base * reaction, 0.0, 1.0)
