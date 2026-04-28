from __future__ import annotations

import os
import struct
from pathlib import Path
from typing import Iterable

import json


class DmxWriter:
    def __init__(self, output_path: Path, fixtures_path: Path, pois_path: Path, frame_rate: int = 50):
        self.output_path = output_path
        self.temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
        self.frame_rate = int(frame_rate)
        self.fixtures = self._load_fixtures(fixtures_path)
        self.pois = self._load_pois(pois_path)
        self._handle = None

    def _load_fixtures(self, fixtures_path: Path) -> dict[str, dict]:
        with fixtures_path.open("r", encoding="utf-8") as handle:
            fixtures = json.load(handle)
        return {fixture["id"]: fixture for fixture in fixtures}

    def _load_pois(self, pois_path: Path) -> dict[str, dict]:
        with pois_path.open("r", encoding="utf-8") as handle:
            pois = json.load(handle)
        return {poi["id"]: poi for poi in pois}

    def __enter__(self) -> "DmxWriter":
        self.temp_path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.temp_path.open("wb")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._handle is not None:
            self._handle.close()
        if exc is None:
            os.replace(self.temp_path, self.output_path)
        elif self.temp_path.exists():
            self.temp_path.unlink(missing_ok=True)

    def write_header(self, total_frames: int) -> None:
        if self._handle is None:
            raise RuntimeError("DMX writer is not open.")
        header = struct.pack(
            "<4sHHII16s",
            b"DMXP",
            1,
            1,
            int(total_frames),
            int(self.frame_rate),
            b"\x00" * 16,
        )
        self._handle.write(header)

    @staticmethod
    def _clamp_channel(value: int) -> int:
        return max(0, min(255, int(value)))

    def write_frame(self, timestamp_ms: int, render_states: Iterable[dict]) -> None:
        if self._handle is None:
            raise RuntimeError("DMX writer is not open.")

        universe = bytearray(512)
        for render_state in render_states:
            fixture_id = render_state.get("fixture_id")
            fixture = self.fixtures.get(fixture_id)
            if fixture is None:
                continue

            base_channel = int(fixture.get("base_channel", 1)) - 1
            if base_channel < 0 or base_channel >= 512:
                continue

            dimmer = self._clamp_channel(render_state.get("dimmer", 0))
            universe[base_channel] = dimmer

            color = render_state.get("color_rgb", (0, 0, 0))
            for offset, channel_value in enumerate(color, start=1):
                index = base_channel + offset
                if 0 <= index < 512:
                    universe[index] = self._clamp_channel(channel_value)

            if "moving_head" in fixture.get("fixture", ""):
                target_poi = render_state.get("target_poi")
                if target_poi and target_poi in self.pois:
                    poi = self.pois[target_poi]
                    poi_fixture = poi.get("fixtures", {}).get(fixture_id, {})
                    pan = int(poi_fixture.get("pan", 0))
                    tilt = int(poi_fixture.get("tilt", 0))
                    pan_byte = self._clamp_channel(pan >> 8)
                    tilt_byte = self._clamp_channel(tilt >> 8)
                    pan_index = base_channel + 4
                    tilt_index = base_channel + 5
                    if pan_index < 512:
                        universe[pan_index] = pan_byte
                    if tilt_index < 512:
                        universe[tilt_index] = tilt_byte

        self._handle.write(struct.pack("<I", int(timestamp_ms)))
        self._handle.write(bytes(universe))
