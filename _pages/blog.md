---
permalink: /blog/
title: "Blog"
layout: default
author_profile: true
---

# Blog

<div class="blog-list">
{% assign main_posts = site.posts | where_exp: "post", "post.lang != 'en'" %}
{% for post in main_posts %}
  <article class="blog-item">
    <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
    <p class="post-meta">
      {{ post.date | date: "%B %d, %Y" }}
      {% if post.categories.size > 0 %}
        | {% for cat in post.categories %}<span class="category-tag">{{ cat }}</span>{% unless forloop.last %} {% endunless %}{% endfor %}
      {% endif %}
    </p>
    <p class="post-excerpt">{{ post.excerpt | strip_html | truncate: 200 }}</p>
    <p class="post-languages">
      🌐 <a href="{{ post.url }}">中文</a> | <a href="{{ post.url | replace: '/vibe-coding-best-practices/', '/vibe-coding-best-practices-en/' }}">English</a>
    </p>
  </article>
  <hr>
{% endfor %}
</div>

{% if main_posts.size == 0 %}
<p>No blog posts yet. Stay tuned!</p>
{% endif %}
