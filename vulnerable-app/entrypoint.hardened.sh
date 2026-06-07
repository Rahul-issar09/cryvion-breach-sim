#!/bin/sh
# Load the DB password from the mounted Docker secret (no plaintext in env/files).
set -e
if [ -f /run/secrets/db_password ]; then
  MYSQL_PASSWORD="$(cat /run/secrets/db_password)"
  export MYSQL_PASSWORD
fi
exec "$@"
