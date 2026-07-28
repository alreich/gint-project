"""Unit tests for the Zi (Gaussian integer) class."""

import random
import unittest

from gint import Zi

# ----------------------------------------------------------------------
# Construction
# ----------------------------------------------------------------------

class TestInit(unittest.TestCase):
    def test_default_is_zero(self):
        z = Zi()
        self.assertEqual((z.real, z.imag), (0, 0))

    def test_int_args(self):
        z = Zi(3, 4)
        self.assertEqual((z.real, z.imag), (3, 4))

    def test_real_only_defaults_imag_zero(self):
        z = Zi(7)
        self.assertEqual((z.real, z.imag), (7, 0))

    def test_float_args_are_rounded(self):
        z = Zi(3.4, 4.6)
        self.assertEqual((z.real, z.imag), (3, 5))

    def test_from_complex(self):
        z = Zi(3 + 4j)
        self.assertEqual((z.real, z.imag), (3, 4))

    def test_from_complex_with_imag_raises(self):
        with self.assertRaises(TypeError):
            Zi(3 + 4j, 1)

    def test_from_zi(self):
        z = Zi(Zi(2, 5))
        self.assertEqual((z.real, z.imag), (2, 5))

    def test_from_zi_with_imag_raises(self):
        with self.assertRaises(TypeError):
            Zi(Zi(2, 5), 1)

    def test_invalid_real_type_raises(self):
        # Strings are a valid `real` argument (see the string-parsing
        # tests below), so this needs a genuinely unsupported type.
        with self.assertRaises(TypeError):
            Zi(object())

    def test_invalid_imag_type_raises(self):
        with self.assertRaises(TypeError):
            Zi(3, "nope")

    def test_invalid_string_raises_value_error(self):
        with self.assertRaises(ValueError):
            Zi('not-a-number')

    def test_from_string_pure_real(self):
        self.assertEqual(Zi('5'), Zi(5, 0))
        self.assertEqual(Zi('-5'), Zi(-5, 0))

    def test_from_string_pair_default_unit(self):
        self.assertEqual(Zi('2-3j'), Zi(2, -3))
        self.assertEqual(Zi('(2-3j)'), Zi(2, -3))
        self.assertEqual(Zi('-2+3j'), Zi(-2, 3))

    def test_from_string_pair_i_unit(self):
        # The parser accepts 'i' regardless of the currently configured
        # unit symbol -- only str() output depends on that setting.
        self.assertEqual(Zi('2-3i'), Zi(2, -3))
        self.assertEqual(Zi('(2-3i)'), Zi(2, -3))

    def test_from_string_imag_only(self):
        self.assertEqual(Zi('3j'), Zi(0, 3))
        self.assertEqual(Zi('-3j'), Zi(0, -3))
        self.assertEqual(Zi('3i'), Zi(0, 3))
        self.assertEqual(Zi('-2i'), Zi(0, -2))

    def test_from_string_with_imag_raises(self):
        with self.assertRaises(TypeError):
            Zi('3', 1)


# ----------------------------------------------------------------------
# Basic protocol: repr/str/hash/getitem/bool/complex
# ----------------------------------------------------------------------

class TestProtocols(unittest.TestCase):
    def test_repr(self):
        self.assertEqual(repr(Zi(3, -4)), "Zi(3, -4)")

    def test_str_pure_real(self):
        self.assertEqual(str(Zi(5, 0)), "5")

    def test_str_complex(self):
        self.assertEqual(str(Zi(3, 4)), str(complex(3, 4)))

    def test_getitem(self):
        z = Zi(3, 4)
        self.assertEqual(z[0], 3)
        self.assertEqual(z[1], 4)
        with self.assertRaises(IndexError):
            _ = z[2]

    def test_unpacking(self):
        a, b = Zi(3, 4)
        self.assertEqual((a, b), (3, 4))

    def test_complex_conversion(self):
        self.assertEqual(complex(Zi(3, 4)), 3 + 4j)

    def test_bool_zero_is_falsy(self):
        self.assertFalse(Zi(0, 0))
        self.assertTrue(Zi(1, 0))
        self.assertTrue(Zi(0, 1))

    def test_hash_equal_objects_equal_hash(self):
        self.assertEqual(hash(Zi(3, 4)), hash(Zi(3, 4)))

    def test_hashable_in_set(self):
        s = {Zi(1, 1), Zi(1, 1), Zi(2, 2)}
        self.assertEqual(len(s), 2)


# ----------------------------------------------------------------------
# String representation, unit-symbol configuration, and round-trip
# parsing (mirrors the equivalent section in test_qi.py, since Zi and
# Qi share a single unit-symbol setting -- see TestZiQiInterop
# below for tests confirming that sharing).
# ----------------------------------------------------------------------

class TestStringRepresentation(unittest.TestCase):
    def setUp(self):
        # Defensive: make sure every test in this class starts from the
        # default, regardless of what earlier tests (in this file or
        # test_qi.py) left the shared setting as.
        Zi.set_unit_symbol('j')

    def tearDown(self):
        Zi.set_unit_symbol('j')

    def test_get_unit_symbol_default(self):
        self.assertEqual(Zi.get_unit_symbol(), 'j')

    def test_str_unit_symbol_configurable(self):
        Zi.set_unit_symbol('i')
        self.assertEqual(str(Zi(2, -3)), '(2-3i)')

    def test_str_default_is_j(self):
        self.assertEqual(str(Zi(2, -3)), '(2-3j)')

    def test_str_imag_only_uses_current_symbol(self):
        Zi.set_unit_symbol('i')
        self.assertEqual(str(Zi(0, 3)), '3i')
        self.assertEqual(str(Zi(0, -3)), '-3i')

    def test_str_pure_real_has_no_unit_regardless_of_symbol(self):
        Zi.set_unit_symbol('i')
        self.assertEqual(str(Zi(5, 0)), '5')

    def test_set_unit_symbol_rejects_invalid(self):
        with self.assertRaises(ValueError):
            Zi.set_unit_symbol('k')

    def test_set_unit_symbol_invalid_does_not_change_setting(self):
        try:
            Zi.set_unit_symbol('k')
        except ValueError:
            pass
        self.assertEqual(Zi.get_unit_symbol(), 'j')

    def test_round_trip_parses_own_str_output_default_unit(self):
        original = Zi(2, -3)
        self.assertEqual(Zi(str(original)), original)

    def test_round_trip_parses_own_str_output_i_unit(self):
        Zi.set_unit_symbol('i')
        original = Zi(-7, 11)
        self.assertEqual(Zi(str(original)), original)

    def test_round_trip_many_random_values(self):
        rng = random.Random(42)
        for symbol in ('j', 'i'):
            Zi.set_unit_symbol(symbol)
            for _ in range(200):
                z = Zi(rng.randint(-1000, 1000), rng.randint(-1000, 1000))
                self.assertEqual(Zi(str(z)), z)


