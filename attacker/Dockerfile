# attacker — external adversary workstation.
# Debian + the offensive toolkit (lighter & more reliable than full Kali on WSL2).
FROM debian:12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        nmap hydra sqlmap curl wget netcat-openbsd \
        openssh-client sshpass dnsutils python3 jq ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /scripts
# scripts are bind-mounted from ./attacker/scripts at runtime (see compose)
RUN mkdir -p /loot
CMD ["sleep", "infinity"]
