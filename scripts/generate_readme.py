#!/usr/bin/env python3
"""Generate README.md from content and worldview profile."""

import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT_DIR = ROOT / "content"
RAW_DIR = CONTENT_DIR / "raw"
PROFILE_PATH = CONTENT_DIR / "worldview-profile.yaml"
README_PATH = ROOT / "README.md"


def load_articles():
    """Load all articles sorted by date descending."""
    articles = []
    for f in sorted(RAW_DIR.glob("*.md"), reverse=True):
        if f.name.startswith("_"):
            continue
        text = f.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        fm = yaml.safe_load(parts[1])
        if fm:
            fm["_filename"] = f.name
            articles.append(fm)
    return articles


def load_profile():
    """Load worldview profile."""
    if not PROFILE_PATH.exists():
        return None
    with open(PROFILE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_articles_section(articles):
    """Generate articles table."""
    lines = ["## 文章\n"]
    lines.append("| 日期 | 標題 | 來源 |")
    lines.append("|------|------|------|")
    for a in articles:
        date = str(a.get("date", ""))
        title = a.get("title", "")
        source_type = a.get("source_type", "")
        source_url = a.get("source_url", "")
        if source_url:
            lines.append(f"| {date} | [{title}]({source_url}) | {source_type} |")
        else:
            lines.append(f"| {date} | {title} | {source_type} |")
    return "\n".join(lines)


def generate_worldview_section(profile):
    """Generate worldview summary."""
    if not profile or "topics" not in profile:
        return ""

    lines = ["## 世界觀快照\n"]
    lines.append(f"最後更新：{profile.get('last_updated', '?')}｜共 {profile.get('total_extractions', 0)} 篇萃取\n")

    for topic, entries in profile["topics"].items():
        if not entries:
            continue
        latest = entries[-1]
        lines.append(f"### {topic}\n")
        lines.append(f"{latest['stance']}\n")
        if latest.get("key_quote"):
            lines.append(f"> {latest['key_quote']}\n")
        if latest.get("tension"):
            lines.append(f"*張力：{latest['tension']}*\n")

    return "\n".join(lines)


def main():
    articles = load_articles()
    profile = load_profile()

    sections = []

    # Header
    sections.append("""# Sunny's README

一個活的、會演化的「我」的紀錄。

Perpetual Beta — 永久測試版本的自己就是最好版本。

---""")

    # Worldview
    if profile:
        sections.append(generate_worldview_section(profile))

    # Articles
    if articles:
        sections.append(generate_articles_section(articles))

    # Skill
    sections.append("""## Skill

這個 repo 包含一個 Claude Code Skill（`think-like-sunny`），用我的思考框架和語氣來回應問題。

<details>
<summary>怎麼使用</summary>

1. 在 Claude Code 裡把這個 repo 加為 project
2. 或直接把 `.claude/skills/think-like-sunny.md` 的內容貼進對話

Skill 會自動隨新文章更新「最近動態」層。核心身份和主題立場由我手動維護。
</details>""")

    # Footer
    sections.append("""---

*這份 README 由腳本自動生成。資料來源：Substack 文章、媒體報導、演講紀錄。*""")

    readme = "\n\n".join(sections) + "\n"
    README_PATH.write_text(readme, encoding="utf-8")
    print(f"✓ README.md generated ({len(articles)} articles, {profile.get('total_extractions', 0) if profile else 0} extractions)")


if __name__ == "__main__":
    main()
