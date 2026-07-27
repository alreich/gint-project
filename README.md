# Gaussian Integers and Gaussian Rational Numbers

This module defines two classes, **Zi** and **Qi**, the Gaussian integers and Gaussian rational numbers, respectively.

Mathematically, the set of integers are denoted by $\mathbb{Z}$, the rational numbers by $\mathbb{Q}$, the real numbers by $\mathbb{R}$, and the complex numbers by $\mathbb{C}$.

$\mathbb{C} = \lbrace a + bi: a, b \in \mathbb{R} \rbrace$ where $i^2 = -1$.

The **Gaussian integers** are denoted by $\mathbb{Z}[i] = \lbrace n + mi: n, m \in \mathbb{Z} \rbrace \subset \mathbb{C}$,

and the **Gaussian rationals** are denoted by $\mathbb{Q}[i] = \lbrace r + si: r, s \in \mathbb{Q} \rbrace \subset \mathbb{C}$.

NOTE:

* Zi and Qi both support arithmetic mixed with each other, as well as ints, floats, and complex numbers; including the following operators: `+`, `-`, `*`, `/`, `//`, `**`, `%`, `==`, `!=`, `+=`, `-=`, and `*=`. See the unittests in the tests directory for examples.
* Python uses $j$ instead of $i$ to represent complex numbers, so $j$ is the default *unit symbol* for Zi and Qi, however, that can be switched to $i$ if desired. Again, see the unittests for examples.
* Although, both **Zi** and **Qi** are subclasses of **numbers.Complex**, and $\mathbb{Z}[i] \subset \mathbb{Q}[i] \subset \mathbb{C}$, the class **Zi** is **not** implemented as a subclass of **Qi**.
* Many of the algorithms and examples here are from ["The Gaussian Integers"](https://kconrad.math.uconn.edu/blurbs/ugradnumthy/Zinotes.pdf) by Keith Conrad

Just for run, the following figure is a plot of Gaussian integers, Gaussian primes, and non-Gaussian primes.

![alt text](../gaussian_integers_plot.png)

## Why define Zi?

Why not simply use Python's built-in complex numbers?

The reason is so that **arbitrarily large Gaussian integers can be exactly represented**.

Python's built-in complex type uses two floating point numbers, and Python floats are limited in size, whereas its integers are not.

To see this, consider the following calculation, where a number with a large number of digits is entered as an integer, `n`, and as a float, `f`, and observe how $(f + 1) - f$ produces an incorrect result, where as $(n + 1) - n$ produces the correct result.


```python
n = 11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
f = 11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111.0

print(f"{n = }")
print(f"\n{f = }")

print(f"\n{(n + 1) - n = }")
print(f"{(f + 1) - f = }")
```

    n = 11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    
    f = 1.111111111111111e+175
    
    (n + 1) - n = 1
    (f + 1) - f = 0.0


## Zi and Qi Examples

The Python module ``gint`` contains two classes, Zi and Qi, which represent a Gaussian integer and a Gaussian rational, respectively.

It is recommended that both Zi & Qi be imported, because some operations on Gaussian integers result in Gaussian rationals (such as true division of Zi's), and vice versa (such as Qi's with integer components).


```python
>>> from gint import Zi, Qi
```

### Zi Construction

The string representation of a Zi will be its equivalent complex or integer value in string form.

A Zi can be created from two integers or floats (floats are rounded) or a single complex number.


```python
>>> z     = Zi(2, -3); print(f"{    z = } == {z}")
>>> zero  = Zi()     ; print(f"{ zero = }  == {zero}")
>>> one   = Zi(1)    ; print(f"{  one = }  == {one}")
>>> two   = Zi.two() ; print(f"{  two = }  == {two}")  # norm = 2
>>> i     = Zi.eye() ; print(f"{    i = }  == {i}")
>>> a     = Zi(2-3j) ; print(f"{    a = } == {a}")
>>> b     = Zi(-2.8, 5.2); print(f"{    b = } == {b}")
>>> c     = Zi('2-3j') ; print(f"    c = Zi({str(c)[1:-1]!r}) == {c}")
>>> d     = Zi('(2-3j)') ; print(f"    d = Zi({str(d)!r}) == {d}")
>>> e     = Zi('5') ; print(f"    e = Zi({str(e)!r}) == {e}")
>>> units = Zi.units() ; print(f"{units = } == {list(map(str, units))}")
```

        z = Zi(2, -3) == (2-3j)
     zero = Zi(0, 0)  == 0
      one = Zi(1, 0)  == 1
      two = Zi(1, 1)  == (1+1j)
        i = Zi(0, 1)  == 1j
        a = Zi(2, -3) == (2-3j)
        b = Zi(-3, 5) == (-3+5j)
        c = Zi('2-3j') == (2-3j)
        d = Zi('(2-3j)') == (2-3j)
        e = Zi('5') == 5
    units = [Zi(1, 0), Zi(-1, 0), Zi(0, 1), Zi(0, -1)] == ['1', '-1', '1j', '-1j']


## Qi Construction


```python
>>> q    = Qi(2.4, 3.25)      ; print(f"{    q = } == {q}")
>>> r    = Qi('12/5', '13/4') ; print(f"{    r = } == {r}")
>>> s    = Qi('24/10', '26/8'); print(f"{    s = } == {s}")  # fractions are reduced to simplest form

>>> t     = Qi('12/5+13/4j') ; print(f"    t = Qi( {str(t)[1:-1]!r} ) == {t}")
>>> u     = Qi('(12/5+13/4j)') ; print(f"    u = Qi({str(u)!r}) == {u}")


>>> zero = Qi()     ; print(f"{ zero = } == {zero}")  # Given integer values, a Qi "collapses" into a Zi:
>>> one  = Qi(1)    ; print(f"{  one = } == {one}")
>>> i    = Qi(0, 1) ; print(f"{    i = } == {i}")
```

        q = Qi('12/5', '13/4') == (12/5+13/4j)
        r = Qi('12/5', '13/4') == (12/5+13/4j)
        s = Qi('12/5', '13/4') == (12/5+13/4j)
        t = Qi( '12/5+13/4j' ) == (12/5+13/4j)
        u = Qi('(12/5+13/4j)') == (12/5+13/4j)
     zero = Zi(0, 0) == 0
      one = Zi(1, 0) == 1
        i = Zi(0, 1) == 1j


## Properties of Gaussian Integers

The usual properties of complex numbers are also supported for Gaussian integers:

* real part
* imaginary part
* norm

### Examples


```python
>>> print(f"{z = }")

>>> print(f"{z.real = }")
>>> print(f"{z.imag = }")
>>> print(f"{z.norm = }")
>>> print(f"{z.is_unit = }")
```

    z = Zi(2, -3)
    z.real = 2
    z.imag = -3
    z.norm = 13
    z.is_unit = False


## Functions of Gaussian Integers

The following operations can be performed on a Gaussian integer:

* conjugate
* compute absolute value
* convert to string
* convert to standard Python complex number
* negate

### Examples


```python
>>> print(f"{z = }")

>>> print(f"{z.conjugate() = }")
>>> print(f"{abs(z) = }")
>>> print(f"{str(z) = }")
>>> print(f"{complex(z) = }")
>>> print(f"{-z = }")
```

    z = Zi(2, -3)
    z.conjugate() = Zi(2, 3)
    abs(z) = 3.605551275463989
    str(z) = '(2-3j)'
    complex(z) = (2-3j)
    -z = Zi(-2, 3)


## Arithmetic

Most of the usual arithmetic operations that can be performed on complex number are supported, such as infix operators and in-place assignment operators.

Additionally, the arithmetic of Gaussian integers can be mixed with standard Python numbers (integers, floats, complex).

### Examples

The following infix operators are supported: ``+``, ``-``, ``*``, ``**``, ``/``, ``//``, ``%``


```python
a * Zi(2.9)**-1
```




    Qi('2/3', '-1')




```python
>>> a = Zi(6, 12)
>>> # b = Zi(1, -2)
>>> b = 2.9
>>> c = a * b

>>> print(f"{a = }, {b = }, a * b = {c = }\n")

>>> print(f"{a + b = }")
>>> print(f"{a - b = }")
>>> print(f"{a * b = }")
>>> print(f"{a / b = }")  # In general, truediv will return a Gaussian rational,
>>> print(f"{c / b = }")  #     unless b | c, in which case, a Zi is returned.
>>> print(f"{a // b = }")  # floordiv uses round instead of floor.
>>> print(f"{c % b = }")
>>> print(f"{a**2 = }")
>>> print(f"{a**0 = }")
>>> print(f"{a**-1 = }")  # This will yield a Gaussian rational, except for units
>>> print(f"{i**-1 = }")  # 1/i = -i
```

    a = Zi(6, 12), b = 2.9, a * b = c = Zi(18, 36)
    
    a + b = Zi(9, 12)
    a - b = Zi(3, 12)
    a * b = Zi(18, 36)
    a / b = Zi(2, 4)
    c / b = Zi(6, 12)
    a // b = Zi(2, 4)
    c % b = Zi(0, 0)
    a**2 = Zi(-108, 144)
    a**0 = Zi(1, 0)
    a**-1 = Qi('1/30', '-1/15')
    i**-1 = Zi(0, -1)


Mixed integer and Gaussian integer arithmetic is supported.


```python
>>> w = 2.0; print(f"{w = }")
>>> print(f"{a = }\n")

>>> print(f"{a + w = }")
>>> print(f"{a - w = }")
>>> print(f"{a * w = }")
>>> print(f"{a / w = }\n")

>>> print(f"{w + a = }")
>>> print(f"{w - a = }")
>>> print(f"{w * a = }")
>>> print(f"{w / a = }")
```

    w = 2.0
    a = Zi(6, 12)
    
    a + w = Zi(8, 12)
    a - w = Zi(4, 12)
    a * w = Zi(12, 24)
    a / w = Zi(3, 6)
    
    w + a = Zi(8, 12)
    w - a = Zi(-4, -12)
    w * a = Zi(12, 24)
    w / a = Qi('1/15', '-2/15')


Mixed float point and Gaussian integer arithmetic is supported. Floats are rounded before being used.


```python
>>> print(f"{a = }\n")

>>> print(f"{a + 2.1 = }")
>>> print(f"{a - 2.1 = }")
>>> print(f"{a * 2.1 = }")
>>> print(f"{a / 2.1 = }\n")

>>> print(f"{2.1 + a = }")
>>> print(f"{2.1 - a = }")
>>> print(f"{2.1 * a = }")
>>> print(f"{2.1 / a = }")
```

    a = Zi(6, 12)
    
    a + 2.1 = Zi(8, 12)
    a - 2.1 = Zi(4, 12)
    a * 2.1 = Zi(12, 24)
    a / 2.1 = Zi(3, 6)
    
    2.1 + a = Zi(8, 12)
    2.1 - a = Zi(-4, -12)
    2.1 * a = Zi(12, 24)
    2.1 / a = Qi('1/15', '-2/15')


Mixed complex number and Gaussian integer arithmetic is supported. Floats are rounded before being used.


```python
>>> print(f"{a = }")
>>> d = 1.1-3.9j; print(f"{d = }")
>>> d_rounded = Zi(d)  # Zi rounds floating point and complex values
>>> print(f"{d_rounded = }\n")

>>> print(f"{a + d = }")
>>> print(f"{a - d = }")
>>> print(f"{a * d = }")
>>> print(f"{a / d = }\n")

>>> print(f"{d + a = }")
>>> print(f"{d - a = }")
>>> print(f"{d * a = }")
>>> print(f"{d / a = }")
```

    a = Zi(6, 12)
    d = (1.1-3.9j)
    d_rounded = Zi(1, -4)
    
    a + d = Zi(7, 8)
    a - d = Zi(5, 16)
    a * d = Zi(54, -12)
    a / d = Qi('-42/17', '36/17')
    
    d + a = Zi(7, 8)
    d - a = Zi(-5, -16)
    d * a = Zi(54, -12)
    d / a = Qi('-7/30', '-1/5')



```python
>>> e = 1-4j

>>> print(f"{a + e = }")
>>> print(f"{a - e = }")
>>> print(f"{a * e = }")
>>> print(f"{a / e = }\n")

>>> print(f"{e + a = }")
>>> print(f"{e - a = }")
>>> print(f"{e * a = }")
>>> print(f"{e / a = }")
```

    a + e = Zi(7, 8)
    a - e = Zi(5, 16)
    a * e = Zi(54, -12)
    a / e = Qi('-42/17', '36/17')
    
    e + a = Zi(7, 8)
    e - a = Zi(-5, -16)
    e * a = Zi(54, -12)
    e / a = Qi('-7/30', '-1/5')


In-place assignment operators, ``+=``, ``-=``, and ``*=`` are also supported.

Here's an example that uses ``+=``:


```python
>>> zi_sum = Zi()
>>> int_sum = 0

>>> for k in range(5):
>>>     int_sum += k
>>>     zi_sum  += Zi(k, k)

>>> print(int_sum, zi_sum)
```

    10 (10+10j)


## Number Theory with Gaussian Integers

Many of the algorithms and examples, below, are from ["The Gaussian Integers"](https://kconrad.math.uconn.edu/blurbs/ugradnumthy/Zinotes.pdf) by Keith Conrad

### The Modified Division Theorem

For $\alpha, \beta \in \mathbb{Z}[i]$ with $\beta \ne 0$, there are $\gamma, \rho \in \mathbb{Z}[i]$ such that $\alpha = \beta \gamma + \rho$ and $N(\rho) \le (1/2)N(\beta)$.


```python
>>> help(Zi.modified_divmod)
```

    Help on function modified_divmod in module gint.zi:
    
    modified_divmod(a, b)
        Divide a by b, rounding the quotient to the nearest Gaussian
        integer (rather than truncating), so that the remainder has
        strictly smaller norm than b. Returns q & r, such that
        a = b * q + r. This is what makes gcd/xgcd below terminate
        correctly, since Z[i] is a Euclidean domain under the norm
        only when division rounds to nearest.
    


**Example**


```python
>>> alpha = Zi(27, -23)
>>> beta = Zi(8, 1)

>>> gamma, rho = Zi.modified_divmod(alpha, beta)

>>> print(f"{beta * gamma + rho} = {beta} * {gamma} + {rho}")

>>> print(f"\nN({rho}) = {rho.norm} and (1/2)*N({beta}) = {(1/2) * beta.norm}")
```

    (27-23j) = (8+1j) * (3-3j) + -2j
    
    N(-2j) = 4 and (1/2)*N((8+1j)) = 32.5


### Greatest Common Divisor (GCD)

**The Euclidean Algorithm**

Let $\alpha, \beta \in \mathbb{Z}[i]$ be non-zero, then we can recursively apply the Division Theorem to obtain the Greatest Common Divisor (GCD) of $\alpha$ and $\beta$.


```python
>>> help(Zi.gcd)
```

    Help on function gcd in module gint.zi:
    
    gcd(a, b)
        A gcd algorithm for Gaussian integers.
        Returns the greatest common divisor of a & b.
    
        This function implements the Euclidean algorithm for Gaussian integers.
    


**Example**


```python
>>> alpha = Zi(11, 3)
>>> beta = Zi(1, 8)

>>> gcd = Zi.gcd(alpha, beta)  # Prints intermediate results

>>> print(f"\ngcd({alpha}, {beta}) -> {gcd}")
```

    
    gcd((11+3j), (1+8j)) -> (1-2j)


### The Extended Euclidean Algorithm (xGCD)

**Bezout's Theorem**

Let $\delta$ be the GCD of $\alpha, \beta \in \mathbb{Z}[i]$, then $\delta = \alpha x + \beta y$ for some $x, y \in \mathbb{Z}[i]$.


```python
>>> help(Zi.xgcd)
```

    Help on function xgcd in module gint.zi:
    
    xgcd(a, b)
        Extended Euclidean algorithm. Returns (g, s, t) such that
        a*s + b*t == g == gcd(a, b) (up to a unit factor).
    


**Example**


```python
>>> delta, x, y = Zi.xgcd(alpha, beta)  # Use alpha & beta from above

>>> print(f"alpha = {alpha} and beta = {beta}")
>>> print(f"delta = {delta}, x = {x}, and y = {y}\n")
>>> print(f"==> {alpha * x  + beta * y} = {alpha} * {x} + {beta} * {y}")

>>> print(f"\n  Note: gcd({alpha},{beta}) = {Zi.gcd(alpha, beta)}")
```

    alpha = (11+3j) and beta = (1+8j)
    delta = (1-2j), x = (2-1j), and y = 3j
    
    ==> (1-2j) = (11+3j) * (2-1j) + (1+8j) * 3j
    
      Note: gcd((11+3j),(1+8j)) = (1-2j)


### True Division

Let $\alpha, \beta \in \mathbb{Z}[i]$. If $\beta \mid \alpha$ then $\alpha / \beta \in \mathbb{Z}[i]$, otherwise $\alpha / \beta \in \mathbb{Q}[i]$

**Examples**


```python
>>> alpha = Zi(4, 5)
>>> beta = Zi(1, -2)

>>> print(f"{alpha / beta = }\n")
>>> print(f"{alpha} / {beta} -> {alpha / beta}")
```

    alpha / beta = Qi('-6/5', '13/5')
    
    (4+5j) / (1-2j) -> (-6/5+13/5j)



```python
>>> (-6/5+13/5j)
```




    (-1.2-2.6j)



### Congruence Modulo

Let $\alpha, \beta, \gamma \in \mathbb{Z}[i]$. If $\gamma \ \vert \ (\alpha - \beta)$, then we say that "$\alpha$ is congruent to $\beta$ modulo $\gamma$", written as $\alpha \equiv \beta \text{ mod } \gamma$.


```python
>>> help(Zi.congruent_modulo)
```

    Help on function congruent_modulo in module gint.zi:
    
    congruent_modulo(a, b, c)
        True iff a is congruent to b modulo c, i.e., iff c divides (a - b).
        Raises ZeroDivisionError if c == Zi(0, 0), via the underlying %
        operator (same behavior as gcd/xgcd on a zero modulus).
    


**Examples**


```python
>>> alpha = Zi(1, 12)
>>> beta = Zi(2, -1)
>>> gamma = Zi(3, 1)

>>> print(f"Test Value: ({alpha} - {beta} / {gamma} -> {(alpha - beta) / gamma}\n")

>>> test = Zi.congruent_modulo(alpha, beta, gamma)

>>> print(f"test = {test}")
```

    Test Value: ((1+12j) - (2-1j) / (3+1j) -> (1+4j)
    
    test = True


An example of non-congruence:


```python
>>> delta = Zi(3, 2)
>>> test = Zi.congruent_modulo(alpha, beta, delta)
>>> print(f"test = {test} is not a Zi")
```

    test = False is not a Zi


### Relatively Prime

Let $\alpha, \beta \in \mathbb{Z}[i]$. If the only factors $\alpha$ and $\beta$ have in common are units (i.e., $1, -1, i, -i$) then they are called *relatively prime*.
>>> help(Zi.is_relatively_prime)
**Examples**
>>> alpha = Zi(4, 5)
>>> alpha_conj  = alpha.conjugate

>>> Zi.is_relatively_prime(alpha, alpha_conj)>>> alpha = Zi(11, 3)
>>> beta = Zi(1, 8)

>>> Zi.is_relatively_prime(alpha, beta)
### Gaussian Primes

See [this link for a definition](https://en.wikipedia.org/wiki/Gaussian_integer#Gaussian_primes) of a Gaussian prime, and see [this link for the algorithm](https://mathworld.wolfram.com/GaussianPrime.html) used here to determine whether a Gaussian integer is prime or not.


```python
>>> help(Zi.is_gaussian_prime)
```

    Help on function is_gaussian_prime in module gint.zi:
    
    is_gaussian_prime(x)
        A Gaussian integer a+bi is prime iff:
    
        - both a,b are nonzero and a^2+b^2 is a rational prime, or
        - one of a,b is zero and the other has absolute value c, where c is
          a rational prime with c % 4 == 3 (primes p == 2 or p == 1 mod 4
          are NOT Gaussian primes: 2 ramifies as -i(1+i)^2, and p == 1 mod 4
          splits into two conjugate Gaussian primes).
    


**Examples**


```python
>>> gints = [alpha, beta, gamma, Zi(2, 0), Zi(3, 0), Zi(5, 0), Zi(7, 0), Zi(0, 2), Zi(0, 3)]

>>> for gi in gints:
>>>     print(f"Is {gi} a Gaussian prime? {Zi.is_gaussian_prime(gi)}")
```

    Is (1+12j) a Gaussian prime? False
    Is (2-1j) a Gaussian prime? True
    Is (3+1j) a Gaussian prime? False
    Is 2 a Gaussian prime? False
    Is 3 a Gaussian prime? True
    Is 5 a Gaussian prime? False
    Is 7 a Gaussian prime? True
    Is 2j a Gaussian prime? False
    Is 3j a Gaussian prime? True


## Miscellaneous

In addition, the following methods are supported. See the respective doc strings for more information.

* **random** -- Returns a random Gaussian integer
* **associates** -- Returns the three associates of a given Gaussian integer
* **is_associate** -- Returns True if two Gaussian integers are associates
* **to_gaussian_rational** -- Converts a Gaussian integer to an equivalent Gaussian rational
* **norms_divide** -- Returns True if one of two Gaussian integers evenly divides the other
* **from_array** -- Returns a Gaussian integer constructed from a two-element array

## Gaussian Rationals

The implementation of the class of Gaussian rationals, ``Qi``, has constructors, accessors, and arithmetic that is similar to those of the class of Gaussian integers, ``Zi``.

So, only the additions and differences are documented below.

The class ``Qi`` is implemented as a pair of [fractions.Fraction](https://docs.python.org/3/library/fractions.html).


```python
>>> r = Qi(2, 3.4)
>>> s = Qi("4/6", "-1/7")

>>> print(f"{r = }")
>>> print(f"{s = }")
```

    r = Qi('2', '17/5')
    s = Qi('2/3', '-1/7')


### Inverses


```python
>>> r_inv = r.inverse()

>>> print(f"{r_inv = }")
```

    r_inv = Qi('50/389', '-85/389')



```python
>>> print(f"{r * r_inv = } = {r * r_inv}")
```

    r * r_inv = Zi(1, 0) = 1


### String to Rational

The static method, ``Qi.string_to_rational``, parses a valid Gaussian rational string and returns the cooresponding ``Qi`` instance.


```python
>>> str(Qi('1/2', '-3/5'))
```




    '(1/2-3/5j)'




```python
>>> Qi('(1/2-3/5j)')
```




    Qi('1/2', '-3/5')


