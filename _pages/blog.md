---
permalink: /blog/
title: "Blog"
layout: default
author_profile: true
---

<style>
.blog-list {
  max-width: 800px;
}

.blog-item {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.blog-item:hover {
  border-color: #c00;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.blog-item h2 {
  margin: 0 0 12px 0;
  font-size: 1.4em;
}

.blog-item h2 a {
  color: #333;
  text-decoration: none;
}

.blog-item h2 a:hover {
  color: #c00;
}

.blog-item .post-meta {
  color: #888;
  font-size: 0.9em;
  margin-bottom: 12px;
}

.blog-item .category-tag {
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85em;
  margin-left: 4px;
}

.blog-item .post-excerpt {
  color: #555;
  line-height: 1.6;
  margin: 0;
}

.blog-list hr {
  display: none;
}

.blog-item .post-lang-link {
  margin-top: 12px;
  margin-bottom: 0;
}

.blog-item .post-lang-link a {
  color: #888;
  font-size: 0.85em;
  text-decoration: none;
  padding: 4px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.blog-item .post-lang-link a:hover {
  color: #c00;
  border-color: #c00;
  background: #fff5f5;
}
</style>

# Blog

<div class="blog-list">
{% assign main_posts = site.posts | where: "lang", "en" %}
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
    <p class="post-lang-link">
      <a href="{{ post.url | replace: '-en/', '/' }}">🇨🇳 中文版</a>
    </p>
  </article>
{% endfor %}
</div>

{% if main_posts.size == 0 %}
<p>No blog posts yet. Stay tuned!</p>
{% endif %}
