/**
 * Profile Cards Renderer
 * Dynamically renders profile cards for experience and students sections
 */

class ProfileCards {
  constructor() {
    this.experienceData = null;
    this.studentsData = null;
    this.activeStudentFilter = 'all';
  }

  async init() {
    // Detect which page we're on and load appropriate data
    const hasExperience = document.getElementById('work-container') ||
                          document.getElementById('education-container') ||
                          document.getElementById('membership-container') ||
                          document.getElementById('awards-container');
    const hasStudents = document.getElementById('students-container');

    const promises = [];

    if (hasExperience) {
      promises.push(this.loadExperience());
    }
    if (hasStudents) {
      promises.push(this.loadStudents());
    }

    await Promise.all(promises);
  }

  async loadExperience() {
    try {
      const res = await fetch('/assets/data/experience.json');
      this.experienceData = await res.json();
      this.renderWork();
      this.renderEducation();
      this.renderMembership();
      this.renderAwards();
    } catch (e) {
      console.warn('Failed to load experience data:', e);
    }
  }

  async loadStudents() {
    try {
      const res = await fetch('/assets/data/students.json');
      this.studentsData = await res.json();
      this.renderStudents();
    } catch (e) {
      console.warn('Failed to load students data:', e);
    }
  }

  // ==================== Work Section ====================
  renderWork() {
    const container = document.getElementById('work-container');
    if (!container || !this.experienceData?.work) return;

    const work = this.experienceData.work;
    container.innerHTML = `
      <div class="profile-container">
        <div class="profile-list">
          ${work.map(w => this.renderWorkCard(w)).join('')}
        </div>
      </div>
    `;
  }

  renderWorkCard(work) {
    const startYear = this.extractYear(work.start_date);
    const currentTag = work.current
      ? '<span class="profile-status-tag profile-status-tag--current">Current</span>'
      : '';

    const iconHtml = work.logo
      ? `<img src="/${work.logo}" alt="" class="profile-logo">`
      : '<div class="profile-card-icon">💼</div>';

    return `
      <div class="profile-card profile-card--work">
        <div class="profile-card-left">
          ${iconHtml}
          <div class="profile-card-year">${startYear}</div>
        </div>
        <div class="profile-card-content">
          <div class="profile-card-header">
            <span class="profile-title">${work.title}</span>
            ${currentTag}
          </div>
          <div class="profile-org">${work.organization}</div>
          <div class="profile-meta">
            <span class="profile-location">${work.location}</span>
            <span class="profile-period">${work.start_date} - ${work.current ? 'Present' : work.end_date}</span>
          </div>
        </div>
      </div>
    `;
  }

  // ==================== Education Section ====================
  renderEducation() {
    const container = document.getElementById('education-container');
    if (!container || !this.experienceData?.education) return;

    const education = this.experienceData.education;
    container.innerHTML = `
      <div class="profile-container">
        <div class="profile-list">
          ${education.map(e => this.renderEducationCard(e)).join('')}
        </div>
      </div>
    `;
  }

  renderEducationCard(edu) {
    const startYear = this.extractYear(edu.start_date);
    const supervisorHtml = edu.supervisor
      ? `<div class="profile-supervisor">Supervised by ${edu.supervisor.title} <a href="${edu.supervisor.url}" target="_blank" rel="noopener">${edu.supervisor.name}</a></div>`
      : '';
    const noteHtml = edu.note
      ? `<div class="profile-note">${edu.note}</div>`
      : '';

    const iconHtml = edu.logo
      ? `<img src="/${edu.logo}" alt="" class="profile-logo">`
      : '<div class="profile-card-icon">🎓</div>';

    return `
      <div class="profile-card profile-card--education">
        <div class="profile-card-left">
          ${iconHtml}
          <div class="profile-card-year">${startYear}</div>
        </div>
        <div class="profile-card-content">
          <div class="profile-card-header">
            <span class="profile-degree-tag">${edu.degree}</span>
            <span class="profile-title">${edu.field}</span>
          </div>
          <div class="profile-org">${edu.institution}</div>
          <div class="profile-meta">
            <span class="profile-location">${edu.location}</span>
            <span class="profile-period">${edu.start_date} - ${edu.end_date}</span>
          </div>
          ${supervisorHtml}
          ${noteHtml}
        </div>
      </div>
    `;
  }

