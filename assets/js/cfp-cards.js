/**
 * CFP Cards Renderer
 * Dynamically renders CCF Class A conference deadlines from JSON data.
 * Categories: DS (Computer Architecture), NW (Network System),
 *             AI (Artificial Intelligence), HI (Computer-Human Interaction)
 */

class CFPCards {
  constructor() {
    this.data = [];
    this.filteredData = [];
    this.activeFilter = 'all';
    this.container = null;
    this.updatedAt = null;
  }

  async init() {
    this.container = document.getElementById('cfp-container');
    if (!this.container) return;

    try {
      const res = await fetch('/assets/data/cfp.json');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();

      this.data = json.conferences || [];
      this.updatedAt = json.updated_at;
      this.filteredData = [...this.data];
      this.render();
    } catch (e) {
      console.warn('Failed to load CFP data:', e);
      this.container.innerHTML = '<p>Failed to load conference deadlines.</p>';
    }
  }

  getCounts() {
    const counts = { all: this.data.length };
    this.data.forEach(c => {
      counts[c.sub] = (counts[c.sub] || 0) + 1;
    });
    return counts;
  }

  render() {
    if (this.data.length === 0) {
      this.container.innerHTML = '<p>No CCF Class A conferences found. Data will be available after the first scheduled run.</p>';
      return;
    }

    const counts = this.getCounts();
    const updatedHtml = this.updatedAt
      ? `<div class="cfp-updated">Last updated: ${this.formatUpdatedAt(this.updatedAt)}</div>`
      : '';

    this.container.innerHTML = `
      ${updatedHtml}
      <div class="cfp-controls">
        <div class="cfp-filters" id="cfp-filters"></div>
      </div>
      <div class="cfp-table-wrapper">
        <table class="cfp-table">
          <thead>
            <tr>
              <th class="cfp-th-deadline">Deadline</th>
              <th class="cfp-th-date">Conf. Date</th>
              <th class="cfp-th-conf">Conference</th>
              <th class="cfp-th-venue">Venue</th>
              <th class="cfp-th-cat">Category</th>
            </tr>
          </thead>
          <tbody id="cfp-tbody">
            ${this.filteredData.map(c => this.renderRow(c)).join('')}
          </tbody>
        </table>
      </div>
    `;

    this.renderFilters(counts);
    this.bindEvents();
  }

  renderFilters(counts) {
    const filtersEl = document.getElementById('cfp-filters');
    if (!filtersEl) return;

    const categories = [
      { key: 'DS', label: 'Computer Architecture' },
      { key: 'NW', label: 'Network System' },
      { key: 'AI', label: 'Artificial Intelligence' },
      { key: 'HI', label: 'Human-Computer Interaction' },
      { key: 'MX', label: 'Interdiscipline' },
    ];

    const allBtn = `<button class="cfp-filter-btn ${this.activeFilter === 'all' ? 'active' : ''}" data-filter="all">All<span class="count">${counts.all || 0}</span></button>`;

    const catBtns = categories
      .map(cat =>
        `<button class="cfp-filter-btn cfp-cat-btn cfp-cat-btn--${cat.key.toLowerCase()} ${this.activeFilter === cat.key ? 'active' : ''}" data-filter="${cat.key}">${cat.label}<span class="count">${counts[cat.key] || 0}</span></button>`
      )
      .join('');

    filtersEl.innerHTML = allBtn + catBtns;
  }

