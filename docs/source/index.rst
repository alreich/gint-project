gint: Gaussian Integers and Rationals
======================================

**gint** provides two related numeric types:

- :class:`~gint.zi.Zi` -- Gaussian integers, :math:`a + bi` with :math:`a, b \in \mathbb{Z}`.
- :class:`~gint.qi.Qi` -- Gaussian rationals, :math:`a + bi` with :math:`a, b \in \mathbb{Q}`,
  represented exactly via :class:`fractions.Fraction`.

A ``Qi`` whose components both reduce to whole numbers is automatically
returned as a ``Zi`` instead -- ``Qi(4, 6)`` *is* a ``Zi(4, 6)``.

Quickstart
----------

.. code-block:: python

    >>> from gint import Zi, Qi
    >>>
    >>> z1, z2, z3 = Zi(2, -3), Zi(1, 4), Zi(-8, 1)
    >>> z1         # ==> Zi(2, -3)
    >>> print(z1)  # ==> (2-3j)
    >>> z12 = z1 * z2
    >>> z12        # ==> Zi(14, 5)
    >>> z12 / z1   # ==> aZi(1, 4)
    >>> z12 / z3   # ==> Qi('-107/65', '-54/65')
    >>> (z12 / z3) * z3  # ==> Zi(14, 5)
    >>> 1 / Zi(1, 1)     # ==> Qi('1/2', '-1/2')
    >>> Zi(1, 1)**-1     # ==> Qi('1/2', '-1/2')
    >>> Zi.gcd(z12, z1)  # ==> Zi(2, -3)
    >>> Zi.lcm(z12, z1)  # ==> Zi(14, 5)
    >>> Qi(1.25, 3.4)    # ==> Qi('5/4', '17/5')
    >>> print(Zi(5, 0))  # ==> 5
    >>>
    >>> from gint.crypto import generate_keypair, encrypt_text, decrypt_text
    >>>
    >>> public_key, private_key = generate_keypair(bits=256)
    >>> ciphertext = encrypt_text("Gaussian primes are cool.", public_key)
    >>> decrypt_text(ciphertext, private_key)  # ==> 'Gaussian primes are cool.'

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   zi
   qi
   crypto
