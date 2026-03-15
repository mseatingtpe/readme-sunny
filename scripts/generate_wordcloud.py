#!/usr/bin/env python3
"""Generate word frequency data from all articles using jieba.

Output includes per-word article associations (top 3) for hover display.
"""

import json
import re
import jieba
import yaml
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).parent.parent
RAW_DIR = ROOT / "content" / "raw"
NOTES_PATH = ROOT / "content" / "substack_notes.md"
OUTPUT_PATH = ROOT / "docs" / "wordcloud.json"

# Stop words — common words that don't carry meaning
STOP_WORDS = {
    # Chinese function words
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一個",
    "上", "也", "而", "到", "說", "要", "會", "可以", "這", "那", "他", "她", "它",
    "們", "很", "看", "去", "又", "把", "被", "從", "但", "對", "讓", "用", "好",
    "如果", "因為", "所以", "還", "沒有", "什麼", "這個", "那個", "自己", "沒",
    "過", "裡", "後", "來", "做", "能", "想", "你", "嗎", "呢", "吧", "啊",
    "時候", "知道", "覺得", "東西", "事情", "這樣", "那樣", "為了", "然後",
    "已經", "還是", "或者", "不是", "只是", "其實", "可能", "應該", "需要",
    "比較", "以後", "之後", "以前", "之前", "開始", "出來", "起來", "下來",
    "進去", "回來", "每個", "一些", "一樣", "不會", "怎麼", "多少", "這些",
    "那些", "大家", "如何", "為什麼", "所有", "一直", "真的", "而且", "不過",
    "當然", "其中", "任何", "之間", "通過", "關於", "以及", "是否", "雖然",
    "同時", "總是", "必須", "只要", "甚至", "最後", "當時",
    # English stop words
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "and", "or", "but", "not", "no", "so", "if", "it", "its", "this",
    "that", "these", "those", "my", "your", "his", "her", "our", "their",
    "me", "him", "us", "them", "who", "what", "which", "when", "where",
    "how", "why", "all", "each", "every", "both", "few", "more", "most",
    "other", "some", "such", "than", "too", "very", "just", "about",
    # Misc / markdown / URL artifacts
    "https", "http", "www", "com", "substack", "auto", "utm",
    "source", "medium", "campaign", "content", "post",
    "我們", "就是", "一種", "時間", "事", "下",
    "問題", "成為", "地方", "方式", "過程", "部分",
    "最", "更", "像是", "得到", "告訴", "發現",
    "完成", "擁有", "理解", "帶來", "認為", "使用",
    "包括", "產生", "面對", "提供", "表示", "成為",
    "重要", "工具", "方法", "結果", "根據", "進行",
    "而是", "感到", "透過", "因此", "一起", "合作",
    "這樣", "真正", "不同", "愛的", "只是", "現在",
    "後來", "最近", "今天", "昨天", "明天", "第一",
    "note", "substack", "備註", "抓取",
}

# Custom dictionary — important terms jieba might split wrong
CUSTOM_WORDS = [
    "AI", "perpetual beta", "dirty work", "Work-Life", "ChatGPT",
    "哲學", "框架", "品味", "真誠", "信念", "靈魂", "管理債務",
    "世界觀", "連連看", "合約產生器", "生產力工具", "女性主義",
    "以柔制剛", "心流", "數位遊牧", "試算表",
]

# Important single-char words to keep
KEEP_SINGLE = {"愛", "人", "書"}


def clean_text(text):
    """Remove URLs, markdown syntax, and HTML artifacts."""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)  # [text](url) -> text
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # images
    text = re.sub(r'#{1,6}\s*', '', text)  # headings
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)  # bold/italic
    text = re.sub(r'<[^>]+>', '', text)  # HTML tags
    text = re.sub(r'[_*`~|>]+', ' ', text)  # markdown chars
    return text


def is_valid_word(w):
    """Check if a word should be counted."""
    if len(w) < 2 and w not in KEEP_SINGLE:
        return False
    if w.lower() in STOP_WORDS or w in STOP_WORDS:
        return False
    if re.match(r'^[\d\s\.,;:!?\-—–…「」『』（）\(\)\[\]#*_/=&%@]+$', w):
        return False
    if re.match(r'^[a-zA-Z]{1,3}$', w):
        return False
    return True


def load_and_segment_articles():
    """Load articles individually, segment each, track word→article mapping."""
    for w in CUSTOM_WORDS:
        jieba.add_word(w)

    counter = Counter()
    # word → list of {title, url, count_in_article}
    word_articles = defaultdict(list)

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
        if not fm:
            continue

        title = fm.get("title", "")
        url = fm.get("source_url", "")
        body = clean_text(parts[2])

        # Count words in this article
        article_counter = Counter()
        for word in jieba.cut(body):
            w = word.strip()
            if is_valid_word(w):
                article_counter[w] += 1

        # Update global counter and word→article mapping
        for w, c in article_counter.items():
            counter[w] += c
            word_articles[w].append({
                "title": title,
                "url": url,
                "count": c,
            })

    # Include Substack Notes (no article association)
    if NOTES_PATH.exists():
        notes_text = clean_text(NOTES_PATH.read_text(encoding="utf-8"))
        for word in jieba.cut(notes_text):
            w = word.strip()
            if is_valid_word(w):
                counter[w] += 1

    return counter, word_articles


def main():
    counter, word_articles = load_and_segment_articles()

    # Top 100 words
    top = counter.most_common(100)

    result = []
    for w, c in top:
        # Sort articles by count descending, take top 3
        arts = sorted(word_articles.get(w, []), key=lambda x: x["count"], reverse=True)[:3]
        entry = {
            "word": w,
            "count": c,
            "articles": [{"title": a["title"], "url": a["url"]} for a in arts],
        }
        result.append(entry)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✓ docs/wordcloud.json ({len(result)} words)")
    print(f"  Top 10: {', '.join(f'{w}({c})' for w, c in top[:10])}")


if __name__ == "__main__":
    main()