# ----------------------------------------------------------------------
# Equality / inequality
# ----------------------------------------------------------------------

class TestEquality(unittest.TestCase):
    def test_equal_zi(self):
        self.assertEqual(Zi(3, 4), Zi(3, 4))

    def test_not_equal_zi(self):
        self.assertNotEqual(Zi(3, 4), Zi(4, 3))

    def test_equal_to_int(self):
        self.assertEqual(Zi(5, 0), 5)
        self.assertEqual(5, Zi(5, 0))

    def test_equal_to_complex(self):
        self.assertEqual(Zi(3, 4), 3 + 4j)

    def test_unequal_incomparable_type_no_raise(self):
        # Must return NotImplemented -> False, not raise.
        self.assertFalse(Zi(3, 4) == "not a number")
        self.assertNotEqual(Zi(3, 4), object())

    def test_eq_in_list_membership(self):
        self.assertIn("anything", ["anything"])  # sanity
        self.assertNotIn(Zi(3, 4), [1, 2, 3, "x", None])

    def test_ne_true_for_different_values(self):
        self.assertTrue(Zi(1, 2) != Zi(2, 1))
        self.assertNotEqual(Zi(1, 2).__ne__(Zi(2, 1)), NotImplemented)

    def test_ne_false_for_equal_values(self):
        self.assertFalse(Zi(1, 2) != Zi(1, 2))

    def test_ne_with_int_and_complex(self):
        self.assertFalse(Zi(5, 0) != 5)
        self.assertTrue(Zi(5, 0) != 6)
        self.assertFalse(Zi(3, 4) != (3 + 4j))

    def test_ne_incomparable_type_returns_true_not_raise(self):
        # __eq__ returns NotImplemented for these; Python's default
        # fallback treats that as "not equal", so != is True, no raise.
        self.assertTrue(Zi(3, 4) != "not a number")
        self.assertTrue(Zi(3, 4) != object())

    def test_ne_is_consistent_with_eq_for_all_pairs(self):
        rng = random.Random(1)
        for _ in range(200):
            a = Zi(rng.randint(-50, 50), rng.randint(-50, 50))
            b = Zi(rng.randint(-50, 50), rng.randint(-50, 50))
            self.assertEqual(a != b, not (a == b))


# ----------------------------------------------------------------------
# Unary ops
# ----------------------------------------------------------------------

class TestUnary(unittest.TestCase):
    def test_neg(self):
        self.assertEqual(-Zi(3, -4), Zi(-3, 4))

    def test_pos(self):
        self.assertEqual(+Zi(3, -4), Zi(3, -4))

    def test_conjugate(self):
        self.assertEqual(Zi(3, 4).conjugate(), Zi(3, -4))

    def test_norm(self):
        self.assertEqual(Zi(3, 4).norm, 25)

    def test_abs(self):
        self.assertEqual(abs(Zi(3, 4)), 5.0)


# ----------------------------------------------------------------------
# Addition / subtraction, including reflected and in-place operators
# ----------------------------------------------------------------------

class TestAddSub(unittest.TestCase):
    def test_add_zi(self):
        self.assertEqual(Zi(1, 2) + Zi(3, 4), Zi(4, 6))

    def test_add_int_both_sides(self):
        self.assertEqual(Zi(1, 2) + 5, Zi(6, 2))
        self.assertEqual(5 + Zi(1, 2), Zi(6, 2))

    def test_iadd(self):
        z = Zi(1, 2)
        z += Zi(3, 4)
        self.assertEqual(z, Zi(4, 6))

    def test_sub_zi(self):
        self.assertEqual(Zi(5, 5) - Zi(2, 1), Zi(3, 4))

    def test_sub_int_both_sides(self):
        self.assertEqual(Zi(5, 5) - 2, Zi(3, 5))
        self.assertEqual(10 - Zi(3, 4), Zi(7, -4))

    def test_isub(self):
        z = Zi(5, 5)
        z -= Zi(2, 1)
        self.assertEqual(z, Zi(3, 4))

    def test_isub_with_int(self):
        z = Zi(5, 5)
        z -= 2
        self.assertEqual(z, Zi(3, 5))

    def test_isub_does_not_mutate_original_object(self):
        # Zi is immutable (slots, no in-place field mutation): -= must
        # rebind the name to a new object, not alter the old one.
        original = Zi(5, 5)
        alias = original
        original -= Zi(1, 1)
        self.assertEqual(alias, Zi(5, 5))
        self.assertEqual(original, Zi(4, 4))


# ----------------------------------------------------------------------
# Multiplication, including reflected and in-place operators
# ----------------------------------------------------------------------

class TestMul(unittest.TestCase):
    def test_mul_zi(self):
        # (1+2i)(3+4i) = 3 + 4i + 6i + 8i^2 = -5 + 10i
        self.assertEqual(Zi(1, 2) * Zi(3, 4), Zi(-5, 10))

    def test_mul_int_both_sides(self):
        self.assertEqual(Zi(1, 2) * 3, Zi(3, 6))
        self.assertEqual(3 * Zi(1, 2), Zi(3, 6))

    def test_mul_by_i(self):
        # multiplying by i rotates 90 degrees: (a+bi)*i = -b + ai
        self.assertEqual(Zi(3, 4) * Zi(0, 1), Zi(-4, 3))

    def test_imul(self):
        z = Zi(1, 2)
        z *= Zi(3, 4)
        self.assertEqual(z, Zi(-5, 10))

    def test_imul_with_int(self):
        z = Zi(1, 2)
        z *= 3
        self.assertEqual(z, Zi(3, 6))

    def test_imul_does_not_mutate_original_object(self):
        original = Zi(1, 2)
        alias = original
        original *= 3
        self.assertEqual(alias, Zi(1, 2))
        self.assertEqual(original, Zi(3, 6))


# ----------------------------------------------------------------------
# True division, including reflected operator and zero division
# ----------------------------------------------------------------------

