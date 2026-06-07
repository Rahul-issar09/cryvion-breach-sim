# Cryvion Networks — End-to-End Breach Lifecycle Simulation in Containerized Environments

![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Wazuh](https://img.shields.io/badge/SIEM-Wazuh-005792)
![MITRE ATT&CK](https://img.shields.io/badge/Mapped%20to-MITRE%20ATT%26CK-c0392b)
![Status](https://img.shields.io/badge/status-complete-2ecc71)

A self-contained, Docker-based lab that runs a **full multi-stage breach** against a
realistic containerized enterprise, **detects** it with a SIEM mapped to MITRE
ATT&CK, **investigates** it forensically, and then **re-architects** the environment
so the *same attack is blocked*. Built as a B.Tech major project (Cyber Group 2).

> ⚠️ **Educational / authorized lab use only.** This repository contains
> *intentionally vulnerable* code, offensive tooling, and a deliberately weak
> configuration. All offensive activity is confined to the lab's private Docker
> networks. **Do not deploy any of this on a public or production system, and never
> point the attack scripts at infrastructure you don't own.**

---

## What it demonstrates

Same attack, two architectures, opposite outcomes:

| | Vulnerable stack | Hardened stack |
|---|---|---|
| SQLi auth bypass | ✅ succeeds | ⛔ blocked |
| RCE (command injection) | ✅ root shell | ⛔ blocked |
| PII exfiltration | ✅ data stolen | ⛔ blocked |
| Lateral movement | ✅ pivot succeeds | ⛔ blocked (segmentation) |
| Container breakout | ✅ socket exposed | ⛔ no socket |

**6 ATT&CK techniques detected** by the SIEM; **8/8 damaging objectives blocked**
after hardening.

## Architecture

```
                         Docker Desktop (Windows / WSL2)
 ┌───────────────────────────────────────────────────────────────────────┐
 │   [ attacker ] ── dmz_net ──► [ web-app ] (Flask, vulnerable)          │
 │                                    │ internal_net                       │
 │                                    ▼                                    │
 │                        [ db ]            [ internal-svc ]               │
 │                        MySQL + PII       SSH backup host                │
 │                                                                         │
 │   ── Wazuh SIEM (manager / indexer / dashboard + agents) ──            │
 └───────────────────────────────────────────────────────────────────────┘
```

The web app is intentionally **dual-homed** (DMZ + internal), so one web compromise
bridges into the internal zone — the central flaw the hardened design removes.

## Tech stack

| Layer | Technology |
|---|---|
| Vulnerable app | Custom Python/Flask (SQLi, command injection, unrestricted upload) |
| Data store | MySQL 8 (seeded synthetic PII) |
| Lateral target | OpenSSH internal host |
| Attacker | Debian + nmap / hydra / sqlmap |
| SIEM | Wazuh (manager, indexer, dashboard, agents) |
| WAF | ModSecurity + OWASP Core Rule Set |
| DevSecOps CI | Hadolint, Semgrep, Checkov, Trivy, OWASP ZAP |

## Repository layout

```
docker-compose.yml              vulnerable enterprise ("before")
docker-compose.hardened.yml     Zero-Trust hardened enterprise ("after")
vulnerable-app/                 Flask app, Dockerfiles, DB seed
internal-svc/                   SSH lateral-movement target
attacker/scripts/               9-stage kill-chain + run-attack.sh
detection/wazuh/                custom rules, decoders, shared agent config
forensics/collect.sh            forensic artifact collector
mitre/                          ATT&CK Navigator layer (JSON)
cicd/.github/workflows/         DevSecOps pipeline
report/                         report/diagram generator scripts
```

## Prerequisites

- Docker Desktop (WSL2) with **≥ 5 GB** RAM allocated to WSL2.
- `git`. The Wazuh stack is **not vendored** here (third-party + generated certs);
  you clone it during setup (below).

## Quick start

```bash
# 1. configure environment (weak lab defaults)
cp .env.example .env

# 2. vulnerable enterprise
docker compose up -d --build

# 3. monitoring — clone Wazuh single-node, generate certs, start it
git clone --depth=1 -b v4.9.2 https://github.com/wazuh/wazuh-docker.git \
    detection/wazuh/wazuh-docker
cd detection/wazuh/wazuh-docker/single-node
#   (low-RAM: set OPENSEARCH_JAVA_OPTS to -Xms768m -Xmx768m in docker-compose.yml)
#   (mount ../../rules, ../../decoders, ../../shared-agent.conf into the manager)
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
cd -

# 4. run the full breach
docker compose exec attacker bash /scripts/run-attack.sh        # add --pause for a demo

# 5. collect forensic evidence
./forensics/collect.sh
```

Wazuh dashboard: **https://localhost:443** (default `admin` / `SecretPassword`).

### Hardened ("after") stack

```bash
# create the Docker secrets the hardened stack expects
mkdir -p secrets
printf 'a-strong-db-password'   > secrets/db_password.txt
printf 'a-strong-root-password' > secrets/mysql_root_password.txt

docker compose down
docker compose -f docker-compose.hardened.yml up -d --build
# re-run the same attack — it is now blocked:
docker compose -f docker-compose.hardened.yml exec attacker bash /scripts/run-attack.sh
```

## Attack chain (MITRE ATT&CK)

| Stage | Technique | MITRE |
|---|---|---|
| Recon | nmap service scan | T1595 |
| Initial Access | brute force + SQL injection | T1110 / T1190 |
| Execution | command injection (RCE) + web shell | T1059 / T1505 |
| Persistence | backdoor user, cron, SSH key | T1136 / T1053 / T1098 |
| Privilege Esc. | Docker socket escape vector | T1611 |
| Credential Access | secrets in files / env | T1552 |
| Lateral Movement | SSH pivot (reused creds) | T1021 / T1078 |
| Collection | PII + internal backup theft | T1005 |
| Exfiltration | HTTP C2 + DNS tunnelling | T1041 / T1048 |

## Hardening controls

WAF (ModSecurity/CRS) · Zero-Trust micro-segmentation · non-root + `cap_drop ALL` +
`no-new-privileges` + read-only filesystem · no Docker socket · Docker secrets ·
key-only SSH · parameterized queries / no-shell exec · DevSecOps CI gates.

## Notes

- `.env`, `secrets/`, certificates, the cloned `wazuh-docker/`, and generated
  artifacts are git-ignored — recreate them with the steps above.
- The intentionally weak credentials and the `vulnerable-app/app/config/db.conf`
  file are part of the simulation, not real secrets.

## License / use

Provided for educational and authorized security-testing use only. Use at your own
risk, exclusively within an isolated lab you control.
