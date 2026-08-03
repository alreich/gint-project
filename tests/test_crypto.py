"""Unit tests for the gint.crypto (Gaussian-integer RSA) module."""

# import math
import random
import unittest

from gint import Zi
from gint.crypto import (
    GaussianRSACiphertext,
    _is_probable_prime,
    _pow_mod,
    _random_inert_prime,
    block_capacity,
    decrypt_block,
    decrypt_bytes,
    decrypt_text,
    encrypt_block,
    encrypt_bytes,
    encrypt_text,
    generate_keypair,
)

# Small bit sizes throughout: fast key generation, and small enough that
# Zi.is_gaussian_prime's trial division stays cheap for cross-checking
# against the library's own primality notion. Real usage should use at
# least bits=1024.
_SMALL_BITS = 24

# ----------------------------------------------------------------------
# Primality helpers
# ----------------------------------------------------------------------

class TestPrimality(unittest.TestCase):
    def test_is_probable_prime_small_known_values(self):
        primes = {2, 3, 5, 7, 11, 13, 97, 7919}
        composites = {0, 1, 4, 6, 8, 9, 100, 7921}
        for p in primes:
            self.assertTrue(_is_probable_prime(p), p)
        for c in composites:
            self.assertFalse(_is_probable_prime(c), c)

    def test_is_probable_prime_agrees_with_trial_division(self):
        def trial_division_is_prime(candidate):
            if candidate < 2:
                return False
            i = 2
            while i * i <= candidate:
                if candidate % i == 0:
                    return False
                i += 1
            return True

        for n in range(2, 2000):
            self.assertEqual(
                _is_probable_prime(n), trial_division_is_prime(n), n
            )

    def test_random_inert_prime_has_correct_bit_length_and_residue(self):
        for _ in range(20):
            p = _random_inert_prime(_SMALL_BITS)
            self.assertEqual(p.bit_length(), _SMALL_BITS)
            self.assertEqual(p % 4, 3)
            self.assertTrue(_is_probable_prime(p))

    def test_random_inert_prime_matches_zi_is_gaussian_prime(self):
        # Cross-check against the library's own (trial-division-based)
        # notion of Gaussian primality, at a size where that's cheap.
        for _ in range(10):
            p = _random_inert_prime(_SMALL_BITS)
            self.assertTrue(Zi.is_gaussian_prime(Zi(p, 0)))

    def test_random_inert_prime_rejects_small_bits(self):
        with self.assertRaises(ValueError):
            _random_inert_prime(3)


# ----------------------------------------------------------------------
# Key generation
# ----------------------------------------------------------------------

class TestKeyGeneration(unittest.TestCase):
    def test_generate_keypair_shapes(self):
        pub, priv = generate_keypair(bits=_SMALL_BITS)
        self.assertEqual(pub.n, priv.n)
        self.assertEqual(pub.n, priv.p * priv.q)
        self.assertNotEqual(priv.p, priv.q)
        self.assertEqual(priv.p % 4, 3)
        self.assertEqual(priv.q % 4, 3)

    def test_public_and_private_exponents_are_inverses_mod_phi(self):
        pub, priv = generate_keypair(bits=_SMALL_BITS)
        phi = (priv.p ** 2 - 1) * (priv.q ** 2 - 1)
        self.assertEqual((pub.e * priv.d) % phi, 1)

    def test_rejects_too_small_bits(self):
        with self.assertRaises(ValueError):
            generate_keypair(bits=3)

    def test_distinct_keypairs_are_distinct(self):
        pub1, _ = generate_keypair(bits=_SMALL_BITS)
        pub2, _ = generate_keypair(bits=_SMALL_BITS)
        # Overwhelmingly likely with random primes at this bit size.
        self.assertNotEqual(pub1.n, pub2.n)


# ----------------------------------------------------------------------
# Core modular exponentiation
# ----------------------------------------------------------------------

