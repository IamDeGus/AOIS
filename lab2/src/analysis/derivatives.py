from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from .canonical_forms import build_sdnf, build_sknf
from ..core.truth_table import TruthTable, from_vector


@dataclass(frozen=True)
class Derivative:
    variables: tuple[str, ...]
    vector: tuple[int, ...]
    sdnf: str
    sknf: str


def derivative_vector(table: TruthTable, by_variables: tuple[str, ...]) -> tuple[int, ...]:
    if not by_variables:
        return table.results_vector

    values = list(table.results_vector)
    n = len(table.variables)
    size = 1 << n

    bits: list[int] = []
    for variable in by_variables:
        try:
            pos = table.variables.index(variable)
        except ValueError as error:
            raise ValueError(f"Переменная '{variable}' отсутствует в функции") from error
        bits.append(1 << (n - 1 - pos))

    for bit in bits:
        next_values = [0] * size
        for index in range(size):
            next_values[index] = values[index] ^ values[index ^ bit]
        values = next_values

    return tuple(values)


def build_derivative(table: TruthTable, by_variables: tuple[str, ...]) -> Derivative:
    vector = derivative_vector(table, by_variables)
    label = "d/d" + "".join(by_variables)

    derived_table = from_vector(source=table, vector=vector, expression=label)
    return Derivative(
        variables=by_variables,
        vector=vector,
        sdnf=build_sdnf(derived_table),
        sknf=build_sknf(derived_table),
    )


def build_all_derivatives(table: TruthTable, max_order: int = 4) -> tuple[Derivative, ...]:
    n = len(table.variables)
    limit = min(max_order, n)

    results: list[Derivative] = []
    for order in range(1, limit + 1):
        for combo in combinations(table.variables, order):
            results.append(build_derivative(table, combo))

    return tuple(results)
