#!/usr/bin/env python
"""Weitere öffentliche Dienste neben GPAA: Website dtnsoft.de, Anmeldung (Keycloak), BayernFisch. Nur lesen, kein Login. Exit 0 = alles wie erwartet."""
import sys
import urllib.error
import urllib.request

# (URL, erwarteter Status, erwartetes Ziel nach Weiterleitungen oder None)
ERWARTET = [
    ("https://dtnsoft.de/", 200, None), ("https://www.dtnsoft.de/", 200, None), ("https://dtnsoft.de/steuerkanzleien.html", 200, None),
    ("https://keycloak.dtnsoft.de/realms/gpaa-v2", 200, None),
    ("https://bayernfisch-lieferdienst.de/", 200, None),
    ("https://office2.bayernfisch-lieferdienst.de/", 200, "https://office2.bayernfisch-lieferdienst.de/login/?next=/"),
]


def holen(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "dtnsoft-status"}), timeout=15) as r: return r.status, r.geturl()
    except urllib.error.HTTPError as e: return e.code, e.geturl()
    except Exception as e: return 0, f"{type(e).__name__}: {e}"


def main():
    rot = 0
    for url, status, ziel in ERWARTET:
        st, end = holen(url)
        ok = st == status and (ziel is None or end == ziel)
        rot += not ok
        print(f"{'✅' if ok else '❌'} {url} → {st}{'' if ziel is None else ' ' + end}" + ("" if ok else f"   (erwartet {status}{'' if ziel is None else ' ' + ziel})"))
    print(f"\nERGEBNIS: {len(ERWARTET) - rot} / {len(ERWARTET)} OK")
    return 1 if rot else 0


if __name__ == "__main__": sys.exit(main())
