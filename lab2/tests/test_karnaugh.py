from src.analysis import analyze_expression


def test_karnaugh_minimization_uses_groups_for_and() -> None:
    result = analyze_expression("a & b")
    karnaugh = result.minimize_karnaugh

    assert karnaugh.method == "karnaugh"
    assert karnaugh.dnf.expression == "(a & b)"
    assert set(karnaugh.dnf.selected_implicants) == {"11"}
    assert set(karnaugh.cnf.selected_implicants) == {"-0", "0-"}
    assert karnaugh.dnf.coverage_table is not None
    assert karnaugh.cnf.coverage_table is not None

    notes = "\n".join(karnaugh.notes)
    assert "K-map" in notes
    assert "Выбрано групп" in notes
    assert "совпадают с расчетно-табличным" not in notes


def test_karnaugh_minimization_detects_large_group() -> None:
    result = analyze_expression("!a")
    karnaugh = result.minimize_karnaugh

    assert karnaugh.dnf.expression == "(!a)"
    assert set(karnaugh.dnf.selected_implicants) == {"0"}
    assert karnaugh.cnf.expression == "(!a)"
    assert set(karnaugh.cnf.selected_implicants) == {"1"}
