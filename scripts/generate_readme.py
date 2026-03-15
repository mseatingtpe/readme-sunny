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
SUBSTACK_URL = "https://masterofnonewithsunnyc.substack.com/"
IG_URL = "https://www.instagram.com/ms.eatingtpe/"
THREADS_URL = "https://www.threads.com/@ms.eatingtpe"

TOPICS = ["AI", "工作", "身份", "愛", "文化", "學習"]


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


def count_articles():
    """Count Substack articles."""
    count = 0
    for f in RAW_DIR.glob("*.md"):
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
            count += 1
    return count


def generate_worldview_snapshot(profile):
    """Generate a compact one-line-per-topic snapshot."""
    if not profile or "topics" not in profile:
        return ""

    lines = []
    for topic in TOPICS:
        entries = profile["topics"].get(topic, [])
        if not entries:
            continue
        latest = entries[-1]
        stance = latest.get("stance", "")
        # Truncate to first sentence if too long
        if len(stance) > 60:
            stance = stance[:58].rsplit("，", 1)[0] + "⋯"
        lines.append(f"**{topic}** — {stance}")

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
    profile = load_profile()
    media = load_media()
    article_count = count_articles()
    total_extractions = profile.get("total_extractions", 0) if profile else 0
    last_updated = profile.get("last_updated", "?") if profile else "?"

    sections = []

    # Header
    sections.append("""# Sunny's README

一個活的、會演化的「我」的紀錄。

*Perpetual Beta* — 永久測試版本的自己就是最好版本。

---""")

    # What is this
    sections.append(f"""## 這是什麼

這個 repo 是一個自動化的世界觀追蹤系統。每當我寫新文章或接受採訪，系統會自動萃取我對六個主題的立場，追蹤它們如何隨時間演變。

六個主題：**AI** · **工作** · **身份** · **愛** · **文化** · **學習**

目前已從 {total_extractions} 篇內容中萃取，最後更新：{last_updated}。""")

    # Worldview snapshot
    snapshot = generate_worldview_snapshot(profile)
    if snapshot:
        sections.append(f"""## 現在的我

{snapshot}

完整的演化過程、語錄、主題共現分析都在 **[互動式儀表板]({PAGES_URL})**。""")

    # Skill
    sections.append("""## Skill

這個 repo 包含一個 Claude Code Skill（[`think-like-sunny`](.claude/skills/think-like-sunny.md)），用我的思考框架和語氣來回應問題。

<details>
<summary>怎麼使用</summary>

1. 在 Claude Code 裡把這個 repo 加為 project
2. 或直接把 `.claude/skills/think-like-sunny.md` 的內容貼進對話

Skill 會自動隨新文章更新「最近動態」層。核心身份和主題立場由我手動維護。
</details>""")

    # Media
    if media:
        sections.append(generate_media_section(media))

    # Links (replaces article table)
    sections.append(f"""## 找到我

[Substack]({SUBSTACK_URL}) · [Instagram]({IG_URL}) · [Threads]({THREADS_URL})""")

    # Footer
    sections.append("""---

*這份 README 由腳本自動生成。資料來源：Substack 文章、媒體報導、演講紀錄。*""")

    readme = "\n\n".join(sections) + "\n"
    README_PATH.write_text(readme, encoding="utf-8")
    print(f"✓ README.md generated ({article_count} articles, {len(media)} media entries)")


if __name__ == "__main__":
    main()
