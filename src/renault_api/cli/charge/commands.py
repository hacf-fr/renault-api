"""Command-line interface."""
import click

from . import control
from . import history
from . import schedule


@click.group()
def charge() -> None:
    """Charge functionality."""
    pass


charge.add_command(control.start)
charge.add_command(control.stop)
charge.add_command(control.mode)
charge.add_command(history.history)
charge.add_command(history.sessions)
charge.add_command(schedule.schedule)