  renderRow(conf) {
    const isPast = !conf.is_future;
    const rowClass = isPast ? 'cfp-row cfp-row--past' : 'cfp-row';

    // Deadline cell
    let deadlineHtml;
    if (conf.deadline) {
      const dlClass = isPast ? 'cfp-deadline cfp-deadline--past' : 'cfp-deadline';
      deadlineHtml = `<span class="${dlClass}">${this.formatDate(conf.deadline)}</span>`;
      if (conf.abstract_deadline) {
        deadlineHtml += `<br><span class="cfp-abs-deadline">Abs: ${this.formatDate(conf.abstract_deadline)}</span>`;
      }
      deadlineHtml += `<br><span class="cfp-tz">${this.escapeHtml(conf.timezone)}</span>`;
    } else {
      deadlineHtml = '<span class="cfp-na">TBD</span>';
    }

    // Conference name cell
    const confTitle = this.escapeHtml(conf.title);
    const confDesc = this.escapeHtml(conf.description);
    const confNameHtml = conf.link
      ? `<a href="${this.escapeHtml(conf.link)}" target="_blank" rel="noopener" class="cfp-conf-link"><strong>${confTitle}</strong></a>`
      : `<strong>${confTitle}</strong>`;

    const badgeClass = `cfp-cat-badge cfp-cat-badge--${conf.sub.toLowerCase()}`;

    return `
      <tr class="${rowClass}">
        <td class="cfp-td-deadline">${deadlineHtml}</td>
        <td class="cfp-td-date">${this.escapeHtml(this.normalizeConfDate(conf.date)) || '<span class="cfp-na">TBD</span>'}</td>
        <td class="cfp-td-conf">
          ${confNameHtml}
          <span class="cfp-conf-desc">${confDesc}</span>
        </td>
        <td class="cfp-td-venue">${this.escapeHtml(this.normalizePlace(conf.place)) || '<span class="cfp-na">TBD</span>'}</td>
        <td class="cfp-td-cat"><span class="${badgeClass}" title="${this.escapeHtml(conf.sub_name)}">${this.escapeHtml(conf.sub)}</span></td>
      </tr>
    `;
  }

