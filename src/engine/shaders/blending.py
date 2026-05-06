from __future__ import annotations

import numpy as np


def additive_blend(*layers: np.ndarray) -> np.ndarray:
    if not layers:
        return np.array([])
    stacked = np.stack(layers, axis=0)
    return np.clip(np.sum(stacked, axis=0), 0.0, 1.0)


def multiplicative_blend(base: np.ndarray, mask: float | np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(base) * mask, 0.0, 1.0)
