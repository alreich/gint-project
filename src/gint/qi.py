"""Gaussian rational (Qi) class: a + bi with a, b in Q, represented
exactly as fractions.Fraction.

Qi is integrated with Zi (Gaussian integers): constructing a Qi whose
real and imaginary parts both happen to be whole numbers transparently
yields a Zi instead of a Qi (see __new__). This means Qi(4, 6) is
actually a Zi(4, 6), while Qi(4, '2/3') is a genuine Qi.

Examples:

>>> from gint import Zi, Qi
>>>
>>> Zi(11, 3) / Zi(1, 8)
>>> # ==> Qi('7/13', '-17/13')
>>>
>>> print(Zi(11, 3) / Zi(1, 8))
>>> # ==> (7/13-17/13j)
>>>
>>> Qi(2.25, -3.6)
>>> # ==> Qi('9/4', '-18/5')
>>>
>>> Qi(2.0, 4)
>>> # ==> Zi(2, 4)
"""

import re
from fractions import Fraction
from math import sqrt, lcm
from numbers import Complex

from .zi import Zi


__author__ = "Alfred J. Reich, Ph.D."
__contact__ = "al.reich@gmail.com"
__copyright__ = "Copyright (C) 2024 Alfred J. Reich, Ph.D."
__license__ = "MIT"
__version__ = "0.2.0"


