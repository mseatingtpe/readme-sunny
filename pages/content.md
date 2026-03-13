---
layout: default
title: 所有文章
permalink: /content/
---

# 所有文章

{% assign sorted = site.pages | where_exp: "p", "p.path contains 'content/raw/'" | sort: "date" | reverse %}
{% for post in sorted %}
<div class="entry">
  <span class="date">{{ post.date | date: "%Y-%m-%d" }}</span>
  <a href="{{ post.url }}">{{ post.title }}</a>
  <span class="tag">{{ post.source_type }}</span>
  {% if post.publication %}<span class="tag">{{ post.publication }}</span>{% endif %}
</div>
{% endfor %}
