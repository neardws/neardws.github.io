/**
 * Grant Cards Renderer
 * Dynamically renders grant cards from JSON data
 * With filtering and search functionality (similar to publications)
 */

class GrantCards {
  constructor() {
    this.data = [];
    this.filteredData = [];
    this.activeFilter = 'all';
    this.searchQuery = '';
    this.container = null;
  }

  async init() {
    this.container = document.getElementById('grant-container');
    if (!this.container) return;

    try {
      const res = await fetch('assets/data/grants.json');
      this.data = await res.json();

      // Sort by start year (newest first)
      this.data.sort((a, b) => {
        const getStartYear = (period) => {
          const match = period.match(/(\d{4})/);
          return match ? parseInt(match[1]) : 0;
        };
        return getStartYear(b.period) - getStartYear(a.period);
      });

      // Add start_year to each grant for display
      this.data = this.data.map(g => ({
        ...g,
        start_year: this.extractStartYear(g.period)
      }));

      this.filteredData = [...this.data];
      this.render();
    } catch (e) {
      console.warn('Failed to load grants:', e);
      this.container.innerHTML = '<p>Failed to load grants.</p>';
    }
  }

  extractStartYear(period) {
    const match = period.match(/(\d{4})/);
    return match ? parseInt(match[1]) : null;
  }

  render() {
    const stats = this.getStats();
    const filters = this.getFilters();

    this.container.innerHTML = `
      ${stats}
      <div class="grant-controls">
        <div class="grant-filters" id="grant-filters">${filters}</div>
        <input type="text" class="grant-search" id="grant-search" placeholder="Search title, number, source..." value="${this.searchQuery}">
      </div>
      <div class="grant-list" id="grant-list">
        ${this.filteredData.map(g => this.renderCard(g)).join('')}
      </div>
    `;

    this.bindEvents();
  }

  getStats() {
    const piCount = this.data.filter(p => p.role === 'PI').length;
    const participantCount = this.data.filter(p => p.role !== 'PI').length;
    const totalAmount = this.data.reduce((sum, p) => {
      const match = p.amount.match(/[\d,]+/);
      return sum + (match ? parseInt(match[0].replace(/,/g, '')) : 0);
    }, 0);

    return `
      <div class="grant-stats">
        <div class="grant-stat">
          <span class="grant-stat-value">${piCount}</span>
          <span class="grant-stat-label">PI/Co-PI</span>
        </div>
        <div class="grant-stat">
          <span class="grant-stat-value">${participantCount}</span>
          <span class="grant-stat-label">Participated</span>
        </div>
        <div class="grant-stat">
          <span class="grant-stat-value">${this.formatAmount(totalAmount)}</span>
          <span class="grant-stat-label">Total (CNY)</span>
        </div>
      </div>
      <div class="grant-sources">${this.renderSources()}</div>
    `;
  }

  renderSources() {
    const sources = [...new Set(this.data.map(p => p.source.name))];
    return sources.map(name => {
      const src = this.data.find(p => p.source.name === name)?.source;
      if (!src) return '';
      const iconHtml = src.icon
        ? `<img src="${src.icon}" alt="${src.name}" class="grant-source-icon">`
        : `<span class="grant-source-icon-text">${src.name}</span>`;
      const linkHtml = src.url
        ? `<a href="${src.url}" target="_blank" class="grant-source-link no-underline">${iconHtml}<span class="grant-source-name-text"><strong>${src.name}</strong>: ${src.full_name}</span></a>`
        : `<span class="grant-source-link">${iconHtml}<span class="grant-source-name-text"><strong>${src.name}</strong>: ${src.full_name}</span></span>`;
      return `<div class="grant-source-item">${linkHtml}</div>`;
    }).join('');
  }

  getFilters() {
    const sources = ['all', ...new Set(this.data.map(p => p.source.name))];
    const sourceLabels = {
      'all': 'All',
      'NSFC': 'NSFC',
      'GBABRF': 'GBABRF',
      'SSTP': 'SSTP',
      'CPSF': 'CPSF',
      'ERC': 'ERC'
    };

    return sources.map(source => {
      const label = sourceLabels[source] || source;
      const active = this.activeFilter === source ? 'grant-filter--active' : '';
      return `<button class="grant-filter ${active}" data-filter="${source}">${label}</button>`;
    }).join('');
  }

  renderCard(grant) {
    const iconHtml = grant.source.icon
      ? `<img src="${grant.source.icon}" alt="${grant.source.name}" class="grant-card-icon">`
      : `<div class="grant-card-icon-placeholder">${grant.source.name}</div>`;

    const yearHtml = grant.start_year
      ? `<div class="grant-card-year">${grant.start_year}</div>`
      : '';

    const roleTag = grant.role === 'PI'
      ? '<span class="grant-role-tag grant-role-tag--pi">PI</span>'
      : '';

    const noteHtml = grant.note
      ? `<div class="grant-note">${grant.note}</div>`
      : '';

    return `
      <div class="grant-card" data-source="${grant.source.name}">
        <div class="grant-card-left">
          ${iconHtml}
          ${yearHtml}
        </div>
        <div class="grant-card-content">
          <div class="grant-card-header">
            <span class="grant-source-name">${grant.source.name}</span>
            ${roleTag}
            <span class="grant-type">${grant.type}</span>
          </div>
          <div class="grant-title">${grant.title}</div>
          <div class="grant-meta">
            <span class="grant-number">${grant.number}</span>
            <span class="grant-amount">${grant.amount}</span>
            <span class="grant-period">${grant.period}</span>
          </div>
          ${noteHtml}
        </div>
      </div>
    `;
  }

  bindEvents() {
    // Filter buttons
    document.querySelectorAll('.grant-filter').forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeFilter = btn.dataset.filter;
        this.applyFilters();
      });
    });

    // Search input
    const searchInput = document.getElementById('grant-search');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.toLowerCase();
        this.applyFilters();
      });
    }
  }

  applyFilters() {
    this.filteredData = this.data.filter(g => {
      // Filter by source
      const matchesFilter = this.activeFilter === 'all' || g.source.name === this.activeFilter;

      // Filter by search query
      const matchesSearch = !this.searchQuery ||
        g.title.toLowerCase().includes(this.searchQuery) ||
        g.number.toLowerCase().includes(this.searchQuery) ||
        g.source.name.toLowerCase().includes(this.searchQuery) ||
        g.source.full_name.toLowerCase().includes(this.searchQuery);

      return matchesFilter && matchesSearch;
    });

    // Update UI
    this.updateFiltersUI();
    this.updateListUI();
  }

  updateFiltersUI() {
    document.querySelectorAll('.grant-filter').forEach(btn => {
      btn.classList.toggle('grant-filter--active', btn.dataset.filter === this.activeFilter);
    });
  }

  updateListUI() {
    const list = document.getElementById('grant-list');
    if (list) {
      list.innerHTML = this.filteredData.map(g => this.renderCard(g)).join('');
    }
  }

  formatAmount(amount) {
    if (amount >= 1000000) {
      return (amount / 1000000).toFixed(1) + 'M';
    } else if (amount >= 1000) {
      return (amount / 1000).toFixed(0) + 'K';
    }
    return amount.toString();
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const grants = new GrantCards();
  grants.init();
});