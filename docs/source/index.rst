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

    from gint import Zi, Qi

    z = Zi(1, 2) * Zi(3, 4)        # Zi(-5, 10)
    q = Zi(1, 0) / Zi(1, 1)        # Qi('1/2', '-1/2'), exact division
    g = Zi.gcd(Zi(4, 2), Zi(1, 1)) # Gaussian-integer gcd

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   zi
   qi
   crypto
