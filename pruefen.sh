#!/usr/bin/env bash
# Ein Lauf: beide Prüfungen; rot erst, wenn auch der zweite Versuch 90 s später rot ist (kein Alarm für einen einzelnen Netz-Wackler).
set -uo pipefail
cd "$(dirname "$0")"
lauf() { python3 gpaa_smoke.py && python3 weitere.py; }
lauf && exit 0
echo; echo "::warning::Erster Versuch rot — zweiter Versuch in 90 s"; sleep 90
lauf
