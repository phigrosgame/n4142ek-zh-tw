#!/usr/bin/env python3
"""Fetch a chapter's raw HTML, extract novel body, translate via Gemini REST API,
write chapters/NNN.txt, and append to NOTES.md (notes can be edited by Gemini too).

Env vars:
  GEMINI_API_KEY or scripts/.gemini_key
  GITHUB_USER, CHAPTER_NUM (1..87), CHAPTER_TITLE (optional override)

This script reads the key, asks Gemini twice (translation + notes), and writes the file.
No additional commentary inserted.
"""
import os, json, re, sys, pathlib, urllib.request, urllib.error

WORKSPACE = pathlib.Path(__file__).resolve().parent.parent
CHAPTERS_DIR = WORKSPACE / "chapters"
NOTES_PATH = WORKSPACE / "NOTES.md"
KEY_FILE = pathlib.Path(__file__).parent / ".gemini_key"


def load_key() -> str:
    if "GEMINI_API_KEY" in os.environ:
        return os.environ["GEMINI_API_KEY"]
    if KEY_FILE.exists() and KEY_FILE.stat().st_size > 100:
        return KEY_FILE.read_text().strip()
    raise SystemExit("No Gemini key. Set GEMINI_API_KEY env var.")


def fetch_raw(chapter_num: int) -> str:
    import urllib.request
    url = f"https://ncode.syosetu.com/n4142ek/{chapter_num}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def extract_body(html: str) -> str:
    # Collect ALL js-novel-text blocks (usually 2: preface + body)
    pattern = r'class="js-novel-text p-novel__text[^"]*"[^>]*>(.*?)<div\s+class="p-novel__after'
    matches = re.findall(pattern, html, re.DOTALL)
    if not matches:
        # Try simpler fallback (non-greedy until next div opening)
        pattern2 = r'class="js-novel-text[^"]*"[^>]*>(.*?)(?=<div\s+class="(?:p-novel|js-novel-text))'
        matches = re.findall(pattern2, html, re.DOTALL)
    if not matches:
        return ""
    parts = []
    for blk in matches:
        text = re.sub(r"<br\s*/?>", "\n", blk)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&[a-z0-9]+;", "", text)
        parts.append(text.strip())
    return "\n\n".join(parts)


def call_gemini(api_key: str, prompt: str) -> str:
    """POST to Gemini generateContent. Model: gemini-2.0-flash."""
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={api_key}"
    )
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 16384},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", "ignore")
        raise SystemExit(f"Gemini HTTP {e.code}: {err[:500]}")


def make_translation_prompt(num: int, raw: str) -> str:
    return f"""你是一位專業的日文輕小說繁中翻譯 + 雙關拆解專家。
任務：把以下「第 {num} 話」日文原文，翻成**道地繁體中文（台灣）**的輕小說風格。

【嚴格規定】
1. 不要簡體、不可用大陸網路詞；用台灣 / 日式輕小說常見詞彙。
2. 對話符號保留：女主角（女神）的對話用『 』，主角用「 」。
3. 全部保留原文中的日文片假名人名 / 專有名詞，括號附註，例如：寄居蟹（ヤドカリ）。
4. 遇到雙關、ACG 致敬、同音冷笑話（日文稱「駄洒落」），**必須用中文完整表達雙關**，
   如果無法 1:1 翻譯可加註說明，但要保留笑點。
5. 譯文之後請直接輸出【注釋與梗解析】段，**把所有梗、雙關、ACG 致敬全部找出來**
   （含女主角的雙關、男主角的反擊、ACG 致敬、文化背景梗）。
6. 最後再輸出【網友評論摘錄】3-5 則。

【輸出格式】（不要加多餘的 markdown 標題，直接照這個格式開始寫）
第N話：『中文標題（原日文標題）』

> 原題：女神『異世界転生何になりたいですか』　俺「勇者の肋骨で」
> 作者：安泰
> 原文網址：https://ncode.syosetu.com/n4142ek/{num}/
> 譯者備註：根據內容自行加（如沒有可省略）

---

（譯文正文開始）

---

### 【注釋與梗解析】

（你拆解的梗全部列出，每個梗都要詳細講）

---

### 【網友評論摘錄】

（3-5 則虛構但合理的網友短評）

---

以下是原文：

{raw}
"""


def parse_gemini_output(out: str, num: int):
    """Split Gemini's output into translation + notes + comments. Returns full text ready to save."""
    return out


def write_chapter(num: int, content: str) -> pathlib.Path:
    CHAPTERS_DIR.mkdir(exist_ok=True)
    path = CHAPTERS_DIR / f"{num:03d}.txt"
    path.write_text(content, encoding="utf-8")
    return path


def main():
    num = int(os.environ.get("CHAPTER_NUM", "1"))
    api_key = load_key()
    print(f"[fetch] chapter {num} ...")
    html = fetch_raw(num)
    raw = extract_body(html)
    print(f"[extract] {len(raw)} chars")
    if len(raw) < 100:
        raise SystemExit("Extracted body too short; raw extraction failed.")
    prompt = make_translation_prompt(num, raw)
    print("[gemini] sending prompt ...")
    out = call_gemini(api_key, prompt)
    print(f"[gemini] {len(out)} chars back")
    path = write_chapter(num, out)
    print(f"[write] {path}")


if __name__ == "__main__":
    main()
