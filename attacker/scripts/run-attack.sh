#!/bin/bash
# Cryvion end-to-end breach — runs the full kill chain (stages 1-9).
# Usage:  run-attack.sh [--pause]    (--pause waits for Enter between stages, for live demos)
source "$(dirname "$0")/lib.sh"
cd "$(dirname "$0")"

PAUSE=0; [ "$1" = "--pause" ] && PAUSE=1
step() { [ "$PAUSE" = "1" ] && { echo; read -rp "  [press Enter for next stage] "; }; }

echo -e "${C_RED}"
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║   CRYVION NETWORKS — END-TO-END BREACH SIMULATION     ║"
echo "  ║   Authorized lab use only. Target: $TARGET_HOST       "
echo "  ╚══════════════════════════════════════════════════════╝"
echo -e "${C_RST}"

bash 01-recon.sh;          step
bash 02-initial-access.sh; step
bash 03-execution.sh;      step
bash 04-persistence.sh;    step
bash 05-privesc.sh;        step
bash 06-credaccess.sh;     step
bash 07-lateral.sh;        step
bash 08-collection.sh;     step
bash 09-exfil.sh

banner "BREACH COMPLETE — loot in $LOOT/ , alerts in the Wazuh dashboard"
ls -la "$LOOT"
