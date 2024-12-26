ifeq ($(OS), Windows_NT)
	MAKE_OS := Windows
else
	MAKE_OS := Linux
endif

PYTHON_VERSION = 3.11
VENV_NAME = .venv
DOCKER_TAG = adopt

BUILD_DIR = ./_build
BUILD_WHEEL_DIR = $(BUILD_DIR)/wheel
BUILD_TEST_DIR = $(BUILD_DIR)/test

ifeq ($(MAKE_OS), Windows)
	CREATE_ENV_CMD=py -$(PYTHON_VERSION) -m venv $(VENV_NAME)
	PYTHON=$(VENV_NAME)\Scripts\python
	ACTIVATE=$(VENV_NAME)\Scripts\activate
else
	CREATE_ENV_CMD=python$(PYTHON_VERSION) -m venv $(VENV_NAME)
	PYTHON=$(VENV_NAME)/bin/python
	ACTIVATE=source $(VENV_NAME)/bin/activate
endif

RUN_MODULE = $(PYTHON) -m
PIP = $(RUN_MODULE) pip

install: create-env install-project install-pre-commit

create-env:
	$(info MAKE: Initializing environment in .venv ...)
	$(CREATE_ENV_CMD)
	$(PIP) install --upgrade "pip>=24" wheel

install-project:
	$(info MAKE: Installing project ...)
	$(PIP) install -e .[dev] --config-settings editable_mode=compat

test:
	$(info MAKE: Running tests ...)
	$(PYTHON) -m pytest tests --junitxml=$(BUILD_TEST_DIR)/test-results.xml --cov=src --cov-report=xml:$(BUILD_TEST_DIR)/coverage.xml --cov-report=html:$(BUILD_TEST_DIR)/htmlcov

install-pre-commit:
	$(info MAKE: Installing pre-commit hooks...)
	$(RUN_MODULE) pre_commit install

pre-commit:
	$(info MAKE: Pre-commit hooks check over all files...)
	$(RUN_MODULE) pre_commit run --all-files

build-wheels:
	$(PYTHON) -m build . --outdir $(BUILD_WHEEL_DIR)

build-docker:
	docker build -t $(DOCKER_TAG) .

run-app:
	$(PYTHON) app/app.py

run-docker:
	docker run -p 8501:8501 $(DOCKER_TAG)

