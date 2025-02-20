import logging

from adopt.cli import cli_root
from adopt.cli.backlog import cli_backlog
from adopt.config import initialize_configuration

LOGGER = logging.getLogger(__name__)


def main():
    initialize_configuration()
    cli_root.add_command(cli_backlog)
    cli_root()


if __name__ == '__main__':
    main()
