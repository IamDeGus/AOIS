from src.minimization.qm import (
    Implicant,
    _merge_patterns,
    _select_cover,
    build_cnf_expression,
    build_dnf_expression,
    pattern_to_cnf_clause,
    pattern_to_dnf_term,
    run_quine_mccluskey,
)


def test_quine_mccluskey_empty_and_expression_helpers() -> None:
    empty = run_quine_mccluskey(minterms=(), variables_count=3)
    assert empty.primes == ()
    assert empty.selected == ()
    assert empty.coverage_table.columns == ()

    assert pattern_to_dnf_term("--", ("a", "b")) == "1"
    assert pattern_to_cnf_clause("--", ("a", "b")) == "0"

    assert build_dnf_expression((), ("a", "b")) == "0"
    assert build_cnf_expression((), ("a", "b")) == "1"


def test_merge_patterns_and_cover_selection_branches() -> None:
    assert _merge_patterns("00", "01") == "0-"
    assert _merge_patterns("00", "00") is None
    assert _merge_patterns("0-", "00") is None
    assert _merge_patterns("00", "11") is None

    primes = (
        Implicant(pattern="0-", covers=frozenset({0, 1})),
        Implicant(pattern="-0", covers=frozenset({0, 2})),
        Implicant(pattern="1-", covers=frozenset({2, 3})),
    )
    selected = _select_cover(primes=primes, minterms=(0, 1, 2))
    assert selected

    fallback = _select_cover(primes=primes, minterms=(5,))
    assert fallback == primes

    assert _select_cover(primes=(), minterms=(1,)) == ()
