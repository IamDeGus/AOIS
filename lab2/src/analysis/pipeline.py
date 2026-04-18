from __future__ import annotations

from dataclasses import dataclass

from .derivatives import Derivative, build_all_derivatives
from .fictive_vars import FictiveVariables, find_fictive_variables
from .canonical_forms import CanonicalForms, build_canonical_forms
from ..minimization import (
    MinimizationResult,
    minimize_calculation,
    minimize_calculation_tabular,
    minimize_karnaugh,
)
from ..core.parser import parse_expression
from .post_classes import PostClasses, classify_post
from ..core.truth_table import TruthTable, build_truth_table
from .zhegalkin import ZhegalkinPolynomial, build_zhegalkin_polynomial


@dataclass(frozen=True)
class AnalysisResult:
    expression: str
    table: TruthTable
    forms: CanonicalForms
    post: PostClasses
    zhegalkin: ZhegalkinPolynomial
    fictive_vars: FictiveVariables
    derivatives: tuple[Derivative, ...]
    minimize_calculation: MinimizationResult
    minimize_calculation_tabular: MinimizationResult
    minimize_karnaugh: MinimizationResult


def analyze_expression(expression: str) -> AnalysisResult:
    ast = parse_expression(expression)
    table = build_truth_table(expression=expression, ast=ast)

    forms = build_canonical_forms(table)
    post = classify_post(table)
    zhegalkin = build_zhegalkin_polynomial(table)
    fictive_vars = find_fictive_variables(table)
    derivatives = build_all_derivatives(table, max_order=4)

    calc = minimize_calculation(table)
    calc_tab = minimize_calculation_tabular(table)
    karnaugh = minimize_karnaugh(table)

    return AnalysisResult(
        expression=expression,
        table=table,
        forms=forms,
        post=post,
        zhegalkin=zhegalkin,
        fictive_vars=fictive_vars,
        derivatives=derivatives,
        minimize_calculation=calc,
        minimize_calculation_tabular=calc_tab,
        minimize_karnaugh=karnaugh,
    )
