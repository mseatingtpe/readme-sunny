---
layout: default
title: Sunny's README
---

# Sunny's README

一個活的、會演化的「我」的紀錄。

Perpetual Beta — 永久測試版本的自己就是最好版本。

## 最新文章

{% assign sorted = site.pages | where_exp: "p", "p.path contains 'content/raw/'" | sort: "date" | reverse %}
{% for post in sorted limit: 5 %}
<div class="entry">
  <span class="date">{{ post.date | date: "%Y-%m-%d" }}</span>
  <a href="{{ post.url }}">{{ post.title }}</a>
  <span class="tag">{{ post.source_type }}</span>
</div>
{% endfor %}

[所有文章 →](/content)
