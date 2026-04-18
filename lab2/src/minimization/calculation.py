from __future__ import annotations

from .models import MinimizedForm, MinimizationResult
from .qm import build_cnf_expression, build_dnf_expression, run_quine_mccluskey
from ..core.truth_table import TruthTable


def minimize_calculation(table: TruthTable) -> MinimizationResult:
    dnf_outcome = run_quine_mccluskey(minterms=table.ones, variables_count=len(table.variables))
    cnf_outcome = run_quine_mccluskey(minterms=table.zeros, variables_count=len(table.variables))

    dnf_expression = build_dnf_expression(dnf_outcome.selected, table.variables)
    cnf_expression = build_cnf_expression(cnf_outcome.selected, table.variables)

    dnf_form = MinimizedForm(
        expression=dnf_expression,
        selected_implicants=tuple(imp.pattern for imp in dnf_outcome.selected),
        glue_stages=dnf_outcome.glue_stages,
        coverage_table=None,
    )

    cnf_form = MinimizedForm(
        expression=cnf_expression,
        selected_implicants=tuple(imp.pattern for imp in cnf_outcome.selected),
        glue_stages=cnf_outcome.glue_stages,
        coverage_table=None,
    )

    return MinimizationResult(
        method="calculation",
        dnf=dnf_form,
        cnf=cnf_form,
        notes=(
            "Результат получен через склейку и выбор покрытия (без таблицы покрытия в выводе).",
        ),
    )
