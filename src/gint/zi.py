"""Gaussian Integer Class

A Gaussian integer is a complex number whose real and imaginary parts are both integers.
Similarly, a Gaussian rational is a complex number whose real and imaginary parts are
rational numbers.

In mathematics, Gaussian integers and rationals are denoted by Z[i] & Q[i], resp.
So, here, Zi & Qi denote the Gaussian integer and rational classes, respectively.

The classes support the arithmetic of Gaussian integers and rationals using the
operators: +, -, *, /, //, %, **, +=, -=, *=, and /=, along with a variety of
number-theoretic algorithms, such as greatest common divisor (gcd), an extended
Euclidean algorithm (xgcd), etc.

Example:
>>> from gint import Zi, Qi
>>>
>>> alpha = Zi(11, 3)
>>> beta = Zi(1, 8)
>>> a, x, y = Zi.xgcd(alpha, beta)
>>> print(f'{alpha * x + beta * y} = {alpha} * {x} + {beta} * {y}')
>>> # ==> (1-2j) = (11+3j) * (2-1j) + (1+8j) * 3j
"""

__author__ = "Alfred J. Reich, Ph.D."
__contact__ = "al.reich@gmail.com"
__copyright__ = "Copyright (C) 2024 Alfred J. Reich, Ph.D."
__license__ = "MIT"
__version__ = "0.2.0"


import re
from fractions import Fraction
from math import sqrt, isqrt
from numbers import Complex
import random as rnd


