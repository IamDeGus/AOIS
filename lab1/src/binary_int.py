from __future__ import annotations
from .representation import Representation


class Binary_int:
    SIZE = 32
    
    def __init__(
            self,
            value: str | list[int],
            representation: Representation = Representation.DIRECT,
            notation: int = 10):

        if isinstance(value, list):
            if len(value) != self.SIZE:
                raise ValueError(f"array len must be {self.SIZE}")
            self.__bits = value
            self.__representation = representation
            return

        if notation == 10:
            self.__bits = self.from_decimal(value)
            self.__representation = Representation.DIRECT

            match representation:
                case Representation.ONES_COMPLEMENT:
                    self = self.ones_complement()
                case Representation.TWOS_COMPLEMENT:
                    self = self.twos_complement()

            return

        if notation == 2:
            self.__bits = self.from_binary(value)
            self.__representation = representation
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

        val: int = int(value)
        iter: int = -1

        while val >= 2:
            if -iter == cls.SIZE:
                raise ValueError("number is very big")
            
            bits[iter] = val % 2
            iter -= 1
            val //= 2
            

        bits[iter] = val

        return bits

    @classmethod
    def from_binary(cls, value: str) -> list[int]:
        bits: list = [0] * cls.SIZE

        for i in range(-1, -len(value)-1, -1):
            bits[i] = int(value[i])

        return bits
    
    def copy(self) -> Binary_int:
        return Binary_int(self.__bits.copy(),
                          self.__representation)

    def direct(self) -> Binary_int:

        if self.__representation != Representation.DIRECT:
            if self.__bits[0] == 0:
                return Binary_int(self.__bits, Representation.DIRECT)
            
            result_bits = [1 - bit for bit in self.__bits]
            result_bits[0] = self.__bits[0]

            if self.__representation == Representation.TWOS_COMPLEMENT:
                result = (Binary_int(result_bits, Representation.TWOS_COMPLEMENT) +
                          Binary_int(str(1), Representation.TWOS_COMPLEMENT))
                result_bits = result.__bits
            
            return Binary_int(result_bits, Representation.DIRECT)

        return self

    def twos_complement(self) -> Binary_int:
        if self.__bits[0] == 1:
            match self.__representation:
                case Representation.DIRECT:
                        return (Binary_int(self.ones_complement().__bits, Representation.TWOS_COMPLEMENT) + 
                                Binary_int(str(1), Representation.TWOS_COMPLEMENT))
                        
                case Representation.ONES_COMPLEMENT:
                    return (Binary_int(self.__bits, Representation.TWOS_COMPLEMENT) + 
                            Binary_int(str(1), Representation.TWOS_COMPLEMENT))
        
        return Binary_int(self.__bits, Representation.TWOS_COMPLEMENT)
    

    def ones_complement(self) -> Binary_int:
        if self.__bits[0] == 1:
            match self.__representation:
                case Representation.DIRECT:
                    result_bits = [1 - bit for bit in self.__bits]
                    result_bits[0] = 1
                    return Binary_int(result_bits, Representation.ONES_COMPLEMENT)
                case Representation.TWOS_COMPLEMENT:
                    result = (self + Binary_int(str(-1)))
                    return Binary_int(result.__bits, Representation.ONES_COMPLEMENT)

        return Binary_int(self.__bits, Representation.ONES_COMPLEMENT)

    def to_decimal_int(self) -> int:
        value = 0
        for bit in self.__bits[1:]:
            value = value * 2 + bit
            
        value *= (-1) ** self.__bits[0]
        return value

    def __str__(self) -> str:
        return ''.join(map(str, self.__bits))

    def __int__(self) -> int:
        return int(str(self))

    def __add__(self, other: Binary_int) -> Binary_int:
        
        elmnt1 = self.copy()
        elmnt2 = other.copy()

        if elmnt1.__representation != Representation.TWOS_COMPLEMENT:
            elmnt1 = elmnt1.twos_complement()
        if elmnt2.__representation != Representation.TWOS_COMPLEMENT:
            elmnt2 = elmnt2.twos_complement()

        result_bits = [0] * self.SIZE
        shift = 0

        for i in range(-1, -self.SIZE - 1, -1):
            adds = elmnt1.__bits[i] + elmnt2.__bits[i] + shift

            result_bits[i] = adds % 2
            shift = adds // 2

        return Binary_int(result_bits, Representation.TWOS_COMPLEMENT)
    
    def __iadd__(self, other: Binary_int) -> Binary_int:
        return self + other

    def __sub__(self, other: Binary_int) -> Binary_int:
        
        minuend = self.copy()
        if minuend.__representation != Representation.TWOS_COMPLEMENT:
            minuend = minuend.twos_complement()
        
        subtrahend = other.copy().direct()
        subtrahend.__bits[0] = (subtrahend.__bits[0] + 1) % 2
        
        return minuend + subtrahend
    
    def __isub__(self, other: Binary_int) -> Binary_int:
        return self - other
    
    def __mul__(self, other: Binary_int) -> Binary_int:
        result = Binary_int('0')
        

        if self.__bits[0] != other.__bits[0]:
            sign = '1'
        else:
            sign = '0'
        
        for i in range(1, self.SIZE):
            if (self.__bits[i] == 1):
                shift = self.SIZE - i - 1
                B = Binary_int(sign 
                               + str(''.join(map(str, other.__bits[1:])))[shift:] 
                               + '0' * shift, 
                               Representation.DIRECT, 2)
                result += B
        
        return result.direct()

    def __truediv__(self, other: Binary_int) -> tuple[Binary_int]:
        if not isinstance(other, Binary_int):
            return NotImplemented

        dividend = self.copy().direct()
        divisor = other.copy().direct()

        if all(bit == 0 for bit in divisor.__bits[1:]):
            raise ZeroDivisionError("division by zero")

        sign = 0 if dividend.__bits[0] == divisor.__bits[0] else 1

        dividend.__bits[0] = 0
        divisor.__bits[0] = 0
        
        scaled_dividend = dividend * Binary_int('32')
        
        remainder = Binary_int('0')
        
        while scaled_dividend >= divisor:
            scaled_dividend -= divisor
            remainder += Binary_int('1')

            
        remainder.__bits[0] = sign
        quotient = scaled_dividend

        return remainder, quotient


    def __ge__(self, other: Binary_int) -> bool:
        if self.__bits[0] != other.__bits[0]:
            return self.__bits[0] < other.__bits[0]
                
        for i in range(1, self.SIZE):
            if self.__bits[i] != other.__bits[i]:
               return self.__bits[i] > other.__bits[i]
           
        return True
    
    def __gt__(self, other: Binary_int) -> bool:
        if self.__bits[0] != other.__bits[0]:
            return self.__bits[0] < other.__bits[0]
                
        for i in range(1, self.SIZE):
            if self.__bits[i] != other.__bits[i]:
               return self.__bits[i] > other.__bits[i]
           
        return False
    
    def __lt__(self, other: Binary_int) -> bool:
        return other > self
