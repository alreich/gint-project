"""Gaussian-integer RSA: an RSA analog over the ring of Gaussian integers Z[i].

Classic RSA works in Z/(n) for n = p*q, a product of two rational primes,
using Euler's theorem: m**phi(n) == 1 (mod n) for m coprime to n, where
phi(n) = (p-1)*(q-1).

This module runs the identical construction one level up, in Z[i]/(n) for
n = p*q, a product of two *inert* rational primes (primes p with p % 4 == 3,
which stay prime -- do not factor further -- in Z[i]). For such a prime p,
Z[i]/(p) is a finite field of p**2 elements (isomorphic to GF(p**2)), so its
multiplicative group has order p**2 - 1, giving the field-theoretic analog
of Fermat's little theorem: m**(p**2) == m (mod p) for every Gaussian
integer m, exactly as m**p == m (mod p) holds for ordinary integers.
Combining the two primes via the Chinese Remainder Theorem gives

    phi(n) = (p**2 - 1) * (q**2 - 1)

and the same RSA identity m**(e*d) == m (mod n) whenever e*d == 1
(mod phi(n)), for every Gaussian integer m -- not just ones coprime to n,
by the usual per-prime argument.

Because a Gaussian integer carries two independent components (real and
imaginary), each block encrypted this way carries twice the payload of a
plain-RSA block for a modulus of the same size, at the same modular-
exponentiation cost per block.

This module is a self-contained teaching implementation of that analog,
built on :class:`gint.zi.Zi`. It is NOT a vetted, side-channel-resistant,
or otherwise production-ready cryptographic implementation -- as with
textbook RSA, it has no OAEP-style padding scheme, so it should not be
used to protect real secrets.

Example:
>>> from gint.crypto import generate_keypair, encrypt_text, decrypt_text
>>> public_key, private_key = generate_keypair(bits=256)
>>> ciphertext = encrypt_text("Gaussian primes are neat.", public_key)
>>> decrypt_text(ciphertext, private_key)
'Gaussian primes are neat.'
"""

__author__ = "Alfred J. Reich, Ph.D."
__contact__ = "al.reich@gmail.com"
__copyright__ = "Copyright (C) 2024 Alfred J. Reich, Ph.D."
__license__ = "MIT"
__version__ = "0.1.0"


import math
import secrets
from typing import List, NamedTuple

from .zi import Zi


# ---------------------------------------------------------------------
# Key containers
# ---------------------------------------------------------------------

class GaussianRSAPublicKey(NamedTuple):
    """A public key: modulus ``n`` and public exponent ``e``.

    ``n = p * q`` is an ordinary (rational) integer -- the product of two
    distinct inert Gaussian primes -- but all encryption arithmetic is
    carried out in Z[i]/(n).
    """
    n: int
    e: int


class GaussianRSAPrivateKey(NamedTuple):
    """A private key: modulus ``n``, private exponent ``d``, and the two
    inert primes ``p``, ``q`` whose product is ``n`` (kept for reference;
    this implementation does not use the CRT speedup during decryption)."""
    n: int
    d: int
    p: int
    q: int


class GaussianRSACiphertext(NamedTuple):
    """The result of encrypting a byte string: a list of encrypted
    :class:`~gint.zi.Zi` blocks, plus the original (unpadded) byte
    length needed to strip padding on decryption."""
    blocks: List[Zi]
    length: int


# ---------------------------------------------------------------------
# Primality (Miller-Rabin -- fast enough for cryptographic key sizes,
# unlike Zi.is_gaussian_prime's trial division, which is not)
# ---------------------------------------------------------------------

_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)


def _is_probable_prime(n: int, rounds: int = 40) -> bool:
    """Miller-Rabin primality test. False-positive probability is at
    most 4**-rounds, negligible at the default of 40 rounds."""
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2  # a random witness in [2, n-2]
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def _random_inert_prime(bits: int) -> int:
    """A random `bits`-bit prime p with p % 4 == 3 -- the condition
    (see Zi.is_gaussian_prime) under which p stays prime in Z[i] rather
    than splitting into two conjugate Gaussian primes."""
    if bits < 4:
        raise ValueError("bits must be >= 4")
    while True:
        candidate = (secrets.randbits(bits - 2) << 2) | 0b11
        candidate |= (1 << (bits - 1))  # fix the top bit: exact bit length
        if _is_probable_prime(candidate):
            return candidate


# ---------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------

def _find_second_prime(p: int, bits: int, e: int) -> tuple:
    """Search for a random inert prime q != p such that e is coprime
    with phi(n) = (p**2 - 1) * (q**2 - 1). Returns (q, phi)."""
    while True:
        q = _random_inert_prime(bits)
        if q == p:
            continue
        phi = (p * p - 1) * (q * q - 1)
        if math.gcd(e, phi) == 1:
            return q, phi


