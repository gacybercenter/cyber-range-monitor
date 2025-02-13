#!/bin/bash/


if [ ! -d "instance" ]; then
    mkdir instance
fi

exec python3 -m scripts.prod_env
exec python3 -m scripts.seed_db

exec fastapi run app