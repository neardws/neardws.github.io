---
name: openprism
description: OpenPrism LaTeX workspace integration. Manage LaTeX projects, edit files, compile documents via local OpenPrism API server (port 8787).
---

# OpenPrism Skill

Interact with local OpenPrism LaTeX workspace server for project management, editing, and compilation.

## Configuration

- **API Base URL**: `http://localhost:8787`
- **Data Directory**: `~/User_Services/openprism/data`

## Project Management

### List Projects
```bash
curl http://localhost:8787/api/projects | jq
```

### Create Project
```bash
# Empty project
curl -X POST http://localhost:8787/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Paper"}'

# From template
curl -X POST http://localhost:8787/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Paper", "template": "ieee-conference"}'
```

### Rename Project
```bash
curl -X POST http://localhost:8787/api/projects/{id}/rename-project \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'
```

### Copy Project
```bash
curl -X POST http://localhost:8787/api/projects/{id}/copy \
  -H "Content-Type: application/json" \
  -d '{"name": "Copy of Project"}'
```

### Delete/Archive
```bash
# Move to trash
curl -X DELETE http://localhost:8787/api/projects/{id}

# Permanent delete
curl -X DELETE http://localhost:8787/api/projects/{id}/permanent

# Archive
curl -X PATCH http://localhost:8787/api/projects/{id}/archive \
  -H "Content-Type: application/json" \
  -d '{"archived": true}'
```

### Tags
```bash
curl -X PATCH http://localhost:8787/api/projects/{id}/tags \
  -H "Content-Type: application/json" \
  -d '{"tags": ["research", "draft"]}'
```

## File Operations

### Get File Tree
```bash
curl http://localhost:8787/api/projects/{id}/tree | jq
```

### Read File
```bash
curl "http://localhost:8787/api/projects/{id}/file?path=main.tex" | jq -r '.content'
```

### Write File
```bash
curl -X PUT http://localhost:8787/api/projects/{id}/file \
  -H "Content-Type: application/json" \
  -d '{"path": "main.tex", "content": "\\documentclass{article}..."}'
```

### Get All Files
```bash
curl http://localhost:8787/api/projects/{id}/files | jq
```

### Create Folder
```bash
curl -X POST http://localhost:8787/api/projects/{id}/folder \
  -H "Content-Type: application/json" \
  -d '{"path": "sections"}'
```

### Rename File/Folder
```bash
curl -X POST http://localhost:8787/api/projects/{id}/rename \
  -H "Content-Type: application/json" \
  -d '{"from": "oldname.tex", "to": "newname.tex"}'
```

### Upload Files
```bash
curl -X POST http://localhost:8787/api/projects/{id}/upload \
  -F "files=@image.png" \
  -F "files=@figure.jpg"
```

### Get Binary Asset (Image/PDF)
```bash
curl "http://localhost:8787/api/projects/{id}/blob?path=figure.png" -o figure.png
curl "http://localhost:8787/api/projects/{id}/blob?path=output.pdf" -o output.pdf
```

## Compilation

### Compile Project
```bash
curl -X POST http://localhost:8787/api/compile \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "{id}",
    "mainFile": "main.tex",
    "engine": "pdflatex"
  }' | jq
```

**Engines**: `pdflatex`, `xelatex`, `lualatex`, `latexmk`, `tectonic`

Response includes:
- `ok`: success status
- `pdf`: base64 encoded PDF (if successful)
- `log`: compilation log
- `status`: exit code

## Templates

### List Templates
```bash
curl http://localhost:8787/api/templates | jq
```

### Apply Template to Project
```bash
curl -X POST http://localhost:8787/api/projects/{id}/template \
  -H "Content-Type: application/json" \
  -d '{"template": "ieee-conference"}'
```

### Convert to Template (Merge)
```bash
curl -X POST http://localhost:8787/api/projects/{id}/convert-template \
  -H "Content-Type: application/json" \
  -d '{"targetTemplate": "ieee-conference", "mainFile": "main.tex"}'
```

## Import

### Import from ZIP
```bash
curl -X POST http://localhost:8787/api/projects/import-zip \
  -F "zip=@project.zip" \
  -F "projectName=Imported Project"
```

### Import from arXiv (SSE stream)
```bash
curl "http://localhost:8787/api/projects/import-arxiv-sse?arxivIdOrUrl=2401.12345&projectName=My+Paper"
```

## arXiv Integration

### Search arXiv
```bash
curl -X POST http://localhost:8787/api/arxiv/search \
  -H "Content-Type: application/json" \
  -d '{"query": "transformer architecture", "maxResults": 10}' | jq
```

### Get arXiv BibTeX
```bash
curl -X POST http://localhost:8787/api/arxiv/bibtex \
  -H "Content-Type: application/json" \
  -d '{"arxivId": "2401.12345"}' | jq -r '.bibtex'
```

## Service Management

### Check Status
```bash
curl http://localhost:8787/ | jq
```

### View Logs (PM2)
```bash
pm2 logs openprism-backend
pm2 logs openprism-frontend
```

### Restart Service
```bash
pm2 restart openprism-backend
pm2 restart openprism-frontend
```

## Common Workflows

### Create and Compile New Paper
```bash
# 1. Create project
PROJECT=$(curl -s -X POST http://localhost:8787/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Research Paper", "template": "ieee-conference"}' | jq -r '.id')

# 2. Edit main.tex
curl -X PUT http://localhost:8787/api/projects/$PROJECT/file \
  -H "Content-Type: application/json" \
  -d '{"path": "main.tex", "content": "\\documentclass{IEEEtran}..."}'

# 3. Compile
curl -X POST http://localhost:8787/api/compile \
  -H "Content-Type: application/json" \
  -d "{\"projectId\": \"$PROJECT\", \"mainFile\": \"main.tex\", \"engine\": \"pdflatex\"}" | jq

# 4. Download PDF
curl "http://localhost:8787/api/projects/$PROJECT/blob?path=output.pdf" -o paper.pdf
```

## Project Structure

Projects stored in: `~/User_Services/openprism/data/{project-id}/`
- `project.json` - Metadata (name, tags, archived status)
- `.tex` files - LaTeX source
- Assets - Images, figures, etc.

## References

- GitHub: <https://github.com/assistant-ui/open-prism>
- Local Data: `~/User_Services/openprism/data`
- Logs: `~/User_Services/services-logs/openprism-*.log`
