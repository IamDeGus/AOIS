from __future__ import annotations

from dataclasses import dataclass

from ..core.truth_table import TruthRow, TruthTable


@dataclass(frozen=True)
class CanonicalForms:
    sdnf: str
    sknf: str
    sdnf_numeric: str
    sknf_numeric: str
    index_form: str


def build_canonical_forms(table: TruthTable) -> CanonicalForms:
    sdnf = build_sdnf(table)
    sknf = build_sknf(table)

    sdnf_numeric = _numeric_form("Sm", table.ones)
    sknf_numeric = _numeric_form("PM", table.zeros)

    index_form = f"i = {table.index_value}, vector = {table.truth_bits}"

    return CanonicalForms(
        sdnf=sdnf,
        sknf=sknf,
        sdnf_numeric=sdnf_numeric,
        sknf_numeric=sknf_numeric,
        index_form=index_form,
    )


def build_sdnf(table: TruthTable) -> str:
    if not table.variables:
        return "1" if table.rows[0].result == 1 else "0"

    terms = [_dnf_term(table.variables, row) for row in table.rows if row.result == 1]
    if not terms:
        return "0"
    return " | ".join(f"({term})" for term in terms)


def build_sknf(table: TruthTable) -> str:
    if not table.variables:
        return "1" if table.rows[0].result == 1 else "0"

    clauses = [_cnf_clause(table.variables, row) for row in table.rows if row.result == 0]
    if not clauses:
        return "1"
    return " & ".join(f"({clause})" for clause in clauses)


def _dnf_term(variables: tuple[str, ...], row: TruthRow) -> str:
    parts = [
        variable if value == 1 else f"!{variable}"
        for variable, value in zip(variables, row.values, strict=True)
    ]
    return " & ".join(parts)


def _cnf_clause(variables: tuple[str, ...], row: TruthRow) -> str:
    parts = [
        variable if value == 0 else f"!{variable}"
        for variable, value in zip(variables, row.values, strict=True)
    ]
    return " | ".join(parts)


def _numeric_form(prefix: str, indexes: tuple[int, ...]) -> str:
    if not indexes:
        return f"{prefix}(empty)"
    values = ", ".join(str(index) for index in indexes)
    return f"{prefix}({values})"
