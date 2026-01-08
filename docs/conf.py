"""Sphinx configuration."""

from datetime import datetime

project = "Renault API"
author = "HACF (created and maintained by @epenet)"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
