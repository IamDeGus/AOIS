from __future__ import annotations

from dataclasses import dataclass

from .calculation_tabular import minimize_calculation_tabular
from .models import CoverageRow, CoverageTable, MinimizedForm, MinimizationResult
from .qm import pattern_to_cnf_clause, pattern_to_dnf_term
from ..core.truth_table import TruthTable


@dataclass(frozen=True)
class KarnaughMap:
    row_vars: tuple[str, ...]
    col_vars: tuple[str, ...]
    row_labels: tuple[str, ...]
    col_labels: tuple[str, ...]
    row_codes: tuple[int, ...]
    col_codes: tuple[int, ...]
    cells: tuple[tuple[int, ...], ...]
    indexes: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class KarnaughGroup:
    pattern: str
    covers: tuple[int, ...]
    cells: tuple[tuple[int, int], ...]
    shape: tuple[int, int]

    @property
    def literals(self) -> int:
        return self.pattern.count("0") + self.pattern.count("1")


@dataclass(frozen=True)
class _KarnaughFormData:
    form: MinimizedForm
    candidates: tuple[KarnaughGroup, ...]
    prime_groups: tuple[KarnaughGroup, ...]
    selected_groups: tuple[KarnaughGroup, ...]


def minimize_karnaugh(table: TruthTable) -> MinimizationResult:
    n = len(table.variables)

    if n == 0:
        value = str(table.rows[0].result)
        empty_coverage = CoverageTable(columns=(), rows=())
        constant_form = MinimizedForm(
            expression=value,
            selected_implicants=(),
            glue_stages=(),
            coverage_table=empty_coverage,
        )
        return MinimizationResult(
            method="karnaugh",
            dnf=constant_form,
            cnf=constant_form,
            notes=("Карта Карно не требуется для константной функции.",),
        )

    if n > 5:
        baseline = minimize_calculation_tabular(table)
        note = "Карта Карно поддерживается только для 1..5 переменных. Выведен результат через склейку/покрытие."
        return MinimizationResult(method="karnaugh", dnf=baseline.dnf, cnf=baseline.cnf, notes=(note,))

    kmap = build_karnaugh_map(table)
    dnf_data = _build_karnaugh_form(kmap, table.variables, target=1, is_cnf=False)
    cnf_data = _build_karnaugh_form(kmap, table.variables, target=0, is_cnf=True)

    return MinimizationResult(
        method="karnaugh",
        dnf=dnf_data.form,
        cnf=cnf_data.form,
        notes=(
            render_karnaugh_map(kmap),
            _render_grouping_summary("DNF", dnf_data, table.variables, is_cnf=False),
            _render_grouping_summary("CNF", cnf_data, table.variables, is_cnf=True),
            "Группы подбирались с приоритетом меньшего числа литералов, затем меньшего числа групп.",
        ),
    )


def build_karnaugh_map(table: TruthTable) -> KarnaughMap:
    n = len(table.variables)
    row_bits, col_bits = _split_bits(n)

    row_vars = table.variables[:row_bits]
    col_vars = table.variables[row_bits:]

    row_codes = _gray_codes(row_bits)
    col_codes = _gray_codes(col_bits)

    row_labels = tuple(_bits(code, row_bits) for code in row_codes)
    col_labels = tuple(_bits(code, col_bits) for code in col_codes)

    cells: list[tuple[int, ...]] = []
    indexes: list[tuple[int, ...]] = []
    values = table.results_vector

    for row_code in row_codes:
        row_values: list[int] = []
        row_indexes: list[int] = []
        for col_code in col_codes:
            index = (row_code << col_bits) | col_code
            row_values.append(values[index])
            row_indexes.append(index)
        cells.append(tuple(row_values))
        indexes.append(tuple(row_indexes))

    return KarnaughMap(
        row_vars=row_vars,
        col_vars=col_vars,
        row_labels=row_labels,
        col_labels=col_labels,
        row_codes=row_codes,
        col_codes=col_codes,
        cells=tuple(cells),
        indexes=tuple(indexes),
    )


