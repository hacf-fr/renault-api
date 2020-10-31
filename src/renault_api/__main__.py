"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Renault API."""


if __name__ == "__main__":
    main(prog_name="renault-api")  # pragma: no cover