class Zi(Complex):
    """A class that represents a Gaussian integer. In mathematics, the set of all integers
    is denoted by Z, and the set of all Gaussian integers is denoted by Z[i]."""

    __slots__ = ('_real', '_imag')

    # The character that represents the imaginary unit in str().
    # Change via Zi.set_unit_symbol('i') or Zi.set_unit_symbol('j').
    # Qi delegates to this same setting, so Zi and Qi always agree,
    # important since a Qi with integer components collapses into a Zi.
    _unit_symbol = 'j'

    # A composite string like '(2-3j)', '3j', or '-2i': an optional signed
    # real part, an optional signed-imaginary+unit part, at least one of
    # the two required. Components are plain (possibly signed) integers,
    # since Zi, unlike Qi, has no fractional part.
    _INT = r'[+-]?\d+'
    _PAIR_RE = re.compile(rf'^(?P<real>{_INT})(?P<sign>[+-])(?P<imag>\d+)[ij]$')
    _IMAG_ONLY_RE = re.compile(rf'^(?P<imag>{_INT})[ij]$')

    def __init__(self, real = None, imag = None) -> None:
        if isinstance(real, str) and imag is None:
            r, i = Zi._parse_string(real)
            super().__setattr__('_real', r)
            super().__setattr__('_imag', i)
        elif isinstance(real, (complex, Zi)):
            if imag is None:
                super().__setattr__('_real', round(real.real))
                super().__setattr__('_imag', round(real.imag))
            else:
                raise TypeError(f"imag must be None if real is a complex: {imag}")
        elif isinstance(real, (int, float)):
            super().__setattr__('_real', round(real))
            if isinstance(imag, (int, float)):
                super().__setattr__('_imag', round(imag))
            elif imag is None:
                super().__setattr__('_imag', 0)
            else:
                raise TypeError(f"Invalid type for imag: {imag}")
        elif real is None and imag is None:
            super().__setattr__('_real', 0)
            super().__setattr__('_imag', 0)
        else:
            raise TypeError(f"Invalid type for real: {real}")

    # ---------------- Accessors -----------------------

    @property
    def real(self) -> int:
        return self._real

    @property
    def imag(self) -> int:
        return self._imag

    def __getitem__(self, idx):
        if idx == 0:
            return self.real
        elif idx == 1:
            return self.imag
        raise IndexError("Zi index out of range (must be 0 or 1)")

    # ---------------- Type Cast -----------------------

    @staticmethod
    def _parse_string(s):
        """Parse a full Zi string representation, e.g. '(2-3j)', '3j',
        '-2i', or a bare real like '4'. Returns an (int, int) pair.
        Raises ValueError if unparsable."""
        s = s.strip()
        inner = s
        if inner.startswith('(') and inner.endswith(')'):
            inner = inner[1:-1].strip()

        if inner and inner[-1] in 'ij':
            m = Zi._PAIR_RE.match(inner)
            if m:
                real = int(m.group('real'))
                mag = int(m.group('imag'))
                imag = mag if m.group('sign') == '+' else -mag
                return real, imag
            m = Zi._IMAG_ONLY_RE.match(inner)
            if m:
                return 0, int(m.group('imag'))
            raise ValueError(f"Cannot parse Zi string: {s!r}")

        # No imaginary unit present: the whole thing is the real part.
        return int(inner), 0

    @staticmethod
    def _ensure_zi(x):
        """Best-effort conversion of x to a Zi, for use inside Zi's own
        arithmetic dunder methods. Returns None (rather than raising) for
        types it doesn't understand, such as Qi, so that operator
        methods can return NotImplemented and let Python fall back to the
        other operand's reflected method (e.g. Qi.__radd__) instead of
        failing outright. See _require_zi for a raising variant used by
        static utilities that have no such fallback available."""
        if isinstance(x, Zi):
            return x
        if isinstance(x, complex):
            return Zi(x)
        if isinstance(x, (int, float)):
            return Zi(x, 0)
        return None

    @staticmethod
    def _require_zi(x):
        """Like _ensure_zi, but raises TypeError on failure. Used by static
        utility methods (modified_divmod, gcd, xgcd) where there's no
        operator-dispatch fallback to defer to."""
        oth = Zi._ensure_zi(x)
        if oth is None:
            raise TypeError(f"Cannot convert {type(x)} to Zi")
        return oth

    # ---------------- Equality -----------------------

    def __eq__(self, other):
        """If other can be cast to a Zi, and if self is equal to that,
        then self == other."""
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        return self.real == oth.real and self.imag == oth.imag

    def __ne__(self, other):
        """Inverse of __eq__. Must correctly propagate NotImplemented so that
        Python falls back to the other operand's __eq__/__ne__ instead of
        treating an incomparable type as simply 'not equal'."""
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    # ---------------- Univariate Methods -----------------------

    def __repr__(self):
        return f"Zi({self.real}, {self.imag})"

    def __str__(self):
        """e.g. Zi(2, -3) -> '(2-3j)' (or '(2-3i)' if the unit symbol has
        been set to 'i'). Matches complex's str() format, real part
        dropped and no parens when it's zero, except a purely real Zi
        prints as a bare integer with no unit at all."""
        if self.imag == 0:
            return str(self._real)
        sym = Zi._unit_symbol
        if self.real == 0:
            return f"{self.imag}{sym}"
        sign = '-' if self.imag < 0 else '+'
        return f"({self.real}{sign}{abs(self.imag)}{sym})"

    def __hash__(self):
        return hash((self.real, self.imag))

    def __complex__(self):
        return complex(self.real, self.imag)

    def __abs__(self):
        return sqrt(self.norm)

    def __neg__(self):
        return Zi(-self._real, -self.imag)

    def __pos__(self):
        return Zi(self._real, self.imag)

    def __bool__(self):
        """True if at least one component (real or imag) is non-zero"""
        return self.real != 0 or self.imag != 0

    def conjugate(self):
        return Zi(self._real, -self.imag)

    @property
    def norm(self):
        return self.real * self.real + self.imag * self.imag

    # ---------------- Arithmetic -----------------------------

    def __add__(self, other):
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        return Zi(self.real + oth.real, self.imag + oth.imag)

    def __radd__(self, other):
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        return oth + self

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        return Zi(self.real - oth.real, self.imag - oth.imag)

    def __rsub__(self, other):
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        return oth - self

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        a, b = self
        c, d = oth
        return Zi(a * c - b * d, a * d + b * c)

    def __rmul__(self, other):
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        return oth * self

    def __imul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):  # implements the / operator
        """Exact division. Returns the precise Gaussian-rational quotient
        as a Qi (or as a Zi, via Qi's auto-collapse, when the division is
        exact). Uses exact integer/Fraction arithmetic throughout, so it
        never loses precision regardless of coefficient size."""
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        n = oth.norm
        if n == 0:
            raise ZeroDivisionError("division by zero Gaussian integer")
        # local import: avoids a circular import, since qi.py imports Zi at module level
        from .qi import Qi
        num = self * oth.conjugate()
        return Qi(Fraction(num.real, n), Fraction(num.imag, n))

    def __rtruediv__(self, other):
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        return oth.__truediv__(self)

    def __floordiv__(self, other):  # implements the // operator
        """Gaussian integers have no natural total order, so 'floor'
        division is defined as rounding to the nearest Gaussian integer
        (using exact Fraction arithmetic, so it stays precise regardless
        of coefficient size). This is distinct from __truediv__, which
        returns the exact quotient as a Qi or Zi."""
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        n = oth.norm
        if n == 0:
            raise ZeroDivisionError("division by zero Zi")
        num = self * oth.conjugate()
        return Zi(round(Fraction(num.real, n)), round(Fraction(num.imag, n)))

    def __rfloordiv__(self, other):
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        return oth.__floordiv__(self)

    def __mod__(self, other):
        """Implements the % operator."""
        oth = Zi._ensure_zi(other)
        if oth is None:
            return NotImplemented
        q = self // oth
        return self - oth * q

    def __pow__(self, exponent):
        """Implements the ** operator."""
        if not isinstance(exponent, int):
            return NotImplemented
        if exponent == 0:
            return Zi(1, 0)
        # For a negative exponent, Zi(1, 0) / self returns the EXACT
        # inverse (a Qi, unless self is a unit) rather than a rounded
        # approximation. The multiplication loop below works correctly
        # even when base/result become Qi partway through, since Qi's
        # arithmetic methods handle mixed Zi/Qi operands transparently.
        base, exp = (self, exponent) if exponent > 0 else (Zi(1, 0) / self, -exponent)
        result = Zi(1, 0)
        while exp > 0:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result

    def __rpow__(self, base):
        if self.imag != 0:
            return NotImplemented
        oth = Zi._ensure_zi(base)
        if oth is None:
            return NotImplemented
        return oth.__pow__(self.real)

    def inverse(self):
        """The exact multiplicative inverse of this Gaussian integer.
        Returns a Zi if self is a unit, otherwise a Qi. Provided so that
        inverse() works uniformly on any value coming out of Qi's
        arithmetic, since a Qi with denominator 1 collapses into a Zi."""
        return Zi(1, 0) / self

    # ---------- Array Conversion ----------

    def to_array(self):
        return [self.real, self.imag]

    @staticmethod
    def from_array(arr):
        if len(arr) != 2:
            raise ValueError("Array must have exactly two elements")
        return Zi(arr[0], arr[1])

    # ---------- Prime Numbers ----------

    @staticmethod
    def _is_rational_prime(n):
        """True if the plain (rational) integer n is prime. This is a
        helper for is_gaussian_prime, not a statement about Gaussian
        primality."""
        n = abs(int(n))
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False
        i = 3
        while i * i <= n:
            if n % i == 0:
                return False
            i += 2
        return True

    @staticmethod
    def is_gaussian_prime(x):
        """A Gaussian integer a+bi is prime iff:

        - both a,b are nonzero and a^2+b^2 is a rational prime, or
        - one of a,b is zero and the other has absolute value c, where c is
          a rational prime with c % 4 == 3 (primes p == 2 or p == 1 mod 4
          are NOT Gaussian primes: 2 ramifies as -i(1+i)^2, and p == 1 mod 4
          splits into two conjugate Gaussian primes).
        """
        if isinstance(x, Zi):
            a, b = x.real, x.imag
        elif isinstance(x, int):
            a, b = x, 0
        else:
            raise TypeError("is_gaussian_prime accepts a Zi or an int")

        if a == 0 and b == 0:
            return False

        if a != 0 and b != 0:
            n = a * a + b * b
            return Zi._is_rational_prime(n)
        else:
            c = abs(a) if b == 0 else abs(b)
            return Zi._is_rational_prime(c) and c % 4 == 3

    # ---------- Number Theory ----------

    @staticmethod
    def modified_divmod(a, b):
        """Divide a by b, rounding the quotient to the nearest Gaussian
        integer (rather than truncating), so that the remainder has
        strictly smaller norm than b. Returns q & r, such that
        a = b * q + r. This is what makes gcd/xgcd below terminate
        correctly, since Z[i] is a Euclidean domain under the norm
        only when division rounds to nearest.
        """
        a = Zi._require_zi(a)
        b = Zi._require_zi(b)
        if b == Zi(0, 0):
            raise ZeroDivisionError("division by zero Zi")
        q = a // b  # rounds to nearest Gaussian integer
        r = a - b * q
        return q, r

    @staticmethod
    def gcd(a, b):
        """A gcd algorithm for Gaussian integers.
        Returns the greatest common divisor of a & b.

        This function implements the Euclidean algorithm for Gaussian integers.
        """
        a = Zi._require_zi(a)
        b = Zi._require_zi(b)
        while b != Zi(0, 0):
            _, r = Zi.modified_divmod(a, b)
            a, b = b, r
        return a

    @staticmethod
    def xgcd(a, b):
        """Extended Euclidean algorithm. Returns (g, s, t) such that
        a*s + b*t == g == gcd(a, b) (up to a unit factor)."""
        a = Zi._require_zi(a)
        b = Zi._require_zi(b)
        old_r, r = a, b
        old_s, s = Zi(1, 0), Zi(0, 0)
        old_t, t = Zi(0, 0), Zi(1, 0)
        while r != Zi(0, 0):
            q, _ = Zi.modified_divmod(old_r, r)
            old_r, r = r, old_r - q * r
            old_s, s = s, old_s - q * s
            old_t, t = t, old_t - q * t
        return old_r, old_s, old_t

    @staticmethod
    def is_associate(a, b):
        """True iff a and b differ only by a unit factor (a == b*u for
        one of Z[i]'s four units). Two Gaussian integers that are
        associates generate the same ideal and share the same
        factorization up to units, e.g. this is why gcd/xgcd only
        determine their result up to a unit. By convention, 0 is only
        an associate of itself."""
        a = Zi._require_zi(a)
        b = Zi._require_zi(b)
        if a == Zi(0, 0) or b == Zi(0, 0):
            return a == b
        return (a / b) in Zi.units()

    @staticmethod
    def is_coprime(a, b):
        """True iff gcd(a, b) is a unit, i.e., a and b share no common
        Gaussian-prime factor. Follows the gcd(0, 0) == 0 convention,
        so is_coprime(0, 0) is False (0 is not a unit)."""
        return Zi.gcd(a, b).is_unit

    @staticmethod
    def divides(a, b):
        """True iff a divides b exactly (there exists a Gaussian integer
        q with b == a*q). By convention, 0 divides only 0."""
        a = Zi._require_zi(a)
        b = Zi._require_zi(b)
        if a == Zi(0, 0):
            return b == Zi(0, 0)
        return b % a == Zi(0, 0)

    @staticmethod
    def lcm(a, b):
        """Least common multiple of two Gaussian integers, computed as
        a*b // gcd(a, b) (exact, since gcd always divides a*b evenly).
        Like gcd, this is only well-defined up to multiplication by a
        unit, Z[i] has four units, so 'the' lcm isn't unique, just as
        'the' gcd isn't."""
        a = Zi._require_zi(a)
        b = Zi._require_zi(b)
        if a == Zi(0, 0) or b == Zi(0, 0):
            return Zi(0, 0)
        g = Zi.gcd(a, b)
        return (a * b) // g

    @staticmethod
    def congruent_modulo(a, b, c):
        """True iff a is congruent to b modulo c, i.e., iff c divides (a - b).
        Raises ZeroDivisionError if c == Zi(0, 0), via the underlying %
        operator (same behavior as gcd/xgcd on a zero modulus).
        """
        a = Zi._require_zi(a)
        b = Zi._require_zi(b)
        c = Zi._require_zi(c)
        return (a - b) % c == Zi(0, 0)

    @staticmethod
    def crt(residues, moduli):
        """Chinese Remainder Theorem over the Gaussian integers.

        Given pairwise-coprime moduli m_0, ..., m_{k-1} in Z[i] and
        matching residues a_0, ..., a_{k-1}, returns a Gaussian integer
        x such that

            x % moduli[j] == residues[j] % moduli[j]   for every j

        i.e. x is congruent to residues[j] modulo moduli[j] for every j
        (see congruent_modulo). x is unique modulo M = prod(moduli),
        the same guarantee the classic integer CRT gives, except
        that here, as with gcd/xgcd/factor, everything is only
        determined up to a unit factor, since Z[i]'s four units (see
        Zi.units) make "the" gcd/product non-unique to begin with.

        Method: fold the two-modulus formula in one pair at a time,
        given x already solving the system for m_0...m_{i-1} (combined
        so far into M), and a new pair (residues[i], moduli[i]),
        xgcd(M, moduli[i]) gives Bezout coefficients s, t with
        M*s + moduli[i]*t == g. Coprimality (required for a solution
        to exist) means g is a unit, so normalizing s, t by g's inverse
        gives M*s + moduli[i]*t == 1 exactly, and
        x_new = x*t*moduli[i] + residues[i]*s*M  (mod M*moduli[i])
        satisfies both x_new == x (mod M) and x_new == residues[i]
        (mod moduli[i]), the standard two-modulus CRT construction.
        Repeating this for each successive modulus folds all of them
        into one solution.

        Raises ValueError if residues and moduli have different
        lengths, if moduli is empty, or if the moduli aren't pairwise
        coprime. (Detected as soon as some modulus fails to be coprime
        with the product of the ones already folded in, which, since
        Z[i] is a UFD, can only happen if it shares a common
        non-unit factor with one of them individually.) Raises
        ZeroDivisionError if any modulus is zero.
        """
        residues = [Zi._require_zi(r) for r in residues]
        moduli = [Zi._require_zi(m) for m in moduli]
        if len(residues) != len(moduli):
            raise ValueError("residues and moduli must have the same length")
        if not moduli:
            raise ValueError("crt requires at least one modulus")
        if any(m == Zi(0, 0) for m in moduli):
            raise ZeroDivisionError("modulus cannot be zero")

        x, m = residues[0] % moduli[0], moduli[0]
        for a_i, m_i in zip(residues[1:], moduli[1:]):
            g, s, t = Zi.xgcd(m, m_i)
            if not g.is_unit:
                raise ValueError("moduli must be pairwise coprime")
            g_inv = g.inverse()  # normalize so m*s + m_i*t == 1 exactly
            s, t = s * g_inv, t * g_inv
            m_new = m * m_i
            x = (x * t * m_i + a_i * s * m) % m_new  # type: ignore
            m = m_new
        return x

    @staticmethod
    def _sum_of_two_squares(p):
        """Find (a, b) with a^2 + b^2 == p, for a rational prime p == 1
        (mod 4), such a representation is guaranteed to exist and be
        essentially unique (up to order/sign) by Fermat's two-square
        theorem. Private helper for factor(), below; brute-force search
        is fine here since p is already a known small factor of a norm
        that's been trial-divided down."""
        for a in range(1, isqrt(p) + 1):
            b_sq = p - a * a
            b = isqrt(b_sq)
            if b * b == b_sq:
                return a, b
        raise ValueError(f"{p} is not expressible as a sum of two squares")

    @staticmethod
    def factor(z):
        """Factor a nonzero Gaussian integer into Gaussian primes.

        Returns (unit, factors) where unit is one of Zi.units() and
        factors is a list of (prime, exponent) pairs, such that
        z == unit * prod(prime ** exponent for prime, exponent in factors)
        and each prime satisfies Zi.is_gaussian_prime. Raises ValueError
        for z == 0, since 0 has no factorization.

        Method: factor the rational integer N(z) by trial division,
        then lift each rational prime factor p to its Gaussian-prime
        form --
          - p == 2 (ramified):        1+i, appearing to the same power
                                       p appears in N(z)
          - p == 3 (mod 4) (inert):   p itself, a Gaussian prime
          - p == 1 (mod 4) (split):   a+bi and its conjugate a-bi,
                                       whose individual exponents in z
                                       are found by direct trial
                                       division on z (not derivable
                                       from N(z) alone, since the two
                                       conjugate primes can divide z to
                                       different powers)
        This is trial division throughout, so it's fine for the sizes
        you'd hit interactively, but isn't meant for cryptographic-size
        inputs.
        """
        z = Zi._require_zi(z)
        if z == Zi(0, 0):
            raise ValueError("cannot factor zero")

        n = z.norm
        rational_factors = []
        d = 2
        while d * d <= n:
            if n % d == 0:
                e = 0
                while n % d == 0:
                    n //= d
                    e += 1
                rational_factors.append((d, e))
            d += 1 if d == 2 else 2
        if n > 1:
            rational_factors.append((n, 1))

        remaining = z
        factors = []
        for p, _norm_exp in rational_factors:
            if p == 2:
                candidates = [Zi(1, 1)]
            elif p % 4 == 3:
                candidates = [Zi(p, 0)]
            else:  # p % 4 == 1: splits into two conjugate Gaussian primes
                a, b = Zi._sum_of_two_squares(p)
                pi = Zi(a, b)
                candidates = [pi, pi.conjugate()]
            for pi in candidates:
                count = 0
                while True:
                    q, r = Zi.modified_divmod(remaining, pi)
                    if r != Zi(0, 0):
                        break
                    remaining = q
                    count += 1
                if count:
                    factors.append((pi, count))

        # Whatever's left after extracting every prime factor is
        # necessarily a unit.
        return remaining, factors
    
    # ---------- Configuration ----------

    @classmethod
    def get_unit_symbol(cls):
        return cls._unit_symbol

    @classmethod
    def set_unit_symbol(cls, symbol):
        if symbol not in ('i', 'j'):
            raise ValueError("unit symbol must be 'i' or 'j'")
        cls._unit_symbol = symbol

    # ---------- utilities ----------

    @staticmethod
    def random(re_min=-100, re_max=100, im_min=None, im_max=None):
        if im_min is None:
            im_min = re_min
        if im_max is None:
            im_max = re_max
        return Zi(rnd.randint(re_min, re_max), rnd.randint(im_min, im_max))

    @staticmethod
    def eye():
        return Zi(0, 1)

    @staticmethod
    def units():
        return [Zi(1), -Zi(1), Zi.eye(), -Zi.eye()]

    @property
    def is_unit(self):
        """A Gaussian integer is a unit iff it has norm 1 (equivalent to,
        but cheaper than, checking membership in Zi.units())."""
        return self.norm == 1

    @staticmethod
    def two():
        return Zi(1, 1)
