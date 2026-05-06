from __future__ import annotations

import numpy as np

from src.engine.shaders.blending import additive_blend, multiplicative_blend
from src.engine.shaders.linear_wave import linear_wave
from src.engine.shaders.radial_pulse import radial_pulse


class Evaluator:
    def __init__(self, canvas_width: float, canvas_height: float, fixtures: list[dict], pois: dict[str, dict]):
        self.canvas_width = float(canvas_width)
        self.canvas_height = float(canvas_height)
        self.fixtures = fixtures
        self.pois = pois
        self.fixture_coords = self._build_mesh(fixtures)

    def _build_mesh(self, fixtures: list[dict]) -> np.ndarray:
        coords = []
        for fixture in fixtures:
            position = fixture.get("position")
            if not isinstance(position, list) or len(position) != 2:
                raise ValueError("Each virtual canvas fixture must define a position [x, y].")
            coords.append([float(position[0]), float(position[1])])
        return np.asarray(coords, dtype=float)

    def _warp_coordinates(self, coords: np.ndarray, state: dict) -> np.ndarray:
        warped = coords.copy()
        warp_strength = float(state.get("mid_warp", 0.0))
        if warp_strength <= 0:
            return warped

        angle = float(state.get("time", 0.0)) * 0.75
        warped[:, 0] += np.sin(warped[:, 1] * 2.0 + angle) * warp_strength
        warped[:, 1] += np.cos(warped[:, 0] * 1.5 + angle) * (warp_strength * 0.5)
        warped[:, 0] = np.clip(warped[:, 0], 0.0, self.canvas_width)
        warped[:, 1] = np.clip(warped[:, 1], 0.0, self.canvas_height)
        return warped

    def _fixture_color(self, state: dict, fixture: dict) -> tuple[int, int, int]:
        base_r = float(state["bands"][1])
        base_g = float(state["bands"][2])
        base_b = float(state["bands"][3])
        cue = float(state.get("cue_trigger", 0.0))

        red = min(1.0, base_r * 0.9 + cue * 0.35)
        green = min(1.0, base_g * 0.85 + cue * 0.2)
        blue = min(1.0, base_b * 0.8 + cue * 0.15)

        if fixture.get("type") == "moving_head":
            red = min(1.0, red * 1.1)
            green = min(1.0, green * 0.9)

        return (
            int(red * 255),
            int(green * 255),
            int(blue * 255),
        )

    def evaluate_frame(self, state: dict) -> list[dict]:
        warped = self._warp_coordinates(self.fixture_coords, state)
        pulse = radial_pulse(warped, state)
        wave = linear_wave(warped, state)

        intensity = additive_blend(pulse, wave)
        intensity = multiplicative_blend(intensity, 1.0 + float(state["bands"][1]) * 0.1)

        render_states = []
        for index, fixture in enumerate(self.fixtures):
            value = float(intensity[index])
            value *= 1.0 + float(state.get("cue_trigger", 0.0)) * 0.22
            if "percussion" in state.get("section_label", ""):
                value *= 1.05
            if "ambient" in state.get("section_label", ""):
                value *= 0.92
            value = min(1.0, max(0.0, value))

            render_states.append(
                {
                    "fixture_id": fixture["source_fixture_id"],
                    "dimmer": int(value * 255),
                    "color_rgb": self._fixture_color(state, fixture),
                    "target_poi": fixture.get("target_poi") if fixture.get("type") == "moving_head" else None,
                }
            )

        return render_states

    def render_canvas_mesh(self, state: dict, resolution: tuple[int, int] = (20, 10)) -> dict[str, object]:
        width, height = resolution
        xs = np.linspace(0.0, self.canvas_width, width)
        ys = np.linspace(0.0, self.canvas_height, height)
        grid_x, grid_y = np.meshgrid(xs, ys)
        coords = np.stack([grid_x.ravel(), grid_y.ravel()], axis=-1)

        warped = self._warp_coordinates(coords, state)
        pulse = radial_pulse(warped, state)
        wave = linear_wave(warped, state)
        intensity = additive_blend(pulse, wave)
        intensity = multiplicative_blend(intensity, 1.0 + float(state["bands"][1]) * 0.1)

        cue = float(state.get("cue_trigger", 0.0))
        red = np.clip(intensity * (float(state["bands"][1]) * 0.9 + 0.2) + cue * 0.2, 0.0, 1.0)
        green = np.clip(intensity * (float(state["bands"][2]) * 0.9 + 0.15) + cue * 0.15, 0.0, 1.0)
        blue = np.clip(intensity * (float(state["bands"][3]) * 0.8 + 0.1) + cue * 0.1, 0.0, 1.0)

        pixels = []
        for row_index in range(height):
            row = []
            for col_index in range(width):
                idx = row_index * width + col_index
                row.append([
                    int(red[idx] * 255),
                    int(green[idx] * 255),
                    int(blue[idx] * 255),
                ])
            pixels.append(row)

        return {"resolution": [width, height], "pixels": pixels}
