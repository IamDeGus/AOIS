import pytest

from src.analysis.canonical_forms import build_canonical_forms
from src.analysis.derivatives import derivative_vector
from src.analysis.fictive_vars import find_fictive_variables
from src.analysis.post_classes import classify_post
from src.core.evaluator import EvaluationError, evaluate_expression
from src.core.expr_ast import BinaryOp, Const, Expr, UnaryOp, Var, collect_variables, iter_nodes
from src.core.parser import ParseError, TokenStream, parse_expression, tokenize
from src.core.truth_table import TruthTableError, build_truth_table, from_vector


def test_parser_and_token_stream_error_paths() -> None:
    tokens = tokenize("a")
    stream = TokenStream(tokens)
    first = stream.pop()
    assert first.kind == "VAR"
    assert stream.peek().kind == "EOF"

    parse_expression("a ~ b ~ c")
    parse_expression("1")

    with pytest.raises(ParseError, match="Пустое выражение"):
        parse_expression("   ")

    with pytest.raises(ParseError, match="Недопустимая переменная"):
        tokenize("x")

    with pytest.raises(ParseError, match="Неожиданный символ"):
        tokenize("@")

    with pytest.raises(ParseError, match="Лишние токены"):
        parse_expression("a b")

    with pytest.raises(ParseError, match="Ожидалась"):
        parse_expression("(a | b")

    with pytest.raises(ParseError, match="Неожиданный токен"):
        parse_expression(")")


def test_evaluator_and_expr_ast_edge_cases() -> None:
    assert evaluate_expression(Const(1), {}) == 1
    assert evaluate_expression(Var("a"), {"a": 0}) == 0

    with pytest.raises(EvaluationError, match="не определена"):
        evaluate_expression(Var("a"), {})

    with pytest.raises(EvaluationError, match="Ожидалось 0/1"):
        evaluate_expression(Var("a"), {"a": 2})

    with pytest.raises(EvaluationError, match="Неподдерживаемая унарная операция"):
        evaluate_expression(UnaryOp(op="-", operand=Const(1)), {})

    with pytest.raises(EvaluationError, match="Неподдерживаемая бинарная операция"):
        evaluate_expression(BinaryOp(op="^", left=Const(0), right=Const(1)), {})

    class DummyExpr(Expr):
        pass

    with pytest.raises(EvaluationError, match="Неподдерживаемый тип узла"):
        evaluate_expression(DummyExpr(), {})

    tree = BinaryOp(op="|", left=UnaryOp(op="!", operand=Var("b")), right=Var("a"))
    assert collect_variables(tree) == ("a", "b")
    assert collect_variables(Const(0)) == ()
    assert len(tuple(iter_nodes(tree))) == 4

    with pytest.raises(TypeError, match="Unsupported AST node"):
        collect_variables(DummyExpr())


def test_truth_table_and_analysis_edge_cases() -> None:
    const_ast = Const(1)
    const_table = build_truth_table(expression="1", ast=const_ast)

    assert const_table.variables == ()
    assert const_table.rows[0].index == 0
    assert const_table.value_map(const_table.rows[0]) == {}

    with pytest.raises(TruthTableError, match="Длина вектора производной"):
        from_vector(source=const_table, vector=(1, 0), expression="bad")

    six_vars_ast = BinaryOp(
        op="|",
        left=Var("a"),
        right=BinaryOp(
            op="|",
            left=Var("b"),
            right=BinaryOp(
                op="|",
                left=Var("c"),
                right=BinaryOp(
                    op="|",
                    left=Var("d"),
                    right=BinaryOp(op="|", left=Var("e"), right=Var("f")),
                ),
            ),
        ),
    )
    with pytest.raises(TruthTableError, match="не более 5 переменных"):
        build_truth_table(expression="too_many", ast=six_vars_ast)

    contradiction = build_truth_table("a & !a", parse_expression("a & !a"))
    tautology = build_truth_table("a | !a", parse_expression("a | !a"))

    contradiction_forms = build_canonical_forms(contradiction)
    tautology_forms = build_canonical_forms(tautology)

    assert contradiction_forms.sdnf == "0"
    assert contradiction_forms.sdnf_numeric == "Sm(empty)"
    assert tautology_forms.sknf == "1"
    assert tautology_forms.sknf_numeric == "PM(empty)"

    assert derivative_vector(tautology, ()) == tautology.results_vector
    with pytest.raises(ValueError, match="отсутствует в функции"):
        derivative_vector(tautology, ("b",))

    fictive_table = build_truth_table("a | (a & b)", parse_expression("a | (a & b)"))
    fictive = find_fictive_variables(fictive_table)
    assert "b" in fictive.fictive
    assert "a" in fictive.essential

    post_const = classify_post(const_table)
    assert post_const.s is False