  // ==================== Membership Section ====================
  renderMembership() {
    const container = document.getElementById('membership-container');
    if (!container || !this.experienceData?.membership) return;

    const membership = this.experienceData.membership;
    const currentCount = membership.filter(m => m.current).length;
    const totalCount = membership.length;

    container.innerHTML = `
      <div class="profile-container">
        <div class="profile-stats">
          <div class="profile-stat">
            <span class="profile-stat-value">${currentCount}</span>
            <span class="profile-stat-label">Active Memberships</span>
          </div>
          <div class="profile-stat">
            <span class="profile-stat-value">${totalCount}</span>
            <span class="profile-stat-label">Total</span>
          </div>
        </div>
        <div class="profile-list profile-list--compact">
          ${membership.map(m => this.renderMembershipCard(m)).join('')}
        </div>
      </div>
    `;
  }

  renderMembershipCard(member) {
    const startYear = this.extractYear(member.start_date);
    const period = member.current
      ? `${member.start_date} - Present`
      : `${member.start_date} - ${member.end_date}`;
    const statusTag = member.current
      ? '<span class="profile-status-tag profile-status-tag--active">Active</span>'
      : '';

    return `
      <div class="profile-card profile-card--membership profile-card--compact">
        <div class="profile-card-left">
          <div class="profile-card-year">${startYear}</div>
        </div>
        <div class="profile-card-content">
          <div class="profile-card-header">
            <span class="profile-abbr">${member.abbreviation}</span>
            <span class="profile-level">${member.level}</span>
            ${statusTag}
          </div>
          <div class="profile-org">${member.organization}</div>
          <div class="profile-meta">
            <span class="profile-period">${period}</span>
          </div>
        </div>
      </div>
    `;
  }

  // ==================== Awards Section ====================
  renderAwards() {
    const container = document.getElementById('awards-container');
    if (!container || !this.experienceData?.awards) return;

    const awards = this.experienceData.awards;
    container.innerHTML = `
      <div class="profile-container">
        <div class="profile-list">
          ${awards.map(a => this.renderAwardCard(a)).join('')}
        </div>
      </div>
    `;
  }

  renderAwardCard(award) {
    const typeLabel = {
      'dissertation': 'Dissertation',
      'paper': 'Paper'
    };
    const typeTag = typeLabel[award.type]
      ? `<span class="profile-award-tag profile-award-tag--${award.type}">${typeLabel[award.type]}</span>`
      : '';

    return `
      <div class="profile-card profile-card--award">
        <div class="profile-card-left">
          <div class="profile-card-icon">🏆</div>
          <div class="profile-card-year">${award.year}</div>
        </div>
        <div class="profile-card-content">
          <div class="profile-card-header">
            <span class="profile-title">${award.name}</span>
            ${typeTag}
          </div>
          <div class="profile-org">${award.issuer}</div>
        </div>
      </div>
    `;
  }

  // ==================== Students Section ====================
  renderStudents() {
    const container = document.getElementById('students-container');
    if (!container || !this.studentsData) return;

    const students = this.studentsData;
    const currentStudents = students.filter(s => s.status === 'current');
    const alumni = students.filter(s => s.status === 'alumni');

    const counts = {
      all: students.length,
      current: currentStudents.length,
      alumni: alumni.length
    };

    container.innerHTML = `
      <div class="profile-container">
        <div class="profile-stats">
          <div class="profile-stat">
            <span class="profile-stat-value">${counts.current}</span>
            <span class="profile-stat-label">Current Students</span>
          </div>
          <div class="profile-stat">
            <span class="profile-stat-value">${counts.alumni}</span>
            <span class="profile-stat-label">Alumni</span>
          </div>
        </div>
        <div class="profile-filters" id="students-filters"></div>
        <div class="profile-list" id="students-list"></div>
      </div>
    `;

    this.renderStudentFilters(counts);
    this.updateStudentsList();
    this.bindStudentEvents();
  }

  renderStudentFilters(counts) {
    const filtersEl = document.getElementById('students-filters');
    if (!filtersEl) return;

    const filters = [
      { key: 'all', label: 'All', count: counts.all },
      { key: 'current', label: 'Current', count: counts.current },
      { key: 'alumni', label: 'Alumni', count: counts.alumni }
    ];

    filtersEl.innerHTML = filters.map(f =>
      `<button class="profile-filter-btn ${f.key === this.activeStudentFilter ? 'active' : ''}" data-filter="${f.key}">
        ${f.label}<span class="count">${f.count}</span>
      </button>`
    ).join('');
  }

