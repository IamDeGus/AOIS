import pytest

from src.binary_float import Binary_float

class TestClassFloatBinary:
    @pytest.mark.parametrize(
        "value, natation, expected",
        [
            ('0', 10, '00000000000000000000000000000000'),
            ('+1', 10, '00111111100000000000000000000000'),
            ('2', 10, '01000000000000000000000000000000'),
            ('3', 10, '01000000010000000000000000000000'),
            ('4', 10, '01000000100000000000000000000000'),
            ('5', 10, '01000000101000000000000000000000'),
            ('+6', 10, '01000000110000000000000000000000'),
            ('+7', 10, '01000000111000000000000000000000'),
            ('8', 10, '01000001000000000000000000000000'),
            ('9', 10, '01000001000100000000000000000000'),
            ('-1', 10, '10111111100000000000000000000000'),
            ('-2', 10, '11000000000000000000000000000000'),
            ('-3', 10, '11000000010000000000000000000000'),
            ('-4', 10, '11000000100000000000000000000000'),
            ('-5', 10, '11000000101000000000000000000000'),
            ('00000000100000000000000001000110', 2,
             '00000000100000000000000001000110'),
            ('00000000000110000000000000100110', 2,
             '00000000000110000000000000100110'),
            ('10000000000000000000000001011111', 2,
             '10000000000000000000000001011111')])
    def test_good_init_str(self, value, natation, expected):
        binary = Binary_float(value, natation)
        assert str(binary) == expected

    @pytest.mark.parametrize(
        "value, natation, expected_exception",
        [
            (123, 10, TypeError),
            ([1, 0, 1], 10, ValueError),
            ("1010", 3, ValueError),
            ("10a01", 2, ValueError),
            (10101, 2, TypeError),
        ],
    )
    def test_bad_init_str(self, value, natation, expected_exception):
        with pytest.raises(expected_exception):
            Binary_float(value, natation)

    @pytest.mark.parametrize(
        "value, expected_sign, expected_exp, expected_val",
        [
            ('0', '0', '00000000', '00000000000000000000000'),
            ('1', '0', '01111111', '00000000000000000000000'),
            ('-1', '1', '01111111', '00000000000000000000000'),
            ('3', '0', '10000000', '10000000000000000000000'),
            ('-5', '1', '10000001', '01000000000000000000000'),
        ],
    )
    def test_unzip(self, value, expected_sign, expected_exp, expected_val):
        binary = Binary_float(value)
        sign, exp, val = binary.unzip()
        assert sign == expected_sign
        assert exp == expected_exp
        assert val == expected_val

    @pytest.mark.parametrize(
        "A, B, expected",
        [
            (Binary_float('4'), Binary_float('8'), '01000001010000000000000000000000'),
            (Binary_float('256'), Binary_float('15'), '01000011100001111000000000000000'),
            (Binary_float('1'), Binary_float('15'), '01000001100000000000000000000000'),
            (Binary_float('-1'), Binary_float('15'), '01000001011000000000000000000000'),
            (Binary_float('-1'), Binary_float('-15'), '11000001100000000000000000000000'),
            (Binary_float('-256'), Binary_float('-15'), '11000011100001111000000000000000'),
            (Binary_float('3'), Binary_float('0'), '01000000010000000000000000000000'),
            (Binary_float('3'), Binary_float('-7'), '11000000100000000000000000000000'),
        ],
    )
    def test_add(self, A, B, expected):
        result = A + B
        assert str(result) == expected

    @pytest.mark.parametrize(
        "A, B, expected",
        [
            (Binary_float('4'), Binary_float('8'), '11000000100000000000000000000000'),
            (Binary_float('256'), Binary_float('15'), '01000011011100010000000000000000'),
            (Binary_float('1'), Binary_float('15'), '11000001011000000000000000000000'),
            (Binary_float('-1'), Binary_float('15'), '11000001100000000000000000000000'),
            (Binary_float('-1'), Binary_float('-15'), '01000001011000000000000000000000'),
            (Binary_float('-256'), Binary_float('-15'), '11000011011100010000000000000000'),
            (Binary_float('3'), Binary_float('0'), '01000000010000000000000000000000'),
            (Binary_float('3'), Binary_float('-7'), '01000001001000000000000000000000'),
        ],
    )
    def test_sub(self, A, B, expected):
        result = A - B
        assert str(result) == expected

    @pytest.mark.parametrize(
        "A, B, expected",
        [
            (Binary_float('4'), Binary_float('8'), '01000010000000000000000000000000'),
            (Binary_float('1'), Binary_float('3'), '01000000010000000000000000000000'),
            (Binary_float('10'), Binary_float('7'), '01000010100011000000000000000000'),
            (Binary_float('-4'), Binary_float('8'), '11000010000000000000000000000000'),
            (Binary_float('1'), Binary_float('-3'), '11000000010000000000000000000000'),
            (Binary_float('-10'), Binary_float('7'), '11000010100011000000000000000000'),
            (Binary_float('-4'), Binary_float('-8'), '01000010000000000000000000000000'),
            (Binary_float('-1'), Binary_float('-3'), '01000000010000000000000000000000'),
            (Binary_float('0'), Binary_float('7'), '00000000000000000000000000000000'),
            (Binary_float('0'), Binary_float('-7'), '00000000000000000000000000000000'),
        ],
    )
    def test_mul(self, A, B, expected):
        result = A * B
        assert str(result) == expected

    @pytest.mark.parametrize(
        "A, B, expected",
        [
            (Binary_float('8'), Binary_float('4'), '01000000000000000000000000000000'),
            (Binary_float('1'), Binary_float('1'), '00111111100000000000000000000000'),
            (Binary_float('13'), Binary_float('1'), '01000001010100000000000000000000'),
            (Binary_float('15'), Binary_float('4'), '01000000011100000000000000000000'),
            (Binary_float('11'), Binary_float('4'), '01000000001100000000000000000000'),
            (Binary_float('0'), Binary_float('3'), '00000000000000000000000000000000'),
            (Binary_float('127'), Binary_float('64'), '00111111111111100000000000000000'),
            (Binary_float('-127'), Binary_float('64'), '10111111111111100000000000000000'),
            (Binary_float('-8'), Binary_float('-4'), '01000000000000000000000000000000'),
            (Binary_float('8'), Binary_float('-4'), '11000000000000000000000000000000'),
        ],
    )
    def test_div(self, A, B, expected):
        result = A / B
        assert str(result) == expected

    def test_zero_div(self):
        with pytest.raises(ZeroDivisionError, match="division by zero"):
            _ = Binary_float('3') / Binary_float('0')

    @pytest.mark.parametrize(
        "value", 
        [
            (0), (1), (466), (-5), (-7774), (16), (-1)
        ])
    def test_to_decimal_float(self, value):
        a = Binary_float(str(value))
        assert a.to_decimal_float() == value
