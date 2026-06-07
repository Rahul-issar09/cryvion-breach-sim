# CryvionPortal — vulnerable web tier (runs as root, fat image — intentional)
FROM python:3.12-slim

# Tools that make post-exploitation realistic: ping (cmd-injection target),
# ssh client + sshpass (lateral movement), cron (persistence), curl, ps.
RUN apt-get update && apt-get install -y --no-install-recommends \
        iputils-ping curl openssh-client sshpass cron procps net-tools gnupg \
    && rm -rf /var/lib/apt/lists/*

# Wazuh agent (HIDS / FIM / log analysis). Enrolled at runtime via entrypoint.
RUN curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | \
        gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import \
    && chmod 644 /usr/share/keyrings/wazuh.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
        > /etc/apt/sources.list.d/wazuh.list \
    && apt-get update \
    && WAZUH_MANAGER="host.docker.internal" apt-get install -y wazuh-agent=4.9.2-1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/
COPY entrypoint.sh /entrypoint.sh
RUN mkdir -p /app/uploads && chmod +x /entrypoint.sh

EXPOSE 8080
# Intentionally NOT dropping privileges / no USER directive -> runs as root (T1611 enabler)
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
