---
layout: default
title: 媒體報導
permalink: /media/
---

# 媒體報導

{% assign media = site.pages | where_exp: "p", "p.path contains 'content/raw/'" | where: "source_type", "media" | sort: "date" | reverse %}
{% assign years = media | map: "date" | map: "year" | uniq %}

{% for year in years %}
## {{ year }}

{% assign year_posts = media | where_exp: "p", "p.date contains year" %}
{% for post in year_posts %}
<div class="entry">
  <span class="date">{{ post.date | date: "%Y-%m-%d" }}</span>
  <a href="{{ post.source_url }}">{{ post.title }}</a>
  {% if post.publication %}<span class="tag">{{ post.publication }}</span>{% endif %}
</div>
{% endfor %}
{% endfor %}

{% if media.size == 0 %}
還沒有媒體報導紀錄。用 `_template-media.md` 範本手動加入。
{% endif %}