def generate_keypair(bits: int = 256, e: int = 65537):
    """Generate a Gaussian-RSA keypair.

    Picks two distinct random inert Gaussian primes p, q (each a `bits`-bit
    rational prime with p % 4 == 3), sets n = p*q, and derives a private
    exponent d = e^-1 (mod phi(n)) with phi(n) = (p**2 - 1) * (q**2 - 1).
    If the requested e is not coprime with phi(n) for a given (p, q) pair,
    q is resampled until it is.

    :param bits: bit length of each of the two primes p, q. The modulus n
        is therefore about ``2 * bits`` bits, but (per the module
        docstring) each block carries two components, each reduced mod n,
        so throughput is comparable to plain RSA with an n of about
        twice that size.
    :param e: public exponent. Defaults to 65537, the conventional RSA
        choice.
    :return: a ``(public_key, private_key)`` pair.
    """
    if bits < 4:
        raise ValueError("bits must be >= 4")
    p = _random_inert_prime(bits)
    q, phi = _find_second_prime(p, bits, e)
    n = p * q
    d = pow(e, -1, phi)
    return (GaussianRSAPublicKey(n=n, e=e),
            GaussianRSAPrivateKey(n=n, d=d, p=p, q=q))


# ---------------------------------------------------------------------
# Core block cipher: modular exponentiation of a Zi mod a rational n
# ---------------------------------------------------------------------

def _pow_mod(base: Zi, exponent: int, n: int) -> Zi:
    """base**exponent, with both the base and every intermediate result
    reduced mod the rational integer n (via Zi's % operator against
    Zi(n, 0)), so that coefficients never grow beyond O(n) regardless of
    how large exponent is."""
    modulus = Zi(n, 0)
    result = Zi(1, 0)
    base = base % modulus
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent >>= 1
    return result


def encrypt_block(m: Zi, public_key: GaussianRSAPublicKey) -> Zi:
    """Encrypt a single message block. `m` must be a Zi with both
    components in [0, public_key.n) -- the canonical representatives of
    Z[i]/(n) that this module's byte-level encoding produces."""
    n = public_key.n
    if not (0 <= m.real < n and 0 <= m.imag < n):
        raise ValueError(
            f"message block {m} out of range: components must be in [0, {n})"
        )
    return _pow_mod(m, public_key.e, n)


def decrypt_block(c: Zi, private_key: GaussianRSAPrivateKey) -> Zi:
    """Decrypt a single ciphertext block, returning the original Zi
    message block with both components in [0, private_key.n)."""
    n = private_key.n
    m = _pow_mod(c, private_key.d, n)
    return Zi(m.real % n, m.imag % n)


# ---------------------------------------------------------------------
# Byte-oriented convenience layer
# ---------------------------------------------------------------------

def block_capacity(n: int) -> int:
    """Number of bytes safely packed into *each* of a Zi block's two
    components for modulus n, leaving a one-bit safety margin so the
    resulting integer is always strictly less than n."""
    return max(1, (n.bit_length() - 1) // 8)


def encrypt_bytes(data: bytes, public_key: GaussianRSAPublicKey) -> GaussianRSACiphertext:
    """Encrypt an arbitrary byte string as a sequence of Zi blocks. Each
    block packs ``2 * block_capacity(n)`` bytes: the first half becomes
    the real component, the second half the imaginary component. The
    final block is zero-padded; the original length is carried in the
    returned :class:`GaussianRSACiphertext` so decryption can strip it."""
    k = block_capacity(public_key.n)
    length = len(data)
    pad_len = (-length) % (2 * k)
    padded = data + b"\x00" * pad_len
    blocks = []
    for i in range(0, len(padded), 2 * k):
        chunk = padded[i:i + 2 * k]
        a = int.from_bytes(chunk[:k], "big")
        b = int.from_bytes(chunk[k:], "big")
        blocks.append(encrypt_block(Zi(a, b), public_key))
    return GaussianRSACiphertext(blocks=blocks, length=length)


def decrypt_bytes(ciphertext: GaussianRSACiphertext, private_key: GaussianRSAPrivateKey) -> bytes:
    """Inverse of :func:`encrypt_bytes`.

    :raises ValueError: if a decrypted block doesn't fit back into
        ``block_capacity(private_key.n)`` bytes per component. With the
        matching private key this never happens (see block_capacity's
        one-bit safety margin); it signals a key/ciphertext mismatch,
        e.g. decrypting with the wrong private key.
    """
    k = block_capacity(private_key.n)
    out = bytearray()
    for c in ciphertext.blocks:
        m = decrypt_block(c, private_key)
        try:
            out += m.real.to_bytes(k, "big")
            out += m.imag.to_bytes(k, "big")
        except OverflowError as exc:
            raise ValueError(
                "decrypted block doesn't fit the expected size -- "
                "wrong private key for this ciphertext?"
            ) from exc
    return bytes(out[:ciphertext.length])


def encrypt_text(text: str, public_key: GaussianRSAPublicKey, encoding: str = "utf-8") -> GaussianRSACiphertext:
    """Encrypt a string (UTF-8 by default). Convenience wrapper around
    :func:`encrypt_bytes`."""
    return encrypt_bytes(text.encode(encoding), public_key)


def decrypt_text(ciphertext: GaussianRSACiphertext, private_key: GaussianRSAPrivateKey, encoding: str = "utf-8") -> str:
    """Inverse of :func:`encrypt_text`."""
    return decrypt_bytes(ciphertext, private_key).decode(encoding)
