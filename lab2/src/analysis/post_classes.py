from __future__ import annotations

from dataclasses import dataclass

from ..core.truth_table import TruthTable
from .zhegalkin import is_linear_polynomial, zhegalkin_coefficients


@dataclass(frozen=True)
class PostClasses:
    t0: bool
    t1: bool
    s: bool
    m: bool
    l: bool


def classify_post(table: TruthTable) -> PostClasses:
    values = table.results_vector
    n = len(table.variables)

    t0 = values[0] == 0
    t1 = values[(1 << n) - 1] == 1
    s = _is_self_dual(values=values, variables_count=n)
    m = _is_monotone(values=values, variables_count=n)

    coeffs = zhegalkin_coefficients(table)
    l = is_linear_polynomial(coeffs, n)

    return PostClasses(t0=t0, t1=t1, s=s, m=m, l=l)


def _is_self_dual(*, values: tuple[int, ...], variables_count: int) -> bool:
    if variables_count == 0:
        return False

    size = 1 << variables_count
    mask = size - 1

    for index, value in enumerate(values):
        opposite = index ^ mask
        if value == values[opposite]:
            return False
    return True


def _is_monotone(*, values: tuple[int, ...], variables_count: int) -> bool:
    size = 1 << variables_count

    for low in range(size):
        for high in range(size):
            if _leq_bitwise(low, high):
                if values[low] > values[high]:
                    return False
    return True


def _leq_bitwise(left: int, right: int) -> bool:
    return (left | right) == right