  formatDate(dateStr) {
    if (!dateStr) return 'TBD';
    try {
      // Parse as UTC (deadline strings are in conference's local tz, stored as-is)
      const s = String(dateStr).replace(' ', 'T');
      const d = new Date(s.includes('T') ? s : s + 'T00:00:00');
      if (isNaN(d.getTime())) return String(dateStr).slice(0, 10);
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        timeZone: 'UTC',
      });
    } catch {
      return String(dateStr).slice(0, 10);
    }
  }

  formatUpdatedAt(isoStr) {
    try {
      const d = new Date(isoStr);
      return d.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'UTC',
        timeZoneName: 'short',
      });
    } catch {
      return isoStr;
    }
  }

  escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Normalize place string to "City, Country [flag]" format
  normalizePlace(place) {
    if (!place) return place;

    const US_STATES_FULL = new Set([
      'Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut',
      'Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa',
      'Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan',
      'Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada',
      'New Hampshire','New Jersey','New Mexico','New York','North Carolina',
      'North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island',
      'South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont',
      'Virginia','Washington','West Virginia','Wisconsin','Wyoming',
    ]);
    const US_STATES_ABBREV = new Set([
      'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA',
      'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
      'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT',
      'VA','WA','WV','WI','WY','DC',
    ]);
    const AU_STATES = new Set(['NSW','VIC','QLD','SA','TAS','ACT','NT']);

    // Normalize country aliases
    let s = place
      .replace(/\bUnited States of America\b/g, 'USA')
      .replace(/\bUnited States\b/g, 'USA');

    const parts = s.split(',').map(p => p.trim()).filter(Boolean);
    if (parts.length === 0) return place;

    // Single part: strip trailing venue keywords (e.g. "Singapore EXPO")
    if (parts.length === 1) {
      const cleaned = parts[0].replace(/\s+(EXPO|CENTRE|CENTER|HALL|ARENA|PLAZA)\s*$/i, '').trim();
      return this.withFlag(cleaned);
    }

    // Two parts: check if last is a US state (country implied)
    if (parts.length === 2) {
      if (US_STATES_FULL.has(parts[1]) || US_STATES_ABBREV.has(parts[1])) {
        return this.withFlag(`${parts[0]}, USA`);
      }
      return this.withFlag(s);
    }

    // Three or more parts: derive city + country
    const last = parts[parts.length - 1];
    const country = (US_STATES_FULL.has(last) || US_STATES_ABBREV.has(last)) ? 'USA' : last;

    const candidates = parts.slice(0, -1).filter(p =>
      p !== country &&
      !US_STATES_FULL.has(p) &&
      !US_STATES_ABBREV.has(p) &&
      !AU_STATES.has(p) &&
      !this.isVenuePart(p)
    );

    const city = candidates.length > 0
      ? candidates[candidates.length - 1]   // prefer the last non-venue/non-state part
      : parts[parts.length - 2];

    return this.withFlag(`${city}, ${country}`);
  }

  isVenuePart(s) {
    const VENUE_KW = new Set([
      'hotel','center','centre','convention','expo','arena',
      'conference','hall','resort','plaza','building','campus',
    ]);
    const words = s.toLowerCase().split(/\s+/);
    return words.length >= 4 || words.some(w => VENUE_KW.has(w));
  }

  withFlag(cityCountry) {
    const FLAGS = {
      'USA': '🇺🇸',
      'China': '🇨🇳', 'Hong Kong': '🇨🇳', 'Macau': '🇨🇳', 'Taiwan': '🇨🇳',
      'Japan': '🇯🇵', 'Korea': '🇰🇷', 'South Korea': '🇰🇷',
      'Singapore': '🇸🇬', 'India': '🇮🇳', 'UAE': '🇦🇪',
      'Australia': '🇦🇺', 'New Zealand': '🇳🇿',
      'UK': '🇬🇧', 'United Kingdom': '🇬🇧',
      'France': '🇫🇷', 'Germany': '🇩🇪', 'Italy': '🇮🇹',
      'Spain': '🇪🇸', 'Portugal': '🇵🇹', 'Netherlands': '🇳🇱',
      'Switzerland': '🇨🇭', 'Austria': '🇦🇹', 'Belgium': '🇧🇪',
      'Sweden': '🇸🇪', 'Norway': '🇳🇴', 'Denmark': '🇩🇰', 'Finland': '🇫🇮',
      'Poland': '🇵🇱', 'Greece': '🇬🇷', 'Turkey': '🇹🇷',
      'Canada': '🇨🇦', 'Mexico': '🇲🇽', 'Brazil': '🇧🇷',
      'Argentina': '🇦🇷', 'Chile': '🇨🇱',
      'South Africa': '🇿🇦', 'Morocco': '🇲🇦', 'Egypt': '🇪🇬',
      'Israel': '🇮🇱', 'Saudi Arabia': '🇸🇦',
    };
    const parts = cityCountry.split(',').map(p => p.trim());
    const country = parts[parts.length - 1];
    const flag = FLAGS[country] || '';
    return flag ? `${cityCountry} ${flag}` : cityCountry;
  }

  // Normalize month names to title case (e.g. "FEBRUARY" → "February")
  normalizeConfDate(str) {
    if (!str) return str;
    return String(str).replace(
      /\b(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\b/g,
      m => m[0] + m.slice(1).toLowerCase()
    );
  }

  bindEvents() {
    document.querySelectorAll('.cfp-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeFilter = btn.dataset.filter;
        this.applyFilters();
      });
    });
  }

  applyFilters() {
    this.filteredData = this.activeFilter === 'all'
      ? [...this.data]
      : this.data.filter(c => c.sub === this.activeFilter);

    this.updateFiltersUI();
    this.updateTableUI();
  }

  updateFiltersUI() {
    document.querySelectorAll('.cfp-filter-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.filter === this.activeFilter);
    });
  }

  updateTableUI() {
    const tbody = document.getElementById('cfp-tbody');
    if (tbody) {
      tbody.innerHTML = this.filteredData.map(c => this.renderRow(c)).join('');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const cfp = new CFPCards();
  cfp.init();
});
