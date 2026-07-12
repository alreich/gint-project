"""gint: Gaussian integers (Zi) and Gaussian rationals (Qi).

    >>> from gint import Zi, Qi
    >>> Zi(1, 2) * Zi(3, 4)
    Zi(-5, 10)
    >>> Zi(1, 0) / Zi(1, 1)
    Qi('1/2', '-1/2')

Zi represent a Gaussian integer and Qi represents a Gaussian rational
(a complex number with rational real and imaginary components).
A Qi ransparently collapses to a Zi whenever both components are whole
numbers, e.g. Qi(4, 6) is a Zi(4, 6).
"""

from .zi import Zi
from .qi import Qi

__all__ = ["Zi", "Qi"]

__version__ = "0.1.0"
