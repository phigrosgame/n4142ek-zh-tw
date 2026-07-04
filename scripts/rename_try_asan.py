#!/usr/bin/env python3
"""Try renaming with progressively stripped-down names until GitHub accepts."""
import json, urllib.request, urllib.error, base64, os, pathlib

OWNER = "phigrosgame"
REPO_ID = 1289221010
TOKEN_FILE = pathlib.Path(__file__).parent.parent / ".gh_token"

CANDIDATES = [
    "女神『異世界轉生想成為什麼』我「勇者的肋骨」",  # 原本要的
    "女神異世界轉生想成為什麼-我勇者的肋骨",
    "女神異世界転生-勇者の肋骨-繁中",
    "shinju-rib-bone-zh",
]


def load_token():
    if "GH_TOKEN" in os.environ:
        return os.environ["GH_TOKEN"]
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    raise SystemExit("missing token")


def main():
    token = load_token()
    auth = base64.b64encode(f"{OWNER}:{token}".encode()).decode()
    for name in CANDIDATES:
        req = urllib.request.Request(
            f"https://api.github.com/repositories/{REPO_ID}",
            data=json.dumps({"name": name}).encode("utf-8"),
            method="PATCH",
            headers={"Authorization": f"Basic {auth}", "Accept": "application/vnd.github+json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read())
                print(f"[OK ] {name!r} -> stored as {d['name']!r} ({len(d['name'])} chars), full_name={d['full_name']}")
                if d['name'] == name:
                    print("✓ NAME MATCHES INTENT — STOP")
                    return
        except urllib.error.HTTPError as e:
            print(f"[ERR] {name!r} -> {e.code} {e.read().decode('utf-8','ignore')[:200]}")


if __name__ == "__main__":
    main()
