#!/bin/sh
# Activate the virtual environment
. .venv/bin/activate

# Check if the database exists, and if not, initialize it
if [ ! -f instance/range_monitor.sqlite ]; then
  flask init-db
fi

# Then start your application
exec flask run --host=0.0.0.0 --port=5000