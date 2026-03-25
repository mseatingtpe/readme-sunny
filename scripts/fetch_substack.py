#!/usr/bin/env python3
"""Fetch new articles from a Substack RSS feed and save as Markdown files."""

import argparse
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from html.parser import HTMLParser


CONTENT_DIR = Path(__file__).parent.parent / "content" / "raw"
DEFAULT_FEED_URL = "https://masterofnonewithsunnyc.substack.com/feed"


class HTMLToMarkdown(HTMLParser):
    """Minimal HTML to Markdown converter."""

    def __init__(self):
        super().__init__()
        self.result = []
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == "p":
            self.result.append("\n\n")
        elif tag in ("h1", "h2", "h3", "h4"):
            level = int(tag[1])
            self.result.append(f"\n\n{'#' * level} ")
        elif tag == "br":
            self.result.append("\n")
        elif tag == "a":
            href = dict(attrs).get("href", "")
            self.result.append(f"[")
            self._href = href
        elif tag in ("strong", "b"):
            self.result.append("**")
        elif tag in ("em", "i"):
            self.result.append("*")
        elif tag == "li":
            self.result.append("\n- ")
        elif tag == "blockquote":
            self.result.append("\n\n> ")

    def handle_endtag(self, tag):
        if tag == "a":
            href = getattr(self, "_href", "")
            self.result.append(f"]({href})")
        elif tag in ("strong", "b"):
            self.result.append("**")
        elif tag in ("em", "i"):
            self.result.append("*")
        self.current_tag = None

    def handle_data(self, data):
        self.result.append(data)

    def get_text(self):
        return re.sub(r"\n{3,}", "\n\n", "".join(self.result).strip())


def html_to_markdown(html_content):
    parser = HTMLToMarkdown()
    parser.feed(html_content)
    return parser.get_text()


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].rstrip("-")


def get_existing_urls():
    """Scan existing files for source_url to detect duplicates."""
    urls = set()
    for f in CONTENT_DIR.glob("*.md"):
        if f.name.startswith("_"):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            for line in content.split("\n"):
                if line.startswith("source_url:"):
                    url = line.split(":", 1)[1].strip().strip('"').strip("'")
                    if url:
                        urls.add(url)
                    break
        except Exception:
            continue
    return urls


def fetch_feed(feed_url):
    """Fetch and parse RSS feed. Returns None if feed is unreachable."""
    req = Request(feed_url, headers={"User-Agent": "sunny-readme/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            return ET.parse(resp)
    except Exception as e:
        print(f"Warning: could not fetch feed: {e}")
        return None


def parse_date(date_str):
    """Parse RSS date format to datetime."""
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return datetime.now()


def save_article(title, date, url, content_html):
    """Save article as Markdown file with YAML frontmatter."""
    date_str = date.strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{date_str}-{slug}.md"
    filepath = CONTENT_DIR / filename

    body = html_to_markdown(content_html)

    frontmatter = f"""---
title: "{title}"
date: {date_str}
source_type: substack
source_url: "{url}"
tags: []
---

{body}
"""
    filepath.write_text(frontmatter, encoding="utf-8")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Fetch Substack RSS articles")
    parser.add_argument("--feed-url", default=DEFAULT_FEED_URL, help="RSS feed URL")
    parser.add_argument("--force", action="store_true", help="Re-fetch existing articles")
    args = parser.parse_args()

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    existing_urls = set() if args.force else get_existing_urls()
    tree = fetch_feed(args.feed_url)
    if tree is None:
        print("\nDone: 0 new, 0 skipped (feed unavailable)")
        return
    root = tree.getroot()

    new_count = 0
    skip_count = 0

    for item in root.iter("item"):
        title = item.findtext("title", "Untitled")
        link = item.findtext("link", "")
        pub_date = item.findtext("pubDate", "")
        content = item.findtext("{http://purl.org/rss/1.0/modules/content/}encoded", "")
        if not content:
            content = item.findtext("description", "")

        if link in existing_urls:
            skip_count += 1
            continue

        date = parse_date(pub_date) if pub_date else datetime.now()
        filepath = save_article(title, date, link, content)
        new_count += 1
        print(f"✓ {filepath.name}")

    print(f"\nDone: {new_count} new, {skip_count} skipped")


if __name__ == "__main__":
    main()
