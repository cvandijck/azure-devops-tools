import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from adopt.env import PAT_ENV, PROJECT_ENV, TEAM_ENV, URL_ENV

TEST_DIR = Path(__file__).parent
PROJECT_DIR = TEST_DIR.parent
TEST_ENV_FILE = PROJECT_DIR / '.test_env'

__all__ = ['url', 'token', 'project', 'team']


@pytest.fixture(scope='session', autouse=True)
def load_test_env():
    load_dotenv(dotenv_path=TEST_ENV_FILE)


@pytest.fixture(scope='session')
def url(load_test_env):
    return os.environ[URL_ENV]


@pytest.fixture(scope='session')
def token(load_test_env):
    return os.environ[PAT_ENV]


@pytest.fixture(scope='session')
def project(load_test_env):
    return os.environ[PROJECT_ENV]


@pytest.fixture(scope='session')
def team(load_test_env):
    return os.environ[TEAM_ENV]
