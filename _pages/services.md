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

.service-item .service-tag.external {
  background: #e7f3ff;
  color: #0066cc;
}

.service-item .service-tag.private {
  background: #fce4ec;
  color: #c2185b;
}

.service-item .service-tag.public {
  background: #e8f5e9;
  color: #2e7d32;
}

.service-item .service-status {
  display: inline-block;
  margin-left: 10px;
  font-size: 0.75em;
}

.service-item .service-status .status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
}

.service-item .service-status.online .status-dot {
  background: #4caf50;
  animation: pulse 2s infinite;
}

.service-item .service-status.offline .status-dot {
  background: #f44336;
}

.service-item .service-status.checking .status-dot {
  background: #ff9800;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

#status-bar {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 24px;
  font-size: 0.9em;
  color: #666;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

#status-bar .overall-status {
  font-weight: 600;
}

#status-bar .overall-status.all-online {
  color: #4caf50;
}

#status-bar .overall-status.has-offline {
  color: #f44336;
}

#status-bar .last-check {
  font-size: 0.85em;
}

.service-item .github-link {
  display: inline-block;
  margin-top: 10px;
  font-size: 0.85em;
}

.service-item .github-link a {
  color: #666;
  text-decoration: none;
}

.service-item .github-link a:hover {
  color: #333;
}

.service-item .github-link svg {
  width: 16px;
  height: 16px;
  vertical-align: middle;
  margin-right: 4px;
  fill: currentColor;
}
</style>

# Services

<div id="status-bar">
  <span class="overall-status">Checking services...</span>
  <span class="last-check"></span>
</div>

<div class="services-list">

<div class="service-item" data-service="pdf2md">
  <h3><a href="https://pdf2md.neardws.com" target="_blank">PDF2MD</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">pdf2md.neardws.com</span>
  <p class="service-desc">PDF to Markdown conversion tool powered by MinerU. GitHub authentication required (<a href="https://github.com/EdgeAI-2000" target="_blank">@EdgeAI-2000</a> org members only).</p>
  <span class="service-tag public">Public (Lab)</span>
  <div class="github-link">
    <a href="https://github.com/opendatalab/MinerU" target="_blank">
      <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      opendatalab/MinerU
    </a>
  </div>
</div>

<div class="service-item" data-service="autofigure">
  <h3><a href="https://autofigure.neardws.com" target="_blank">AutoFigure-Edit</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">autofigure.neardws.com</span>
  <p class="service-desc">AI-powered academic figure editing and generation tool. GitHub authentication required (<a href="https://github.com/EdgeAI-2000" target="_blank">@EdgeAI-2000</a> org members only).</p>
  <span class="service-tag public">Public (Lab)</span>
  <div class="github-link">
    <a href="https://github.com/ResearAI/AutoFigure-Edit" target="_blank">
      <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      ResearAI/AutoFigure-Edit
    </a>
  </div>
</div>

<div class="service-item" data-service="1panel">
  <h3><a href="https://1panel.neardws.com" target="_blank">1Panel</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">1panel.neardws.com</span>
  <p class="service-desc">Modern Linux server management panel with web UI.</p>
  <span class="service-tag private">Private</span>
  <div class="github-link">
    <a href="https://github.com/1Panel-dev/1Panel" target="_blank">
      <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      1Panel-dev/1Panel
    </a>
  </div>
</div>

<div class="service-item" data-service="fish">
  <h3><a href="https://fish.neardws.com" target="_blank">BettaFish</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">fish.neardws.com</span>
  <p class="service-desc">Personal media and content management service.</p>
  <span class="service-tag private">Private</span>
  <div class="github-link">
    <a href="https://github.com/666ghj/BettaFish" target="_blank">
      <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      666ghj/BettaFish
    </a>
  </div>
</div>

<div class="service-item" data-service="mcp">
  <h3><a href="https://mcp.neardws.com" target="_blank">MetaMCP</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">mcp.neardws.com</span>
  <p class="service-desc">Model Context Protocol management service.</p>
  <span class="service-tag private">Private</span>
  <div class="github-link">
    <a href="https://github.com/metatool-ai/metamcp" target="_blank">
      <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      metatool-ai/metamcp
    </a>
  </div>
