#!/usr/bin/env python3
"""Generate README.md from content, worldview profile, and media data."""

import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT_DIR = ROOT / "content"
RAW_DIR = CONTENT_DIR / "raw"
PROFILE_PATH = CONTENT_DIR / "worldview-profile.yaml"
MEDIA_PATH = CONTENT_DIR / "media.yaml"
README_PATH = ROOT / "README.md"

PAGES_URL = "https://mseatingtpe.github.io/readme-sunny/"


def load_articles():
    """Load Substack articles sorted by date descending."""
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
        if fm and fm.get("source_type") == "substack":
            articles.append(fm)
    return articles


def load_profile():
    """Load worldview profile."""
    if not PROFILE_PATH.exists():
        return None
    with open(PROFILE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_media():
    """Load media data."""
    if not MEDIA_PATH.exists():
        return []
    with open(MEDIA_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data else []


def generate_articles_section(articles):
    """Generate Substack articles table."""
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


def generate_media_section(media):
    """Generate media & talks section from media.yaml."""
    if not media:
        return ""

    interviews = sorted([m for m in media if m.get("type") == "interview"],
                        key=lambda x: str(x.get("date", "")), reverse=True)
    talks = sorted([m for m in media if m.get("type") == "talk"],
                   key=lambda x: str(x.get("date", "")), reverse=True)
    writing = sorted([m for m in media if m.get("type") == "writing"],
                     key=lambda x: str(x.get("date", "")), reverse=True)

    lines = ["## 媒體與分享\n"]

    if interviews:
        lines.append("### 採訪報導\n")
        lines.append("| 日期 | 標題 | 媒體 |")
        lines.append("|------|------|------|")
        for m in interviews:
            date = str(m.get("date", ""))
            title = m.get("title", "")
            pub = m.get("publication", "")
            url = m.get("url", "")
            if url:
                lines.append(f"| {date} | [{title}]({url}) | {pub} |")
            else:
                lines.append(f"| {date} | {title} | {pub} |")
        lines.append("")

    if talks:
        lines.append("### 演講與論壇\n")
        lines.append("| 日期 | 主題 | 場合 |")
        lines.append("|------|------|------|")
        for m in talks:
            date = str(m.get("date", ""))
            title = m.get("title", "")
            pub = m.get("publication", "")
            url = m.get("url", "")
            if url:
                lines.append(f"| {date} | [{title}]({url}) | {pub} |")
            else:
                lines.append(f"| {date} | {title} | {pub} |")
        lines.append("")

    if writing:
        lines.append("### 供稿\n")
        lines.append("| 日期 | 標題 | 刊物 |")
        lines.append("|------|------|------|")
        for m in writing:
            date = str(m.get("date", ""))
            title = m.get("title", "")
            pub = m.get("publication", "")
            url = m.get("url", "")
            if url:
                lines.append(f"| {date} | [{title}]({url}) | {pub} |")
            else:
                lines.append(f"| {date} | {title} | {pub} |")
        lines.append("")

    return "\n".join(lines)


def main():
    articles = load_articles()
    profile = load_profile()
    media = load_media()

    sections = []

    # Header
    sections.append("""# Sunny's README

一個活的、會演化的「我」的紀錄。

Perpetual Beta — 永久測試版本的自己就是最好版本。

---""")

    # Skill (moved to top for prominence)
    sections.append("""## Skill

這個 repo 包含一個 Claude Code Skill（`think-like-sunny`），用我的思考框架和語氣來回應問題。

<details>
<summary>怎麼使用</summary>

1. 在 Claude Code 裡把這個 repo 加為 project
2. 或直接把 `.claude/skills/think-like-sunny.md` 的內容貼進對話

Skill 會自動隨新文章更新「最近動態」層。核心身份和主題立場由我手動維護。
</details>""")

    # Worldview
    if profile:
        sections.append(generate_worldview_section(profile))

    # Dashboard
    sections.append(f"""## 互動式儀表板

包含四個視覺化：世界觀演化網格、文字雲、時間軸、主題雷達圖。

[前往儀表板]({PAGES_URL})""")

    # Media
    if media:
        sections.append(generate_media_section(media))

    # Articles
    if articles:
        sections.append(generate_articles_section(articles))

    # Footer
    sections.append("""---

*這份 README 由腳本自動生成。資料來源：Substack 文章、媒體報導、演講紀錄。*""")

    readme = "\n\n".join(sections) + "\n"
    README_PATH.write_text(readme, encoding="utf-8")
    print(f"✓ README.md generated ({len(articles)} articles, {len(media)} media entries)")


if __name__ == "__main__":
    main()
