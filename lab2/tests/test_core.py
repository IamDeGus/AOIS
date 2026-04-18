from src.analysis import analyze_expression


def test_truth_table_for_implication() -> None:
    result = analyze_expression("a -> b")

    assert result.table.variables == ("a", "b")
    assert result.table.truth_bits == "1101"
    assert result.table.ones == (0, 1, 3)
    assert result.table.zeros == (2,)


def test_canonical_forms_for_implication() -> None:
    result = analyze_expression("a -> b")

    assert result.forms.sdnf == "(!a & !b) | (!a & b) | (a & b)"
    assert result.forms.sknf == "(!a | b)"
    assert result.forms.sdnf_numeric == "Sm(0, 1, 3)"
    assert result.forms.sknf_numeric == "PM(2)"


def test_post_class_and_zhegalkin() -> None:
    result = analyze_expression("a | b")

    assert result.post.t0 is True
    assert result.post.t1 is True
    assert result.post.s is False
    assert result.post.m is True
    assert result.post.l is False
    assert result.zhegalkin.polynomial == "a ^ b ^ a*b"
