"""Sphinx configuration for gint's documentation."""

import os
import sys

# Make the package importable without installing it, so autodoc can find
# it even in a bare checkout: docs/source/conf.py -> ../../src
sys.path.insert(0, os.path.abspath("../../src"))

project = "gint"
copyright = "2026, Al"
author = "Al"

from gint import __version__ as release  # noqa: E402
version = release

extensions = [
    "sphinx.ext.autodoc",       # pull docs from docstrings
    "sphinx.ext.napoleon",      # Google/NumPy-style docstring support
    "sphinx.ext.viewcode",      # "view source" links next to each entry
    "sphinx.ext.mathjax",       # render LaTeX math in docstrings
    "sphinx.ext.intersphinx",   # link out to Python's own docs
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "special-members": "__init__, __add__, __sub__, __mul__, __truediv__, __floordiv__",
    "show-inheritance": True,
}
autodoc_member_order = "bysource"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
