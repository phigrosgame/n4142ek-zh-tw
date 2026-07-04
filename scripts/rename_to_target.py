#!/usr/bin/env python3
"""Rename via repositories/{ID} endpoint, with manual redirect handling."""
import json, urllib.request, urllib.error, base64, os, pathlib

OWNER = "phigrosgame"
REPO = "-"
NEW_NAME = "女神『異世界轉生想成為什麼』我「勇者的肋骨」"
TOKEN_FILE = pathlib.Path(__file__).parent.parent / ".gh_token"


def load_token():
    if "GH_TOKEN" in os.environ:
        return os.environ["GH_TOKEN"]
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    raise SystemExit("missing token")


def patch(url, token, body):
    auth = base64.b64encode(f"{OWNER}:{token}".encode()).decode()
    req = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), method="PATCH",
        headers={"Authorization": f"Basic {auth}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return 200, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "ignore")


def main():
    token = load_token()
    # GET via /repos/{owner}/{repo}
    auth = base64.b64encode(f"{OWNER}:{token}".encode()).decode()
    g = urllib.request.Request(
        f"https://api.github.com/repos/{OWNER}/{REPO}", method="GET",
        headers={"Authorization": f"Basic {auth}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(g, timeout=30) as r:
        d = json.loads(r.read())
        repo_id = d.get("id")
        print("repo_id:", repo_id)
        print("full_name:", repr(d.get("full_name")))
        print("description:", d.get("description"))
        print("html_url:", d.get("html_url"))

    # PATCH via /repositories/{ID} to avoid redirect
    print("\n--- PATCH rename ---")
    status, result = patch(
        f"https://api.github.com/repositories/{repo_id}",
        token,
        {"name": NEW_NAME},
    )
    print(f"[{status}] {result.get('full_name') if isinstance(result, dict) else result}")
    if isinstance(result, dict):
        print("html_url:", result.get("html_url"))
        print("clone_url:", result.get("clone_url"))


if __name__ == "__main__":
    main()