# 3 * 6
# 00000000000000000000000000000110
# 00000000000000000000000000010010


# 6 / 3 = 2
# 14 / 2 = 7
# 01110 / 00010 = 00111
# 

# 3 - 2  +1
# 1 < 2     1,_
# 10 - 2 +1
# ...
# 2 - 2  +1 1,5

# 101 - 10 +1
# 011 - 10 +1
# 001 < 10  1,_
# 10 - 10 +1
# 1,1
# 


# 1 на 10 нет
# 11 на 10 - да 11 - 10 = 01 (1)
# 11 на 10 - да 11 - 10 = 01 (11)
# 10 на 10 - да 11 - 10 = 01 (111)
# все -> ...111

# 126 / 3 = 
#  3  

    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, Binary):
    #         return NotImplemented
    #     return self._bits == other._bits

    # @classmethod
    # def from_decimal(cls, value: int) -> Binary:
    #     return cls(value, notation=10)

    # @classmethod
    # def from_bits(cls, bits: Sequence[int] | str | int) -> Binary:
    #     return cls(bits, notation=2)

    # @staticmethod
    # def _from_decimal(value: int | str | Sequence[int] | Binary) -> list[int]:
    #     if not isinstance(value, int):
    #         raise TypeError("for notation=10 value must be int")
    #     if value < 0:
    #         raise ValueError("only unsigned integers are supported")

    #     if value == 0:
    #         return [0]

    #     reversed_bits: list[int] = []
    #     current = value
    #     while current > 0:
    #         reversed_bits.append(current % 2)
    #         current //= 2

    #     bits: list[int] = []
    #     idx = len(reversed_bits) - 1
    #     while idx >= 0:
    #         bits.append(reversed_bits[idx])
    #         idx -= 1
    #     return bits

    # @classmethod
    # def _from_binary(cls, value: int | str | Sequence[int] | Binary) -> list[int]:
    #     if isinstance(value, str):
    #         return cls._bits_from_string(value)

    #     if isinstance(value, int):
    #         return cls._bits_from_binary_int(value)

    #     if isinstance(value, Sequence):
    #         bits = cls._bits_from_sequence(value)
    #         return cls._normalize(bits)

    #     raise TypeError("for notation=2 value must be int, str or sequence of bits")

    # @staticmethod
    # def _bits_from_string(raw: str) -> list[int]:
    #     if raw == "":
    #         raise ValueError("binary string cannot be empty")

    #     bits: list[int] = []
    #     for ch in raw:
    #         if ch == "0":
    #             bits.append(0)
    #             continue
    #         if ch == "1":
    #             bits.append(1)
    #             continue
    #         raise ValueError("binary string can contain only '0' and '1'")
    #     return Binary._normalize(bits)

    # @staticmethod
    # def _bits_from_sequence(raw: Sequence[int]) -> list[int]:
    #     if len(raw) == 0:
    #         raise ValueError("bit sequence cannot be empty")

    #     bits: list[int] = []
    #     for item in raw:
    #         if not isinstance(item, int):
    #             raise TypeError("bit sequence must contain only ints 0/1")
    #         if item not in (0, 1):
    #             raise ValueError("bit sequence must contain only 0 and 1")
    #         bits.append(item)
    #     return bits

    # @staticmethod
    # def _bits_from_binary_int(raw: int) -> list[int]:
    #     if raw < 0:
    #         raise ValueError("binary int cannot be negative")

    #     if raw == 0:
    #         return [0]

    #     reversed_bits: list[int] = []
    #     current = raw
    #     while current > 0:
    #         digit = current % 10
    #         if digit not in (0, 1):
    #             raise ValueError("for notation=2 int must contain only digits 0/1")
    #         reversed_bits.append(digit)
    #         current //= 10

    #     bits: list[int] = []
    #     idx = len(reversed_bits) - 1
    #     while idx >= 0:
    #         bits.append(reversed_bits[idx])
    #         idx -= 1
    #     return Binary._normalize(bits)

    # @staticmethod
    # def _normalize(bits: list[int]) -> list[int]:
    #     first_one = -1
    #     idx = 0
    #     while idx < len(bits):
    #         if bits[idx] == 1:
    #             first_one = idx
    #             break
    #         idx += 1

    #     if first_one == -1:
    #         return [0]

    #     normalized: list[int] = []
    #     idx = first_one
    #     while idx < len(bits):
    #         normalized.append(bits[idx])
    #         idx += 1
    #     return normalized
