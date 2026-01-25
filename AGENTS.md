# AGENTS.md

This document provides essential information for AI agents working with this repository.

## Project Overview

Personal academic website for Xincao Xu, built with Jekyll and hosted on GitHub Pages.

- **Framework**: Jekyll (Ruby-based static site generator)
- **Hosting**: GitHub Pages
- **Language**: Ruby 3.1+, HTML, Markdown, Sass, JavaScript

## Quick Start

```bash
# Install dependencies
bundle install

# Run local development server
bundle exec jekyll serve

# Or use the convenience script
./run_server.sh
```

The site will be available at `http://localhost:4000`

## Project Structure

```
.
├── _config.yml          # Jekyll configuration
├── _data/               # Data files (YAML)
│   └── navigation.yml   # Site navigation menu
├── _includes/           # Reusable HTML partials
├── _layouts/            # Page layout templates
├── _pages/              # Static pages (about, blog, etc.)
├── _posts/              # Blog posts (YYYY-MM-DD-title.html)
├── _sass/               # Sass stylesheets
├── assets/              # Static assets (CSS, JS, images)
├── images/              # Image files
├── docs/                # Documentation
├── google_scholar_crawler/  # Python script for citation data
├── Gemfile              # Ruby dependencies
└── Gemfile.lock         # Locked dependency versions
```

## Build Commands

| Command | Description |
|---------|-------------|
| `bundle install` | Install Ruby dependencies |
| `bundle exec jekyll serve` | Start development server with live reload |
| `bundle exec jekyll build` | Build static site to `_site/` |
| `bundle exec jekyll serve --livereload` | Server with automatic browser refresh |

## Code Quality

### Linting

```bash
# Install RuboCop
gem install rubocop

# Run linter
rubocop

# Auto-fix issues
rubocop --auto-correct
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## Content Guidelines

### Adding Blog Posts

1. Create file in `_posts/` with format: `YYYY-MM-DD-title.html` or `.md`
2. Include YAML front matter:

```yaml
---
layout: post
title: "Post Title"
date: YYYY-MM-DD
lang: en  # or zh for Chinese
permalink: /blog/post-slug/
excerpt: "Brief description for card preview"
---
```

### Modifying Pages

- Static pages are in `_pages/`
- Use Markdown or HTML with YAML front matter
- Navigation links configured in `_data/navigation.yml`

## Environment Variables

For the Google Scholar crawler workflow:
- `GOOGLE_SCHOLAR_ID` - Required for citation data (set in GitHub Actions secrets)

## CI/CD

### GitHub Actions Workflows

1. **Deploy Jekyll site to Pages** (`jekyll.yml`)
   - Triggers: Push to `main` branch
   - Builds and deploys site to GitHub Pages

2. **Get Citation Data** (`google_scholar_crawler.yaml`)
   - Triggers: Daily at 08:00 UTC, on page build
   - Updates Google Scholar citation statistics

## Common Tasks

### Update Site Content
1. Edit Markdown/HTML files in `_pages/` or `_posts/`
2. Commit and push to `main`
3. GitHub Actions will auto-deploy

### Update Dependencies
```bash
bundle update
```

### Test Build Locally
```bash
bundle exec jekyll build --drafts
```

## Troubleshooting

- **Bundle install fails**: Ensure Ruby 3.1+ is installed
- **Jekyll serve errors**: Check `_config.yml` syntax
- **Styles not updating**: Clear `.jekyll-cache/` and rebuild
