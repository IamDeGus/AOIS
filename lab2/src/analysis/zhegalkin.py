from __future__ import annotations

from dataclasses import dataclass

from ..core.truth_table import TruthTable


@dataclass(frozen=True)
class ZhegalkinPolynomial:
    coefficients: tuple[int, ...]
    polynomial: str


def zhegalkin_coefficients(table: TruthTable) -> tuple[int, ...]:
    values = list(table.results_vector)
    n = len(table.variables)
    size = 1 << n

    if len(values) != size:
        raise ValueError("Размер таблицы не соответствует числу переменных")

    for bit in range(n):
        mask = 1 << bit
        for current in range(size):
            if current & mask:
                values[current] ^= values[current ^ mask]

    return tuple(values)


def build_zhegalkin_polynomial(table: TruthTable) -> ZhegalkinPolynomial:
    coeffs = zhegalkin_coefficients(table)
    terms_data: list[tuple[int, str]] = []

    for mask, coefficient in enumerate(coeffs):
        if coefficient == 0:
            continue
        term = _mask_to_term(mask=mask, variables=table.variables)
        terms_data.append((mask, term))

    terms_data.sort(key=lambda item: (_popcount(item[0]), item[1]))
    terms = [term for _, term in terms_data]
    polynomial = " ^ ".join(terms) if terms else "0"
    return ZhegalkinPolynomial(coefficients=coeffs, polynomial=polynomial)


def is_linear_polynomial(coefficients: tuple[int, ...], variables_count: int) -> bool:
    for mask, coefficient in enumerate(coefficients):
        if coefficient == 0:
            continue
        if _popcount(mask) > 1:
            return False
    expected_size = 1 << variables_count
    return len(coefficients) == expected_size


def _mask_to_term(mask: int, variables: tuple[str, ...]) -> str:
    if mask == 0:
        return "1"

    parts: list[str] = []
    n = len(variables)
    for i, variable in enumerate(variables):
        bit = 1 << (n - 1 - i)
        if mask & bit:
            parts.append(variable)

    return "*".join(parts) if parts else "1"


def _popcount(value: int) -> int:
    return value.bit_count()
