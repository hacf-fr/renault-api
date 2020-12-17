"""Command-line interface."""
import click

from . import control
from . import history


@click.group()
def hvac() -> None:
    """HVAC functionality."""
    pass


hvac.add_command(control.start)
hvac.add_command(control.cancel)
hvac.add_command(history.history)
hvac.add_command(history.sessions)
