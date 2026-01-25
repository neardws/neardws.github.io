---
permalink: /services/
title: "Services"
layout: default
author_profile: true
---

<style>
.services-list {
  max-width: 800px;
}

.service-item {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.service-item:hover {
  border-color: #8e8e93;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  transform: translateY(-2px);
}

.service-item h3 {
  margin: 0 0 8px 0;
  font-size: 1.3em;
}

.service-item h3 a {
  color: #333;
  text-decoration: none;
}

.service-item h3 a:hover {
  color: #636366;
}

.service-item .service-url {
  color: #007aff;
  font-size: 0.9em;
  margin-bottom: 12px;
  display: block;
}

.service-item .service-desc {
  color: #555;
  line-height: 1.6;
  margin: 0;
}

.service-item .service-tag {
  display: inline-block;
  background: #f0f0f0;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 0.8em;
  color: #666;
  margin-top: 12px;
}

.service-item .service-tag.internal {
  background: #fff3cd;
  color: #856404;
}

.service-item .service-tag.public {
  background: #d4edda;
  color: #155724;
}
</style>

# Services

Self-hosted services running via Cloudflare Tunnel.

<div class="services-list">

<div class="service-item">
  <h3><a href="https://fish.neardws.com" target="_blank">BettaFish</a></h3>
  <span class="service-url">fish.neardws.com</span>
  <p class="service-desc">Personal media and content management service.</p>
  <span class="service-tag internal">Internal</span>
</div>

<div class="service-item">
  <h3><a href="https://1panel.neardws.com" target="_blank">1Panel</a></h3>
  <span class="service-url">1panel.neardws.com</span>
  <p class="service-desc">Modern Linux server management panel with web UI.</p>
  <span class="service-tag internal">Internal</span>
</div>

<div class="service-item">
  <h3><a href="https://kanban.neardws.com" target="_blank">Kanban</a></h3>
  <span class="service-url">kanban.neardws.com</span>
  <p class="service-desc">Project management and task tracking board.</p>
  <span class="service-tag internal">Internal</span>
</div>

<div class="service-item">
  <h3><a href="https://mcp.neardws.com" target="_blank">MetaMCP</a></h3>
  <span class="service-url">mcp.neardws.com</span>
  <p class="service-desc">Model Context Protocol management service.</p>
  <span class="service-tag internal">Internal</span>
</div>

<div class="service-item">
  <h3><a href="https://embedding.neardws.com" target="_blank">Embedding Service</a></h3>
  <span class="service-url">embedding.neardws.com</span>
  <p class="service-desc">Vector embedding API for semantic search and AI applications.</p>
  <span class="service-tag internal">Internal</span>
</div>

<div class="service-item">
  <h3><a href="https://cliproxy.neardws.com" target="_blank">CLI Proxy API</a></h3>
  <span class="service-url">cliproxy.neardws.com</span>
  <p class="service-desc">Command-line interface proxy service for remote access.</p>
  <span class="service-tag internal">Internal</span>
</div>

</div>
