// Publication Cards - Dynamic v3
// Full citation info: venue_full, volume, issue, pages, month, scholar citations

(function() {
  'use strict';

  const DATA_FILE = '/assets/data/publications.json';
  const SCHOLAR_USER = 'DK5avZUAAAAJ';
  const SCHOLAR_STATS_URL = 'https://cdn.jsdelivr.net/gh/Neardws/neardws.github.io@google-scholar-stats/gs_data.json';
  const SHIELDS_SCHOLAR = (scholarId) => {
    const url = encodeURIComponent('https://cdn.jsdelivr.net/gh/Neardws/neardws.github.io@google-scholar-stats/gs_data.json');
    const query = encodeURIComponent(`$['publications']['${scholarId}']['num_citations']`);
    return `https://img.shields.io/badge/dynamic/json?logo=Google%20Scholar&url=${url}&query=${query}&labelColor=f6f6f6&color=9cf&style=flat&label=Citations`;
  };
  const SHIELDS_BIBTEX = 'https://img.shields.io/badge/-BibTeX-blue?labelColor=white&color=F5F5F5&logo=latex&logoColor=008080';
  const SHIELDS_PDF = 'https://img.shields.io/badge/-PDF-blue?logo=onlyoffice&logoColor=B7472A&labelColor=white&color=F5F5F5&style=flat';
  const SHIELDS_STARS = (repo) => `https://img.shields.io/github/stars/${repo}?style=social`;
  const SHIELDS_YOUTUBE = (videoId) => `https://img.shields.io/youtube/views/${videoId}?style=social`;
  const SHIELDS_BILIBILI = (bvid) => {
    const url = encodeURIComponent(`https://api.bilibili.com/x/web-interface/view?bvid=${bvid}`);
    return `https://img.shields.io/badge/dynamic/json?label=views&style=social&logo=bilibili&query=data.stat.view&url=${url}`;
  };

  class PublicationCards {
    constructor() {
      this.data = [];
      this.filteredData = [];
      this.currentFilter = 'all';
      this.searchQuery = '';
      this.scholarStats = {};

      this.init();
    }

    async init() {
      try {
        const [pubRes, scholarRes] = await Promise.allSettled([
          fetch(DATA_FILE).then(r => r.json()),
          fetch(SCHOLAR_STATS_URL).then(r => r.json())
        ]);

        this.data = pubRes.status === 'fulfilled' ? pubRes.value : [];
        if (scholarRes.status === 'fulfilled' && scholarRes.value.publications) {
          this.scholarStats = scholarRes.value.publications;
        }

        // Sort all publications by year descending, then by month descending
        const monthOrder = {
          'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
          'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
        };
        const getMonthNum = (m) => monthOrder[m] || 0;
        
        this.data.sort((a, b) => {
          if (b.year !== a.year) return b.year - a.year;
          return getMonthNum(b.month) - getMonthNum(a.month);
        });

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
        <div class="pub-list" id="pub-grid"></div>
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
      const firstAuthors = this.data.filter(p => {
        // First author: Xincao Xu is the first author
        const isFirst = p.authors[0].includes('Xincao');
        // Corresponding author: any author with "Xincao" AND "*"
        const isCorr = p.authors.some(a => a.includes('Xincao') && a.includes('*'));
        return isFirst || isCorr;
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
            <span class="pub-stat-label">1st/Corr. Author</span>
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
        { key: 'chinese', label: 'Chinese' },
        { key: 'dissertation', label: 'Dissertation' }
      ];

      filtersEl.innerHTML = types.map(t =>
        `<button class="pub-filter-btn ${t.key === this.currentFilter ? 'active' : ''}"
          data-filter="${t.key}">
          ${t.label}<span class="count">${counts[t.key] || 0}</span>
        </button>`
      ).join('');
    }

    buildCitation(pub) {
      // Build the full citation string like the old Markdown version
      const authors = this.formatAuthorsText(pub.authors);
      const titleLink = pub.doi
        ? `<a href="${pub.doi}" target="_blank" class="pub-title-link">${this.escapeHtml(pub.title)}</a>`
        : `<span>${this.escapeHtml(pub.title)}</span>`;

      let venue = '';
      if (pub.type === 'journal' || pub.type === 'chinese') {
        // Use venue_full (English) as primary, venue (Chinese) in parentheses if available
        const venueFull = pub.venue_full || pub.venue;
        const venueShort = pub.venue_full && pub.venue ? pub.venue : null;
        const venuePart = venueShort
          ? `<em>${this.escapeHtml(venueFull)}</em> (<em>${this.escapeHtml(venueShort)}</em>)`
          : `<em>${this.escapeHtml(venueFull)}</em>`;
        const vol = pub.volume ? `, vol. ${pub.volume}` : '';
        const iss = pub.issue ? `, no. ${pub.issue}` : '';
        const pages = pub.pages ? `, pp. ${pub.pages}` : '';
        const date = pub.month ? `, ${pub.month} ${pub.year}` : `, ${pub.year}`;
        venue = `${venuePart}${vol}${iss}${pages}${date}.`;
      } else if (pub.type === 'conference') {
        const venuePart = pub.venue_full
          ? `<em>${this.escapeHtml(pub.venue_full)}</em> (<em>${this.escapeHtml(pub.venue)}</em>)`
          : `<em>${this.escapeHtml(pub.venue)}</em>`;
        const loc = pub.location ? `, ${pub.location}` : '';
        const date = pub.conf_date ? `, ${pub.conf_date}` : `, ${pub.year}`;
        venue = `${venuePart}${loc}${date}.`;
      } else if (pub.type === 'dissertation') {
        venue = `<em>${this.escapeHtml(pub.venue_full || pub.venue)}</em>, Doctoral Dissertation, ${pub.month || ''} ${pub.year}.`;
      }

      return `${authors}, ${titleLink}, ${venue}`;
    }

    formatAuthorsText(authors) {
      return authors.map(author => {
        const isCorr = author.includes('*');
        const cleanName = author.replace(/\*/g, '').trim();
        // Only match if name contains "Xincao" (avoids matching "Xuqi Cai" etc.)
        const isMe = cleanName.includes('Xincao');
        const corrMark = isCorr ? '<sup>*</sup>' : '';

        if (isMe) {
          return `<strong>${this.escapeHtml(cleanName)}${corrMark}</strong>`;
        }
        return `${this.escapeHtml(cleanName)}${corrMark}`;
      }).join(', ');
    }

    getCitations(pub) {
      if (!pub.scholar_id || !this.scholarStats[pub.scholar_id]) return null;
      return this.scholarStats[pub.scholar_id].num_citations;
    }

    renderCards() {
      const grid = document.getElementById('pub-grid');

      if (this.filteredData.length === 0) {
        grid.innerHTML = '<div class="pub-no-results">No publications found.</div>';
        return;
      }

      grid.innerHTML = this.filteredData.map((pub, idx) => {
        const citation = this.buildCitation(pub);
        const citations = this.getCitations(pub);
        const scholarUrl = pub.scholar_id
          ? `https://scholar.google.com/citations?view_op=view_citation&hl=en&user=${SCHOLAR_USER}&citation_for_view=${pub.scholar_id}`
          : null;

        const ifBadge = pub.if ? `<span class="pub-if">IF: ${pub.if}</span>` : '';

        const tags = pub.tags.map(t => {
          const cls = t.includes('Best Paper') || t.includes('Best Paper Candidate') ? 'best-paper' : '';
          return `<span class="pub-tag ${cls}">${t}</span>`;
        }).join('');

        // shields.io badges — same row as IF + tags
        const bibBadge = pub.bib
          ? `<a href="${pub.bib}" target="_blank" class="pub-badge-link"><img src="${SHIELDS_BIBTEX}" alt="BibTeX" loading="lazy"></a>`
          : '';
        const pdfBadge = pub.pdf
          ? `<a href="${pub.pdf}" target="_blank" class="pub-badge-link"><img src="${SHIELDS_PDF}" alt="PDF" loading="lazy"></a>`
          : '';
        const scholarBadge = pub.scholar_id && scholarUrl
          ? `<a href="${scholarUrl}" target="_blank" class="pub-badge-link"><img src="${SHIELDS_SCHOLAR(pub.scholar_id)}" alt="Citations" loading="lazy"></a>`
          : '';
        const githubRepo = pub.github ? pub.github.replace('https://github.com/', '') : null;
        const starsBadge = githubRepo
          ? `<a href="${pub.github}" target="_blank" class="pub-badge-link"><img src="${SHIELDS_STARS(githubRepo)}" alt="GitHub Stars" loading="lazy"></a>`
          : '';
        const ytVideoId = pub.youtube ? pub.youtube.replace('https://youtu.be/', '').replace('https://www.youtube.com/watch?v=', '').split('&')[0] : null;
        const youtubeBadge = ytVideoId
          ? `<a href="${pub.youtube}" target="_blank" class="pub-badge-link"><img src="${SHIELDS_YOUTUBE(ytVideoId)}" alt="YouTube Views" loading="lazy"></a>`
          : '';
        const bvid = pub.bilibili ? pub.bilibili.replace('https://www.bilibili.com/video/', '') : null;
        const bilibiliBadge = bvid
          ? `<a href="${pub.bilibili}" target="_blank" class="pub-badge-link"><img src="${SHIELDS_BILIBILI(bvid)}" alt="Bilibili Views" loading="lazy"></a>`
          : '';

        return `
          <div class="pub-item" data-id="${pub.id}" data-type="${pub.type}">
            <div class="pub-item-left">
              <span class="pub-type-badge ${pub.type}">${this.getTypeLabel(pub.type)}</span>
              <span class="pub-year-badge">${pub.year}</span>
            </div>
            <div class="pub-item-body">
              <div class="pub-citation">${citation}</div>
              <div class="pub-meta-row">
                ${ifBadge}
                ${tags}
                ${bibBadge}
                ${pdfBadge}
                ${scholarBadge}
                ${starsBadge}
                ${youtubeBadge}
                ${bilibiliBadge}
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    getTypeLabel(type) {
      const labels = {
        journal: 'Journal',
        conference: 'Conference',
        chinese: 'Chinese',
        dissertation: 'Dissertation'
      };
      return labels[type] || type;
    }

    escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    bindEvents() {
      document.getElementById('pub-filters').addEventListener('click', (e) => {
        const btn = e.target.closest('.pub-filter-btn');
        if (!btn) return;
        this.currentFilter = btn.dataset.filter;
        document.querySelectorAll('.pub-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.applyFilters();
      });

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
        if (this.currentFilter !== 'all' && pub.type !== this.currentFilter) return false;
        if (this.searchQuery) {
          const searchIn = [
            pub.title, pub.venue, pub.venue_full || '',
            ...pub.authors, ...(pub.tags || []),
            pub.location || '', pub.pages || ''
          ].join(' ').toLowerCase();
          return searchIn.includes(this.searchQuery);
        }
        return true;
      });
      this.renderCards();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new PublicationCards());
  } else {
    new PublicationCards();
  }
})();