class TestTrueDiv(unittest.TestCase):
    """
    / (__truediv__) returns the EXACT Gaussian-rational quotient,
    a Qi, or a Zi when the division happens to be exact, rather than rounding.

    // (__floordiv__) is tested in TestFloorDivMod, below, and rounds to the
    nearest Gaussian integer.
    """

    def test_exact_division(self):
        # (1+2i)*(2+1i) = 2 + i + 4i + 2i^2 = 0 + 5i
        product = Zi(1, 2) * Zi(2, 1)
        self.assertEqual(product / Zi(2, 1), Zi(1, 2))
        self.assertEqual(product / Zi(1, 2), Zi(2, 1))

    def test_exact_division_collapses_to_zi(self):
        from gint import Qi
        product = Zi(1, 2) * Zi(2, 1)
        result = product / Zi(2, 1)
        self.assertIsInstance(result, Zi)
        self.assertNotIsInstance(result, Qi)

    def test_rtruediv(self):
        # 4 / Zi(2, 0) should behave like ordinary division of reals
        self.assertEqual(4 / Zi(2, 0), Zi(2, 0))

    def test_division_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            Zi(1, 1) / Zi(0, 0)

    def test_inexact_division_returns_exact_qi(self):
        from gint import Qi
        result = Zi(1, 0) / Zi(1, 1)
        self.assertIsInstance(result, Qi)
        # 1/(1+i) = (1-i)/2 = 1/2 - 1/2 i, exactly -- no rounding.
        self.assertEqual(result, Qi('1/2', '-1/2'))
        self.assertEqual(Zi(1, 1) * result, Zi(1, 0))

    def test_division_precise_for_large_coefficients(self):
        # Exercise the exact conjugate/norm path with values large enough
        # that a naive float-based division could lose precision.
        big = Zi(123_456_789, 987_654_321)
        divisor = Zi(3, 7)
        product = big * divisor
        self.assertEqual(product / divisor, big)


# ----------------------------------------------------------------------
# Floor division, modulus, and modified_divmod agreement
# ----------------------------------------------------------------------

