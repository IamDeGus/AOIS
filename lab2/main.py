from __future__ import annotations

import sys

from src.analysis import analyze_expression, format_analysis
from src.core.parser import ParseError
from src.core.truth_table import TruthTableError


def _read_expression() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()

    return input("Введите логическую функцию: ").strip()


def main() -> None:
    expression = _read_expression()

    if not expression:
        print("Пустой ввод. Пример: !(a & b) -> c")
        return

    try:
        report = analyze_expression(expression)
    except (ParseError, TruthTableError, ValueError) as error:
        print(f"Ошибка: {error}")
        return

    print(format_analysis(report))


if __name__ == "__main__":
    main()
