#!/usr/bin/env bash

set -e 


if ["$APP_ENV" = dev;] then
    echo "Running API in Development mode"
    exec fastapi run run.py --reload --host 0.0.0.0 --port 8000
else
    echo "Running API in Production mode"
    exec fastapi dev run.py --reload --host 0.0.0.0 --port 8000 
fi





