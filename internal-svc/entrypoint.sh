#!/bin/bash
# Enroll + start the Wazuh agent (if a manager is configured), then run sshd.
set -e

MGR="${WAZUH_MANAGER:-host.docker.internal}"

# Start rsyslog so sshd auth events land in /var/log/auth.log (read by Wazuh)
service rsyslog start 2>/dev/null || rsyslogd 2>/dev/null || true

if [ -d /var/ossec ]; then
  echo "[entrypoint] pointing Wazuh agent at manager: $MGR"
  sed -i "s|<address>.*</address>|<address>${MGR}</address>|" /var/ossec/etc/ossec.conf || true
  for i in $(seq 1 12); do
    if /var/ossec/bin/agent-auth -m "$MGR" -A "internal-$(hostname)" 2>&1 | grep -q "Valid key"; then
      echo "[entrypoint] enrolled to $MGR"; break
    fi
    echo "[entrypoint] enrollment attempt $i failed; retrying in 5s"; sleep 5
  done
  /var/ossec/bin/wazuh-control start 2>/dev/null || true
fi

echo "[entrypoint] starting sshd"
exec "$@"
