"""
Contract Interface: Procedural Shader API
This defines the structural boundaries of a pattern generator/shader
that the Evaluator function must call via NumPy.
"""
from typing import TypedDict
import numpy as np

class MusicalStateBuffer(TypedDict):
    """The `q_buffer` injected into all shaders per 20ms frame."""
    time: float
    bands: np.ndarray  # Shape (5,)
    intensity_hit: float
    cumulative_rotation: float
    mid_warp: float

class EvaluatorInterface:
    """
    Contract for rendering multiple shaders into a single output frame on a 2D mesh.
    """
    def __init__(self, canvas_width: float, canvas_height: float, fixtures: list[dict]):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.fixture_coords = self._build_mesh(fixtures)

    def _build_mesh(self, fixtures: list[dict]) -> np.ndarray:
        """
        Extract exact fixed-sample fixture coordinates from the derived virtual canvas.
        Moving heads carry named POI targets in v1 but still resolve to a single sampling coordinate per frame.
        Returns: NumPy array of shape (N, 2) where N is number of fixtures.
        """
        pass

    def evaluate_frame(self, state: MusicalStateBuffer) -> np.ndarray:
        """
        Core pipeline rasterizer.
        1. Base coordinates
        2. Apply mid-warp spatial distortion algorithm
        3. Iterate active layered procedural shaders (e.g., radial pulse, linear wave)
        4. Blend intensities additively or multiplicatively
        Returns: NumPy array of shape (N,) containing calculated intensity at each fixture location.
        """
        pass

def procedural_shader_contract(coords: np.ndarray, state: MusicalStateBuffer, **kwargs) -> np.ndarray:
    """
    A single mathematical visualizer (like a wave or a pulse).
    Arguments:
        coords: Spatial (X,Y) layout block of the fixtures, shape (N, 2).
        state: The `q_buffer` ensuring musical awareness.
        kwargs: Shader-specific params (e.g., speed, angle, thickness).
    Returns:
        Array of intensities corresponding to `coords`, shape (N,).
    """
    pass
