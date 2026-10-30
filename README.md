# dtnsoft-status

[![status](https://github.com/thanhtuanh/dtnsoft-status/actions/workflows/status.yml/badge.svg)](https://github.com/thanhtuanh/dtnsoft-status/actions/workflows/status.yml)

Prüft **alle 15 Minuten von außen** (GitHub Actions, unabhängig vom eigenen Server), ob die öffentlichen Dienste von DTN Software
so antworten, wie ein Mensch sie im Browser sieht: GPAA (`gastro.`, `portal.`, `demo.`, `api.gpaa.`), Anmeldung, Website, BayernFisch.

- Nur öffentliche Adressen, kein Login, keine Zugangsdaten, keine Kundendaten.
- Grün = alle Adressen liefern den erwarteten Status (auch: interne Seiten sind von außen **nicht** erreichbar — 404/401 ist dort Absicht).
- Rot erst, wenn ein zweiter Versuch 90 Sekunden später ebenfalls rot ist.

| Datei | Inhalt |
|---|---|
| `gpaa_smoke.py` | Kopie von `gpaa-v3/scripts/dev/prod_smoke.py` (Quelle; dort ändern, dann `gpaa-v3/scripts/ops/status-sync.sh`) |
| `weitere.py` | Website, Keycloak, BayernFisch |
| `pruefen.sh` | beide Prüfungen, mit zweitem Versuch |

Lokal: `./pruefen.sh`
