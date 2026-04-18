from __future__ import annotations

from .pipeline import AnalysisResult
from ..minimization import CoverageTable, GlueStage, MinimizationResult


def format_analysis(result: AnalysisResult) -> str:
    lines: list[str] = []

    lines.append(f"Function: {result.expression}")
    lines.append(f"Variables: {', '.join(result.table.variables) or '(none)'}")
    lines.append("")

    lines.append("=== Truth Table ===")
    lines.extend(_format_truth_table(result))
    lines.append("")

    lines.append("=== Canonical Forms ===")
    lines.append(f"SDNF: {result.forms.sdnf}")
    lines.append(f"SKNF: {result.forms.sknf}")
    lines.append(f"SDNF numeric: {result.forms.sdnf_numeric}")
    lines.append(f"SKNF numeric: {result.forms.sknf_numeric}")
    lines.append(f"Index form: {result.forms.index_form}")
    lines.append("")

    lines.append("=== Post Classes ===")
    lines.append(f"T0={int(result.post.t0)} T1={int(result.post.t1)} S={int(result.post.s)} M={int(result.post.m)} L={int(result.post.l)}")
    lines.append("")

    lines.append("=== Zhegalkin Polynomial ===")
    lines.append(result.zhegalkin.polynomial)
    lines.append("")

    lines.append("=== Fictive Variables ===")
    lines.append(f"Essential: {', '.join(result.fictive_vars.essential) or '(none)'}")
    lines.append(f"Fictive: {', '.join(result.fictive_vars.fictive) or '(none)'}")
    lines.append("")

    lines.append("=== Boolean Derivatives (1..4 order) ===")
    if not result.derivatives:
        lines.append("No derivatives for constant function")
    else:
        for derivative in result.derivatives:
            suffix = "".join(derivative.variables)
            lines.append(f"d/d{suffix}: vector={''.join(str(v) for v in derivative.vector)}")
            lines.append(f"  SDNF: {derivative.sdnf}")
            lines.append(f"  SKNF: {derivative.sknf}")
    lines.append("")

    lines.append("=== Minimization: Calculation ===")
    lines.extend(_format_minimization(result.minimize_calculation))
    lines.append("")

    lines.append("=== Minimization: Calculation-Tabular ===")
    lines.extend(_format_minimization(result.minimize_calculation_tabular))
    lines.append("")

    lines.append("=== Minimization: Karnaugh ===")
    lines.extend(_format_minimization(result.minimize_karnaugh))

    return "\n".join(lines)


def _format_truth_table(result: AnalysisResult) -> list[str]:
    headers = ["idx", *result.table.variables, "f"]
    widths = [max(3, len(header)) for header in headers]

    lines: list[str] = []
    header_line = " | ".join(header.rjust(width) for header, width in zip(headers, widths, strict=True))
    lines.append(header_line)
    lines.append("-+-".join("-" * width for width in widths))

    for row in result.table.rows:
        cells = [str(row.index), *(str(value) for value in row.values), str(row.result)]
        lines.append(" | ".join(cell.rjust(width) for cell, width in zip(cells, widths, strict=True)))

    return lines


def _format_minimization(result: MinimizationResult) -> list[str]:
    lines: list[str] = []
    is_karnaugh = result.method == "karnaugh"

    lines.append("DNF:")
    lines.append(f"  {result.dnf.expression}")
    if is_karnaugh:
        lines.append(f"  Selected groups: {', '.join(result.dnf.selected_implicants) or '(none)'}")
    else:
        lines.extend(_format_glue_stages(result.dnf.glue_stages, indent="  "))
    if result.dnf.coverage_table is not None:
        label = "  Coverage table (DNF groups):" if is_karnaugh else "  Coverage table (DNF):"
        lines.append(label)
        lines.extend(_format_coverage_table(result.dnf.coverage_table, indent="    "))

    lines.append("CNF:")
    lines.append(f"  {result.cnf.expression}")
    if is_karnaugh:
        lines.append(f"  Selected groups: {', '.join(result.cnf.selected_implicants) or '(none)'}")
    else:
        lines.extend(_format_glue_stages(result.cnf.glue_stages, indent="  "))
    if result.cnf.coverage_table is not None:
        label = "  Coverage table (CNF groups):" if is_karnaugh else "  Coverage table (CNF):"
        lines.append(label)
        lines.extend(_format_coverage_table(result.cnf.coverage_table, indent="    "))

    for note in result.notes:
        lines.append(f"Note: {note}")

    return lines


def _format_glue_stages(stages: tuple[GlueStage, ...], indent: str) -> list[str]:
    lines: list[str] = []
    if not stages:
        lines.append(f"{indent}Glue stages: (none)")
        return lines

    lines.append(f"{indent}Glue stages:")
    for stage in stages:
        lines.append(f"{indent}  Iteration {stage.iteration}:")
        for pair in stage.pairs:
            merged = pair.merged or "-"
            lines.append(f"{indent}    {pair.left} + {pair.right} -> {merged}")

    return lines


def _format_coverage_table(table: CoverageTable, indent: str) -> list[str]:
    lines: list[str] = []

    if not table.columns:
        lines.append(f"{indent}(empty)")
        return lines

    column_header = "".join(str(column).rjust(3) for column in table.columns)
    lines.append(f"{indent}implicant | {column_header}")

    for row in table.rows:
        covered_set = set(row.covers)
        marks = ["  X" if column in covered_set else "  ." for column in table.columns]
        lines.append(f"{indent}{row.implicant:>9} | {''.join(marks)}")

    return lines
