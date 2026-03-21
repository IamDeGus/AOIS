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

        if int(value) == 0:
            return bits

        val: float = float(value)
        exp: int = 0

        while val >= 2 and exp <= cls.SHIFT:
            val /= 2
            exp += 1
        while val < 1 and -exp > cls.SHIFT:
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
    
    def to_decimal_float(self) -> float:
        if int(self) == 0:
            return 0
        
        sign, exp, val = self.unzip()
        
        value: float = 0
        for bit in val[::-1]:
            value = value / 2 + int(bit)
        value = value / 2 + 1
        
        exponent: int = 0
        for bit in exp:
            exponent = exponent * 2 + int(bit)

        exponent -= self.SHIFT

        return ((-1) ** int(sign)) * value * (2 ** exponent)
    
    def __str__(self) -> str:
        return ''.join(map(str, self.__bits))

    def __int__(self) -> int:
        return int(str(self))

    def unzip(self) -> tuple[list[int]]:
        sign = str(self)[0]
        exp = str(self)[self.SIGN: self.EXPONENT + self.SIGN]
        val = str(self)[self.EXPONENT + self.SIGN:]
        return sign, exp, val

    @classmethod
    def val_normalize(cls, val: str) -> tuple:
        diff = len(val) - cls.FRACTION - 1

        if diff < 0:
            val = val + '0' * (-diff)
        if diff > 0:
            val = val[:-diff]

        val = val[1:]

        return val, diff

    def __add__(self, other: Binary_float) -> Binary_float:
        elmnt1 = self.copy()
        elmnt2 = other.copy()

        result_sign = '0'
        result_exp = Binary_int(str(self.SHIFT))
        result_val = Binary_int('0')

        exp1 = Binary_int(elmnt1.unzip()[1], Representation.DIRECT, 2)
        exp2 = Binary_int(elmnt2.unzip()[1], Representation.DIRECT, 2)

        diff = (exp1 - exp2).direct().to_decimal_int()
        
        if int(exp1) == 0:
            val1 = '0' + elmnt1.unzip()[2]
        else:
            val1 = '1' + elmnt1.unzip()[2]

        if int(exp2) == 0:
            val2 = '0' + elmnt2.unzip()[2]
        else:
            val2 = '1' + elmnt2.unzip()[2]

        if diff > 0:
            val2 = ('0' * diff + val2)[:self.FRACTION + 1]
            result_exp = exp1
        elif diff < 0:
            val1 = ('0' * (-diff) + val1)[:self.FRACTION + 1]
            result_exp = exp2
        else:
            result_exp = exp1

        val2 = Binary_int(val2, Representation.DIRECT, 2, 64)
        val1 = Binary_int(val1, Representation.DIRECT, 2, 64)

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
        result_val, diff = self.val_normalize(result_val)

        result_exp += Binary_int(str(diff))
        result_exp = str(result_exp)[-self.EXPONENT:]

        return Binary_float(result_sign + result_exp + result_val, 2)

    def __sub__(self, other: Binary_float) -> Binary_float:
        sign = (other.__bits[0] + 1) % 2
        sub_other = Binary_float(str(sign) + str(other)[1:], 2)
        return self + sub_other

    def __mul__(self, other: Binary_float) -> Binary_float:
        elmnt1 = self.copy()
        elmnt2 = other.copy()
        
        if int(elmnt1) == 0 or int(elmnt2) == 0:
            return Binary_float('0')

        result_sign = str((elmnt1.__bits[0] + elmnt2.__bits[0]) % 2)

        exp1 = Binary_int(elmnt1.unzip()[1], Representation.DIRECT, 2)
        exp2 = Binary_int(elmnt2.unzip()[1], Representation.DIRECT, 2)

        result_exp = (exp1 + exp2 - Binary_int(str(self.SHIFT))).direct()

        if int(str(exp1)) == 0:
            val1 = '0' + elmnt1.unzip()[2]
        else:
            val1 = '1' + elmnt1.unzip()[2]

        if int(str(exp2)) == 0:
            val2 = '0' + elmnt2.unzip()[2]
        else:
            val2 = '1' + elmnt2.unzip()[2]

        result_val = str(int(
            Binary_int(val1, Representation.DIRECT, 2, 64) *
            Binary_int(val2, Representation.DIRECT, 2, 64)))

        result_val, diff = self.val_normalize(result_val)

        result_exp += Binary_int(str(diff // 24))
        result_exp = str(result_exp)[-self.EXPONENT:]

        return Binary_float(result_sign + result_exp + result_val, 2)

    def __truediv__(self, other: Binary_float) -> Binary_float:
        elmnt1 = self.copy()
        elmnt2 = other.copy()
        
        if int(elmnt1) == 0 and int(elmnt2) != 0:
            return Binary_float('0')

        result_sign = str((elmnt1.__bits[0] + elmnt2.__bits[0]) % 2)

        exp1 = Binary_int(elmnt1.unzip()[1], Representation.DIRECT, 2)
        exp2 = Binary_int(elmnt2.unzip()[1], Representation.DIRECT, 2)

        result_exp = (exp1 - exp2 + Binary_int(str(self.SHIFT))).direct()

        if int(str(exp1)) == 0:
            val1 = '0' + elmnt1.unzip()[2]
        else:
            val1 = '1' + elmnt1.unzip()[2]

        if int(str(exp2)) == 0:
            val2 = '0' + elmnt2.unzip()[2]
        else:
            val2 = '1' + elmnt2.unzip()[2]
            
        div, _ = (Binary_int(val1, Representation.DIRECT, 2, 64, 10) /
                  Binary_int(val2, Representation.DIRECT, 2, 64, 10))

        result_val = str(int(div))[-2 * (self.FRACTION + 1):]

        result_val, diff = self.val_normalize(result_val)

        result_exp += Binary_int(str(diff + 13))
        result_exp = str(result_exp)[-self.EXPONENT:]

        return Binary_float(result_sign + result_exp + result_val, 2)
