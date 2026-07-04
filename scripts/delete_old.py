#!/usr/bin/env python3
"""Delete the old 'phigrosgame/-' repo by following redirects."""
import json, urllib.request, urllib.error, base64, os, pathlib

OWNER = "phigrosgame"
REPO_ID = 1289221010
TOKEN_FILE = pathlib.Path(__file__).parent.parent / ".gh_token"


def load_token():
    if "GH_TOKEN" in os.environ:
        return os.environ["GH_TOKEN"]
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    raise SystemExit("missing token")


def main():
    token = load_token()
    auth = base64.b64encode(f"{OWNER}:{token}".encode()).decode()
    req = urllib.request.Request(
        f"https://api.github.com/repositories/{REPO_ID}",
        method="DELETE",
        headers={"Authorization": f"Basic {auth}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("[DELETE OK]", r.status)
    except urllib.error.HTTPError as e:
        print("[DELETE ERR]", e.code, e.read().decode("utf-8", "ignore")[:300])


if __name__ == "__main__":
    main()
