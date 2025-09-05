import click

from adopt.cli.backlog import cli_backlog
from adopt.utils import clear_caches


@click.group()
def cli_root():
    """Root CLI group to hold all subcommands."""
    clear_caches()


# add each subcommand to the root command
cli_root.add_command(cli_backlog)
