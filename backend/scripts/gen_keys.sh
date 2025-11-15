#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
********************
scripts/gen_keys.sh
*********************

Usage: $0 [--kid KID] [--force]

Env:
  SECRETS_DIR   secrets directory (default: secrets)
  ENV_FILE      .env file to write JWT_KID if missing (default: .env)
  BITS          RSA key size (default: 2048)

Behavior:
  - Generates RSA private/public keys: \$SECRETS_DIR/jwt_private_key, jwt_public_key
  - Generates CSRF secret: \$SECRETS_DIR/csrf_secret
  - Computes KID from public key if not provided

Options:
  --kid KID     provide a specific key id instead of deriving
  --force       overwrite existing files
  -h, --help    show help
EOF
}


readonly SECRETS_DIR="${SECRETS_DIR:-secrets}"
readonly ENV_FILE="${ENV_FILE:-.env}"
readonly BITS="${BITS:-2048}"
readonly FORCE=0
KID=""


while [[ $# -gt 0 ]]; do
  case "$1" in
    --kid)
      KID="${2:-}";
      shift 2 ;;

    --force)
      FORCE=1;
      shift ;;

    -h|--help)
      usage;
      exit 0 ;;

    *)
      echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
done

mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"

JWT_PRIV="$SECRETS_DIR/jwt_private_key"
JWT_PUB="$SECRETS_DIR/jwt_public_key"
FERNET_KEY="$SECRETS_DIR/fernet_key"
PBKDF2_SALT="$SECRETS_DIR/pbkdf2_salt"

create_if_missing() {
  local path="$1"
  shift
  if [[ -f "$path" && $FORCE -eq 0 ]]; then
    echo "[skip] $path exists"
  else
    "$@"
    echo "[ok] wrote $path"
  fi
}


create_if_missing "$JWT_PRIV" bash -c "openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:${BITS} -out '$JWT_PRIV' && chmod 600 '$JWT_PRIV'"
create_if_missing "$JWT_PUB" bash -c "openssl rsa -in '$JWT_PRIV' -pubout -out '$JWT_PUB'"
create_if_missing "$FERNET_KEY" bash -c "openssl rand 32 | openssl base64 -A | tr '+/' '-_' | tr -d '=' > '$FERNET_KEY' && chmod 600 '$FERNET_KEY'"
create_if_missing "$PBKDF2_SALT" bash -c "openssl rand -hex 16 > '$PBKDF2_SALT' && chmod 600 '$PBKDF2_SALT'"

if [[ -z "$KID" ]]; then
  KID="$(openssl rsa -pubin -in "$JWT_PUB" 2>/dev/null \
    | openssl dgst -sha256 -binary \
    | base64 | tr '+/' '-_' | tr -d '=' | cut -c1-16)"
fi

touch "$ENV_FILE"
if ! grep -q '^JWT_KID=' "$ENV_FILE"; then
  printf 'JWT_KID=%s\n' "$KID" >> "$ENV_FILE"
  echo "[ok] appended JWT_KID=$KID to $ENV_FILE"
else
  echo "[skip] JWT_KID already set in $ENV_FILE"
fi

echo "kid=$KID"
