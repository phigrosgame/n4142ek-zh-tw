#!/usr/bin/env python3
"""Final repo cleanup:
1. Delete the bogus 'phigrosgame/---' repo.
2. Create a clean ASCII-named repo 'n4142ek-zh-tw'.
3. Report new clone URL.
"""
import json, urllib.request, urllib.error, base64, os, pathlib

OWNER = "phigrosgame"
TOKEN_FILE = pathlib.Path(__file__).parent.parent / ".gh_token"

NEW_REPO = "n4142ek-zh-tw"
DESCRIPTION = "《女神『異世界転生何になりたいですか』俺「勇者の肋骨で」》繁體中文翻譯（每章一 commit，全書完後合 epub / txt）"


def load_token():
    if "GH_TOKEN" in os.environ:
        return os.environ["GH_TOKEN"]
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    raise SystemExit("missing token")


def request(method, url, token, body=None):
    auth = base64.b64encode(f"{OWNER}:{token}".encode()).decode()
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"Basic {auth}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "ignore")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def main():
    token = load_token()

    # 1. 砍舊的 ---
    print("=== STEP 1: delete bogus repo ---")
    s, d = request("DELETE", f"https://api.github.com/repos/{OWNER}/-", token)
    print(f"[{s}] {d if isinstance(d, str) else json.dumps(d)}")

    # 2. 建新
    print("\n=== STEP 2: create n4142ek-zh-tw ===")
    s, d = request(
        "POST",
        "https://api.github.com/user/repos",
        token,
        {"name": NEW_REPO, "description": DESCRIPTION, "private": False, "auto_init": False},
    )
    if isinstance(d, dict) and "full_name" in d:
        print(f"[{s}] CREATED {d['full_name']} -> {d['html_url']}")
        print(f"      clone: {d['clone_url']}")
    else:
        print(f"[{s}] {d}")


if __name__ == "__main__":
    main()
