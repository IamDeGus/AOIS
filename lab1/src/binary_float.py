from __future__ import annotations
from .binary_int import Binary_int
from .representation import Representation


class Binary_float:
    SIZE = 32
    SIGN = 1
    EXPONENT = 8
    FRACTION = 23

    SHIFT = 127

    def __init__(self, value: str | list[int], notation: int = 10):
        if isinstance(value, list):
            if len(value) != self.SIZE:
                raise ValueError(f"array len must be {self.SIZE}")
            self.__bits = value
            return

        if notation == 10:
            self.__bits = self.from_decimal(value)
            return
        if notation == 2:
            self.__bits = self.from_binary(value)
            return

        raise ValueError("notation must be 10 or 2")

    @classmethod
    def from_decimal(cls, value: str) -> list[int]:
        if not isinstance(value, str):
            raise TypeError("value must be str")

        bits: list = [0] * cls.SIZE

        if value[0] == '-':
            bits[0] = 1
            value = value[1:]
        elif value[0] == '+':
            value = value[1:]
        
        if str(value == 0):
            return list('00000000011111111111111111111111')

        val: float = float(value)
        exp: int = 0

        while val >= 2:
            val /= 2
            exp += 1
        while val < 1:
            val *= 2
            exp -= 1

        true_exp: int = exp + cls.SHIFT
        true_val: float = val - 1

        for i in range(-cls.FRACTION, 0):
            true_val *= 2
            if true_val >= 1:
                bits[i] = 1
                true_val -= 1

        iter: int = -cls.FRACTION - 1

        while true_exp >= 2:
            if -iter == cls.SIZE:
                raise ValueError("number is very big")

            bits[iter] = true_exp % 2
            iter -= 1
            true_exp //= 2

        bits[iter] = true_exp

        return bits

    @classmethod
    def from_binary(cls, value: str) -> list[int]:
        bits: list = [0] * cls.SIZE

        for i in range(-1, -len(value)-1, -1):
            bits[i] = int(value[i])

        return bits

    def copy(self) -> Binary_float:
        return Binary_float(self.__bits.copy())

    def __str__(self) -> str:
        return ''.join(map(str, self.__bits))

    def __int__(self) -> int:
        return int(str(self))

    def unzip(self) -> tuple[list[int]]:
        sign = str(self)[0]
        exp = str(self)[self.SIGN: self.EXPONENT + self.SIGN]
        val = str(self)[self.EXPONENT + self.SIGN:]
        return sign, exp, val

    def __add__(self, other: Binary_float) -> Binary_float:
        elmnt1 = self.copy()
        elmnt2 = other.copy()

        result_sign = '0'
        result_exp = Binary_int(str(self.SHIFT))
        result_val = Binary_int('0')

        exp1 = Binary_int(elmnt1.unzip()[1], Representation.DIRECT, 2)
        exp2 = Binary_int(elmnt2.unzip()[1], Representation.DIRECT, 2)

        diff = (exp1 - exp2).to_decimal_int()

        val1 = '1' + elmnt1.unzip()[2]
        val2 = '1' + elmnt2.unzip()[2]

        if diff > 0:
            val2 = ('0' * (diff) + val2)[:self.FRACTION + 1]
            result_exp = exp1

        if diff < 0:
            val1 = ('0' * (-diff) + val1)[:self.FRACTION + 1]
            result_exp = exp2

        val2 = Binary_int(val2, Representation.DIRECT, 2)
        val1 = Binary_int(val1, Representation.DIRECT, 2)

        sign1 = elmnt1.unzip()[0]
        sign2 = elmnt2.unzip()[0]

        if sign1 == sign2:
            result_sign = sign1
            result_val = val1 + val2
        elif val1 > val2:
            result_sign = sign1
            result_val = val1 - val2
        elif val1 < val2:
            result_sign = sign2
            result_val = val2 - val1

        result_val = str(int(result_val))
        diff = len(result_val) - self.FRACTION - 1

        if diff < 0:
            result_val = result_val + '0' * (-diff)
        if diff > 0:
            result_val = result_val[:-diff]

        result_val = result_val[1:]

        result_exp += Binary_int(str(diff))
        result_exp = str(result_exp)[-self.EXPONENT:]

        return Binary_float(result_sign + result_exp + result_val, 2)