class Qi(Complex):
    """A class that represents a Gaussian rational: a + bi with a, b in Q,
    the set of all rational numbers."""

    __slots__ = ('_real', '_imag')

    # The imaginary-unit symbol used in str() lives on Zi, not here --
    # Qi.get_unit_symbol()/set_unit_symbol() below just forward to it.
    # This keeps a single source of truth, which matters because a Qi
    # with whole-number components collapses into a Zi (see __new__):
    # without sharing the setting, str() on the collapsed Zi could show
    # a different unit symbol than str() on the Qi it came from.

    # Default cap used by limit_denominator() when none is given
    # Change via Qi.set_max_denominator(...)
    _max_denominator = 1_000_000

    # A composite string like '(1/2-3/5j)', '3/5j', or '-2i': an optional
    # signed real part, an optional signed-imaginary+unit part, at least
    # one of the two required. Numbers may be plain integers, fractions
    # ("num/den"), or decimals ("3.4").
    _NUMBER = r'[+-]?\d+(?:\.\d+)?(?:/\d+)?'
    _PAIR_RE = re.compile(
        rf'^(?P<real>{_NUMBER})(?P<sign>[+-])(?P<imag>\d+(?:\.\d+)?(?:/\d+)?)[ij]$'
    )
    _IMAG_ONLY_RE = re.compile(rf'^(?P<imag>{_NUMBER})[ij]$')

    # ---------------- Construction -----------------------

    def __new__(cls, real=None, imag=None):
        r, i = Qi._coerce(real, imag)
        if r.denominator == 1 and i.denominator == 1:
            return Zi(int(r), int(i))
        # noinspection PyTypeChecker
        return super().__new__(cls)

    def __init__(self, real=None, imag=None) -> None:
        # If __new__ returned a Zi (denominators both 1), Python does not
        # call __init__ at all, since the returned object isn't an
        # instance of Qi. So by the time we get here, we know this is a
        # genuine Qi.
        r, i = Qi._coerce(real, imag)
        super().__setattr__('_real', r)
        super().__setattr__('_imag', i)

    @staticmethod
    def _to_fraction(x):
        """Convert a single scalar component to an exact Fraction. Floats
        are converted via str() first, so Qi(2, 3.4) captures the decimal
        value 17/5 that was typed, rather than the binary floating-point
        noise you'd get from Fraction(3.4) directly."""
        if isinstance(x, Fraction):
            return x
        if isinstance(x, bool):
            return Fraction(int(x))
        if isinstance(x, int):
            return Fraction(x)
        if isinstance(x, float):
            return Fraction(str(x))
        if isinstance(x, str):
            return Fraction(x.strip())
        raise TypeError(f"Cannot convert {x!r} ({type(x).__name__}) to Fraction")

    @classmethod
    def _parse_string(cls, s):
        """Parse a full Qi string representation, e.g. '(1/2-3/5j)',
        '3/5j', '-2i', or a bare real like '4/6'. Returns a
        (Fraction, Fraction) pair. Raises ValueError if unparsable."""
        s = s.strip()
        inner = s
        if inner.startswith('(') and inner.endswith(')'):
            inner = inner[1:-1].strip()

        if inner and inner[-1] in 'ij':
            m = cls._PAIR_RE.match(inner)
            if m:
                real = Fraction(m.group('real'))
                mag = Fraction(m.group('imag'))
                imag = mag if m.group('sign') == '+' else -mag
                return real, imag
            m = cls._IMAG_ONLY_RE.match(inner)
            if m:
                return Fraction(0), Fraction(m.group('imag'))
            raise ValueError(f"Cannot parse Qi string: {s!r}")

        # No imaginary unit present: the whole thing is the real part.
        return Fraction(inner), Fraction(0)

    @staticmethod
    def _coerce(real, imag):
        """Turn constructor arguments into a (Fraction, Fraction) pair."""
        if isinstance(real, str) and imag is None:
            return Qi._parse_string(real)

        if isinstance(real, (complex, Zi, Qi)):
            if imag is not None:
                raise TypeError(
                    f"imag must be None if real is a {type(real).__name__}: {imag}"
                )
            return Qi._to_fraction(real.real), Qi._to_fraction(real.imag)

        if real is None and imag is None:
            return Fraction(0), Fraction(0)

        r = Qi._to_fraction(real) if real is not None else Fraction(0)
        i = Qi._to_fraction(imag) if imag is not None else Fraction(0)
        return r, i

    # ---------------- Accessors -----------------------

    @property
    def real(self) -> Fraction:
        return self._real

    @property
    def imag(self) -> Fraction:
        return self._imag

    def __getitem__(self, idx):
        if idx == 0:
            return self.real
        elif idx == 1:
            return self.imag
        raise IndexError("Qi index out of range (must be 0 or 1)")

    # ---------------- Type Cast -----------------------

    @staticmethod
    def _parts(x):
        """Extract a (Fraction, Fraction) pair from any operand type Qi's
        arithmetic understands (Qi, Zi, complex, Fraction, int, float).
        Returns None for anything else, so operator methods can return
        NotImplemented rather than raising an exception."""
        if isinstance(x, Qi):
            return x.real, x.imag
        if isinstance(x, Zi):
            return Fraction(x.real), Fraction(x.imag)
        if isinstance(x, complex):
            return Qi._to_fraction(x.real), Qi._to_fraction(x.imag)
        if isinstance(x, Fraction):
            return x, Fraction(0)
        if isinstance(x, bool):
            return Fraction(int(x)), Fraction(0)
        if isinstance(x, int):
            return Fraction(x), Fraction(0)
        if isinstance(x, float):
            return Qi._to_fraction(x), Fraction(0)
        return None

    @staticmethod
    def _require_qi(x):
        """Like _parts, but raises TypeError on failure (rather than
        returning None) and wraps the result back up as a Qi. Used by
        static utilities (gcd, congruent_modulo) that have no
        operator-dispatch fallback to defer to."""
        parts = Qi._parts(x)
        if parts is None:
            raise TypeError(f"Cannot convert {type(x)} to Qi")
        return Qi(*parts)

    # ---------------- Equality -----------------------

    def __eq__(self, other):
        parts = Qi._parts(other)
        if parts is None:
            return NotImplemented
        or_, oi = parts
        return self.real == or_ and self.imag == oi

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    # ---------------- Univariate Methods -----------------------

    def __repr__(self):
        return f"Qi('{self.real}', '{self.imag}')"

    def __str__(self):
        """e.g. Qi('1/2', '-3/5') -> '(1/2-3/5j)'. Always shows both
        components with an explicit sign, unlike complex's str() (which
        omits the real part when it's zero); this keeps the format simple
        and unambiguous to parse back with Qi(str(q))."""
        sign = '-' if self.imag < 0 else '+'
        return f"({self.real}{sign}{abs(self.imag)}{Zi.get_unit_symbol()})"

    def __hash__(self):
        return hash((self.real, self.imag))

    def __complex__(self):
        return complex(float(self.real), float(self.imag))

    def __abs__(self):
        return sqrt(self.norm)

    def __neg__(self):
        return Qi(-self.real, -self.imag)

    def __pos__(self):
        return self

    def __bool__(self):
        return self.real != 0 or self.imag != 0

    def conjugate(self):
        return Qi(self.real, -self.imag)

    @property
    def norm(self):
        return self.real * self.real + self.imag * self.imag

    # ---------------- Arithmetic -----------------------------

    def __add__(self, other):
        parts = Qi._parts(other)
        if parts is None:
            return NotImplemented
        or_, oi = parts
        return Qi(self.real + or_, self.imag + oi)

    def __radd__(self, other):
        return self.__add__(other)

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        parts = Qi._parts(other)
        if parts is None:
            return NotImplemented
        or_, oi = parts
        return Qi(self.real - or_, self.imag - oi)

    def __rsub__(self, other):
        parts = Qi._parts(other)
        if parts is None:
            return NotImplemented
        or_, oi = parts
        return Qi(or_ - self.real, oi - self.imag)

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        parts = Qi._parts(other)
        if parts is None:
            return NotImplemented
        c, d = parts
        a, b = self.real, self.imag
        return Qi(a * c - b * d, a * d + b * c)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        parts = Qi._parts(other)
        if parts is None:
            return NotImplemented
        c, d = parts
        denom = c * c + d * d
        if denom == 0:
            raise ZeroDivisionError("division by zero Gaussian rational")
        a, b = self.real, self.imag
        # (a+bi)/(c+di) = (a+bi)(c-di) / (c^2+d^2)
        return Qi((a * c + b * d) / denom, (b * c - a * d) / denom)

    def __rtruediv__(self, other):
        """other / self."""
        parts = Qi._parts(other)
        if parts is None:
            return NotImplemented
        c, d = parts
        a, b = self.real, self.imag
        denom = a * a + b * b
        if denom == 0:
            raise ZeroDivisionError("division by zero Gaussian rational")
        # (c+di)/(a+bi) = (c+di)(a-bi) / (a^2+b^2)
        return Qi((c * a + d * b) / denom, (d * a - c * b) / denom)

    def inverse(self):
        """Returns the exact multiplicative inverse of this Gaussian rational."""
        denom = self.real * self.real + self.imag * self.imag
        if denom == 0:
            raise ZeroDivisionError("cannot invert zero Gaussian rational")
        return Qi(self.real / denom, -self.imag / denom)

    def __pow__(self, exponent):
        if not isinstance(exponent, int):
            return NotImplemented
        if exponent == 0:
            return Qi(1, 0)
        base, exp = (self, exponent) if exponent > 0 else (self.inverse(), -exponent)
        result = Qi(1, 0)
        while exp > 0:
            if exp & 1:
                result = result * base
            base = base * base
            exp >>= 1
        return result

    def __rpow__(self, base):
        # A Qi that survived construction (wasn't collapsed to a Zi) is,
        # by definition, not both real-valued and integer-valued, so a
        # well-defined integer power of `base` raised to this exponent
        # isn't supported.
        return NotImplemented

    # ---------- Array Conversion ----------

    def to_array(self):
        """Returns a two-element array representation of this Gaussian rational."""
        return [self.real, self.imag]

    @staticmethod
    def from_array(arr):
        """Returns a Gaussian rational, given a two-element array."""
        if len(arr) != 2:
            raise ValueError("Array must have exactly two elements")
        return Qi(arr[0], arr[1])

    # ---------- Configuration ----------

    @classmethod
    def get_unit_symbol(cls):
        """Forwards to Zi.get_unit_symbol(), the single source of truth
        (see the note by __slots__ above)."""
        return Zi.get_unit_symbol()

    @classmethod
    def set_unit_symbol(cls, symbol):
        """Forwards to Zi.set_unit_symbol(); setting it on either class
        affects both, since they share the same underlying setting."""
        Zi.set_unit_symbol(symbol)

    @classmethod
    def get_max_denominator(cls):
        return cls._max_denominator

    @classmethod
    def set_max_denominator(cls, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("max_denominator must be a positive integer")
        cls._max_denominator = value

    def limit_denominator(self, max_denominator=None):
        """Return a new Qi (or Zi, if both parts become whole numbers)
        with each component approximated by the closest fraction whose
        denominator does not exceed max_denominator (defaults to
        Qi.get_max_denominator())."""
        if max_denominator is None:
            max_denominator = Qi._max_denominator
        return Qi(self.real.limit_denominator(max_denominator),
                   self.imag.limit_denominator(max_denominator))

    # ---------- Number Theory ----------

    @staticmethod
    def _clear_denominator(x):
        """Return (Zi numerator, positive int denominator) such that
        x == numerator / denominator, using the least common denominator
        of x's real and imaginary Fraction parts. Private helper for
        gcd, below."""
        x = Qi._require_qi(x)
        if isinstance(x, Zi):
            return x, 1
        d = lcm(x.real.denominator, x.imag.denominator)
        num = Zi(int(x.real * d), int(x.imag * d))
        return num, d

    @staticmethod
    def gcd(a, b):
        """Greatest common divisor of two Gaussian rationals, generalizing
        the classic rational-number identity
            gcd(p1/q1, p2/q2) == gcd(p1, p2) / lcm(q1, q2)
        to Q(i): clear denominators down to Zi numerators, take Zi.gcd
        of those, and divide by the lcm of the original denominators.
        The defining property -- the one this is tested against -- is
        that a/g and b/g both come out as exact Zi values.

        Like Zi.gcd, the result is only defined up to a unit factor.
        gcd(0, 0) returns 0, matching Zi.gcd's convention.
        """
        na, da = Qi._clear_denominator(a)
        nb, db = Qi._clear_denominator(b)
        g = Zi.gcd(na, nb)
        denom = lcm(da, db)
        return g / Zi(denom, 0)

    @staticmethod
    def congruent_modulo(a, b, c):
        """True iff a is congruent to b modulo c over the Gaussian
        rationals Q(i): i.e., iff (a - b) / c is an exact Gaussian
        integer. This generalizes Zi.congruent_modulo to inputs drawn
        from all of Q(i), not just Z[i] -- and agrees with it exactly
        when a, b, c all happen to be Gaussian integers.

        Raises ZeroDivisionError if c == 0.
        """
        a = Qi._require_qi(a)
        b = Qi._require_qi(b)
        c = Qi._require_qi(c)
        if not c:
            raise ZeroDivisionError("modulus cannot be zero")
        quotient = (a - b) / c
        return isinstance(quotient, Zi)

    @staticmethod
    def crt(residues, moduli):
        """Chinese Remainder Theorem, exposed on Qi purely as an
        input-flexibility convenience over Zi.crt -- it does NOT
        generalize the theorem itself to fractional values.

        Q(i) is a field: it has no proper nonzero ideals, so there's
        no ring Q(i)/(m) for a nonzero m to generalize the classical
        Z[i]/(m) statement to. And it isn't just a matter of finding
        the right formula, either -- unlike congruent_modulo (which
        only ever checks a candidate x someone already has in hand),
        crt *constructs* a solution, and coprime moduli alone stop
        being enough to guarantee one exists once residues are allowed
        to be fractional: e.g. no x satisfies both (x-1/2) in Z[i] and
        (x-1/3) in Z[i], regardless of what moduli those residues are
        paired with, since a single x can't simultaneously have two
        different fractional parts.

        So every residue and modulus passed here must still be
        Gaussian-integer-*valued* -- each argument must itself be, or
        coerce via Qi's usual type handling to, a Zi (so int, complex,
        Fraction, Zi, and integer-valued Qi are all fine; a genuinely
        fractional Qi or Fraction is not). That's the actual
        generalization on offer: passing e.g. Fraction(6, 1) or
        3+0j instead of only a bare Zi. Raises ValueError if any
        residue or modulus is fractional. Everything else -- pairwise
        coprimality, zero moduli, mismatched/empty input -- is
        Zi.crt's to enforce; see its docstring for the algorithm.
        Returns a Zi, same as Zi.crt.
        """
        def _as_zi(x, label, plural):
            v = Qi._require_qi(x)
            if not isinstance(v, Zi):
                raise ValueError(
                    f"Qi.crt requires Gaussian-integer {plural}; "
                    f"got non-integer {label} {x!r}"
                )
            return v

        zi_residues = [_as_zi(r, "residue", "residues") for r in residues]
        zi_moduli = [_as_zi(m, "modulus", "moduli") for m in moduli]
        return Zi.crt(zi_residues, zi_moduli)