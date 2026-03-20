import pytest

from src.binary_int import Binary_int
from src.representation import Representation

class TestClassIntBinary:
    @pytest.mark.parametrize(
        "value, natation, expected", 
        [
            ('0', 10, 0), 
            ('+1', 10, 1),             
            ('2', 10, 10),             
            ('3', 10, 11),             
            ('4', 10, 100),             
            ('5', 10, 101),             
            ('+6', 10, 110),             
            ('+7', 10, 111),             
            ('8', 10, 1000),             
            ('9', 10, 1001),             
            ('-1', 10, 10000000000000000000000000000001),             
            ('-2', 10, 10000000000000000000000000000010),             
            ('-3', 10, 10000000000000000000000000000011),             
            ('-4', 10, 10000000000000000000000000000100),             
            ('-5', 10, 10000000000000000000000000000101),
            ('1000110', 2, 1000110),             
            ('0100110', 2, 100110),             
            ('1011111', 2, 1011111),             
            ('0001011', 2, 1011),             
            ([1, 0, 0, 0, 0, 0, 0, 0, 
              0, 0, 0, 0, 0, 0, 0, 0, 
              0, 0, 0, 0, 0, 0, 0, 0, 
              0, 1, 0, 0, 0, 1, 0, 1], 10, 10000000000000000000000001000101),
            ([0, 0, 0, 0, 0, 0, 0, 0, 
              0, 0, 0, 0, 0, 0, 0, 0, 
              0, 0, 0, 0, 0, 0, 0, 0, 
              0, 1, 1, 0, 0, 1, 0, 1], 10, 1100101)])
    def test_good_init_direct_str(self, value, natation, expected):
        binary = Binary_int(value, Representation.DIRECT, natation)
        assert int(binary) == expected
        
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
    def test_bad_init_direct_str(self, value, natation, expected_exception):
        with pytest.raises(expected_exception):
            Binary_int(value, Representation.DIRECT, natation)


    @pytest.mark.parametrize(
        "value, representation, expected", 
        [
            ('11000000000000000000000000011001',
             Representation.DIRECT,
             '10111111111111111111111111100110'),
            ('01000000000000000000000000011001',
             Representation.DIRECT,
             '01000000000000000000000000011001'),            
            ('01000000000000000000000000011001',
             Representation.ONES_COMPLEMENT,
             '01000000000000000000000000011001'),   
            ('11000000000000000000000000011001',
             Representation.ONES_COMPLEMENT,
             '11000000000000000000000000011001'),
            ('11000000000000000000000000011001',
             Representation.TWOS_COMPLEMENT,
             '11000000000000000000000000011000'),
            ('01000000000000000000000000011001',
             Representation.TWOS_COMPLEMENT,
             '01000000000000000000000000011001')])
    def test_ones_complement(self, value, representation, expected):
        binary = Binary_int(value, representation, 2)
        assert str(binary.ones_complement()) == expected
    
    @pytest.mark.parametrize(
        "value, representation, expected", 
        [
            ('11000000000000000000000000011001',
             Representation.DIRECT,
             '10111111111111111111111111100111'),
            ('01000000000000000000000000011001',
             Representation.DIRECT,
             '01000000000000000000000000011001'),            
            ('01000000000000000000000000011001',
             Representation.ONES_COMPLEMENT,
             '01000000000000000000000000011001'),   
            ('11000000000000000000000000011001',
             Representation.ONES_COMPLEMENT,
             '11000000000000000000000000011010'),
            ('11000000000000000000000000011001',
             Representation.TWOS_COMPLEMENT,
             '11000000000000000000000000011001'),
            ('01000000000000000000000000011001',
             Representation.TWOS_COMPLEMENT,
             '01000000000000000000000000011001')])
    def test_twos_complement(self, value, representation, expected):
        binary = Binary_int(value, representation, 2)
        assert str(binary.twos_complement()) == expected
    
    
    @pytest.mark.parametrize(
        "value, representation, expected", 
        [
            ('11000000000000000000000000011001',
             Representation.DIRECT,
             '11000000000000000000000000011001'),
            ('01000000000000000000000000011001',
             Representation.DIRECT,
             '01000000000000000000000000011001'),            
            ('01000000000000000000000000011001',
             Representation.ONES_COMPLEMENT,
             '01000000000000000000000000011001'),   
            ('11000000000000000000000000011001',
             Representation.ONES_COMPLEMENT,
             '10111111111111111111111111100110'),
            ('11000000000000000000000000011001',
             Representation.TWOS_COMPLEMENT,
             '10111111111111111111111111100111'),
            ('01000000000000000000000000011001',
             Representation.TWOS_COMPLEMENT,
             '01000000000000000000000000011001')])
    def test_direct(self, value, representation, expected):
        binary = Binary_int(value, representation, 2)
        assert str(binary.direct()) == expected
            
    @pytest.mark.parametrize(
        "A, B, expected",
        [
            (Binary_int('4'),
             Binary_int('8'),
             '00000000000000000000000000001100'),
            (Binary_int('256'),
             Binary_int('15'),
             '00000000000000000000000100001111'),
            (Binary_int('1'),
             Binary_int('15'),
             '00000000000000000000000000010000'),
            (Binary_int('-1'),
             Binary_int('15'),
             '00000000000000000000000000001110'),
            (Binary_int('-1'),
             Binary_int('-15'),
             '10000000000000000000000000010000'),
            (Binary_int('-256'),
             Binary_int('-15'),
             '10000000000000000000000100001111'),
            (Binary_int('3'),
             Binary_int('0'),
             '00000000000000000000000000000011'),
            (Binary_int('3'),
             Binary_int('-0'),
             '00000000000000000000000000000011'),
            (Binary_int('3'),
             Binary_int('-7'),
             '10000000000000000000000000000100'),
        ])
    def test_add(self, A, B, expected):
        result = (A + B).direct()
        assert str(result) == expected
    
    @pytest.mark.parametrize(
        "A, B, expected",
        [
            (Binary_int('4'),
             Binary_int('8'),
             '10000000000000000000000000000100'),
            (Binary_int('256'),
             Binary_int('15'),
             '00000000000000000000000011110001'),
            (Binary_int('1'),
             Binary_int('15'),
             '10000000000000000000000000001110'),
            (Binary_int('-1'),
             Binary_int('15'),
             '10000000000000000000000000010000'),
            (Binary_int('-1'),
             Binary_int('-15'),
             '00000000000000000000000000001110'),
            (Binary_int('-256'),
             Binary_int('-15'),
             '10000000000000000000000011110001'),
            (Binary_int('3'),
             Binary_int('0'),
             '00000000000000000000000000000011'),
            (Binary_int('3'),
             Binary_int('-0'),
             '00000000000000000000000000000011'),
            (Binary_int('3'),
             Binary_int('-7'),
             '00000000000000000000000000001010'),
        ])
    def test_sub(self, A, B, expected):
        result = (A - B).direct()
        assert str(result) == expected
      
      
    @pytest.mark.parametrize(
        "A, B, expected",
        [
            (Binary_int('4'),
             Binary_int('8'),
             '00000000000000000000000000100000'),
            (Binary_int('1'),
             Binary_int('3'),
             '00000000000000000000000000000011'),
            (Binary_int('10'),
             Binary_int('7'),
             '00000000000000000000000001000110'),
             (Binary_int('-4'),
             Binary_int('8'),
             '10000000000000000000000000100000'),
            (Binary_int('1'),
             Binary_int('-3'),
             '10000000000000000000000000000011'),
            (Binary_int('-10'),
             Binary_int('7'),
             '10000000000000000000000001000110'),
            (Binary_int('-4'),
             Binary_int('-8'),
             '00000000000000000000000000100000'),
            (Binary_int('-1'),
             Binary_int('-3'),
             '00000000000000000000000000000011'),
            (Binary_int('0'),
             Binary_int('7'),
             '00000000000000000000000000000000'),
            (Binary_int('0'),
             Binary_int('-7'),
             '00000000000000000000000000000000'),
        ])  
    def test_mul(self, A, B, expected):
        result = A * B
        assert str(result) == expected


    @pytest.mark.parametrize(
        "A, B, expectedR, expectedQ",
        [
            (Binary_int('8'),
             Binary_int('4'),
             '00000000000000000000000001000000',
             '00000000000000000000000000000000'),
            (Binary_int('1'),
             Binary_int('1'),
             '00000000000000000000000000100000',
             '00000000000000000000000000000000'),
            (Binary_int('13'),
             Binary_int('1'),
             '00000000000000000000000110100000',
             '00000000000000000000000000000000'),
            (Binary_int('15'),
             Binary_int('4'),
             '00000000000000000000000001111000',
             '00000000000000000000000000000000'),
            (Binary_int('11'),
             Binary_int('4'),
             '00000000000000000000000001011000',
             '00000000000000000000000000000000'),
            (Binary_int('0'),
             Binary_int('3'),
             '00000000000000000000000000000000',
             '00000000000000000000000000000000'),
            (Binary_int('127'),
             Binary_int('64'),
             '00000000000000000000000000111111',
             '00000000000000000000000000100000'),
            (Binary_int('-127'),
             Binary_int('64'),
             '10000000000000000000000000111111',
             '00000000000000000000000000100000'),
            (Binary_int('-8'),
             Binary_int('-4'),
             '00000000000000000000000001000000',
             '00000000000000000000000000000000'),
            (Binary_int('8'),
             Binary_int('-4'),
             '10000000000000000000000001000000',
             '00000000000000000000000000000000'),
        ])  
    def test_div(self, A, B, expectedR, expectedQ):
        remainder, quotient = A / B
        assert str(remainder) == expectedR
        assert str(quotient) == expectedQ

    def test_zero_div(self):
        with pytest.raises(ZeroDivisionError, match="division by zero"):
            _ = Binary_int('3') / Binary_int('0')


    @pytest.mark.parametrize(
        "value", 
        [
            (0), (1), (466), (-5), (-7774), (16)
        ])
    def test_to_decimal_int(self, value):
        a = Binary_int(str(value))
        assert a.to_decimal_int() == value