  updateStudentsList() {
    const listEl = document.getElementById('students-list');
    if (!listEl || !this.studentsData) return;

    let filtered = this.studentsData;
    if (this.activeStudentFilter === 'current') {
      filtered = this.studentsData.filter(s => s.status === 'current');
    } else if (this.activeStudentFilter === 'alumni') {
      filtered = this.studentsData.filter(s => s.status === 'alumni');
    }

    listEl.innerHTML = filtered.map(s => this.renderStudentCard(s)).join('');
  }

  renderStudentCard(student) {
    const isAlumni = student.status === 'alumni';
    const cardClass = isAlumni ? 'profile-card--alumni' : 'profile-card--student';
    const statusTag = isAlumni
      ? '<span class="profile-status-tag profile-status-tag--alumni">Alumni</span>'
      : '<span class="profile-status-tag profile-status-tag--current">Current</span>';

    const yearDisplay = student.start_year;

    const githubBadge = student.github
      ? `<a href="https://github.com/${student.github}" target="_blank" rel="noopener" class="profile-github-badge">
          <svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
          ${student.github}
        </a>`
      : '';

    const emailHtml = student.email
      ? `<span class="profile-email"><a href="mailto:${student.email}">${student.email}</a></span>`
      : '';

    const coAdvisorHtml = student.co_advisor
      ? `<div class="profile-supervisor">Co-advised with ${student.co_advisor.title} ${student.co_advisor.name}, ${student.co_advisor.institution}</div>`
      : '';

    // Alumni-specific details
    let alumniDetails = '';
    if (isAlumni) {
      const dissertationHtml = student.dissertation_title
        ? `<div class="profile-dissertation"><span class="profile-dissertation-label">Dissertation:</span> ${student.dissertation_title}</div>`
        : '';
      const firstJobHtml = student.first_job
        ? `<div class="profile-first-job"><span class="profile-dissertation-label">First Position:</span> ${student.first_job.title} at <a href="${student.first_job.url}" target="_blank" rel="noopener">${student.first_job.company}</a></div>`
        : '';

      if (dissertationHtml || firstJobHtml) {
        alumniDetails = `
          <div class="profile-alumni-details">
            ${dissertationHtml}
            ${firstJobHtml}
          </div>
        `;
      }
    }

    // GitHub avatar or default icon
    const avatarHtml = student.github
      ? `<img src="https://github.com/${student.github}.png?size=64" alt="${student.name_en}" class="profile-avatar">`
      : '<div class="profile-card-icon">👨‍🎓</div>';

    return `
      <div class="profile-card ${cardClass}">
        <div class="profile-card-left">
          ${avatarHtml}
          <div class="profile-card-year">${yearDisplay}</div>
        </div>
        <div class="profile-card-content">
          <div class="profile-card-header">
            <span class="profile-title">${student.name_en} (${student.name_cn})</span>
            <span class="profile-degree-tag">${student.degree}</span>
            ${statusTag}
          </div>
          <div class="profile-org">${student.field}, ${student.institution}</div>
          ${coAdvisorHtml}
          <div class="profile-contact">
            ${githubBadge}
            ${emailHtml}
          </div>
          ${alumniDetails}
        </div>
      </div>
    `;
  }

  bindStudentEvents() {
    document.querySelectorAll('#students-filters .profile-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        this.activeStudentFilter = btn.dataset.filter;
        // Update active state
        document.querySelectorAll('#students-filters .profile-filter-btn').forEach(b => {
          b.classList.toggle('active', b.dataset.filter === this.activeStudentFilter);
        });
        this.updateStudentsList();
      });
    });
  }

  // ==================== Utility Methods ====================
  extractYear(dateStr) {
    if (!dateStr) return null;
    const match = dateStr.match(/(\d{4})/);
    return match ? parseInt(match[1]) : null;
  }

  parseDate(dateStr) {
    if (!dateStr) return null;
    // Expected format: "Mon YYYY" (e.g., "Sep 2019")
    const months = {
      'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'Jun': 5,
      'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11
    };
    const parts = dateStr.split(' ');
    if (parts.length === 2) {
      const month = months[parts[0]];
      const year = parseInt(parts[1]);
      if (month !== undefined && !isNaN(year)) {
        return new Date(year, month);
      }
    }
    return null;
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  const profileCards = new ProfileCards();
  profileCards.init();
});
