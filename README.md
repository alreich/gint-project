# gint

Gaussian integers (`Zi`) and Gaussian rationals (`Qi`) for Python.

```python
from gint import Zi, Qi

Zi(1, 2) * Zi(3, 4)      # Zi(-5, 10)
Zi(1, 0) / Zi(1, 1)      # Qi('1/2', '-1/2') -- exact division
Zi.gcd(Zi(4, 2), Zi(1, 1))
Qi(2, 3.4)                # Qi('2', '17/5')
```

`Qi` values whose components both reduce to whole numbers collapse
automatically into a `Zi` -- `Qi(4, 6)` *is* a `Zi(4, 6)`.

## Install (editable, for development)

```bash
pip install -e ".[test,docs]"
```

## Test

```bash
pytest
```

## Docs

Full API documentation: https://gint.readthedocs.io

Build locally:

```bash
sphinx-build -b html docs/source docs/_build/html
```
