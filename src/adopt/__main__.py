import logging

from dotenv import find_dotenv, load_dotenv

from adopt.cli import cli_root
from adopt.cli.backlog import cli_backlog

# TODO: separate tokens in env and other settings in config file
load_dotenv(dotenv_path=find_dotenv(usecwd=True))


LOGGER = logging.getLogger(__name__)


def main():
    cli_root.add_command(cli_backlog)
    cli_root()


if __name__ == '__main__':
    main()
