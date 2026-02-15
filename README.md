# Xincao Xu's Homepage

Personal academic website built with Jekyll and hosted on GitHub Pages.

## 🔗 Live Site

**https://neardws.github.io**

(Redirects to your custom domain if configured)

## 🛠️ Architecture

| Layer | Technology |
|-------|------------|
| Framework | Jekyll 4.x |
| Hosting | GitHub Pages |
| Source | `main` branch |
| Build | GitHub Actions (Jekyll workflow) |
| Domain | Custom domain (via CNAME) |

## 📁 Project Structure

```
├── _config.yml          # Jekyll configuration (site metadata, plugins, defaults)
├── _data/navigation.yml # Navigation menu
├── _includes/          # Reusable HTML partials
├── _layouts/           # Page templates
├── _pages/             # Static pages (about, blog, etc.)
├── _posts/             # Blog posts (YYYY-MM-DD-title.html)
├── _sass/              # Sass stylesheets
├── assets/             # CSS, JS, images
├── images/             # Static images
│   └── posts/          # Blog post images
├── .github/workflows/  # CI/CD pipelines
│   └── jekyll.yml      # Deploy workflow
└── google_scholar_crawler/ # Citation data updater
```

## ✍️ Adding Content

### Blog Posts

Create a new file in `_posts/` with format `YYYY-MM-DD-title.html`:

```yaml
---
layout: post
title: "Your Title"
date: YYYY-MM-DD
categories: [Category1, Category2]
lang: zh  # or en
permalink: /path/url/
excerpt: "Brief description"
---
```

### Images for Posts

Place images in `images/posts/<post-slug>/`:

```
images/posts/lalaland-10-years/
├── lalaland-griffith-observatory.jpg
├── lalaland-sebastian-piano.jpg
├── lalaland-dancing.jpg
└── lalaland-audition.jpg
```

## 🚀 Deployment

1. Push to `main` branch
2. GitHub Actions automatically builds and deploys
3. Visit https://github.com/neardws/neardws.github.io/actions to monitor

## 🔧 Local Development

```bash
# Install dependencies
bundle install

# Run local server
bundle exec jekyll serve

# Build for production
bundle exec jekyll build
```

## 📊 Google Scholar Stats

Citation data is updated automatically via GitHub Actions:
- Workflow: `.github/workflows/google_scholar_crawler.yaml`
- Runs: Daily at 08:00 UTC
- Profile: https://scholar.google.com/citations?user=DK5avZUAAAAJ

## 👤 Author

**Xincao Xu (徐新操)**
- Associate Researcher @ UESTC
- Research: Edge Intelligence, Agentic AI, Agentic RL
- Email: xc.xu@uestc.edu.cn
- Google Scholar: https://scholar.google.com/citations?user=DK5avZUAAAAJ
