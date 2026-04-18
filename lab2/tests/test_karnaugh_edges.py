import pytest

from src.core.parser import parse_expression
from src.core.truth_table import TruthRow, TruthTable, build_truth_table, from_vector
from src.minimization import CoverageTable, MinimizedForm
from src.minimization import karnaugh as km


def test_karnaugh_constant_and_out_of_range_paths() -> None:
    const_table = TruthTable(
        expression="1",
        variables=(),
        rows=(TruthRow(index=0, values=(), result=1),),
    )
    const_result = km.minimize_karnaugh(const_table)
    assert const_result.dnf.expression == "1"
    assert const_result.cnf.expression == "1"

    five_vars = build_truth_table("a | b | c | d | e", parse_expression("a | b | c | d | e"))
    limited = km.minimize_karnaugh(five_vars)
    assert "только для 1..4 переменных" in "\n".join(limited.notes)


def test_karnaugh_full_zero_and_full_one_vectors() -> None:
    source = build_truth_table("a | b", parse_expression("a | b"))

    all_zero = from_vector(source=source, vector=(0, 0, 0, 0), expression="0")
    zero_result = km.minimize_karnaugh(all_zero)
    assert zero_result.dnf.expression == "0"
    assert zero_result.dnf.coverage_table is not None
    assert zero_result.dnf.coverage_table.columns == ()

    all_one = from_vector(source=source, vector=(1, 1, 1, 1), expression="1")
    one_result = km.minimize_karnaugh(all_one)
    assert one_result.cnf.expression == "1"
    assert one_result.cnf.coverage_table is not None
    assert one_result.cnf.coverage_table.columns == ()


def test_karnaugh_internal_helpers_and_group_selection() -> None:
    assert km._covers_to_pattern((), 0) == ""
    assert km._covers_to_pattern((), 2) == "--"

    with pytest.raises(ValueError, match="только для 1..4"):
        km._split_bits(5)

    empty_map = km.KarnaughMap(
        row_vars=(),
        col_vars=(),
        row_labels=(),
        col_labels=(),
        row_codes=(),
        col_codes=(),
        cells=(),
        indexes=(),
    )
    assert km._collect_candidate_groups(empty_map, target=1) == ()

    group_a = km.KarnaughGroup(pattern="0-", covers=(0, 1), cells=((0, 0), (0, 1)), shape=(1, 2))
    group_b = km.KarnaughGroup(pattern="-0", covers=(0, 2), cells=((0, 0), (1, 0)), shape=(2, 1))
    group_c = km.KarnaughGroup(pattern="-1", covers=(1, 2), cells=((0, 1), (1, 0)), shape=(2, 1))

    assert km._select_groups(prime_groups=(), required=()) == ()
    assert km._select_groups(prime_groups=(), required=(0,)) == ()

    selected = km._select_groups(
        prime_groups=(group_a, group_b, group_c),
        required=(0, 1, 2),
    )
    assert selected

    assert km._find_best_cover_subset(
        prime_groups=(group_a,),
        candidates=(0,),
        required=set(),
    ) == ()
    assert km._find_best_cover_subset(
        prime_groups=(group_a,),
        candidates=(),
        required={0},
    ) == ()

    assert km._build_expression(patterns=(), variables=("a",), is_cnf=False) == "0"
    assert km._build_expression(patterns=("--",), variables=("a", "b"), is_cnf=True) == "0"
    assert km._build_expression(patterns=("--",), variables=("a", "b"), is_cnf=False) == "1"

    empty_form = MinimizedForm(
        expression="0",
        selected_implicants=(),
        glue_stages=(),
        coverage_table=CoverageTable(columns=(), rows=()),
    )
    data = km._KarnaughFormData(
        form=empty_form,
        candidates=(),
        prime_groups=(),
        selected_groups=(),
    )
    summary = km._render_grouping_summary("DNF", data, ("a",), is_cnf=False)
    assert "Выбранные группы: (none)" in summary
