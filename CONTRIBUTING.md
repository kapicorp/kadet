# Contributing to kadet

Thanks for contributing! kadet is a small library, so the workflow is light.

## Development setup

kadet uses [uv](https://docs.astral.sh/uv/) for dependency management and
[ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```sh
make install            # uv sync
uv run pre-commit install   # optional: run hooks on every commit
```

## Common commands

```sh
make test            # run the test suite
make test_coverage   # run tests with coverage (fails under 65%)
make test_formatting # check ruff format + lint
make format_codestyle# auto-format and auto-fix lint
```

Run a single test:

```sh
uv run python -m unittest tests.test_kadet.KadetTest.test_parse_kwargs
```

## Before opening a pull request

1. Add or update tests for your change.
2. Run `make test` and `make test_formatting` — both must pass.
3. Keep changes focused; avoid mixing unrelated refactors.
4. Match the existing code style.

## Reporting bugs

Open an issue using the bug report template. Include the kadet version, Python
version, and a minimal reproduction.

## Security

For security issues, do not open a public issue. See [SECURITY.md](SECURITY.md).
