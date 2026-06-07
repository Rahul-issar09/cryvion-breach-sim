#!/bin/bash
# Stage 1 — Reconnaissance (MITRE T1595 Active Scanning)
source "$(dirname "$0")/lib.sh"
banner "STAGE 1 — RECON (T1595)"

log "nmap service scan of $TARGET_HOST ..."
nmap -Pn -sV -T4 --top-ports 50 "$TARGET_HOST" | tee "$LOOT/01-nmap.txt"

ok "Recon saved to $LOOT/01-nmap.txt"
log "Confirming the web app is alive:"
curl -s -o /dev/null -w "  HTTP %{http_code} on http://$TARGET/\n" "http://$TARGET/"
