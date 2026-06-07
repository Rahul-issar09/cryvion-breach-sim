# internal-svc — internal "backup" host, the lateral-movement target.
# Reachable only on internal_net. Weak SSH creds + credential reuse from the web tier.
FROM debian:12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server ca-certificates curl gnupg rsyslog \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /run/sshd

# Wazuh agent (detects the SSH lateral-movement login). Enrolled at runtime.
RUN curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | \
        gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import \
    && chmod 644 /usr/share/keyrings/wazuh.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" \
        > /etc/apt/sources.list.d/wazuh.list \
    && apt-get update \
    && WAZUH_MANAGER="host.docker.internal" apt-get install -y wazuh-agent=4.9.2-1 \
    && rm -rf /var/lib/apt/lists/*

ARG SSH_USER=svc-backup
ARG SSH_PASSWORD=Password1
RUN useradd -m -s /bin/bash ${SSH_USER} \
    && echo "${SSH_USER}:${SSH_PASSWORD}" | chpasswd

# VULN: password auth enabled for a reused service-account credential.
RUN sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config

# Deeper crown-jewels: a "backup export" the attacker collects after pivoting.
RUN mkdir -p /home/${SSH_USER}/backups \
    && printf 'id,name,ssn,credit_card\n1,Alice Morgan,111-22-3333,4111-1111-1111-1111\n2,Emi Tanaka,555-66-7777,4555-5555-5555-5555\n' \
        > /home/${SSH_USER}/backups/customer_export.csv \
    && echo "CRYVION{lateral-movement-successful}" > /home/${SSH_USER}/backups/FLAG.txt \
    && chown -R ${SSH_USER}:${SSH_USER} /home/${SSH_USER}/backups

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
# log via syslog (not -e/stderr) so rsyslog writes /var/log/auth.log for Wazuh
CMD ["/usr/sbin/sshd", "-D"]
