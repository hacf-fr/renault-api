"""Sphinx configuration."""
from datetime import datetime


project = "Renault API"
author = "epenet"
copyright = f"{datetime.now().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "furo",
]
autodoc_typehints = "description"
html_theme = "furo"
