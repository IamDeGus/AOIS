from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .expr_ast import BinaryOp, Const, Expr, UnaryOp, Var


ALLOWED_VARIABLES: Final[set[str]] = {"a", "b", "c", "d", "e"}


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    pos: int


class ParseError(ValueError):
    pass


class TokenStream:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._index = 0

    def peek(self) -> Token:
        return self._tokens[self._index]

    def pop(self) -> Token:
        token = self._tokens[self._index]
        self._index += 1
        return token

    def match(self, *kinds: str) -> Token | None:
        token = self.peek()
        if token.kind in kinds:
            self._index += 1
            return token
        return None


def tokenize(expression: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0

    while i < len(expression):
        ch = expression[i]

        if ch.isspace():
            i += 1
            continue

        if ch in "()&|!~":
            kind = {
                "(": "LPAREN",
                ")": "RPAREN",
                "&": "AND",
                "|": "OR",
                "!": "NOT",
                "~": "EQUIV",
            }[ch]
            tokens.append(Token(kind=kind, value=ch, pos=i))
            i += 1
            continue

        if ch == "-" and i + 1 < len(expression) and expression[i + 1] == ">":
            tokens.append(Token(kind="IMPL", value="->", pos=i))
            i += 2
            continue

        if ch in "01":
            tokens.append(Token(kind="CONST", value=ch, pos=i))
            i += 1
            continue

        if ch.isalpha():
            name = ch.lower()
            if name not in ALLOWED_VARIABLES:
                raise ParseError(
                    f"Недопустимая переменная '{ch}' на позиции {i}. Допустимо: a,b,c,d,e"
                )
            tokens.append(Token(kind="VAR", value=name, pos=i))
            i += 1
            continue

        raise ParseError(f"Неожиданный символ '{ch}' на позиции {i}")

    tokens.append(Token(kind="EOF", value="", pos=len(expression)))
    return tokens


class Parser:
    def __init__(self, expression: str) -> None:
        self.expression = expression
        self.stream = TokenStream(tokenize(expression))

    def parse(self) -> Expr:
        if not self.expression.strip():
            raise ParseError("Пустое выражение")

        node = self._parse_equiv()
        tail = self.stream.peek()
        if tail.kind != "EOF":
            raise ParseError(f"Лишние токены после позиции {tail.pos}")
        return node

    def _parse_equiv(self) -> Expr:
        node = self._parse_impl()
        while self.stream.match("EQUIV"):
            right = self._parse_impl()
            node = BinaryOp(op="~", left=node, right=right)
        return node

    def _parse_impl(self) -> Expr:
        left = self._parse_or()
        if self.stream.match("IMPL"):
            right = self._parse_impl()
            return BinaryOp(op="->", left=left, right=right)
        return left

    def _parse_or(self) -> Expr:
        node = self._parse_and()
        while self.stream.match("OR"):
            right = self._parse_and()
            node = BinaryOp(op="|", left=node, right=right)
        return node

    def _parse_and(self) -> Expr:
        node = self._parse_unary()
        while self.stream.match("AND"):
            right = self._parse_unary()
            node = BinaryOp(op="&", left=node, right=right)
        return node

    def _parse_unary(self) -> Expr:
        if self.stream.match("NOT"):
            return UnaryOp(op="!", operand=self._parse_unary())

        token = self.stream.peek()
        if self.stream.match("LPAREN"):
            node = self._parse_equiv()
            if not self.stream.match("RPAREN"):
                raise ParseError(f"Ожидалась ')' после позиции {token.pos}")
            return node

        const = self.stream.match("CONST")
        if const is not None:
            return Const(value=int(const.value))

        var = self.stream.match("VAR")
        if var is not None:
            return Var(name=var.value)

        raise ParseError(f"Неожиданный токен '{token.value}' на позиции {token.pos}")


def parse_expression(expression: str) -> Expr:
    return Parser(expression).parse()
