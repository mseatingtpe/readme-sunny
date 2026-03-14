#!/usr/bin/env python3
"""Generate docs/data.json from worldview-profile.yaml and articles."""

import json
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT_DIR = ROOT / "content"
RAW_DIR = CONTENT_DIR / "raw"
PROFILE_PATH = CONTENT_DIR / "worldview-profile.yaml"
OUTPUT_PATH = ROOT / "docs" / "data.json"


def load_articles():
    articles = []
    for f in sorted(RAW_DIR.glob("*.md")):
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
            articles.append({
                "title": fm.get("title", ""),
                "date": str(fm.get("date", "")),
                "source_type": fm.get("source_type", ""),
                "source_url": fm.get("source_url", ""),
            })
    articles.sort(key=lambda x: x["date"])
    return articles


def load_profile():
    if not PROFILE_PATH.exists():
        return None
    with open(PROFILE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    profile = load_profile()
    articles = load_articles()

    # Collect timeline events from all topic entries
    timeline = []
    seen = set()
    if profile and "topics" in profile:
        for topic, entries in profile["topics"].items():
            for entry in entries:
                source = entry.get("source", "")
                key = (entry["timestamp"], source)
                if key not in seen:
                    seen.add(key)
                    timeline.append({
                        "date": str(entry["timestamp"]),
                        "stance": entry.get("stance", ""),
                        "key_quote": entry.get("key_quote", ""),
                        "tension": entry.get("tension"),
                        "shift_signal": entry.get("shift_signal"),
                        "source": source,
                        "topics": [topic],
                    })
                else:
                    # Add topic to existing entry
                    for t in timeline:
                        if str(t["date"]) == str(entry["timestamp"]) and t["source"] == source:
                            if topic not in t["topics"]:
                                t["topics"].append(topic)
                            break

    timeline.sort(key=lambda x: x["date"])

    # Topic counts for radar
    topic_counts = {}
    if profile and "topics" in profile:
        for topic, entries in profile["topics"].items():
            topic_counts[topic] = len(entries)

    # Keywords for word cloud
    keywords = {}
    if profile and "keywords" in profile:
        keywords = profile["keywords"]

    data = {
        "last_updated": profile.get("last_updated", "") if profile else "",
        "total_extractions": profile.get("total_extractions", 0) if profile else 0,
        "articles": articles,
        "timeline": timeline,
        "topic_counts": topic_counts,
        "topics": dict(profile["topics"]) if profile and "topics" in profile else {},
        "keywords": keywords,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ docs/data.json ({len(timeline)} timeline events, {len(topic_counts)} topics)")


if __name__ == "__main__":
    main()
