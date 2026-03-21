import pytest

from src.bsd import Gray_bcd


class TestGrayBcd:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("0", "0000"),
            ("5", "0111"),
            ("19", "00011101"),
            (27, "00110100"),
            ("102", "000100000011"),
        ],
    )
    def test_init_from_decimal_and_str(self, value, expected):
        number = Gray_bcd(value)
        assert str(number) == expected

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("00011101", 19),
            ("00110100", 27),
            ("0001 0000 0011", 102),
            ("0001_1101", 19),
        ],
    )
    def test_from_gray_bcd_to_decimal(self, value, expected):
        number = Gray_bcd(value, 2)
        assert number.to_decimal_int() == expected
        assert int(number) == expected

    @pytest.mark.parametrize(
        "left, right, expected_decimal, expected_bits",
        [
            ("19", "8", 27, "00110100"),
            ("95", "7", 102, "000100000011"),
            ("0", "0", 0, "0000"),
        ],
    )
    def test_add(self, left, right, expected_decimal, expected_bits):
        result = Gray_bcd(left) + Gray_bcd(right)
        assert int(result) == expected_decimal
        assert str(result) == expected_bits

    @pytest.mark.parametrize(
        "value, notation, expected_exception",
        [
            (-1, 10, ValueError),
            ("-10", 10, ValueError),
            ("12a", 10, ValueError),
            ("", 10, ValueError),
            ("010", 2, ValueError),
            ("0102", 2, ValueError),
            ("1111", 2, ValueError),  # Gray nibble -> binary 1010 (not BCD)
            (1010, 2, TypeError),
            ("10", 7, ValueError),
        ],
    )
    def test_bad_init(self, value, notation, expected_exception):
        with pytest.raises(expected_exception):
            Gray_bcd(value, notation)

    def test_init_decimal_with_plus_sign(self):
        number = Gray_bcd("+27")
        assert str(number) == "00110100"
        assert number.to_decimal_int() == 27

    def test_bad_init_decimal_type(self):
        with pytest.raises(TypeError):
            Gray_bcd(1.5, 10)

    def test_bad_init_binary_empty_after_clean(self):
        with pytest.raises(ValueError):
            Gray_bcd(" _  _ ", 2)

    def test_add_with_not_gray_bcd_returns_not_implemented(self):
        assert Gray_bcd("5").__add__(5) is NotImplemented

    def test_normalized_gray_bits_empty_internal_storage(self):
        number = Gray_bcd("0")
        number._Gray_bcd__bits = []
        assert number._normalized_gray_bits() == "0000"

    def test_normalized_gray_bits_padding_to_nibble(self):
        number = Gray_bcd("0")
        number._Gray_bcd__bits = [1, 0, 1]
        assert number._normalized_gray_bits() == "0101"

    def test_to_decimal_digits_empty_normalized_bits(self, monkeypatch):
        number = Gray_bcd("0")
        monkeypatch.setattr(number, "_normalized_gray_bits", lambda: "")
        assert number._to_decimal_digits() == [0]
