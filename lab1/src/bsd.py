from __future__ import annotations
from .binary_int import Binary_int

class Gray_bcd:
    DIGIT_BITS = 4
    SIZE = 32

    def __init__(self, value: str | int, notation: int = 10):
        if notation == 10:
            self.__bits = self.from_decimal(value)
            return

        if notation == 2:
            self.__bits = self.from_binary(value)
            return

        raise ValueError("notation must be 10 or 2")

    @classmethod
    def from_decimal(cls, value: str | int) -> list[int]:
        if isinstance(value, int):
            if value < 0:
                raise ValueError("value must be non-negative")
            decimal = str(value)
        elif isinstance(value, str):
            decimal = value.strip()
            if decimal.startswith("+"):
                decimal = decimal[1:]
            if decimal.startswith("-"):
                raise ValueError("value must be non-negative")
            if decimal == "":
                raise ValueError("value must not be empty")
            if not decimal.isdigit():
                raise ValueError("value must contain only decimal digits")
        else:
            raise TypeError("value must be str or int")

        bits = ""
        for ch in decimal:
            digit = int(ch)
            bin_nibble = Binary_int(str(digit))
            gray_nibble = cls._binary_nibble_to_gray(bin_nibble)
            bits += gray_nibble

        return [int(bit) for bit in bits]

    @classmethod
    def from_binary(cls, value: str) -> list[int]:
        if not isinstance(value, str):
            raise TypeError("value must be str")

        cleaned = ""
        for ch in value:
            if ch == " " or ch == "_":
                continue
            cleaned += ch

        if cleaned == "":
            raise ValueError("value must not be empty")

        for ch in cleaned:
            if ch != "0" and ch != "1":
                raise ValueError("gray-bcd must contain only 0 and 1")

        if len(cleaned) % cls.DIGIT_BITS != 0:
            raise ValueError("gray-bcd length must be multiple of 4")

        for i in range(0, len(cleaned), cls.DIGIT_BITS):
            nibble = cleaned[i:i + cls.DIGIT_BITS]
            cls._gray_nibble_to_digit(nibble)

        bits: list[int] = []
        for ch in cleaned:
            bits.append(int(ch))

        return bits

    @classmethod
    def _binary_nibble_to_gray(cls, binary_nibble: Binary_int) -> str:
        binary = str(binary_nibble)[-cls.DIGIT_BITS:]
        result = binary[0]

        for i in range(1, cls.DIGIT_BITS):
            prev_bit = int(binary[i - 1])
            curr_bit = int(binary[i])
            result += str((prev_bit + curr_bit) % 2)

        return result

    @staticmethod
    def _gray_nibble_to_binary(gray_nibble: str) -> str:
        b0 = int(gray_nibble[0])
        b1 = (b0 + int(gray_nibble[1])) % 2
        b2 = (b1 + int(gray_nibble[2])) % 2
        b3 = (b2 + int(gray_nibble[3])) % 2
        return f"{b0}{b1}{b2}{b3}"

    @classmethod
    def _gray_nibble_to_digit(cls, gray_nibble: str) -> int:
        binary_nibble = cls._gray_nibble_to_binary(gray_nibble)
        digit = 0
        for bit in binary_nibble:
            digit = digit * 2 + int(bit)
        if digit > 9:
            raise ValueError(
                f"invalid BCD digit in gray nibble: {gray_nibble}")
        return digit

    def __str__(self) -> str:
        return "".join(map(str, self.__bits))

    def __int__(self) -> int:
        return self.to_decimal_int()

    def to_decimal_int(self) -> int:
        bits = self._normalized_gray_bits()
        value = 0

        for i in range(0, len(bits), self.DIGIT_BITS):
            nibble = bits[i:i + self.DIGIT_BITS]
            digit = self._gray_nibble_to_digit(nibble)
            value = value * 10 + digit

        return value

    def __add__(self, other: Gray_bcd) -> Gray_bcd:
        if not isinstance(other, Gray_bcd):
            return NotImplemented

        left_digits = self._to_decimal_digits()
        right_digits = other._to_decimal_digits()

        i = len(left_digits) - 1
        j = len(right_digits) - 1
        carry = 0
        result_digits: list[int] = []

        while i >= 0 or j >= 0 or carry:
            left = left_digits[i] if i >= 0 else 0
            right = right_digits[j] if j >= 0 else 0
            total = left + right + carry

            if total >= 10:
                total -= 10
                carry = 1
            else:
                carry = 0

            result_digits.append(total)
            i -= 1
            j -= 1

        result_digits.reverse()

        result_decimal = ""
        for digit in result_digits:
            result_decimal += str(digit)

        return Gray_bcd(result_decimal)

    def _normalized_gray_bits(self) -> str:
        bits = str(self)

        if bits == "":
            return "0000"

        first_one = -1
        for idx, bit in enumerate(bits):
            if bit == "1":
                first_one = idx
                break

        if first_one == -1:
            return "0000"

        bits = bits[first_one:]
        while len(bits) % self.DIGIT_BITS != 0:
            bits = "0" + bits

        return bits

    def _to_decimal_digits(self) -> list[int]:
        bits = self._normalized_gray_bits()
        digits: list[int] = []

        for i in range(0, len(bits), self.DIGIT_BITS):
            nibble = bits[i:i + self.DIGIT_BITS]
            digits.append(self._gray_nibble_to_digit(nibble))

        if not digits:
            return [0]

        return digits
