#!/usr/bin/env bash

set -ex

ruff check app
mypy app
ruff format app --check