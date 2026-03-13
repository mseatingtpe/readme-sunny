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

EXTRACTION_PROMPT = """你是一個世界觀萃取系統。請從以下文章中萃取七個維度。

規則：
- 用繁體中文回應
- 每個欄位都要填寫，除非標註「可為 null」
- key_quote 必須是文章中的原文，不要改寫
- stance 用一到三句話概括
- 如果文章沒有明確的轉變訊號，shift_signal 填 null
- 如果沒有明確的矛盾或張力，tension 填 null
- topics 使用簡短標籤，如：AI、創業、身份、愛、文化、管理、自動化

請以 JSON 格式回應，結構如下：
{
  "topics": ["標籤1", "標籤2"],
  "stance": "這時候的作者相信什麼",
  "tension": "這個信念跟什麼對立或矛盾（或 null）",
  "connections": ["跨領域串連1", "跨領域串連2"],
  "shift_signal": "轉變訊號（或 null）",
  "key_quote": "最代表這篇的一句原文"
}

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
        "stance": result.get("stance", ""),
        "tension": result.get("tension"),
        "connections": result.get("connections", []),
        "shift_signal": result.get("shift_signal"),
        "key_quote": result.get("key_quote", ""),
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

    # Group by topic
    by_topic = {}
    for ext in extractions:
        for topic in ext.get("topics", []):
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append({
                "timestamp": ext["timestamp"],
                "stance": ext["stance"],
                "tension": ext.get("tension"),
                "shift_signal": ext.get("shift_signal"),
                "key_quote": ext["key_quote"],
                "source": ext["source"],
            })

    # Sort each topic by timestamp
    for topic in by_topic:
        by_topic[topic].sort(key=lambda x: str(x["timestamp"]))

    profile = {
        "last_updated": str(max(str(e["timestamp"]) for e in extractions)) if extractions else "",
        "total_extractions": len(extractions),
        "topics": by_topic,
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
