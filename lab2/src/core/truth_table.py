from __future__ import annotations

from dataclasses import dataclass
from itertools import product

from .evaluator import evaluate_expression
from .expr_ast import Expr, collect_variables


@dataclass(frozen=True)
class TruthRow:
    index: int
    values: tuple[int, ...]
    result: int


@dataclass(frozen=True)
class TruthTable:
    expression: str
    variables: tuple[str, ...]
    rows: tuple[TruthRow, ...]

    @property
    def results_vector(self) -> tuple[int, ...]:
        return tuple(row.result for row in self.rows)

    @property
    def ones(self) -> tuple[int, ...]:
        return tuple(row.index for row in self.rows if row.result == 1)

    @property
    def zeros(self) -> tuple[int, ...]:
        return tuple(row.index for row in self.rows if row.result == 0)

    @property
    def truth_bits(self) -> str:
        return "".join(str(bit) for bit in self.results_vector)

    @property
    def index_value(self) -> int:
        bits = self.truth_bits
        return int(bits, 2) if bits else 0

    def value_map(self, row: TruthRow) -> dict[str, int]:
        return dict(zip(self.variables, row.values, strict=True))


class TruthTableError(ValueError):
    pass


def build_truth_table(expression: str, ast: Expr) -> TruthTable:
    variables = collect_variables(ast)
    if len(variables) > 5:
        raise TruthTableError("Допускается не более 5 переменных")

    rows: list[TruthRow] = []
    for values in product([0, 1], repeat=len(variables)):
        env = dict(zip(variables, values, strict=True))
        result = evaluate_expression(ast, env)
        index = _assignment_index(values)
        rows.append(TruthRow(index=index, values=tuple(values), result=result))

    return TruthTable(
        expression=expression,
        variables=variables,
        rows=tuple(sorted(rows, key=lambda item: item.index)),
    )


def from_vector(
    *,
    source: TruthTable,
    vector: tuple[int, ...],
    expression: str,
) -> TruthTable:
    if len(vector) != len(source.rows):
        raise TruthTableError("Длина вектора производной не совпадает с размером таблицы")

    rows = tuple(
        TruthRow(index=row.index, values=row.values, result=vector[i])
        for i, row in enumerate(source.rows)
    )
    return TruthTable(expression=expression, variables=source.variables, rows=rows)


def _assignment_index(values: tuple[int, ...]) -> int:
    if not values:
        return 0
    return int("".join(str(bit) for bit in values), 2)
