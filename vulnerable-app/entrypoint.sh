#!/bin/bash
# Enroll + start the Wazuh agent (if a manager is configured), then run the app.
set -e

MGR="${WAZUH_MANAGER:-host.docker.internal}"

if [ -d /var/ossec ]; then
  echo "[entrypoint] pointing Wazuh agent at manager: $MGR"
  sed -i "s|<address>.*</address>|<address>${MGR}</address>|" /var/ossec/etc/ossec.conf || true
  # auto-enroll with the manager (1515); retry until the manager is reachable
  for i in $(seq 1 12); do
    if /var/ossec/bin/agent-auth -m "$MGR" -A "web-$(hostname)" 2>&1 | grep -q "Valid key"; then
      echo "[entrypoint] enrolled to $MGR"; break
    fi
    echo "[entrypoint] enrollment attempt $i failed; retrying in 5s"; sleep 5
  done
  /var/ossec/bin/wazuh-control start 2>/dev/null || true
fi

echo "[entrypoint] starting CryvionPortal"
exec "$@"
