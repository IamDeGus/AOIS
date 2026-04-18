from __future__ import annotations

from dataclasses import dataclass

from ..core.truth_table import TruthTable


@dataclass(frozen=True)
class FictiveVariables:
    fictive: tuple[str, ...]
    essential: tuple[str, ...]


def find_fictive_variables(table: TruthTable) -> FictiveVariables:
    values = table.results_vector
    n = len(table.variables)
    size = 1 << n

    fictive: list[str] = []
    essential: list[str] = []

    for position, variable in enumerate(table.variables):
        bit = 1 << (n - 1 - position)
        depends = False

        for index in range(size):
            if index & bit:
                continue
            if values[index] != values[index | bit]:
                depends = True
                break

        if depends:
            essential.append(variable)
        else:
            fictive.append(variable)

    return FictiveVariables(fictive=tuple(fictive), essential=tuple(essential))
