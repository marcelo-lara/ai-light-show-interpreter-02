from __future__ import annotations

import json
from pathlib import Path


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _derive_canvas_pois(stage_data: dict, poi_path: Path) -> list[dict]:
    canvas = stage_data.get("canvas", {})
    width = float(canvas.get("width", 10.0))
    height = float(canvas.get("height", 5.0))

    if stage_data.get("pois"):
        return stage_data["pois"]

    pois = _load_json(poi_path)
    derived = []
    for poi in pois:
        location = poi.get("location", {})
        derived.append(
            {
                "id": poi["id"],
                "source_poi_id": poi["id"],
                "position": [float(location.get("x", 0.0)) * width, float(location.get("y", 0.0)) * height],
                "group": "derived",
            }
        )
    return derived


def export_stage_layout_svg(
    output_path: Path,
    stage_virtual_canvas_path: Path | None = None,
    poi_path: Path | None = None,
) -> Path:
    stage_virtual_canvas_path = stage_virtual_canvas_path or Path("src/config/stage_virtual_canvas.json")
    poi_path = poi_path or Path("data/fixtures/pois.json")

    stage_data = _load_json(stage_virtual_canvas_path)
    canvas = stage_data.get("canvas", {})
    fixtures = stage_data.get("fixtures", [])
    pois = _derive_canvas_pois(stage_data, poi_path)

    canvas_width = float(canvas.get("width", 10.0))
    canvas_height = float(canvas.get("height", 5.0))
    scale = 100
    padding = 40
    width_px = int(canvas_width * scale + padding * 2)
    height_px = int(canvas_height * scale + padding * 2)

    def to_x(value: float) -> float:
        return padding + value * scale

    def to_y(value: float) -> float:
        return padding + value * scale

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" viewBox="0 0 {width_px} {height_px}">',
        '<rect width="100%" height="100%" fill="#ffffff" />',
        f'<rect x="{padding}" y="{padding}" width="{canvas_width * scale}" height="{canvas_height * scale}" fill="#f8f8fb" stroke="#222" stroke-width="2" />',
        f'<text x="{padding}" y="24" font-family="monospace" font-size="16" fill="#111">Stage Layout Debug Export</text>',
    ]

    poi_lookup = {poi.get("id"): poi for poi in pois}

    for fixture in fixtures:
        if fixture.get("type") != "moving_head":
            continue
        target_poi = fixture.get("target_poi")
        poi = poi_lookup.get(target_poi)
        if not poi:
            continue
        fixture_x, fixture_y = fixture.get("position", [0.0, 0.0])
        poi_x, poi_y = poi.get("position", [0.0, 0.0])
        parts.append(
            f'<line x1="{to_x(float(fixture_x))}" y1="{to_y(float(fixture_y))}" '
            f'x2="{to_x(float(poi_x))}" y2="{to_y(float(poi_y))}" '
            'stroke="#ff7f0e" stroke-width="2" stroke-dasharray="6 4" opacity="0.85" />'
        )

    for poi in pois:
        x, y = poi.get("position", [0.0, 0.0])
        px = to_x(float(x))
        py = to_y(float(y))
        label = _escape_xml(str(poi.get("id", "poi")))
        parts.append(f'<rect x="{px - 4}" y="{py - 4}" width="8" height="8" fill="#1f77b4" stroke="#0d3b66" stroke-width="1" />')
        parts.append(f'<text x="{px + 8}" y="{py + 4}" font-family="monospace" font-size="12" fill="#0d3b66">{label}</text>')

    for fixture in fixtures:
        x, y = fixture.get("position", [0.0, 0.0])
        px = to_x(float(x))
        py = to_y(float(y))
        fixture_type = fixture.get("type", "fixture")
        label = _escape_xml(str(fixture.get("id", "fixture")))
        color = "#7b68ee" if fixture_type == "moving_head" else "#b8b8d9"
        parts.append(f'<circle cx="{px}" cy="{py}" r="16" fill="{color}" stroke="#222" stroke-width="1.5" />')
        parts.append(f'<text x="{px}" y="{py + 4}" text-anchor="middle" font-family="monospace" font-size="10" fill="#111">{label}</text>')
        if fixture_type == "moving_head" and fixture.get("target_poi"):
            target_label = _escape_xml(str(fixture.get("target_poi")))
            parts.append(f'<text x="{px}" y="{py - 22}" text-anchor="middle" font-family="monospace" font-size="9" fill="#a34d00">-&gt; {target_label}</text>')

    parts.append('</svg>')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(parts), encoding="utf-8")
    return output_path