</div>

<div class="service-item" data-service="latex">
  <h3><a href="https://latex.neardws.com" target="_blank">OpenPrism</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">latex.neardws.com</span>
  <p class="service-desc">Open-source AI LaTeX writing workspace.</p>
  <span class="service-tag private">Private</span>
  <div class="github-link">
    <a href="https://github.com/assistant-ui/open-prism" target="_blank">
      <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      assistant-ui/open-prism
    </a>
  </div>
</div>

<div class="service-item" data-service="openclaw">
  <h3><a href="https://openclaw.neardws.com" target="_blank">OpenClaw</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">openclaw.neardws.com</span>
  <p class="service-desc">Self-hosted personal AI assistant.</p>
  <span class="service-tag private">Private</span>
  <div class="github-link">
    <a href="https://github.com/openclaw/openclaw" target="_blank">
      <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      openclaw/openclaw
    </a>
  </div>
</div>

<div class="service-item" data-service="coder">
  <h3><a href="https://coder.neardws.com" target="_blank">Coder</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">coder.neardws.com</span>
  <p class="service-desc">Remote VS Code development environment.</p>
  <span class="service-tag external">External</span>
  <div class="github-link">
    <a href="https://github.com/coder/coder" target="_blank">
      <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      coder/coder
    </a>
  </div>
</div>

<div class="service-item" data-service="vpn">
  <h3><a href="https://vpn.neardws.com" target="_blank">VPN</a> <span class="service-status checking"><span class="status-dot"></span><span class="status-text">Checking</span></span></h3>
  <span class="service-url">vpn.neardws.com</span>
  <p class="service-desc">Private VPN gateway for secure remote access.</p>
  <span class="service-tag external">External</span>
</div>

</div>

<script>
// Service health check
const services = [
  { name: 'pdf2md', url: 'https://pdf2md.neardws.com', checkPath: '/' },
  { name: 'autofigure', url: 'https://autofigure.neardws.com', checkPath: '/' },
  { name: '1panel', url: 'https://1panel.neardws.com', checkPath: '/' },
  { name: 'fish', url: 'https://fish.neardws.com', checkPath: '/' },
  { name: 'mcp', url: 'https://mcp.neardws.com', checkPath: '/' },
  { name: 'latex', url: 'https://latex.neardws.com', checkPath: '/' },
  { name: 'openclaw', url: 'https://openclaw.neardws.com', checkPath: '/' },
  { name: 'coder', url: 'https://coder.neardws.com', checkPath: '/' },
  { name: 'vpn', url: 'https://vpn.neardws.com', checkPath: '/' }
];

async function checkService(service) {
  const element = document.querySelector(`[data-service="${service.name}"] .service-status`);
  if (!element) return;

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    
    const response = await fetch(service.url + service.checkPath, {
      method: 'HEAD',
      mode: 'no-cors',
      signal: controller.signal
    });
    
    clearTimeout(timeout);
    
    // If we get here (no error), service is likely online
    // Note: no-cors returns opaque response, so we can't check status
    element.className = 'service-status online';
    element.querySelector('.status-text').textContent = 'Online';
    return true;
  } catch (error) {
    element.className = 'service-status offline';
    element.querySelector('.status-text').textContent = 'Offline';
    return false;
  }
}

async function checkAllServices() {
  const results = await Promise.all(services.map(checkService));
  const online = results.filter(r => r).length;
  const total = services.length;
  
  const statusBar = document.getElementById('status-bar');
  const overallStatus = statusBar.querySelector('.overall-status');
  const lastCheck = statusBar.querySelector('.last-check');
  
  if (online === total) {
    overallStatus.className = 'overall-status all-online';
    overallStatus.textContent = `All ${total} services online`;
  } else {
    overallStatus.className = 'overall-status has-offline';
    overallStatus.textContent = `${online}/${total} services online`;
  }
  
  const now = new Date();
  lastCheck.textContent = `Last check: ${now.toLocaleTimeString()}`;
}

// Check on load and every 60 seconds
checkAllServices();
setInterval(checkAllServices, 60000);
</script>