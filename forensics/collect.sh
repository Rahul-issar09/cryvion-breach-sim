#!/bin/bash
# Cryvion forensic artifact collector.
# Captures post-breach evidence from the compromised containers + SIEM, builds a
# timeline and IOC list, and bundles everything into a timestamped archive.
#
# Usage:  ./forensics/collect.sh        (run from the repo root, Docker running)
export MSYS_NO_PATHCONV=1           # stop Git-Bash mangling in-container paths
set -u

WEB=cryvion-web
INT=cryvion-internal
ATK=cryvion-attacker
MGR=single-node-wazuh.manager-1

TS=$(date +%Y%m%d-%H%M%S)
OUT="forensics/output/$TS"
mkdir -p "$OUT"
echo "[*] Collecting forensic evidence -> $OUT"

dexec() { docker exec "$1" bash -c "$2" 2>/dev/null; }

# ---------------------------------------------------------------- container state
for C in "$WEB" "$INT"; do
  D="$OUT/$C"; mkdir -p "$D"
  echo "[*] $C: filesystem changes, logs, persistence artifacts"
  # docker diff = everything the attacker added/changed vs the base image
  docker diff "$C" > "$D/docker-diff.txt" 2>/dev/null
  docker logs "$C" > "$D/container-stdout.log" 2>&1
  dexec "$C" "cat /etc/passwd"                       > "$D/etc-passwd.txt"
  dexec "$C" "ls -la /etc/cron.d/ 2>/dev/null; echo '---'; cat /etc/cron.d/* 2>/dev/null" > "$D/cron.txt"
  dexec "$C" "cat /root/.ssh/authorized_keys 2>/dev/null" > "$D/root-authorized_keys.txt"
  dexec "$C" "ls -la /app/uploads 2>/dev/null"       > "$D/uploads-listing.txt"
  dexec "$C" "ps -ef"                                > "$D/processes.txt"
  dexec "$C" "(ss -tunap || netstat -tunap) 2>/dev/null" > "$D/network-connections.txt"
  dexec "$C" "cat ~/.bash_history 2>/dev/null"       > "$D/root-bash_history.txt"
done

echo "[*] Application + auth logs"
dexec "$WEB" "cat /var/log/cryvion/security.log 2>/dev/null" > "$OUT/web-security.log"
dexec "$INT" "cat /var/log/auth.log 2>/dev/null"             > "$OUT/internal-auth.log"

# ---------------------------------------------------------------- attacker loot
echo "[*] Attacker loot (what was actually staged/exfiltrated)"
docker cp "$ATK":/loot "$OUT/attacker-loot" 2>/dev/null

# ---------------------------------------------------------------- SIEM timeline
echo "[*] Reconstructing attack timeline from Wazuh alerts"
docker exec -i "$MGR" python3 - > "$OUT/attack-timeline.txt" 2>/dev/null <<'PYEOF'
import json
ev=[]
with open('/var/ossec/logs/alerts/alerts.json') as f:
    for line in f:
        try: a=json.loads(line)
        except: continue
        r=a.get('rule',{}); rid=r.get('id',''); grps=r.get('groups',[])
        keep = rid.startswith('1001') or 'sshd' in r.get('description','').lower() or 'syscheck' in grps
        if not keep: continue
        ev.append((a.get('timestamp',''), r.get('level',''), rid,
                   r.get('description','')[:70],
                   ",".join(r.get('mitre',{}).get('id',[])),
                   a.get('data',{}).get('srcip','') or a.get('agent',{}).get('name','')))
ev.sort()
print(f"{'TIMESTAMP':26} {'LVL':3} {'RULE':7} {'MITRE':10} DESCRIPTION / SOURCE")
print("-"*110)
for t,l,rid,desc,mit,src in ev:
    print(f"{t:26} {l:>3} {rid:7} {mit:10} {desc}  [{src}]")
print(f"\nTotal correlated attack alerts: {len(ev)}")
PYEOF

# ---------------------------------------------------------------- IOCs
echo "[*] Extracting indicators of compromise (IOCs)"
{
  echo "# Cryvion Breach — Indicators of Compromise ($TS)"
  echo
  echo "## Malicious files (web tier)"
  dexec "$WEB" "for f in /app/uploads/*; do [ -f \"\$f\" ] && sha256sum \"\$f\"; done" 2>/dev/null
  echo
  echo "## Backdoor account (uid=0)"
  dexec "$WEB" "awk -F: '\$3==0 && \$1!=\"root\"{print}' /etc/passwd"
  echo
  echo "## Persistence — cron"
  dexec "$WEB" "cat /etc/cron.d/* 2>/dev/null"
  echo
  echo "## Persistence — rogue SSH key"
  dexec "$WEB" "cat /root/.ssh/authorized_keys 2>/dev/null"
  echo
  echo "## Attacker source IPs (from app security log)"
  dexec "$WEB" "grep -oE 'src=[0-9.]+' /var/log/cryvion/security.log 2>/dev/null | sort -u"
  echo
  echo "## Exfiltration destination (C2)"
  dexec "$WEB" "grep -oE 'http://attacker:[0-9]+' /etc/cron.d/* 2>/dev/null | sort -u"
} > "$OUT/IOCs.md"

# ---------------------------------------------------------------- bundle
echo "[*] Bundling evidence archive"
( cd forensics/output && tar czf "$TS.tar.gz" "$TS" )
echo "[+] Done. Evidence in $OUT/  (archive: forensics/output/$TS.tar.gz)"
echo "[+] Key files: attack-timeline.txt, IOCs.md, */docker-diff.txt"
