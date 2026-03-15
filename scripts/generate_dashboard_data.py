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
    """Load articles and build a source-path → metadata lookup."""
    articles = []
    source_lookup = {}  # "content/raw/filename.md" → {title, url}
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
            title = fm.get("title", "")
            url = fm.get("source_url", "")
            articles.append({
                "title": title,
                "date": str(fm.get("date", "")),
                "source_type": fm.get("source_type", ""),
                "source_url": url,
            })
            # Key matches the format used in worldview-profile.yaml
            source_lookup[f"content/raw/{f.name}"] = {
                "title": title,
                "url": url,
                "source_type": fm.get("source_type", ""),
            }
    articles.sort(key=lambda x: x["date"])
    return articles, source_lookup


def load_profile():
    if not PROFILE_PATH.exists():
        return None
    with open(PROFILE_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    profile = load_profile()
    articles, source_lookup = load_articles()

    def enrich_entry(entry):
        """Add source_title and source_url from lookup."""
        source = entry.get("source", "")
        meta = source_lookup.get(source, {})
        enriched = dict(entry)
        enriched["source_title"] = meta.get("title", "")
        enriched["source_url"] = meta.get("url", "")
        enriched["source_type"] = meta.get("source_type", "")
        return enriched

    # Collect timeline events from all topic entries
    timeline = []
    seen = set()
    if profile and "topics" in profile:
        for topic, entries in profile["topics"].items():
            for entry in entries:
                source = entry.get("source", "")
                key = (entry["timestamp"], source)
                meta = source_lookup.get(source, {})
                if key not in seen:
                    seen.add(key)
                    timeline.append({
                        "date": str(entry["timestamp"]),
                        "stance": entry.get("stance", ""),
                        "key_quote": entry.get("key_quote", ""),
                        "tension": entry.get("tension"),
                        "shift_signal": entry.get("shift_signal"),
                        "source": source,
                        "source_title": meta.get("title", ""),
                        "source_url": meta.get("url", ""),
                        "source_type": meta.get("source_type", ""),
                        "topics": [topic],
                    })
                else:
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

    # Enrich topic entries with source metadata
    enriched_topics = {}
    if profile and "topics" in profile:
        for topic, entries in profile["topics"].items():
            enriched_topics[topic] = [enrich_entry(e) for e in entries]

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
        "topics": enriched_topics,
        "keywords": keywords,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ docs/data.json ({len(timeline)} timeline events, {len(topic_counts)} topics)")


if __name__ == "__main__":
    main()
