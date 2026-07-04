#!/usr/bin/env python3
"""Create GitHub repo via API. Reads PAT from GH_TOKEN env var (or .gh_token)."""
import json, urllib.request, urllib.error, base64, os, pathlib

USERNAME = "phigrosgame"
TOKEN_FILE = pathlib.Path(__file__).parent.parent / ".gh_token"


def load_token() -> str:
    if "GH_TOKEN" in os.environ:
        return os.environ["GH_TOKEN"]
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    raise SystemExit("Set GH_TOKEN env or create .gh_token file.")


def main():
    token = load_token()
    repo_name = "女神異世界轉生想成為什麼-我勇者的肋骨輕小說"
    description = (
        "《女神『異世界転生何になりたいですか』俺「勇者の肋骨で」》繁體中文翻譯"
        "（每章一 commit，全書完後合 epub / txt）"
    )
    auth = base64.b64encode(f"{USERNAME}:{token}".encode()).decode()
    req = urllib.request.Request(
        "https://api.github.com/user/repos",
        data=json.dumps({"name": repo_name, "description": description, "private": False}).encode("utf-8"),
        method="POST",
        headers={"Authorization": f"Basic {auth}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
        print("CREATED:", d["full_name"], d["html_url"])


if __name__ == "__main__":
    main()
