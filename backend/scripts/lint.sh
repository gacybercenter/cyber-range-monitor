#!/usr/bin/env bash

set -e
set -x

ruff check app
mypy app
ruff format app --check