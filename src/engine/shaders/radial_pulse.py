from __future__ import annotations

import numpy as np


def radial_pulse(coords: np.ndarray, state: dict, center: tuple[float, float] = (5.0, 2.5), width: float = 2.0) -> np.ndarray:
    offsets = coords - np.asarray(center, dtype=float)
    distances = np.linalg.norm(offsets, axis=1)
    phase = (distances / width) - float(state.get("time", 0.0)) * 1.2
    base = 0.5 + 0.5 * np.cos(phase)
    energy = float(state.get("intensity_hit", 0.0)) * 1.5 + float(state["bands"][0]) * 0.3
    energy = np.clip(energy, 0.0, 1.0)
    return np.clip(base * energy, 0.0, 1.0)
