import os
import subprocess
import sys

import pytest

from adopt.connect import create_connection
from adopt.env import PAT_ENV, URL_ENV

PYTHON_EXE = sys.executable


def test_connect():
    url = os.getenv(URL_ENV)
    token = os.getenv(PAT_ENV)
    create_connection(organization_url=url, token_password=token)
    # TODO: do better testing on connection


def test_import_package():
    """Test basic import of package."""
    import adopt  # noqa: F401


@pytest.mark.console
def test_console_help():
    """Calls help file of console script and tests for failure."""
    process = subprocess.run([PYTHON_EXE, '-m', 'adopt', '--help'], capture_output=True, universal_newlines=True)
    assert process.returncode == 0, process.stderr