class TestPowMod(unittest.TestCase):
    def test_pow_mod_exponent_zero_is_one(self):
        n = 101
        self.assertEqual(_pow_mod(Zi(5, 7), 0, n), Zi(1, 0))

    def test_pow_mod_matches_naive_repeated_multiplication(self):
        n = 97
        base = Zi(11, 13)
        modulus = Zi(n, 0)
        expected = Zi(1, 0)
        for _ in range(9):
            expected = (expected * base) % modulus
        self.assertEqual(_pow_mod(base, 9, n), expected)

    def test_pow_mod_result_components_in_range(self):
        n = 1009
        result = _pow_mod(Zi(500, -700), 12345, n)
        self.assertTrue(-n < result.real < n)
        self.assertTrue(-n < result.imag < n)


# ----------------------------------------------------------------------
# Block-level encryption round trip and RSA identity
# ----------------------------------------------------------------------

class TestBlockRoundTrip(unittest.TestCase):
    def setUp(self):
        self.public_key, self.private_key = generate_keypair(bits=_SMALL_BITS)

    def test_round_trip_various_blocks(self):
        n = self.public_key.n
        rng = random.Random(1234)
        for _ in range(25):
            m = Zi(rng.randrange(n), rng.randrange(n))
            c = encrypt_block(m, self.public_key)
            self.assertEqual(decrypt_block(c, self.private_key), m)

    def test_round_trip_zero_block(self):
        m = Zi(0, 0)
        c = encrypt_block(m, self.public_key)
        self.assertEqual(decrypt_block(c, self.private_key), m)

    def test_encrypt_out_of_range_raises(self):
        n = self.public_key.n
        with self.assertRaises(ValueError):
            encrypt_block(Zi(n, 0), self.public_key)
        with self.assertRaises(ValueError):
            encrypt_block(Zi(0, -1), self.public_key)

    def test_encryption_is_not_trivially_identity(self):
        # Sanity check that encrypt_block actually transforms non-trivial
        # messages (guards against a degenerate e or d slipping through).
        n = self.public_key.n
        m = Zi(n // 3, n // 5)
        c = encrypt_block(m, self.public_key)
        self.assertNotEqual(c, m)


# ----------------------------------------------------------------------
# Byte- and text-level round trip
# ----------------------------------------------------------------------

class TestBytesAndTextRoundTrip(unittest.TestCase):
    def setUp(self):
        self.public_key, self.private_key = generate_keypair(bits=_SMALL_BITS)

    def test_empty_bytes(self):
        ct = encrypt_bytes(b"", self.public_key)
        self.assertEqual(decrypt_bytes(ct, self.private_key), b"")

    def test_short_and_long_bytes(self):
        k = block_capacity(self.public_key.n)
        samples = [
            b"x",
            b"hello, gaussian integers",
            bytes(range(256)) * 3,
            b"\x00" * (2 * k) + b"\x01",  # leading/embedded null bytes
        ]
        for data in samples:
            ct = encrypt_bytes(data, self.public_key)
            self.assertEqual(decrypt_bytes(ct, self.private_key), data)

    def test_ciphertext_length_field(self):
        data = b"twelve bytes"
        ct = encrypt_bytes(data, self.public_key)
        self.assertIsInstance(ct, GaussianRSACiphertext)
        self.assertEqual(ct.length, len(data))

    def test_text_round_trip_ascii_and_unicode(self):
        for text in ["hello world", "Gaussian primes: a + bi", "π ≈ 3.14159, √2 ≈ 1.41"]:
            ct = encrypt_text(text, self.public_key)
            self.assertEqual(decrypt_text(ct, self.private_key), text)

    def test_wrong_key_decryption_fails_cleanly(self):
        other_public, other_private = generate_keypair(bits=_SMALL_BITS)
        ct = encrypt_text("a secret", self.public_key)
        with self.assertRaises((ValueError, Exception)):
            decrypt_text(ct, other_private)


# ----------------------------------------------------------------------
# block_capacity
# ----------------------------------------------------------------------

class TestBlockCapacity(unittest.TestCase):
    def test_block_capacity_fits_under_modulus(self):
        for bits in (8, 16, 24, 40):
            _, priv = generate_keypair(bits=bits)
            k = block_capacity(priv.n)
            self.assertLess(2 ** (8 * k), priv.n)

    def test_block_capacity_at_least_one(self):
        self.assertGreaterEqual(block_capacity(3), 1)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
