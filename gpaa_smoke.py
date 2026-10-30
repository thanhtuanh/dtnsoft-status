#!/usr/bin/env python
"""PROD-Smoke nach jedem Deploy (QA-Entscheidung B, 29.10.2026) — nur lesen, kein Login, kein Browser. Prüft die Host-Matrix so, wie sie der Mensch von
außen sieht: Caddy-Allowlist + Django-URLconf zusammen. Anlass: demo./ → /muster/ war 404, weil die Caddy-Allowlist fehlte — die Django-Tests sahen das nicht.
Aufruf: .venv/bin/python scripts/dev/prod_smoke.py        Exit 0 = alles wie erwartet.
Öffentliche Kopie läuft alle 15 min im Repo dtnsoft-status (GitHub Actions) — nach Änderung hier: scripts/ops/status-sync.sh."""
import re
import sys
from urllib.parse import urljoin, urlparse
import urllib.error
import urllib.request

# (Host, Pfad, erwarteter Status, erwartetes Ziel nach Weiterleitungen oder None)
ERWARTET = [
    ("gastro.dtnsoft.de", "/", 200, None), ("gastro.dtnsoft.de", "/fibu/", 200, None), ("gastro.dtnsoft.de", "/muster/", 200, "https://demo.dtnsoft.de/muster/"),
    ("gastro.dtnsoft.de", "/muster/stapel/", 200, "https://demo.dtnsoft.de/muster/stapel/"), ("gastro.dtnsoft.de", "/login/", 404, None), ("gastro.dtnsoft.de", "/admin/", 404, None),
    ("gastro.dtnsoft.de", "/posteingang/", 404, None), ("gastro.dtnsoft.de", "/health/", 200, None),
    ("demo.dtnsoft.de", "/", 200, "https://demo.dtnsoft.de/muster/"), ("demo.dtnsoft.de", "/muster/beleg/12/", 200, None),
    ("demo.dtnsoft.de", "/api/v2/public/preise", 200, None), ("demo.dtnsoft.de", "/login/", 404, None), ("demo.dtnsoft.de", "/admin/", 404, None),
    ("api.gpaa.dtnsoft.de", "/api/v2/public/preise", 200, None), ("api.gpaa.dtnsoft.de", "/login/", 404, None), ("api.gpaa.dtnsoft.de", "/", 404, None),
    ("portal.dtnsoft.de", "/login/", 200, None), ("portal.dtnsoft.de", "/posteingang/", 200, "https://portal.dtnsoft.de/login/?next=/posteingang/"),
    ("admin.dtnsoft.de", "/login/", 200, None), ("admin.dtnsoft.de", "/fibu/", 404, None),
    ("restaurant.dtnsoft.de", "/", 200, "https://gastro.dtnsoft.de/"),
    ("v3.gpaa.dtnsoft.de", "/", 401, None), ("v3.gpaa.dtnsoft.de", "/login/", 401, None),   # QA nur intern (Basic-Auth vor allem)
]


# Seiten, deren /static/-Assets (CSS/JS/Icon) auf DEMSELBEN Host laden müssen — 29.10.2026: demo./muster/ lief ohne CSS/JS (Caddy-Allowlist ohne /static/*)
ASSET_SEITEN = ["https://demo.dtnsoft.de/muster/", "https://demo.dtnsoft.de/muster/beleg/12/", "https://gastro.dtnsoft.de/fibu/", "https://portal.dtnsoft.de/login/"]
TYPEN = {".css": "text/css", ".js": "javascript", ".ico": "image/", ".png": "image/", ".svg": "image/", ".woff2": "font"}


def assets(seite):
    """→ [(url, status, content-type, ok)] für alle /static/-Verweise der Seite."""
    try:
        with urllib.request.urlopen(urllib.request.Request(seite, headers={"User-Agent": "gpaa-v3-prod-smoke"}), timeout=15) as r: html, basis = r.read().decode("utf-8", "replace"), r.geturl()
    except Exception as e: return [(seite, 0, f"{type(e).__name__}", False)]
    out = []
    for ref in sorted(set(re.findall(r'(?:href|src)="(/static/[^"]+)"', html))):
        u = urljoin(basis, ref)
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "gpaa-v3-prod-smoke"}), timeout=15) as r: st, ct = r.status, r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e: st, ct = e.code, e.headers.get("Content-Type", "")
        except Exception as e: st, ct = 0, type(e).__name__
        erwartet = next((t for ext, t in TYPEN.items() if urlparse(u).path.endswith(ext)), "")
        out.append((u, st, ct, st == 200 and erwartet in ct))
    return out or [(seite, 0, "keine /static/-Verweise gefunden", False)]


def holen(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "gpaa-v3-prod-smoke"}), timeout=15) as r: return r.status, r.geturl()
    except urllib.error.HTTPError as e: return e.code, e.geturl()
    except Exception as e: return 0, f"{type(e).__name__}: {e}"


def main():
    rot = 0
    for host, pfad, status, ziel in ERWARTET:
        st, url = holen(f"https://{host}{pfad}")
        ok = st == status and (ziel is None or url == ziel)
        rot += not ok
        print(f"{'✅' if ok else '❌'} {host}{pfad} → {st}{'' if ziel is None else ' ' + url}" + ("" if ok else f"   (erwartet {status}{'' if ziel is None else ' ' + ziel})"))
    n = len(ERWARTET)
    for seite in ASSET_SEITEN:
        for u, st, ct, ok in assets(seite):
            n += 1; rot += not ok
            if not ok: print(f"❌ Asset {u} → {st} {ct}   (von {seite})")
        print(f"{'✅' if all(a[3] for a in assets(seite)) else '❌'} Assets {seite}")
    print(f"\nERGEBNIS: {n - rot} / {n} OK")
    return 1 if rot else 0


if __name__ == "__main__": sys.exit(main())
