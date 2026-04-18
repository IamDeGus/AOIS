from dataclasses import replace

from src.analysis import analyze_expression, format_analysis
from src.analysis import report as report_module
from src.minimization import CoverageTable, GluePair, GlueStage


def test_format_analysis_contains_all_main_sections() -> None:
    result = analyze_expression("a & b")

    rendered = format_analysis(result)

    assert "=== Truth Table ===" in rendered
    assert "=== Canonical Forms ===" in rendered
    assert "=== Boolean Derivatives (1..4 order) ===" in rendered
    assert "=== Minimization: Calculation ===" in rendered
    assert "=== Minimization: Calculation-Tabular ===" in rendered
    assert "=== Minimization: Karnaugh ===" in rendered
    assert "Selected groups:" in rendered
    assert "K-map" in rendered


def test_format_analysis_without_derivatives_and_empty_tables() -> None:
    result = analyze_expression("a & b")
    without_derivatives = replace(result, derivatives=())

    rendered = format_analysis(without_derivatives)
    assert "No derivatives for constant function" in rendered

    assert report_module._format_glue_stages((), indent="  ") == ["  Glue stages: (none)"]
    assert report_module._format_coverage_table(CoverageTable(columns=(), rows=()), indent="    ") == ["    (empty)"]

    lines = report_module._format_glue_stages(
        (
            GlueStage(
                iteration=1,
                pairs=(GluePair(left="00", right="01", merged="0-"),),
            ),
        ),
        indent="  ",
    )
    assert any("Iteration 1" in line for line in lines)
