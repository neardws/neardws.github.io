// Publication Cards - Dynamic v2
// Loads publications from JSON data and renders interactive cards with filtering

(function() {
  'use strict';

  const DATA_FILE = '/assets/data/publications.json';

  class PublicationCards {
    constructor() {
      this.data = [];
      this.filteredData = [];
      this.currentFilter = 'all';
      this.searchQuery = '';

      this.init();
    }

    async init() {
      try {
        const res = await fetch(DATA_FILE);
        this.data = await res.json();
        this.filteredData = [...this.data];
        this.render();
      } catch (e) {
          console.warn('Failed to load publications:', e);
          document.getElementById('pub-container').innerHTML = '<p>Failed to load publications.</p>';
      }
    }

    render() {
      const container = document.getElementById('pub-container');
      if (!container) return;

      const counts = this.getCounts();
      const stats = this.getStats();

      container.innerHTML = `
        ${stats}
        <div class="pub-controls">
          <div class="pub-filters" id="pub-filters"></div>
          <input type="text" class="pub-search" id="pub-search" placeholder="Search title, author, venue..." />
        </div>
        <div class="pub-grid" id="pub-grid"></div>
      `;

      this.renderFilters(counts);
      this.renderCards();
      this.bindEvents();
    }

    getCounts() {
      const counts = { all: this.data.length };
      this.data.forEach(p => {
        counts[p.type] = (counts[p.type] || 0) + 1;
      });
      return counts;
    }

    getStats() {
      const journals = this.data.filter(p => p.type === 'journal').length;
      const conferences = this.data.filter(p => p.type === 'conference').length;
      const highlights = this.data.filter(p => p.highlight).length;
      const firstAuthors = this.data.filter(p => {
        const firstAuthor = p.authors[0];
        return firstAuthor.includes('Xincao') || firstAuthor.includes('Xu');
      }).length;

      return `
        <div class="pub-stats">
          <div class="pub-stat">
            <span class="pub-stat-value">${journals}</span>
            <span class="pub-stat-label">Journal</span>
          </div>
          <div class="pub-stat">
            <span class="pub-stat-value">${conferences}</span>
            <span class="pub-stat-label">Conference</span>
          </div>
          <div class="pub-stat">
            <span class="pub-stat-value">${firstAuthors}</span>
            <span class="pub-stat-label">1st Author</span>
          </div>
          <div class="pub-stat">
            <span class="pub-stat-value">${highlights}</span>
            <span class="pub-stat-label">Featured</span>
          </div>
        </div>
      `;
    }

    renderFilters(counts) {
      const filtersEl = document.getElementById('pub-filters');
      const types = [
        { key: 'all', label: 'All' },
        { key: 'journal', label: 'Journal' },
        { key: 'conference', label: 'Conference' },
        { key: 'dissertation', label: 'Dissertation' },
        { key: 'chinese', label: '中文论文' }
      ];

      filtersEl.innerHTML = types.map(t =>
        `<button class="pub-filter-btn ${t.key === this.currentFilter ? 'active' : ''}"
          data-filter="${t.key}">
          ${t.label}<span class="count">${counts[t.key] || 0}</span>
        </button>`
      ).join('');
    }

    renderCards() {
      const grid = document.getElementById('pub-grid');

      if (this.filteredData.length === 0) {
        grid.innerHTML = '<div class="pub-no-results">No publications found.</div>';
        return;
      }

      grid.innerHTML = this.filteredData.map(pub => `
        <div class="pub-card entering ${pub.highlight ? 'highlight' : ''}" data-id="${pub.id}">
          <div class="pub-card-header">
            <span class="pub-venue ${pub.type}">${this.getTypeLabel(pub.type)}</span>
            <span class="pub-year">${pub.year}</span>
          </div>
          <div class="pub-title">
            ${pub.doi ? `<a href="${pub.doi}" target="_blank">${this.escapeHtml(pub.title)}</a>` : this.escapeHtml(pub.title)}
          </div>
          <div class="pub-authors">${this.formatAuthors(pub.authors)}</div>
          <div class="pub-tags">
            ${pub.tags.map(t => `<span class="pub-tag">${t}</span>`).join('')}
            ${pub.highlight ? '<span class="pub-tag best-paper">★ Featured</span>' : ''}
          </div>
          <div class="pub-links">
            ${pub.doi ? `<a class="pub-link" href="${pub.doi}" target="_blank"><span class="icon">📄</span> Paper</a>` : ''}
            ${pub.bib ? `<a class="pub-link" href="${pub.bib}" target="_blank"><span class="icon">📋</span> BibTeX</a>` : ''}
            ${pub.github ? `<a class="pub-link" href="${pub.github}" target="_blank"><span class="icon">💻</span> Code</a>` : ''}
            ${pub.youtube ? `<a class="pub-link" href="${pub.youtube}" target="_blank"><span class="icon">▶️</span> Video</a>` : ''}
          </div>
        </div>
      `).join('');

      // Animate cards in
      requestAnimationFrame(() => {
        const cards = grid.querySelectorAll('.pub-card');
        cards.forEach((card, i) => {
          setTimeout(() => {
            card.classList.remove('entering');
            card.classList.add('visible');
          }, i * 80);
        });
      });
    }

    formatAuthors(authors) {
      return authors.map(author => {
        const isCorr = author.includes('*');
        const isMe = author.includes('Xincao') || author.includes('Xu');
        let cleanName = author.replace(/\*|\^/g, '');
        if (isMe) {
          return `<strong class="${isCorr ? 'corresponding' : ''}">${cleanName}</strong>`;
        }
        return cleanName;
      }).join(', ');
    }

    getTypeLabel(type) {
      const labels = {
        journal: 'Journal',
        conference: 'Conference',
        chinese: '中文论文',
        dissertation: 'Dissertation'
      };
      return labels[type] || type;
    }

    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    bindEvents() {
      // Filter buttons
      document.getElementById('pub-filters').addEventListener('click', (e) => {
        if (e.target.classList.contains('pub-filter-btn')) {
          this.currentFilter = e.target.dataset.filter;
          document.querySelectorAll('.pub-filter-btn').forEach(btn => btn.classList.remove('active'));
          e.target.classList.add('active');
          this.applyFilters();
        }
      });

      // Search
      const searchInput = document.getElementById('pub-search');
      let searchTimeout;
      searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          this.searchQuery = e.target.value.toLowerCase().trim();
          this.applyFilters();
        }, 200);
      });
    }

    applyFilters() {
      this.filteredData = this.data.filter(pub => {
        // Type filter
        if (this.currentFilter !== 'all') {
          if (this.currentFilter === 'chinese') {
            if (pub.type !== 'chinese') return false;
          } else if (pub.type !== this.currentFilter) {
            return false;
          }
        }

        // Search filter
        if (this.searchQuery) {
          const searchIn = [
            pub.title,
            pub.venue,
            ...pub.authors,
            ...(pub.tags || [])
          ].join(' ').toLowerCase();
          return searchIn.includes(this.searchQuery);
        }

        return true;
      });

      this.renderCards();
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new PublicationCards());
  } else {
    new PublicationCards();
  }
})();
