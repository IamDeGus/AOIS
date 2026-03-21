from __future__ import annotations

from src import Binary_float, Binary_int, Gray_bcd


def _read_choice(prompt: str, allowed: tuple[str, ...]) -> str:
    while True:
        value = input(prompt).strip()
        if value in allowed:
            return value
        print(f"Неверный выбор. Допустимо: {', '.join(allowed)}")


def _read_notation() -> int:
    choice = _read_choice("Система ввода (10 или 2): ", ("10", "2"))
    return int(choice)


def _read_number(name: str, notation: int) -> str:
    raw = input(f"Введите {name} число: ").strip()
    if notation == 2:
        return raw.replace(" ", "").replace("_", "")
    return raw


def _print_int_result(result: Binary_int) -> None:
    direct = result.direct()
    print("Результат (binary):", str(direct))
    print("Результат (decimal):", direct.to_decimal_int())


def _print_float_result(result: Binary_float) -> None:
    print("Результат (binary):", str(result))
    print("Результат (decimal):", result.to_decimal_float())


def _print_bsd_result(result: Gray_bcd) -> None:
    print("Результат (gray-bcd):", str(result))
    print("Результат (decimal):", result.to_decimal_int())


def _run_int_mode() -> None:
    print("\n[Режим Binary_int]")
    print("Операции: +  -  *  /")

    notation = _read_notation()
    op = _read_choice("Операция (+, -, *, /): ", ("+", "-", "*", "/"))

    left = Binary_int(_read_number("первое", notation), notation=notation)
    right = Binary_int(_read_number("второе", notation), notation=notation)

    if op == "+":
        _print_int_result(left + right)
        return
    if op == "-":
        _print_int_result(left - right)
        return
    if op == "*":
        _print_int_result(left * right)
        return

    remainder, quotient = left / right
    print("Частное:")
    _print_int_result(remainder)
    print("Остаток:")
    _print_int_result(quotient)


def _run_float_mode() -> None:
    print("\n[Режим Binary_float]")
    print("Операции: +  -  *  /")

    notation = _read_notation()
    op = _read_choice("Операция (+, -, *, /): ", ("+", "-", "*", "/"))

    left = Binary_float(_read_number("первое", notation), notation=notation)
    right = Binary_float(_read_number("второе", notation), notation=notation)

    if op == "+":
        _print_float_result(left + right)
        return
    if op == "-":
        _print_float_result(left - right)
        return
    if op == "*":
        _print_float_result(left * right)
        return

    _print_float_result(left / right)


def _run_bsd_mode() -> None:
    print("\n[Режим Gray_bcd]")
    print("Операции: +")

    notation = _read_notation()
    _ = _read_choice("Операция (+): ", ("+",))

    left = Gray_bcd(_read_number("первое", notation), notation=notation)
    right = Gray_bcd(_read_number("второе", notation), notation=notation)

    _print_bsd_result(left + right)


def main() -> None:
    print("Калькулятор бинарных типов")
    print("1 - Binary_int")
    print("2 - Binary_float")
    print("3 - Gray_bcd")
    print("0 - Выход")

    while True:
        choice = _read_choice("\nВыберите режим: ", ("0", "1", "2", "3"))
        if choice == "0":
            print("Выход.")
            return

        try:
            if choice == "1":
                _run_int_mode()
            elif choice == "2":
                _run_float_mode()
            else:
                _run_bsd_mode()
        except Exception as error:  # noqa: BLE001 - simple CLI needs broad guard
            print("Ошибка:", error)


if __name__ == "__main__":
    main()
