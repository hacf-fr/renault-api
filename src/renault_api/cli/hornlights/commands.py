"""Command-line interface."""

import click

from . import control


@click.group()
def hornlights() -> None:
    """hornlights functionality."""
    pass


hornlights.add_command(control.lights)
hornlights.add_command(control.horn)