def render_karnaugh_map(kmap: KarnaughMap) -> str:
    lines: list[str] = []
    left_header = "".join(kmap.row_vars) or "-"
    top_header = "".join(kmap.col_vars) or "-"
    cell_width = max(
        len(f"{index}:{value}")
        for row_indexes, row_values in zip(kmap.indexes, kmap.cells, strict=True)
        for index, value in zip(row_indexes, row_values, strict=True)
    )

    lines.append(f"K-map {left_header} x {top_header}")
    header_cells = " | ".join(label.rjust(cell_width) for label in kmap.col_labels)
    lines.append("row\\col | " + header_cells)

    for row_label, row_indexes, row_values in zip(kmap.row_labels, kmap.indexes, kmap.cells, strict=True):
        rendered_cells = [
            f"{index}:{value}".rjust(cell_width)
            for index, value in zip(row_indexes, row_values, strict=True)
        ]
        lines.append(f"{row_label:>7} | " + " | ".join(rendered_cells))

    return "\n".join(lines)


def _build_karnaugh_form(
    kmap: KarnaughMap,
    variables: tuple[str, ...],
    *,
    target: int,
    is_cnf: bool,
) -> _KarnaughFormData:
    columns = _target_indexes(kmap, target=target)
    if not columns:
        empty_form = MinimizedForm(
            expression="1" if is_cnf else "0",
            selected_implicants=(),
            glue_stages=(),
            coverage_table=CoverageTable(columns=(), rows=()),
        )
        return _KarnaughFormData(
            form=empty_form,
            candidates=(),
            prime_groups=(),
            selected_groups=(),
        )

    candidates = _collect_candidate_groups(kmap, target=target)
    prime_groups = _extract_prime_groups(candidates)
    selected_groups = _select_groups(prime_groups=prime_groups, required=columns)
    selected_patterns = tuple(group.pattern for group in selected_groups)
    expression = _build_expression(
        patterns=selected_patterns,
        variables=variables,
        is_cnf=is_cnf,
    )

    form = MinimizedForm(
        expression=expression,
        selected_implicants=selected_patterns,
        glue_stages=(),
        coverage_table=_build_coverage_table(columns=columns, groups=prime_groups),
    )
    return _KarnaughFormData(
        form=form,
        candidates=candidates,
        prime_groups=prime_groups,
        selected_groups=selected_groups,
    )


def _target_indexes(kmap: KarnaughMap, *, target: int) -> tuple[int, ...]:
    indexes = [
        kmap.indexes[row][col]
        for row, row_values in enumerate(kmap.cells)
        for col, value in enumerate(row_values)
        if value == target
    ]
    return tuple(sorted(indexes))


def _collect_candidate_groups(kmap: KarnaughMap, *, target: int) -> tuple[KarnaughGroup, ...]:
    variables_count = len(kmap.row_vars) + len(kmap.col_vars)
    if variables_count == 0:
        return ()

    target_indexes = set(_target_indexes(kmap, target=target))
    if not target_indexes:
        return ()

    index_to_cell = {
        index: (row, col)
        for row, row_indexes in enumerate(kmap.indexes)
        for col, index in enumerate(row_indexes)
    }

    groups: list[KarnaughGroup] = []
    for pattern in _iter_patterns(variables_count):
        covers = _covers_for_pattern(pattern=pattern, variables_count=variables_count)
        if not covers:
            continue

        cover_set = set(covers)
        if not cover_set <= target_indexes:
            continue

        cells = tuple(sorted(index_to_cell[index] for index in covers))
        shape = _shape_from_pattern(pattern, row_bits=len(kmap.row_vars), col_bits=len(kmap.col_vars))
        groups.append(
            KarnaughGroup(
                pattern=pattern,
                covers=covers,
                cells=cells,
                shape=shape,
            )
        )

    return tuple(sorted(groups, key=_group_sort_key))


def _extract_prime_groups(groups: tuple[KarnaughGroup, ...]) -> tuple[KarnaughGroup, ...]:
    cover_sets = [set(group.covers) for group in groups]
    prime_groups: list[KarnaughGroup] = []

    for i, group in enumerate(groups):
        group_set = cover_sets[i]
        is_subgroup = False
        for j, other in enumerate(groups):
            if i == j:
                continue
            if group_set < cover_sets[j]:
                is_subgroup = True
                break
        if not is_subgroup:
            prime_groups.append(group)

    dedup_by_pattern: dict[str, KarnaughGroup] = {}
    for group in sorted(prime_groups, key=_group_sort_key):
        previous = dedup_by_pattern.get(group.pattern)
        if previous is None:
            dedup_by_pattern[group.pattern] = group
            continue
        if _group_sort_key(group) < _group_sort_key(previous):
            dedup_by_pattern[group.pattern] = group

    return tuple(sorted(dedup_by_pattern.values(), key=lambda item: item.pattern))


