---
permalink: /blog/
title: "Blog"
layout: default
author_profile: true
---

# Blog

<div class="blog-list">
{% for post in site.posts %}
  <article class="blog-item">
    <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
    <p class="post-meta">{{ post.date | date: "%B %d, %Y" }}</p>
    <p class="post-excerpt">{{ post.excerpt | strip_html | truncate: 200 }}</p>
  </article>
  <hr>
{% endfor %}
</div>

{% if site.posts.size == 0 %}
<p>No blog posts yet. Stay tuned!</p>
{% endif %}
