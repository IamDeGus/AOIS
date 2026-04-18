from src.analysis import analyze_expression
from src.analysis.derivatives import build_derivative


def test_partial_derivative_of_equivalence() -> None:
    result = analyze_expression("a ~ b")

    derivative = build_derivative(result.table, ("a",))
    assert derivative.vector == (1, 1, 1, 1)


def test_mixed_derivative_order_two() -> None:
    result = analyze_expression("a & b & c")

    derivative = build_derivative(result.table, ("a", "b"))
    assert derivative.vector == (0, 1, 0, 1, 0, 1, 0, 1)
