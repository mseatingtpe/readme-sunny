#!/usr/bin/env python3
"""Extract worldview dimensions from content files using Claude API."""

import argparse
import json
import os
import re
import yaml
from pathlib import Path
from urllib.request import urlopen, Request


CONTENT_DIR = Path(__file__).parent.parent / "content"
RAW_DIR = CONTENT_DIR / "raw"
EXTRACT_DIR = CONTENT_DIR / "extractions"
PROFILE_PATH = CONTENT_DIR / "worldview-profile.yaml"

EXTRACTION_PROMPT = """你是一個世界觀萃取系統。請從以下文章中萃取作者的世界觀。

重要：每個主題必須有**獨立的、針對該主題的** stance。不要把同一句話複製到多個主題。

主題標籤限定以下六組（只選文章真正有討論到的，不要硬湊）：
- AI（AI 工具、自動化、數位轉型）
- 工作（管理、組織、職場）
- 身份（自我認同、生活方式、情緒）
- 愛（愛情、友情、關係）
- 文化（品味、創作、內容產業）
- 學習（知識、信仰、成長）

規則：
- 用繁體中文回應
- 每個 topic 的 stance 必須針對該主題，用一到兩句話概括作者在這篇文章中對該主題的態度
- key_quote 必須是文章中的原文，不要改寫
- keywords 從文章中提取 3-8 個有代表性的詞彙或短語（用於文字雲）
- 如果文章沒有明確的轉變訊號，shift_signal 填 null
- 如果沒有明確的矛盾或張力，tension 填 null

請以 JSON 格式回應，結構如下：
{{
  "topics": [
    {{
      "name": "主題標籤",
      "stance": "作者在這篇文章中對這個主題的態度",
      "tension": "這個態度跟什麼對立或矛盾（或 null）",
      "shift_signal": "轉變訊號（或 null）",
      "key_quote": "這個主題最代表的一句原文"
    }}
  ],
  "connections": ["跨領域串連1", "跨領域串連2"],
  "keywords": ["關鍵詞1", "關鍵詞2", "關鍵詞3"]
}}

文章內容：
---
{content}
---

請只回應 JSON，不要加任何其他文字。"""


def call_claude_api(prompt):
    """Call Claude API to extract dimensions."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. "
            "Export it or add to GitHub Secrets."
        )

    body = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    with urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())

    text = result["content"][0]["text"]
    # Strip markdown code fences if present
    text = re.sub(r"^```json?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    return json.loads(text)


def read_content_file(filepath):
    """Read a content file and return frontmatter + body."""
    text = filepath.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return frontmatter, body
    return {}, text


def extract_file(filepath, force=False):
    """Extract dimensions from a single content file."""
    stem = filepath.stem
    output_path = EXTRACT_DIR / f"{stem}.yaml"

    if output_path.exists() and not force:
        return None

    frontmatter, body = read_content_file(filepath)
    if not body or len(body) < 50:
        print(f"  Skipping {filepath.name}: too short")
        return None

    title = frontmatter.get("title", stem)
    date = str(frontmatter.get("date", "unknown"))

    prompt = EXTRACTION_PROMPT.format(content=f"標題：{title}\n日期：{date}\n\n{body}")
    result = call_claude_api(prompt)

    extraction = {
        "source": f"content/raw/{filepath.name}",
        "timestamp": date,
        "topics": result.get("topics", []),
        "connections": result.get("connections", []),
        "keywords": result.get("keywords", []),
    }

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(extraction, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return output_path


def update_worldview_profile():
    """Regenerate worldview-profile.yaml from all extractions."""
    extractions = []
    for f in sorted(EXTRACT_DIR.glob("*.yaml")):
        if f.name.startswith("_"):
            continue
        with open(f, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            if data:
                extractions.append(data)

    # Group by topic — new format has per-topic stances
    by_topic = {}
    all_keywords = []
    for ext in extractions:
        all_keywords.extend(ext.get("keywords", []))
        topics = ext.get("topics", [])
        for topic_entry in topics:
            # New format: topic_entry is a dict with name, stance, etc.
            if isinstance(topic_entry, dict):
                name = topic_entry["name"]
                if name not in by_topic:
                    by_topic[name] = []
                by_topic[name].append({
                    "timestamp": ext["timestamp"],
                    "stance": topic_entry.get("stance", ""),
                    "tension": topic_entry.get("tension"),
                    "shift_signal": topic_entry.get("shift_signal"),
                    "key_quote": topic_entry.get("key_quote", ""),
                    "source": ext["source"],
                })
            else:
                # Old format: topic_entry is a string
                if topic_entry not in by_topic:
                    by_topic[topic_entry] = []
                by_topic[topic_entry].append({
                    "timestamp": ext["timestamp"],
                    "stance": ext.get("stance", ""),
                    "tension": ext.get("tension"),
                    "shift_signal": ext.get("shift_signal"),
                    "key_quote": ext.get("key_quote", ""),
                    "source": ext["source"],
                })

    # Sort each topic by timestamp
    for topic in by_topic:
        by_topic[topic].sort(key=lambda x: str(x["timestamp"]))

    # Keyword frequency
    keyword_freq = {}
    for kw in all_keywords:
        keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

    profile = {
        "last_updated": str(max(str(e["timestamp"]) for e in extractions)) if extractions else "",
        "total_extractions": len(extractions),
        "topics": by_topic,
        "keywords": keyword_freq,
    }

    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        yaml.dump(profile, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    return PROFILE_PATH


def main():
    parser = argparse.ArgumentParser(description="Extract worldview dimensions")
    parser.add_argument("--file", type=str, help="Extract a single file")
    parser.add_argument("--all", action="store_true", help="Extract all unprocessed files")
    parser.add_argument("--force", action="store_true", help="Re-extract even if already done")
    parser.add_argument("--update-profile", action="store_true", help="Only update worldview profile")
    args = parser.parse_args()

    if args.update_profile:
        path = update_worldview_profile()
        print(f"✓ Updated {path}")
        return

    files = []
    if args.file:
        files = [Path(args.file)]
    elif args.all:
        files = sorted(f for f in RAW_DIR.glob("*.md") if not f.name.startswith("_"))
    else:
        parser.print_help()
        return

    new_count = 0
    skip_count = 0

    for f in files:
        print(f"Processing: {f.name}")
        result = extract_file(f, force=args.force)
        if result:
            print(f"  ✓ {result.name}")
            new_count += 1
        else:
            skip_count += 1

    if new_count > 0:
        profile_path = update_worldview_profile()
        print(f"\n✓ Updated {profile_path}")

    print(f"\nDone: {new_count} extracted, {skip_count} skipped")


if __name__ == "__main__":
    main()
