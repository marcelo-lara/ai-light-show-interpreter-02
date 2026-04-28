from pathlib import Path

from src.io.layout_debug import export_stage_layout_svg


def test_export_stage_layout_svg_contains_fixture_and_poi_labels(tmp_path: Path) -> None:
    output_path = tmp_path / "stage-layout.svg"

    result = export_stage_layout_svg(output_path)

    assert result == output_path
    assert output_path.exists()

    content = output_path.read_text(encoding="utf-8")
    assert "<svg" in content
    assert "mini_beam_prism_l" in content
    assert "table_center" in content
    assert "wall_art_center" in content
    assert "stroke-dasharray=\"6 4\"" in content
    assert "-&gt; piano_left" in content