def _select_groups(*, prime_groups: tuple[KarnaughGroup, ...], required: tuple[int, ...]) -> tuple[KarnaughGroup, ...]:
    required_set = set(required)
    if not required_set:
        return ()
    if not prime_groups:
        return ()

    index_coverers: dict[int, list[int]] = {}
    for required_index in required:
        coverers = [i for i, group in enumerate(prime_groups) if required_index in group.covers]
        index_coverers[required_index] = coverers

    essential_indexes = {
        coverers[0]
        for coverers in index_coverers.values()
        if len(coverers) == 1
    }

    covered = set()
    for index in essential_indexes:
        covered.update(prime_groups[index].covers)

    remaining_required = required_set - covered
    if not remaining_required:
        return tuple(sorted((prime_groups[i] for i in essential_indexes), key=lambda item: item.pattern))

    optional_indexes = tuple(
        i
        for i, group in enumerate(prime_groups)
        if i not in essential_indexes and set(group.covers) & remaining_required
    )
    extra_indexes = _find_best_cover_subset(
        prime_groups=prime_groups,
        candidates=optional_indexes,
        required=remaining_required,
    )
    selected_indexes = essential_indexes | set(extra_indexes)
    return tuple(sorted((prime_groups[i] for i in selected_indexes), key=lambda item: item.pattern))


def _find_best_cover_subset(
    *,
    prime_groups: tuple[KarnaughGroup, ...],
    candidates: tuple[int, ...],
    required: set[int],
) -> tuple[int, ...]:
    if not required:
        return ()
    if not candidates:
        return ()

    coverage = {index: set(prime_groups[index].covers) & required for index in candidates}
    ordered = tuple(
        sorted(
            candidates,
            key=lambda index: (
                -len(coverage[index]),
                prime_groups[index].literals,
                prime_groups[index].pattern,
            ),
        )
    )

    suffix_cover: list[set[int]] = [set() for _ in range(len(ordered) + 1)]
    for i in range(len(ordered) - 1, -1, -1):
        suffix_cover[i] = suffix_cover[i + 1] | coverage[ordered[i]]

    best_score: tuple[int, int, tuple[str, ...]] | None = None
    best_selection: tuple[int, ...] = ()

    def dfs(
        pos: int,
        selected: tuple[int, ...],
        covered: set[int],
        literals_sum: int,
    ) -> None:
        nonlocal best_score, best_selection

        if required <= covered:
            patterns = tuple(sorted(prime_groups[index].pattern for index in selected))
            score = (literals_sum, len(selected), patterns)
            if best_score is None or score < best_score:
                best_score = score
                best_selection = selected
            return

        if pos >= len(ordered):
            return

        if not required <= (covered | suffix_cover[pos]):
            return

        if best_score is not None:
            best_literals, best_terms, _ = best_score
            if literals_sum > best_literals:
                return
            if literals_sum == best_literals and len(selected) >= best_terms:
                return

        index = ordered[pos]
        index_cover = coverage[index]

        if index_cover - covered:
            dfs(
                pos + 1,
                selected + (index,),
                covered | index_cover,
                literals_sum + prime_groups[index].literals,
            )

        dfs(pos + 1, selected, covered, literals_sum)

    dfs(pos=0, selected=(), covered=set(), literals_sum=0)

    return best_selection


def _build_expression(*, patterns: tuple[str, ...], variables: tuple[str, ...], is_cnf: bool) -> str:
    if not patterns:
        return "1" if is_cnf else "0"

    if is_cnf:
        clauses = [pattern_to_cnf_clause(pattern, variables) for pattern in patterns]
        if len(clauses) == 1 and clauses[0] in {"0", "1"}:
            return clauses[0]
        return " & ".join(f"({clause})" for clause in clauses)

    terms = [pattern_to_dnf_term(pattern, variables) for pattern in patterns]
    if len(terms) == 1 and terms[0] in {"0", "1"}:
        return terms[0]
    return " | ".join(f"({term})" for term in terms)


