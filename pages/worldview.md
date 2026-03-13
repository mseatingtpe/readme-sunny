---
layout: default
title: 世界觀演變
permalink: /worldview/
---

# 世界觀演變

這個頁面追蹤我在不同主題上的信念如何隨時間改變。

資料來自每篇文章的萃取結果。每個主題下按時間排列，讓你看到演變的軌跡。

{% assign extractions = site.data.extractions %}

{% if site.data.worldview-profile %}
{% assign profile = site.data.worldview-profile %}

**最後更新：** {{ profile.last_updated }}
**總萃取數：** {{ profile.total_extractions }}

{% for topic in profile.topics %}
## {{ topic[0] }}

{% for entry in topic[1] %}
<div class="entry">
  <span class="date">{{ entry.timestamp }}</span>
  <p>{{ entry.stance }}</p>
  {% if entry.tension %}<p><strong>張力：</strong>{{ entry.tension }}</p>{% endif %}
  {% if entry.shift_signal %}<p><strong>轉變：</strong>{{ entry.shift_signal }}</p>{% endif %}
  {% if entry.key_quote %}<blockquote>{{ entry.key_quote }}</blockquote>{% endif %}
</div>
{% endfor %}
{% endfor %}

{% else %}
尚未產生世界觀 profile。執行萃取後會自動生成。
{% endif %}
