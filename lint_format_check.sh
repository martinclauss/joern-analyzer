#!/usr/bin/env bash

black .
ruff check --fix .
bandit -r .
mypy --install-types; mypy .
semgrep --config=p/python --verbose .