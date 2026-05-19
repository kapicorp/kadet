all: clean package

.PHONY: install
install:
	@echo ----- Installing dependencies with uv -----
	uv sync

.PHONY: test
test:
	@echo ----- Running python tests -----
	uv run python -m unittest discover

.PHONY: test_coverage
test_coverage:
	@echo ----- Testing code coverage -----
	uv run coverage run --source=kadet -m unittest discover
	uv run coverage report --fail-under=65 -m

.PHONY: test_formatting
test_formatting:
	@echo ----- Testing code formatting -----
	uv run ruff format --check .
	uv run ruff check .
	@echo

.PHONY: format_codestyle
format_codestyle:
	uv run ruff format .
	uv run ruff check --fix .
	@echo

.PHONY: build
build:
	@echo ----- Building package -----
	uv build

.PHONY: clean
clean:
	rm -rf dist build *.egg-info