class TestFloorDivMod(unittest.TestCase):
    """
    // (__floordiv__) rounds to the nearest Gaussian integer.

    / (__truediv__) is exact and returns a Qi when the division
    isn't exact, but // and / must still agree whenever the
    division IS exact.
    """

    def test_floordiv_matches_truediv_when_exact(self):
        rng = random.Random(7)
        for _ in range(200):
            a = Zi(rng.randint(-30, 30), rng.randint(-30, 30))
            b = Zi(rng.randint(-30, 30), rng.randint(-30, 30))
            if b == Zi(0, 0):
                continue
            product = a * b
            self.assertEqual(product // b, product / b)

    def test_floordiv_rounds_when_inexact(self):
        # 1/(1+i) = 0.5 - 0.5i; both components round-half-to-even to 0.
        self.assertEqual(Zi(1, 0) // Zi(1, 1), Zi(0, 0))

    def test_floordiv_exact(self):
        product = Zi(1, 2) * Zi(2, 1)
        self.assertEqual(product // Zi(2, 1), Zi(1, 2))

    def test_floordiv_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            Zi(1, 1) // Zi(0, 0)

    def test_rfloordiv(self):
        self.assertEqual(4 // Zi(2, 0), Zi(2, 0))
        self.assertEqual((4 // Zi(2, 0)), (Zi(4, 0) // Zi(2, 0)))

    def test_floordiv_precise_for_large_coefficients(self):
        big = Zi(123_456_789, 987_654_321)
        divisor = Zi(3, 7)
        product = big * divisor
        self.assertEqual(product // divisor, big)

    def test_mod_exact_division_gives_zero_remainder(self):
        product = Zi(1, 2) * Zi(2, 1)
        self.assertEqual(product % Zi(2, 1), Zi(0, 0))

    def test_mod_matches_a_minus_b_times_floordiv(self):
        rng = random.Random(11)
        for _ in range(200):
            a = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            b = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            if b == Zi(0, 0):
                continue
            self.assertEqual(a % b, a - b * (a // b))

    def test_mod_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            Zi(1, 1) % Zi(0, 0)


# ----------------------------------------------------------------------
# Power, including reflected operator
# ----------------------------------------------------------------------

class TestPow(unittest.TestCase):
    def test_pow_zero(self):
        self.assertEqual(Zi(3, 4) ** 0, Zi(1, 0))

    def test_pow_positive(self):
        z = Zi(1, 1)
        self.assertEqual(z ** 2, z * z)
        self.assertEqual(z ** 3, z * z * z)

    def test_pow_one(self):
        self.assertEqual(Zi(3, 4) ** 1, Zi(3, 4))

    def test_rpow_real_exponent(self):
        self.assertEqual(2 ** Zi(3, 0), 8)

    def test_rpow_nonreal_exponent_not_implemented(self):
        self.assertIs(Zi(1, 1).__rpow__(2), NotImplemented)

    def test_pow_of_unit_negative_exponent_exact(self):
        # i is a unit: i^-1 == -i, exact (no rounding loss)
        i = Zi(0, 1)
        self.assertEqual(i ** -1, Zi(0, -1))

    def test_pow_negative_exponent_non_unit_returns_exact_qi(self):
        # 3+4i is not a unit (norm 25), so its inverse is a genuine
        # Gaussian rational, returned exactly as a Qi.
        from gint import Qi
        z = Zi(3, 4)
        result = z ** -1
        self.assertIsInstance(result, Qi)
        self.assertEqual(result, Qi('3/25', '-4/25'))
        self.assertEqual(z * result, Zi(1, 0))

    def test_pow_negative_two_non_unit_exact(self):
        # from gint import Qi
        z = Zi(1, 2)  # norm 5
        result = z ** -2
        self.assertEqual(z * z * result, Zi(1, 0))


class TestInverse(unittest.TestCase):
    def test_inverse_of_unit_is_zi(self):
        i = Zi(0, 1)
        self.assertEqual(i.inverse(), Zi(0, -1))
        self.assertIsInstance(i.inverse(), Zi)

    def test_inverse_of_non_unit_is_qi(self):
        from gint import Qi
        z = Zi(3, 4)
        self.assertEqual(z.inverse(), Qi('3/25', '-4/25'))

    def test_inverse_round_trips(self):
        rng = random.Random(13)
        for _ in range(100):
            z = Zi(rng.randint(-50, 50), rng.randint(-50, 50))
            if z == Zi(0, 0):
                continue
            self.assertEqual(z * z.inverse(), Zi(1, 0))

    def test_inverse_of_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            Zi(0, 0).inverse()


# ----------------------------------------------------------------------
# Array conversion
# ----------------------------------------------------------------------

class TestArrayConversion(unittest.TestCase):
    def test_to_array(self):
        self.assertEqual(Zi(3, -4).to_array(), [3, -4])

    def test_from_array(self):
        self.assertEqual(Zi.from_array([3, -4]), Zi(3, -4))

    def test_from_array_wrong_length_raises(self):
        with self.assertRaises(ValueError):
            Zi.from_array([1])
        with self.assertRaises(ValueError):
            Zi.from_array([1, 2, 3])

    def test_round_trip(self):
        z = Zi(7, -9)
        self.assertEqual(Zi.from_array(z.to_array()), z)


# ----------------------------------------------------------------------
# Rational and Gaussian primality
# ----------------------------------------------------------------------

class TestPrimality(unittest.TestCase):
    def test_is_rational_prime_small_primes(self):
        for p in (2, 3, 5, 7, 11, 13, 97):
            self.assertTrue(Zi._is_rational_prime(p))

    def test_is_rational_prime_small_composites(self):
        for n in (0, 1, 4, 6, 8, 9, 10, 100):
            self.assertFalse(Zi._is_rational_prime(n))

    def test_is_rational_prime_negative_uses_absolute_value(self):
        self.assertTrue(Zi._is_rational_prime(-7))
        self.assertFalse(Zi._is_rational_prime(-8))

    def test_gaussian_prime_zero_is_not_prime(self):
        self.assertFalse(Zi.is_gaussian_prime(Zi(0, 0)))
        self.assertFalse(Zi.is_gaussian_prime(0))

    def test_gaussian_prime_ramified_two_is_not_prime(self):
        # 2 = -i * (1+i)^2, so the rational prime 2 is NOT a Gaussian prime.
        self.assertFalse(Zi.is_gaussian_prime(Zi(2, 0)))
        self.assertFalse(Zi.is_gaussian_prime(2))

    def test_gaussian_prime_one_plus_i_is_prime(self):
        # 1+i has norm 2, which is a rational prime -> Gaussian prime.
        self.assertTrue(Zi.is_gaussian_prime(Zi(1, 1)))

    def test_gaussian_prime_split_prime_is_not_prime(self):
        # 5 == 1 (mod 4): splits as (2+i)(2-i), so 5 itself is not prime
        # in Z[i], though 2+i and 2-i are.
        self.assertFalse(Zi.is_gaussian_prime(Zi(5, 0)))
        self.assertTrue(Zi.is_gaussian_prime(Zi(2, 1)))
        self.assertTrue(Zi.is_gaussian_prime(Zi(2, -1)))

    def test_gaussian_prime_inert_prime_is_prime(self):
        # 3 and 7 are == 3 (mod 4): they remain prime (inert) in Z[i].
        self.assertTrue(Zi.is_gaussian_prime(Zi(3, 0)))
        self.assertTrue(Zi.is_gaussian_prime(3))
        self.assertTrue(Zi.is_gaussian_prime(Zi(7, 0)))

    def test_gaussian_prime_norm_prime_off_axis(self):
        # 2+3i has norm 13, a rational prime -> Gaussian prime.
        self.assertTrue(Zi.is_gaussian_prime(Zi(2, 3)))

    def test_gaussian_prime_norm_composite_off_axis_not_prime(self):
        # 3+3i has norm 18 = 2 * 3^2, not a rational prime -> not prime.
        self.assertFalse(Zi.is_gaussian_prime(Zi(3, 3)))

    def test_is_gaussian_prime_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            Zi.is_gaussian_prime("nope")


# ----------------------------------------------------------------------
# modified_divmod, gcd, xgcd
# ----------------------------------------------------------------------

class TestNumberTheory(unittest.TestCase):
    def test_modified_divmod_exact(self):
        product = Zi(1, 2) * Zi(2, 1)
        q, r = Zi.modified_divmod(product, Zi(2, 1))
        self.assertEqual(q, Zi(1, 2))
        self.assertEqual(r, Zi(0, 0))

    def test_modified_divmod_reconstructs_dividend(self):
        rng = random.Random(3)
        for _ in range(200):
            a = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            b = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            if b == Zi(0, 0):
                continue
            q, r = Zi.modified_divmod(a, b)
            self.assertEqual(b * q + r, a)

    def test_modified_divmod_remainder_norm_smaller_than_divisor(self):
        rng = random.Random(4)
        for _ in range(200):
            a = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            b = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            if b == Zi(0, 0):
                continue
            _, r = Zi.modified_divmod(a, b)
            self.assertLess(r.norm, b.norm)

    def test_modified_divmod_by_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            Zi.modified_divmod(Zi(1, 1), Zi(0, 0))

    def test_gcd_of_zero_and_x_is_x(self):
        self.assertEqual(Zi.gcd(Zi(0, 0), Zi(3, 4)), Zi(3, 4))

    def test_gcd_known_case(self):
        # gcd(4+2i, 1+i) -- 1+i divides 4+2i? (4+2i)/(1+i) = 3-i exactly.
        self.assertEqual((Zi(4, 2) / Zi(1, 1)), Zi(3, -1))
        g = Zi.gcd(Zi(4, 2), Zi(1, 1))
        self.assertEqual(g.norm, Zi(1, 1).norm)

    def test_gcd_divides_both_operands(self):
        rng = random.Random(5)
        for _ in range(100):
            a = Zi(rng.randint(-200, 200), rng.randint(-200, 200))
            b = Zi(rng.randint(-200, 200), rng.randint(-200, 200))
            if a == Zi(0, 0) or b == Zi(0, 0):
                continue
            g = Zi.gcd(a, b)
            self.assertEqual(a % g, Zi(0, 0))
            self.assertEqual(b % g, Zi(0, 0))

    def test_xgcd_bezout_identity(self):
        rng = random.Random(6)
        for _ in range(100):
            a = Zi(rng.randint(-200, 200), rng.randint(-200, 200))
            b = Zi(rng.randint(-200, 200), rng.randint(-200, 200))
            if a == Zi(0, 0) or b == Zi(0, 0):
                continue
            g, s, t = Zi.xgcd(a, b)
            self.assertEqual(a * s + b * t, g)

    def test_xgcd_matches_gcd_up_to_unit(self):
        rng = random.Random(8)
        for _ in range(100):
            a = Zi(rng.randint(-200, 200), rng.randint(-200, 200))
            b = Zi(rng.randint(-200, 200), rng.randint(-200, 200))
            if a == Zi(0, 0) or b == Zi(0, 0):
                continue
            g, _, _ = Zi.xgcd(a, b)
            plain_g = Zi.gcd(a, b)
            self.assertEqual(g.norm, plain_g.norm)

    def test_xgcd_with_zero(self):
        g, s, t = Zi.xgcd(Zi(0, 0), Zi(3, 4))
        self.assertEqual(g, Zi(3, 4))
        self.assertEqual(Zi(0, 0) * s + Zi(3, 4) * t, g)

    def test_lcm_basic(self):
        # lcm(4, 6) == 12 in the ordinary integers (embedded in Z[i]).
        self.assertEqual(Zi.lcm(Zi(4, 0), Zi(6, 0)).norm, Zi(12, 0).norm)

    def test_lcm_with_zero_is_zero(self):
        self.assertEqual(Zi.lcm(Zi(0, 0), Zi(3, 4)), Zi(0, 0))

    def test_lcm_is_divisible_by_both_operands(self):
        rng = random.Random(15)
        for _ in range(200):
            a = Zi(rng.randint(-100, 100), rng.randint(-100, 100))
            b = Zi(rng.randint(-100, 100), rng.randint(-100, 100))
            if a == Zi(0, 0) or b == Zi(0, 0):
                continue
            _l = Zi.lcm(a, b)
            self.assertEqual(_l % a, Zi(0, 0))
            self.assertEqual(_l % b, Zi(0, 0))

    def test_gcd_times_lcm_norm_matches_product_norm(self):
        # |gcd(a,b)| * |lcm(a,b)| == |a| * |b| (norms, since gcd/lcm
        # are each only defined up to a unit -- exact equality won't
        # hold, but the norm identity is unit-independent).
        rng = random.Random(16)
        for _ in range(200):
            a = Zi(rng.randint(-100, 100), rng.randint(-100, 100))
            b = Zi(rng.randint(-100, 100), rng.randint(-100, 100))
            if a == Zi(0, 0) or b == Zi(0, 0):
                continue
            g = Zi.gcd(a, b)
            _l = Zi.lcm(a, b)
            self.assertEqual(g.norm * _l.norm, a.norm * b.norm)

    def test_is_associate_true_for_unit_multiples(self):
        a = Zi(3, 4)
        for u in Zi.units():
            self.assertTrue(Zi.is_associate(a, a * u))

    def test_is_associate_false_for_non_associates(self):
        self.assertFalse(Zi.is_associate(Zi(1, 1), Zi(2, 2)))

    def test_is_associate_zero_only_associate_with_itself(self):
        self.assertTrue(Zi.is_associate(Zi(0, 0), Zi(0, 0)))
        self.assertFalse(Zi.is_associate(Zi(0, 0), Zi(1, 1)))
        self.assertFalse(Zi.is_associate(Zi(1, 1), Zi(0, 0)))

    def test_is_coprime_true_case(self):
        # 1+i and 1-i: gcd has norm 2 -- NOT coprime, a good negative
        # check -- so use a genuinely coprime pair instead: 2+i and 3.
        self.assertTrue(Zi.is_coprime(Zi(2, 1), Zi(3, 0)))

    def test_is_coprime_false_case(self):
        self.assertFalse(Zi.is_coprime(Zi(1, 1), Zi(1, -1)))  # both norm 2
        self.assertFalse(Zi.is_coprime(Zi(2, 0), Zi(4, 0)))

    def test_is_coprime_zero_zero_is_false(self):
        self.assertFalse(Zi.is_coprime(Zi(0, 0), Zi(0, 0)))

    def test_divides_true_case(self):
        self.assertTrue(Zi.divides(Zi(1, 1), Zi(4, 2)))

    def test_divides_false_case(self):
        self.assertFalse(Zi.divides(Zi(1, 1), Zi(1, 2)))

    def test_divides_by_zero_convention(self):
        self.assertTrue(Zi.divides(Zi(0, 0), Zi(0, 0)))
        self.assertFalse(Zi.divides(Zi(0, 0), Zi(1, 1)))

    def test_divides_consistent_with_gcd(self):
        # gcd(a, b) must divide both a and b, by definition.
        rng = random.Random(17)
        for _ in range(200):
            a = Zi(rng.randint(-100, 100), rng.randint(-100, 100))
            b = Zi(rng.randint(-100, 100), rng.randint(-100, 100))
            if a == Zi(0, 0) or b == Zi(0, 0):
                continue
            g = Zi.gcd(a, b)
            self.assertTrue(Zi.divides(g, a))
            self.assertTrue(Zi.divides(g, b))

# ----------------------------------------------------------------------
# Gaussian integer factorization
# ----------------------------------------------------------------------

class TestFactor(unittest.TestCase):
    def test_factor_zero_raises(self):
        with self.assertRaises(ValueError):
            Zi.factor(Zi(0, 0))

    def test_factor_unit_is_itself_with_no_prime_factors(self):
        for u in Zi.units():
            unit, factors = Zi.factor(u)
            self.assertEqual(unit, u)
            self.assertEqual(factors, [])

    def test_factor_ramified_two(self):
        # 2 == -i * (1+i)^2
        unit, factors = Zi.factor(Zi(2, 0))
        self.assertEqual(factors, [(Zi(1, 1), 2)])
        self.assertEqual(unit * Zi(1, 1) ** 2, Zi(2, 0))

    def test_factor_inert_prime(self):
        # 3 == 3 (mod 4): stays prime in Z[i], factors as itself.
        unit, factors = Zi.factor(Zi(3, 0))
        self.assertEqual(factors, [(Zi(3, 0), 1)])
        self.assertTrue(Zi.is_gaussian_prime(Zi(3, 0)))

    # def test_factor_split_prime(self):
    #     # 5 == 1 (mod 4): splits as (2+i)(2-i) (up to units/ordering).
    #     unit, factors = Zi.factor(Zi(5, 0))
    #     primes = {p for p, _ in factors}
    #     self.assertEqual(primes, {Zi(2, 1), Zi(2, -1)})
    #     for p, e in factors:
    #         self.assertEqual(e, 1)

    def test_factor_split_prime(self):
        # 5 == 1 (mod 4): splits into two conjugate Gaussian primes of
        # norm 5. We don't hardcode which specific representative
        # (e.g. 1+2i vs 2+i) the search returns -- those are associates
        # of each other, differing only by a unit -- just that the
        # factorization is a conjugate pair of norm-5 Gaussian primes
        # whose product reconstructs 5.
        unit, factors = Zi.factor(Zi(5, 0))
        self.assertEqual(len(factors), 2)
        for p, e in factors:
            self.assertEqual(e, 1)
            self.assertEqual(p.norm, 5)
            self.assertTrue(Zi.is_gaussian_prime(p))
        p1, p2 = factors[0][0], factors[1][0]
        self.assertEqual(p1.conjugate(), p2)
        product = unit
        for p, e in factors:
            product = product * (p**e)
        self.assertEqual(product, Zi(5, 0))

    def test_factor_already_prime(self):
        unit, factors = Zi.factor(Zi(1, 1))
        self.assertEqual(factors, [(Zi(1, 1), 1)])

    def test_factor_reconstructs_original_value(self):
        rng = random.Random(30)
        for _ in range(200):
            z = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            if z == Zi(0, 0):
                continue
            unit, factors = Zi.factor(z)
            product = unit
            for p, e in factors:
                product = product * (p ** e)
            self.assertEqual(product, z)

    def test_factor_unit_component_is_a_unit(self):
        rng = random.Random(31)
        for _ in range(200):
            z = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            if z == Zi(0, 0):
                continue
            unit, _ = Zi.factor(z)
            self.assertIn(unit, Zi.units())

    def test_factor_all_components_are_gaussian_primes(self):
        rng = random.Random(32)
        for _ in range(200):
            z = Zi(rng.randint(-500, 500), rng.randint(-500, 500))
            if z == Zi(0, 0):
                continue
            _, factors = Zi.factor(z)
            for p, _e in factors:
                self.assertTrue(Zi.is_gaussian_prime(p))

# ----------------------------------------------------------------------
# congruent_modulo
# ----------------------------------------------------------------------

class TestCongruentModulo(unittest.TestCase):
    def test_basic_true_case(self):
        # 7 == 2 (mod 5) on the real axis, same as ordinary integers.
        self.assertTrue(Zi.congruent_modulo(Zi(7, 0), Zi(2, 0), Zi(5, 0)))

    def test_basic_false_case(self):
        self.assertFalse(Zi.congruent_modulo(Zi(7, 0), Zi(3, 0), Zi(5, 0)))

    def test_congruent_gaussian_example(self):
        # Construct b so that b - a is a guaranteed multiple of c.
        c = Zi(2, 1)
        a = Zi(3, 4)
        b = a + c * Zi(5, -2)
        self.assertTrue(Zi.congruent_modulo(a, b, c))

    def test_not_congruent_gaussian_example(self):
        c = Zi(2, 1)
        a = Zi(3, 4)
        b = a + c * Zi(5, -2) + Zi(1, 0)  # offset by a non-multiple of c
        self.assertFalse(Zi.congruent_modulo(a, b, c))

    def test_congruent_reflexive_simple(self):
        self.assertTrue(Zi.congruent_modulo(Zi(3, 4), Zi(3, 4), Zi(2, 1)))

    def test_congruent_with_unit_modulus_always_true(self):
        # Units divide everything, so congruence mod a unit is vacuous.
        for u in Zi.units():
            self.assertTrue(Zi.congruent_modulo(Zi(3, 4), Zi(-7, 2), u))

    def test_congruent_modulo_zero_raises(self):
        with self.assertRaises(ZeroDivisionError):
            Zi.congruent_modulo(Zi(1, 1), Zi(2, 2), Zi(0, 0))

    def test_congruent_modulo_accepts_int(self):
        # _require_zi should coerce plain ints, same as gcd/xgcd do.
        self.assertTrue(Zi.congruent_modulo(7, 2, 5))
        self.assertFalse(Zi.congruent_modulo(7, 3, 5))


# ----------------------------------------------------------------------
# crt (Chinese Remainder Theorem)
# ----------------------------------------------------------------------

class TestCRT(unittest.TestCase):
    def test_classic_integer_case(self):
        # x == 2 (mod 3), x == 3 (mod 5) -- classic textbook example,
        # unique solution 23 (mod 15), here on the real axis of Z[i].
        x = Zi.crt([Zi(2, 0), Zi(3, 0)], [Zi(3, 0), Zi(5, 0)])
        self.assertTrue(Zi.congruent_modulo(x, Zi(2, 0), Zi(3, 0)))
        self.assertTrue(Zi.congruent_modulo(x, Zi(3, 0), Zi(5, 0)))
        self.assertTrue(Zi.congruent_modulo(x, Zi(23, 0), Zi(15, 0)))

    def test_gaussian_integer_moduli(self):
        # 2+i and 3 are coprime (norm 5 vs norm 9, no common factor).
        m1, m2 = Zi(2, 1), Zi(3, 0)
        a1, a2 = Zi(1, 1), Zi(0, 2)
        x = Zi.crt([a1, a2], [m1, m2])
        self.assertTrue(Zi.congruent_modulo(x, a1, m1))
        self.assertTrue(Zi.congruent_modulo(x, a2, m2))

    def test_single_modulus_reduces_to_congruent_modulo(self):
        x = Zi.crt([Zi(7, 2)], [Zi(10, 0)])
        self.assertTrue(Zi.congruent_modulo(x, Zi(7, 2), Zi(10, 0)))

    def test_three_moduli(self):
        moduli = [Zi(3, 0), Zi(2, 1), Zi(1, 2)]  # pairwise coprime
        residues = [Zi(1, 0), Zi(2, -1), Zi(0, 3)]
        x = Zi.crt(residues, moduli)
        for a, m in zip(residues, moduli):
            self.assertTrue(Zi.congruent_modulo(x, a, m))

    def test_solution_unique_modulo_product(self):
        moduli = [Zi(2, 1), Zi(3, 0)]
        residues = [Zi(1, 0), Zi(2, 0)]
        x = Zi.crt(residues, moduli)
        product = moduli[0] * moduli[1]
        # Any shift by a multiple of the product modulus must still
        # satisfy every original congruence.
        shifted = x + product * Zi(4, -2)
        self.assertTrue(Zi.congruent_modulo(x, shifted, product))
        for a, m in zip(residues, moduli):
            self.assertTrue(Zi.congruent_modulo(shifted, a, m))

    def test_non_coprime_moduli_raises(self):
        with self.assertRaises(ValueError):
            Zi.crt([Zi(1, 0), Zi(1, 0)], [Zi(2, 0), Zi(4, 0)])

    def test_non_coprime_detected_against_combined_product(self):
        # 1+2i and 1-2i are themselves coprime (norm 5 each, neither
        # divides the other). But their product is exactly 5, and
        # crt() folds moduli in one at a time by testing each new
        # modulus against the *running product* of the ones already
        # combined, not against every earlier modulus individually. So
        # a third modulus of 5 is never compared directly to 1+2i or
        # 1-2i -- only to their product -- yet the shared factor is
        # still caught, which is what this test exercises.
        with self.assertRaises(ValueError):
            Zi.crt([Zi(0, 0), Zi(0, 0), Zi(0, 0)],
                   [Zi(1, 2), Zi(1, -2), Zi(5, 0)])

    def test_zero_modulus_raises(self):
        with self.assertRaises(ZeroDivisionError):
            Zi.crt([Zi(1, 0)], [Zi(0, 0)])

    def test_mismatched_lengths_raises(self):
        with self.assertRaises(ValueError):
            Zi.crt([Zi(1, 0)], [Zi(2, 0), Zi(3, 0)])

    def test_empty_input_raises(self):
        with self.assertRaises(ValueError):
            Zi.crt([], [])

    def test_fuzz_random_coprime_gaussian_primes(self):
        rng = random.Random(19)

        def random_gaussian_prime():
            while True:
                z = Zi(rng.randint(-50, 50), rng.randint(-50, 50))
                if z != Zi(0, 0) and Zi.is_gaussian_prime(z):
                    return z

        for _ in range(200):
            k = rng.randint(2, 4)
            primes = []
            while len(primes) < k:
                p = random_gaussian_prime()
                # Distinct, non-associate primes are pairwise coprime.
                if all(not Zi.is_associate(p, q) for q in primes):
                    primes.append(p)
            residues = [Zi(rng.randint(-50, 50), rng.randint(-50, 50))
                        for _ in primes]
            x = Zi.crt(residues, primes)
            for a, m in zip(residues, primes):
                self.assertTrue(Zi.congruent_modulo(x, a, m))


# ----------------------------------------------------------------------
# Utilities: random, eye, units, is_unit, two
# ----------------------------------------------------------------------

class TestUtilities(unittest.TestCase):
    def test_random_within_bounds(self):
        for _ in range(200):
            z = Zi.random(-10, 10)
            self.assertIsInstance(z, Zi)
            self.assertTrue(-10 <= z.real <= 10)
            self.assertTrue(-10 <= z.imag <= 10)

    def test_random_asymmetric_bounds(self):
        for _ in range(200):
            z = Zi.random(re_min=0, re_max=5, im_min=-3, im_max=3)
            self.assertTrue(0 <= z.real <= 5)
            self.assertTrue(-3 <= z.imag <= 3)

    def test_eye(self):
        self.assertEqual(Zi.eye(), Zi(0, 1))
        self.assertEqual(Zi.eye() * Zi.eye(), Zi(-1, 0))

    def test_units(self):
        expected = {Zi(1, 0), Zi(-1, 0), Zi(0, 1), Zi(0, -1)}
        self.assertEqual(set(Zi.units()), expected)
        self.assertEqual(len(Zi.units()), 4)

    def test_is_unit_true_for_units(self):
        for u in Zi.units():
            self.assertTrue(u.is_unit)

    def test_is_unit_false_for_non_units(self):
        for z in (Zi(0, 0), Zi(2, 0), Zi(1, 1), Zi(3, 4)):
            self.assertFalse(z.is_unit)

    def test_is_unit_matches_norm_one(self):
        rng = random.Random(9)
        for _ in range(200):
            z = Zi(rng.randint(-10, 10), rng.randint(-10, 10))
            self.assertEqual(z.is_unit, z.norm == 1)

    def test_two(self):
        self.assertEqual(Zi.two(), Zi(1, 1))
        # 1+i has norm 2 and is the Gaussian prime lying above the
        # ramified rational prime 2.
        self.assertEqual(Zi.two().norm, 2)
        self.assertTrue(Zi.is_gaussian_prime(Zi.two()))


# ----------------------------------------------------------------------
# Fuzz tests: algebraic properties that must hold for ALL Gaussian ints
# ----------------------------------------------------------------------

class TestFuzz(unittest.TestCase):
    SEED = 20260710
    N_TRIALS = 500
    COORD_RANGE = 1000

    def setUp(self):
        self.rng = random.Random(self.SEED)

    def _random_zi(self, allow_zero=True):
        while True:
            a = self.rng.randint(-self.COORD_RANGE, self.COORD_RANGE)
            b = self.rng.randint(-self.COORD_RANGE, self.COORD_RANGE)
            if allow_zero or (a, b) != (0, 0):
                return Zi(a, b)

    def test_addition_commutative(self):
        for _ in range(self.N_TRIALS):
            a, b = self._random_zi(), self._random_zi()
            self.assertEqual(a + b, b + a)

    def test_addition_associative(self):
        for _ in range(self.N_TRIALS):
            a, b, c = (self._random_zi() for _ in range(3))
            self.assertEqual((a + b) + c, a + (b + c))

    def test_additive_identity(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            self.assertEqual(a + Zi(0, 0), a)

    def test_additive_inverse(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            self.assertEqual(a + (-a), Zi(0, 0))

    def test_multiplication_commutative(self):
        for _ in range(self.N_TRIALS):
            a, b = self._random_zi(), self._random_zi()
            self.assertEqual(a * b, b * a)

    def test_multiplication_associative(self):
        for _ in range(self.N_TRIALS):
            a, b, c = (self._random_zi() for _ in range(3))
            self.assertEqual((a * b) * c, a * (b * c))

    def test_multiplicative_identity(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            self.assertEqual(a * Zi(1, 0), a)

    def test_distributive_law(self):
        for _ in range(self.N_TRIALS):
            a, b, c = (self._random_zi() for _ in range(3))
            self.assertEqual(a * (b + c), a * b + a * c)

    def test_norm_is_multiplicative(self):
        # N(a*b) == N(a) * N(b) -- classic Gaussian integer identity
        for _ in range(self.N_TRIALS):
            a, b = self._random_zi(), self._random_zi()
            self.assertEqual((a * b).norm, a.norm * b.norm)

    def test_conjugate_involution(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            self.assertEqual(a.conjugate().conjugate(), a)

    def test_conjugate_norm_identity(self):
        # a * conj(a) == N(a) (a real, nonnegative Gaussian integer)
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            self.assertEqual(a * a.conjugate(), Zi(a.norm, 0))

    def test_conjugate_of_product(self):
        for _ in range(self.N_TRIALS):
            a, b = self._random_zi(), self._random_zi()
            self.assertEqual((a * b).conjugate(), a.conjugate() * b.conjugate())

    def test_abs_squared_equals_norm(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            self.assertAlmostEqual(abs(a) ** 2, a.norm, places=6)  # type: ignore

    def test_exact_division_round_trips(self):
        # Construct a*b deliberately so a*b / b == a exactly (no rounding).
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            b = self._random_zi(allow_zero=False)
            product = a * b
            self.assertEqual(product / b, a)
            self.assertEqual(product / a if a else Zi(0, 0),
                              b if a else Zi(0, 0))

    def test_radd_matches_add(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            n = self.rng.randint(-1000, 1000)
            self.assertEqual(n + a, a + n)

    def test_rmul_matches_mul(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            n = self.rng.randint(-1000, 1000)
            self.assertEqual(n * a, a * n)

    def test_rsub_consistent_with_neg_add(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            n = self.rng.randint(-1000, 1000)
            self.assertEqual(n - a, -a + n)  # type: ignore

    def test_pow_matches_repeated_multiplication(self):
        for _ in range(self.N_TRIALS // 5):  # smaller range: pow grows fast
            a = self._random_zi(allow_zero=False)
            exp = self.rng.randint(0, 6)
            expected = Zi(1, 0)
            for _ in range(exp):
                expected = expected * a
            self.assertEqual(a ** exp, expected)

    def test_equality_reflexive_and_hash_stable(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            self.assertEqual(a, a)
            self.assertEqual(hash(a), hash(Zi(a.real, a.imag)))

    def test_floordiv_and_mod_reconstruct_dividend(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            b = self._random_zi(allow_zero=False)
            self.assertEqual(b * (a // b) + (a % b), a)

    def test_gcd_result_divides_both_operands(self):
        for _ in range(self.N_TRIALS // 5):
            a = self._random_zi(allow_zero=False)
            b = self._random_zi(allow_zero=False)
            g = Zi.gcd(a, b)
            self.assertEqual(a % g, Zi(0, 0))
            self.assertEqual(b % g, Zi(0, 0))

    def test_xgcd_bezout_identity_fuzz(self):
        for _ in range(self.N_TRIALS // 5):
            a = self._random_zi(allow_zero=False)
            b = self._random_zi(allow_zero=False)
            g, s, t = Zi.xgcd(a, b)
            self.assertEqual(a * s + b * t, g)

    def test_congruent_modulo_reflexive(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi()
            m = self._random_zi(allow_zero=False)
            self.assertTrue(Zi.congruent_modulo(a, a, m))

    def test_congruent_modulo_symmetric(self):
        for _ in range(self.N_TRIALS):
            a, b = self._random_zi(), self._random_zi()
            m = self._random_zi(allow_zero=False)
            self.assertEqual(Zi.congruent_modulo(a, b, m), Zi.congruent_modulo(b, a, m))

    def test_congruent_modulo_transitive(self):
        # Random unrelated triples would almost never satisfy a==b (mod m),
        # making transitivity vacuously true and the test meaningless. So
        # we deliberately construct b and c to be congruent to a mod m,
        # then confirm a is therefore congruent to c.
        for _ in range(self.N_TRIALS // 5):
            a = self._random_zi()
            m = self._random_zi(allow_zero=False)
            b = a + m * self._random_zi()
            c = b + m * self._random_zi()
            self.assertTrue(Zi.congruent_modulo(a, b, m))
            self.assertTrue(Zi.congruent_modulo(b, c, m))
            self.assertTrue(Zi.congruent_modulo(a, c, m))

    def test_is_associate_for_random_unit_multiples(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi(allow_zero=False)
            u = self.rng.choice(Zi.units())
            self.assertTrue(Zi.is_associate(a, a * u))

    def test_divides_matches_mod_zero(self):
        for _ in range(self.N_TRIALS):
            a = self._random_zi(allow_zero=False)
            b = self._random_zi()
            self.assertEqual(Zi.divides(a, b), (b % a == Zi(0, 0)))

    def test_is_coprime_matches_gcd_is_unit(self):
        for _ in range(self.N_TRIALS // 2):
            a = self._random_zi(allow_zero=False)
            b = self._random_zi(allow_zero=False)
            self.assertEqual(Zi.is_coprime(a, b), Zi.gcd(a, b).is_unit)

    def test_factor_reconstructs_random_values(self):
        for _ in range(self.N_TRIALS):
            z = self._random_zi(allow_zero=False)
            unit, factors = Zi.factor(z)
            product = unit
            for p, e in factors:
                product = product * (p**e)
            self.assertEqual(product, z)

    def test_factor_norm_matches_product_of_prime_norms(self):
        # N(z) == prod(N(p)^e) since norm is multiplicative and the
        # unit contributes norm 1.
        for _ in range(self.N_TRIALS):
            z = self._random_zi(allow_zero=False)
            unit, factors = Zi.factor(z)
            norm_product = 1
            for p, e in factors:
                norm_product *= p.norm**e
            self.assertEqual(norm_product, z.norm)

# ----------------------------------------------------------------------
# Interoperability with Qi (Gaussian rationals)
# ----------------------------------------------------------------------

class TestZiQiInterop(unittest.TestCase):
    """Zi's arithmetic methods must return NotImplemented (not raise) for
    operand types they don't recognize, so Python can fall back to Qi's
    reflected methods -- and vice versa. These tests exercise both
    directions."""

    def setUp(self):
        from gint import Qi
        self.Qi = Qi

    def test_zi_plus_qi(self):
        Qi = self.Qi
        self.assertEqual(Zi(1, 2) + Qi('1/2', '1/3'), Qi('3/2', '7/3'))

    def test_qi_plus_zi(self):
        Qi = self.Qi
        self.assertEqual(Qi('1/2', '1/3') + Zi(1, 2), Qi('3/2', '7/3'))

    def test_zi_minus_qi_and_reverse(self):
        Qi = self.Qi
        self.assertEqual(Zi(1, 2) - Qi('1/2', '0'), Qi('1/2', '2'))
        self.assertEqual(Qi('1/2', '0') - Zi(1, 2), Qi('-1/2', '-2'))

    def test_zi_times_qi(self):
        Qi = self.Qi
        # (1+2i)(1/2+1/3i) = 1/2 + 1/3i + i + 2/3 i^2
        #                  = (1/2 - 2/3) + (1/3+1)i = -1/6 + 4/3 i
        self.assertEqual(Zi(1, 2) * Qi('1/2', '1/3'), Qi('-1/6', '4/3'))
        self.assertEqual(Qi('1/2', '1/3') * Zi(1, 2), Qi('-1/6', '4/3'))

    def test_zi_equals_qi_when_value_matches(self):
        Qi = self.Qi
        # Qi('1', '2') collapses to a Zi at construction, so this is
        # really testing Zi == Zi, but via the Qi constructor path.
        self.assertEqual(Zi(1, 2), Qi('1', '2'))

    def test_zi_not_equal_to_fractional_qi(self):
        Qi = self.Qi
        self.assertNotEqual(Zi(1, 2), Qi('1', '5/2'))
        self.assertNotEqual(Qi('1', '5/2'), Zi(1, 2))

    def test_zi_incomparable_type_still_returns_false_not_raise(self):
        # Unrelated to Qi, but confirms the NotImplemented plumbing
        # change didn't reintroduce a raise for genuinely bad types.
        self.assertFalse(Zi(1, 2) == "nope")
        self.assertNotEqual(Zi(1, 2), "nope")

    def test_unit_symbol_is_shared_between_zi_and_qi(self):
        # A single source of truth (living on Zi): setting it via either
        # class must be visible through both classes' getters.
        Qi = self.Qi
        try:
            Zi.set_unit_symbol('i')
            self.assertEqual(Qi.get_unit_symbol(), 'i')
            Qi.set_unit_symbol('j')
            self.assertEqual(Zi.get_unit_symbol(), 'j')
        finally:
            Zi.set_unit_symbol('j')

    def test_qi_collapsed_to_zi_reflects_current_symbol(self):
        # Before the fix this shared setting exists to prevent, a Qi
        # that collapses to a Zi at construction (see Qi.__new__) could
        # print with a different unit symbol than the Qi it came from,
        # since each class tracked its own separate setting.
        Qi = self.Qi
        try:
            Qi.set_unit_symbol('i')
            collapsed = Qi(4, 6)
            self.assertIsInstance(collapsed, Zi)
            self.assertEqual(str(collapsed), '(4+6i)')
        finally:
            Qi.set_unit_symbol('j')


def main():
    unittest.main()


if __name__ == "__main__":
    main()
