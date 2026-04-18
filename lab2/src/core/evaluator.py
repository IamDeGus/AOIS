from __future__ import annotations

from .expr_ast import BinaryOp, Const, Expr, UnaryOp, Var


class EvaluationError(ValueError):
    pass


def evaluate_expression(node: Expr, values: dict[str, int]) -> int:
    if isinstance(node, Const):
        return node.value

    if isinstance(node, Var):
        if node.name not in values:
            raise EvaluationError(f"Переменная '{node.name}' не определена")
        value = values[node.name]
        if value not in (0, 1):
            raise EvaluationError(f"Ожидалось 0/1 для '{node.name}', получено: {value}")
        return value

    if isinstance(node, UnaryOp):
        if node.op != "!":
            raise EvaluationError(f"Неподдерживаемая унарная операция: {node.op}")
        return 1 - evaluate_expression(node.operand, values)

    if isinstance(node, BinaryOp):
        left = evaluate_expression(node.left, values)
        right = evaluate_expression(node.right, values)

        if node.op == "&":
            return left & right
        if node.op == "|":
            return left | right
        if node.op == "->":
            return int((not left) or right)
        if node.op == "~":
            return int(left == right)

        raise EvaluationError(f"Неподдерживаемая бинарная операция: {node.op}")

    raise EvaluationError(f"Неподдерживаемый тип узла: {type(node)!r}")
