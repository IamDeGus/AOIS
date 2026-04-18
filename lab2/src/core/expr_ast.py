from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Expr:
    """Base class for expression AST nodes."""


@dataclass(frozen=True)
class Var(Expr):
    name: str


@dataclass(frozen=True)
class Const(Expr):
    value: int


@dataclass(frozen=True)
class UnaryOp(Expr):
    op: str
    operand: Expr


@dataclass(frozen=True)
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr


def collect_variables(node: Expr) -> tuple[str, ...]:
    names: set[str] = set()

    def _walk(current: Expr) -> None:
        if isinstance(current, Var):
            names.add(current.name)
            return
        if isinstance(current, UnaryOp):
            _walk(current.operand)
            return
        if isinstance(current, BinaryOp):
            _walk(current.left)
            _walk(current.right)
            return
        if isinstance(current, Const):
            return
        raise TypeError(f"Unsupported AST node: {type(current)!r}")

    _walk(node)
    return tuple(sorted(names))


def iter_nodes(node: Expr) -> Iterable[Expr]:
    yield node
    if isinstance(node, UnaryOp):
        yield from iter_nodes(node.operand)
    elif isinstance(node, BinaryOp):
        yield from iter_nodes(node.left)
        yield from iter_nodes(node.right)
