/**
 * Grant Cards Renderer
 * Dynamically renders grant cards from JSON data
 */

class GrantCards {
  constructor() {
    this.data = [];
    this.container = null;
  }

  async init() {
    this.container = document.getElementById('grant-container');
    if (!this.container) return;

    try {
      const res = await fetch('assets/data/grants.json');
      this.data = await res.json();

      // Sort by role (PI first), then by period start date (newest first)
      this.data.sort((a, b) => {
        // PI projects first
        if (a.role === 'PI' && b.role !== 'PI') return -1;
        if (a.role !== 'PI' && b.role === 'PI') return 1;

        // Then by period (extract start year)
        const getStartYear = (period) => {
          const match = period.match(/(\d{4})/);
          return match ? parseInt(match[1]) : 0;
        };
        return getStartYear(b.period) - getStartYear(a.period);
      });

      this.render();
    } catch (e) {
      console.warn('Failed to load grants:', e);
      this.container.innerHTML = '<p>Failed to load grants.</p>';
    }
  }

  render() {
    const piProjects = this.data.filter(p => p.role === 'PI');
    const participantProjects = this.data.filter(p => p.role !== 'PI');

    // Build sources legend
    const sources = [...new Set(this.data.map(p => p.source.name))];
    const sourcesHtml = sources.map(name => {
      const src = this.data.find(p => p.source.name === name)?.source;
      if (!src) return '';
      const iconHtml = src.icon
        ? `<img src="${src.icon}" alt="${src.name}" class="grant-source-icon">`
        : `<span class="grant-source-icon-text">${src.name}</span>`;
      const linkHtml = src.url
        ? `<a href="${src.url}" target="_blank" class="grant-source-link no-underline">${iconHtml} <strong>${src.name}</strong>: ${src.full_name}</a>`
        : `<span>${iconHtml} <strong>${src.name}</strong>: ${src.full_name}</span>`;
      return `<div class="grant-source-item">${linkHtml}</div>`;
    }).join('');

    // Build stats
    const totalAmount = this.data.reduce((sum, p) => {
      const match = p.amount.match(/[\d,]+/);
      return sum + (match ? parseInt(match[0].replace(/,/g, '')) : 0);
    }, 0);

    const statsHtml = `
      <div class="grant-stats">
        <div class="grant-stat">
          <span class="grant-stat-value">${piProjects.length}</span>
          <span class="grant-stat-label">PI/Co-PI Projects</span>
        </div>
        <div class="grant-stat">
          <span class="grant-stat-value">${participantProjects.length}</span>
          <span class="grant-stat-label">Participated</span>
        </div>
        <div class="grant-stat">
          <span class="grant-stat-value">${this.formatAmount(totalAmount)}</span>
          <span class="grant-stat-label">Total (CNY)</span>
        </div>
      </div>
      <div class="grant-sources">${sourcesHtml}</div>
    `;

    // Build PI projects
    const piHtml = piProjects.length > 0 ? `
      <h4 class="grant-section-title">Principal Investigator</h4>
      <div class="grant-list">
        ${piProjects.map(p => this.renderCard(p)).join('')}
      </div>
    ` : '';

    // Build Participant projects
    const participantHtml = participantProjects.length > 0 ? `
      <h4 class="grant-section-title">Participation</h4>
      <div class="grant-list">
        ${participantProjects.map(p => this.renderCard(p)).join('')}
      </div>
    ` : '';

    this.container.innerHTML = `
      ${statsHtml}
      ${piHtml}
      ${participantHtml}
    `;
  }

  renderCard(grant) {
    const iconHtml = grant.source.icon
      ? `<img src="${grant.source.icon}" alt="${grant.source.name}" class="grant-card-icon">`
      : `<div class="grant-card-icon-placeholder">${grant.source.name}</div>`;

    const roleClass = grant.role === 'PI' ? 'grant-card--pi' : 'grant-card--participant';
    const roleTag = grant.role === 'PI'
      ? '<span class="grant-role-tag grant-role-tag--pi">PI</span>'
      : '';

    const noteHtml = grant.note
      ? `<div class="grant-note">${grant.note}</div>`
      : '';

    return `
      <div class="grant-card ${roleClass}">
        <div class="grant-card-left">
          ${iconHtml}
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