def _build_coverage_table(
    *,
    columns: tuple[int, ...],
    groups: tuple[KarnaughGroup, ...],
) -> CoverageTable:
    column_set = set(columns)
    rows = tuple(
        CoverageRow(
            implicant=group.pattern,
            covers=tuple(index for index in group.covers if index in column_set),
        )
        for group in groups
    )
    return CoverageTable(columns=columns, rows=rows)


def _render_grouping_summary(
    form_name: str,
    data: _KarnaughFormData,
    variables: tuple[str, ...],
    *,
    is_cnf: bool,
) -> str:
    lines: list[str] = [f"{form_name} группировка:"]
    lines.append(f"Кандидатных групп: {len(data.candidates)}")
    lines.append(f"Простых групп: {len(data.prime_groups)}")
    lines.append(f"Выбрано групп: {len(data.selected_groups)}")

    if data.selected_groups:
        lines.append("Выбранные группы:")
        for group in data.selected_groups:
            term = pattern_to_cnf_clause(group.pattern, variables) if is_cnf else pattern_to_dnf_term(group.pattern, variables)
            covered = ", ".join(str(index) for index in group.covers)
            lines.append(
                f"  {group.pattern} -> ({term}), size={len(group.covers)}, cover=[{covered}]"
            )
    else:
        lines.append("Выбранные группы: (none)")

    return "\n".join(lines)


def _group_sort_key(group: KarnaughGroup) -> tuple[int, int, str, tuple[int, int], tuple[int, ...]]:
    return (
        group.literals,
        -len(group.covers),
        group.pattern,
        group.shape,
        group.covers,
    )


def _powers_of_two(limit: int) -> tuple[int, ...]:
    values: list[int] = []
    current = 1
    while current <= limit:
        values.append(current)
        current *= 2
    return tuple(values)


def _covers_to_pattern(covers: tuple[int, ...], variables_count: int) -> str:
    if variables_count == 0:
        return ""
    if not covers:
        return "-" * variables_count

    chars: list[str] = []
    for bit_index in range(variables_count):
        bit_mask = 1 << (variables_count - 1 - bit_index)
        bit_values = {(cover & bit_mask) >> (variables_count - 1 - bit_index) for cover in covers}
        if len(bit_values) == 1:
            chars.append(str(next(iter(bit_values))))
        else:
            chars.append("-")
    return "".join(chars)


def _iter_patterns(bits: int) -> tuple[str, ...]:
    if bits == 0:
        return ("",)

    tails = _iter_patterns(bits - 1)
    patterns: list[str] = []
    for head in ("0", "1", "-"):
        patterns.extend(head + tail for tail in tails)
    return tuple(patterns)


def _covers_for_pattern(*, pattern: str, variables_count: int) -> tuple[int, ...]:
    size = 1 << variables_count
    return tuple(
        index
        for index in range(size)
        if _index_matches_pattern(index=index, pattern=pattern, variables_count=variables_count)
    )


def _index_matches_pattern(*, index: int, pattern: str, variables_count: int) -> bool:
    for bit_index, char in enumerate(pattern):
        if char == "-":
            continue

        bit = (index >> (variables_count - 1 - bit_index)) & 1
        if bit != int(char):
            return False

    return True


def _shape_from_pattern(pattern: str, *, row_bits: int, col_bits: int) -> tuple[int, int]:
    free_row = pattern[:row_bits].count("-")
    free_col = pattern[row_bits:row_bits + col_bits].count("-")
    return (1 << free_row, 1 << free_col)


def _split_bits(variables_count: int) -> tuple[int, int]:
    if variables_count == 1:
        return 0, 1
    if variables_count == 2:
        return 1, 1
    if variables_count == 3:
        return 1, 2
    if variables_count == 4:
        return 2, 2
    if variables_count == 5:
        return 2, 3
    raise ValueError("Карта Карно поддерживается только для 1..5 переменных")


def _gray_codes(bits: int) -> tuple[int, ...]:
    if bits == 0:
        return (0,)
    return tuple(i ^ (i >> 1) for i in range(1 << bits))


def _bits(value: int, bits: int) -> str:
    if bits == 0:
        return "-"
    return format(value, f"0{bits}b")
