#!/usr/bin/env python3
"""Show current repo state of phigrosgame/- and try rename."""
import json, urllib.request, urllib.error, base64, os, pathlib

OWNER = "phigrosgame"
REPO = "-"
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
    url = f"https://api.github.com/repos/{OWNER}/{REPO}"
    req = urllib.request.Request(
        url, method="GET",
        headers={"Authorization": f"Basic {auth}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
        print("CURRENT NAME:", repr(d.get("name")))
        print("FULL NAME:", d.get("full_name"))
        print("HTML:", d.get("html_url"))
        print("CLONE:", d.get("clone_url"))


if __name__ == "__main__":
    main()
