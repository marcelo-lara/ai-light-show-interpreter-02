import numpy as np

from src.engine.shaders.blending import additive_blend, multiplicative_blend
from src.engine.shaders.linear_wave import linear_wave
from src.engine.shaders.radial_pulse import radial_pulse


def _build_state() -> dict:
    return {
        "time": 0.1,
        "bands": np.array([0.2, 0.4, 0.6, 0.3, 0.1]),
        "intensity_hit": 0.8,
        "mid_warp": 0.2,
        "section_label": "verse",
        "section_progress": 0.3,
        "cue_trigger": 0.1,
    }


def test_radial_pulse_shape_and_bounds() -> None:
    coords = np.array([[1.0, 1.0], [5.0, 2.5], [8.0, 4.0]])
    state = _build_state()
    result = radial_pulse(coords, state)

    assert result.shape == (3,)
    assert np.all(result >= 0.0)
    assert np.all(result <= 1.0)


def test_linear_wave_shape_and_response() -> None:
    coords = np.array([[0.0, 0.0], [10.0, 0.0]])
    state = _build_state()
    result = linear_wave(coords, state)

    assert result.shape == (2,)
    assert np.all(result >= 0.0)
    assert np.all(result <= 1.0)
    assert not np.allclose(result[0], result[1])


def test_blending_functions() -> None:
    a = np.array([0.2, 0.3])
    b = np.array([0.5, 0.4])
    sum_layer = additive_blend(a, b)
    product_layer = multiplicative_blend(a, b)

    assert np.allclose(sum_layer, [0.7, 0.7])
    assert np.allclose(product_layer, [0.1, 0.12])
