/**
 * Grant Cards Renderer
 * Dynamically renders grant cards from JSON data
 * With filtering and search functionality (style matches publications)
 */

class GrantCards {
  constructor() {
    this.data = [];
    this.filteredData = [];
    this.activeFilter = 'all';
    this.activeRoleFilter = 'all';
    this.searchQuery = '';
    this.container = null;
  }

  async init() {
    this.container = document.getElementById('grant-container');
    if (!this.container) return;

    try {
      const res = await fetch('/assets/data/grants.json');
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
    const counts = this.getCounts();
    const stats = this.getStats();
    const legend = this.renderLegend();

    this.container.innerHTML = `
      ${legend}
      ${stats}
      <div class="grant-controls">
        <div class="grant-filters" id="grant-filters"></div>
        <input type="text" class="grant-search" id="grant-search" placeholder="Search title, number, source...">
      </div>
      <div class="grant-list" id="grant-list">
        ${this.filteredData.map(g => this.renderCard(g)).join('')}
      </div>
    `;

    this.renderFilters(counts);
    this.bindEvents();
  }

  getCounts() {
    const counts = { all: this.data.length };
    this.data.forEach(g => {
      counts[g.source.name] = (counts[g.source.name] || 0) + 1;
    });
    return counts;
  }

  getStats() {
    const piCount = this.data.filter(p => p.role === 'PI').length;
    const participantCount = this.data.filter(p => p.role !== 'PI').length;
    // Only count PI project amounts
    const piAmount = this.data.filter(p => p.role === 'PI').reduce((sum, p) => {
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
          <span class="grant-stat-value">${this.formatAmount(piAmount)}</span>
          <span class="grant-stat-label">PI Amount (CNY)</span>
        </div>
      </div>
    `;
  }

  renderLegend() {
    // Build legend dynamically from data, with links where available
    const order = ['NSFC', 'GBABRF', 'CPSF', 'SSTP', 'ERC'];
    const sourceMap = {};
    this.data.forEach(g => {
      if (!sourceMap[g.source.name]) sourceMap[g.source.name] = g.source;
    });
    const sources = order.filter(name => sourceMap[name]).map(name => sourceMap[name]);

    return `
      <div class="grant-legend">
        ${sources.map(s => {
          const abbr = s.url
            ? `<a href="${s.url}" target="_blank" rel="noopener" class="grant-legend-link"><strong>${s.name}</strong></a>`
            : `<strong>${s.name}</strong>`;
          return `<span class="grant-legend-item">${abbr}: ${s.full_name}</span>`;
        }).join('')}
      </div>
    `;
  }

  renderFilters(counts) {
    const filtersEl = document.getElementById('grant-filters');

    // All button — active only when both source and role filters are cleared
    const isAllActive = this.activeFilter === 'all' && this.activeRoleFilter === 'all';
    const allBtn = `<button class="grant-filter-btn ${isAllActive ? 'active' : ''}" data-filter="all">All<span class="count">${counts.all || 0}</span></button>`;

    // Role filter buttons (after All)
    const roleCounts = {
      PI: this.data.filter(g => g.role === 'PI').length,
      Participant: this.data.filter(g => g.role !== 'PI').length
    };
    const roleTypes = [
      { key: 'PI', label: 'PI Projects' },
      { key: 'Participant', label: 'Participated' }
    ];
    const roleBtns = roleTypes.map(t =>
      `<button class="grant-filter-btn grant-role-btn ${t.key === this.activeRoleFilter ? 'active' : ''}" data-role-filter="${t.key}">
        ${t.label}<span class="count">${roleCounts[t.key] || 0}</span>
      </button>`
    ).join('');

    // Source filter buttons (NSFC, GBABRF, etc.)
    const sourceTypes = [
      { key: 'NSFC', label: 'NSFC' },
      { key: 'GBABRF', label: 'GBABRF' },
      { key: 'CPSF', label: 'CPSF' },
      { key: 'SSTP', label: 'SSTP' },
      { key: 'ERC', label: 'ERC' }
    ];
    const sourceBtns = sourceTypes.map(t =>
      `<button class="grant-filter-btn ${t.key === this.activeFilter ? 'active' : ''}" data-filter="${t.key}">
        ${t.label}<span class="count">${counts[t.key] || 0}</span>
      </button>`
    ).join('');

    filtersEl.innerHTML = allBtn + roleBtns + `<span class="grant-filter-separator"></span>` + sourceBtns;
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

    // Source type for hover color
    const sourceType = this.getSourceType(grant.source.name);

    return `
      <div class="grant-card grant-card--${sourceType}" data-source="${grant.source.name}">
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

  getSourceType(sourceName) {
    const typeMap = {
      'NSFC': 'nsfc',
      'GBABRF': 'gbabrf',
      'CPSF': 'cpsf',
      'SSTP': 'sstp',
      'ERC': 'erc'
    };
    return typeMap[sourceName] || 'other';
  }

  bindEvents() {
    // Source filter buttons (data-filter attribute)
    document.querySelectorAll('.grant-filter-btn[data-filter]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeFilter = btn.dataset.filter;
        if (btn.dataset.filter === 'all') this.activeRoleFilter = 'all';
        this.applyFilters();
      });
    });

    // Role filter buttons (data-role-filter attribute)
    document.querySelectorAll('.grant-filter-btn[data-role-filter]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeRoleFilter = btn.dataset.roleFilter;
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
      const matchesFilter = this.activeFilter === 'all' || g.source.name === this.activeFilter;
      const matchesRole = this.activeRoleFilter === 'all' ||
        (this.activeRoleFilter === 'PI' ? g.role === 'PI' : g.role !== 'PI');
      const matchesSearch = !this.searchQuery ||
        g.title.toLowerCase().includes(this.searchQuery) ||
        g.number.toLowerCase().includes(this.searchQuery) ||
        g.source.name.toLowerCase().includes(this.searchQuery) ||
        g.source.full_name.toLowerCase().includes(this.searchQuery);
      return matchesFilter && matchesRole && matchesSearch;
    });

    this.updateFiltersUI();
    this.updateListUI();
  }

  updateFiltersUI() {
    const isAllActive = this.activeFilter === 'all' && this.activeRoleFilter === 'all';
    document.querySelectorAll('.grant-filter-btn[data-filter]').forEach(btn => {
      if (btn.dataset.filter === 'all') {
        btn.classList.toggle('active', isAllActive);
      } else {
        btn.classList.toggle('active', btn.dataset.filter === this.activeFilter);
      }
    });
    document.querySelectorAll('.grant-filter-btn[data-role-filter]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.roleFilter === this.activeRoleFilter);
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
