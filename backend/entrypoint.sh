#!/usr/bin/env sh

set -euo pipefail

echo "[entrypoint] starting app container."


for f in /run/secrets/jwt_private_key /run/secrets/jwt_public_key /run/secrets/csrf_secret; do
  [ ! -f "$f" ] && {
    echo "[entrypoint] ERROR: Missing required secret $f, run 'make keys'" >&2
    exit 1
  }
done

if [ "${APP_ENV:-dev}" = "dev" ]; then
  echo "[entrypoint] Launching in development mode"
  exec fastapi dev --host 0.0.0.0 server/run.py
else
  echo "[entrypoint] Launching in production mode"
  exec fastapi run --host 0.0.0.0 --workers "${WEB_CONCURRENCY:-4}" server/run.py
fi
