#!/usr/bin/env python3
"""Try multiple renaming candidates and report which one is accepted."""
import json, urllib.request, urllib.error, base64, os, pathlib

OWNER = "phigrosgame"
REPO = "-"
TOKEN_FILE = pathlib.Path(__file__).parent.parent / ".gh_token"

CANDIDATES = [
    "女神「異世界轉生想成為什麼」我「勇者的肋骨」",
    "女神異世界轉生想成為什麼-我勇者的肋骨",
    "shinju-no-rib-bone",
    "女神異世界轉生",
]


def load_token():
    if "GH_TOKEN" in os.environ:
        return os.environ["GH_TOKEN"]
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    raise SystemExit("missing token")


def try_one(token, name):
    auth = base64.b64encode(f"{OWNER}:{token}".encode()).decode()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}"
    body = json.dumps({"name": name}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="PATCH",
        headers={"Authorization": f"Basic {auth}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.loads(r.read())
            return "OK", d.get("full_name"), d.get("html_url")
    except urllib.error.HTTPError as e:
        return "ERR", e.code, e.read().decode("utf-8", "ignore")[:300]


def main():
    token = load_token()
    for name in CANDIDATES:
        status, a, b = try_one(token, name)
        print(f"[{status}] {name!r} -> {a} {b if status == 'ERR' else ''}")
        if status == "OK":
            print("STOPPED — first success")
            return


if __name__ == "__main__":
    main()
