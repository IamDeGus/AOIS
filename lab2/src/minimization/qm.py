from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import CoverageRow, CoverageTable, GluePair, GlueStage


@dataclass(frozen=True)
class Implicant:
    pattern: str
    covers: frozenset[int]


@dataclass(frozen=True)
class QmOutcome:
    primes: tuple[Implicant, ...]
    selected: tuple[Implicant, ...]
    glue_stages: tuple[GlueStage, ...]
    coverage_table: CoverageTable


def run_quine_mccluskey(*, minterms: tuple[int, ...], variables_count: int) -> QmOutcome:
    columns = tuple(sorted(set(minterms)))

    if not columns:
        empty_table = CoverageTable(columns=(), rows=())
        return QmOutcome(primes=(), selected=(), glue_stages=(), coverage_table=empty_table)

    current = tuple(
        Implicant(pattern=_index_to_pattern(index, variables_count), covers=frozenset({index}))
        for index in columns
    )

    prime_implicants: dict[str, Implicant] = {}
    glue_stages: list[GlueStage] = []
    iteration = 1

    while True:
        groups: dict[int, list[Implicant]] = {}
        for implicant in current:
            groups.setdefault(_ones_count(implicant.pattern), []).append(implicant)

        used_patterns: set[str] = set()
        next_map: dict[str, set[int]] = {}
        pairs: list[GluePair] = []

        for group_index in sorted(groups):
            left_group = sorted(groups.get(group_index, []), key=lambda item: item.pattern)
            right_group = sorted(groups.get(group_index + 1, []), key=lambda item: item.pattern)
            if not right_group:
                continue

            for left in left_group:
                for right in right_group:
                    merged = _merge_patterns(left.pattern, right.pattern)
                    if merged is None:
                        continue
                    used_patterns.add(left.pattern)
                    used_patterns.add(right.pattern)
                    next_map.setdefault(merged, set()).update(left.covers)
                    next_map.setdefault(merged, set()).update(right.covers)
                    pairs.append(GluePair(left=left.pattern, right=right.pattern, merged=merged))

        for implicant in current:
            if implicant.pattern not in used_patterns:
                prime_implicants[implicant.pattern] = implicant

        if pairs:
            glue_stages.append(
                GlueStage(
                    iteration=iteration,
                    pairs=tuple(sorted(pairs, key=lambda item: (item.left, item.right, item.merged or ""))),
                )
            )

        if not next_map:
            break

        current = tuple(
            Implicant(pattern=pattern, covers=frozenset(covers))
            for pattern, covers in sorted(next_map.items(), key=lambda item: item[0])
        )
        iteration += 1

    primes = tuple(sorted(prime_implicants.values(), key=lambda item: item.pattern))
    selected = _select_cover(primes=primes, minterms=columns)

    coverage_table = CoverageTable(
        columns=columns,
        rows=tuple(
            CoverageRow(
                implicant=implicant.pattern,
                covers=tuple(sorted(set(implicant.covers) & set(columns))),
            )
            for implicant in primes
        ),
    )

    return QmOutcome(
        primes=primes,
        selected=selected,
        glue_stages=tuple(glue_stages),
        coverage_table=coverage_table,
    )


def pattern_to_dnf_term(pattern: str, variables: tuple[str, ...]) -> str:
    parts: list[str] = []
    for variable, bit in zip(variables, pattern, strict=True):
        if bit == "1":
            parts.append(variable)
        elif bit == "0":
            parts.append(f"!{variable}")

    if not parts:
        return "1"
    return " & ".join(parts)


def pattern_to_cnf_clause(pattern: str, variables: tuple[str, ...]) -> str:
    parts: list[str] = []
    for variable, bit in zip(variables, pattern, strict=True):
        if bit == "0":
            parts.append(variable)
        elif bit == "1":
            parts.append(f"!{variable}")

    if not parts:
        return "0"
    return " | ".join(parts)


def build_dnf_expression(implicants: Iterable[Implicant], variables: tuple[str, ...]) -> str:
    terms = [pattern_to_dnf_term(implicant.pattern, variables) for implicant in implicants]
    if not terms:
        return "0"
    return " | ".join(f"({term})" for term in terms)


def build_cnf_expression(implicants: Iterable[Implicant], variables: tuple[str, ...]) -> str:
    clauses = [pattern_to_cnf_clause(implicant.pattern, variables) for implicant in implicants]
    if not clauses:
        return "1"
    return " & ".join(f"({clause})" for clause in clauses)


def _index_to_pattern(index: int, variables_count: int) -> str:
    return format(index, f"0{variables_count}b")


def _ones_count(pattern: str) -> int:
    return pattern.count("1")


def _merge_patterns(left: str, right: str) -> str | None:
    diff_count = 0
    diff_pos = -1

    for i, (l_char, r_char) in enumerate(zip(left, right, strict=True)):
        if l_char == r_char:
            continue

        if l_char == "-" or r_char == "-":
            return None

        diff_count += 1
        diff_pos = i
        if diff_count > 1:
            return None

    if diff_count != 1:
        return None

    merged = list(left)
    merged[diff_pos] = "-"
    return "".join(merged)


def _select_cover(*, primes: tuple[Implicant, ...], minterms: tuple[int, ...]) -> tuple[Implicant, ...]:
    if not minterms or not primes:
        return ()

    minterm_set = set(minterms)
    remaining = set(minterms)
    selected_indexes: set[int] = set()

    while True:
        changed = False
        for minterm in list(remaining):
            coverers = [i for i, imp in enumerate(primes) if minterm in imp.covers]
            if len(coverers) == 1:
                index = coverers[0]
                if index not in selected_indexes:
                    selected_indexes.add(index)
                    remaining -= set(primes[index].covers)
                    changed = True
        if not changed:
            break

    while remaining:
        best_index = -1
        best_gain = -1
        best_literals = 10**9

        for i, implicant in enumerate(primes):
            if i in selected_indexes:
                continue
            gain = len(set(implicant.covers) & remaining)
            if gain == 0:
                continue

            literals = implicant.pattern.count("0") + implicant.pattern.count("1")

            if gain > best_gain:
                best_index = i
                best_gain = gain
                best_literals = literals
                continue

            if gain == best_gain and literals < best_literals:
                best_index = i
                best_literals = literals
                continue

            if gain == best_gain and literals == best_literals:
                if best_index == -1 or implicant.pattern < primes[best_index].pattern:
                    best_index = i

        if best_index == -1:
            # Страховка: если что-то не покрыто из-за неконсистентных данных.
            break

        selected_indexes.add(best_index)
        remaining -= set(primes[best_index].covers)

    selected = tuple(primes[i] for i in sorted(selected_indexes, key=lambda idx: primes[idx].pattern))

    covered = set()
    for implicant in selected:
        covered.update(implicant.covers)

    if covered >= minterm_set:
        return selected

    fallback = tuple(primes)
    return fallback
