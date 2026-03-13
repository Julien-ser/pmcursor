# PMCursor

**AI-Powered Product Management Assistant**

PMCursor is an AI-native system that helps teams figure out what to build. Upload customer interviews and product usage data, ask "what should we build next?", and get comprehensive feature recommendations complete with justifications, proposed changes to UI/data model/workflows, and broken-down development tasks for your coding agents.

## Features

- **Multi-format Data Ingestion**: Support for PDF, TXT, CSV, JSON, and Markdown files
- **AI-Powered Analysis**: Uses GPT-4 to synthesize customer feedback and usage patterns
- **Comprehensive Proposals**: Feature ideas with UI changes, data model modifications, and workflow adjustments
- **Development Task Breakdown**: Automatically generates actionable development tasks with estimates
- **Web Interface**: Clean, intuitive UI for uploading files and viewing recommendations
- **Project Organization**: Manage multiple product projects separately

## Architecture

```
pmcursor/
├── src/
│   ├── api/              # FastAPI REST API and web server
│   │   ├── routes.py    # API endpoints
│   │   └── server.py    # Application factory and server setup
│   ├── core/            # Business logic
│   │   ├── data_processor.py   # File content extraction
│   │   └── feature_proposer.py # AI-powered feature generation
│   ├── models/          # Database models
│   │   └── database.py  # SQLAlchemy models
│   ├── storage/         # File management
│   │   └── file_manager.py
│   └── utils/           # Helper utilities
│       └── helpers.py
├── templates/           # Jinja2 HTML templates
├── static/             # Static assets (CSS, JS)
├── uploads/            # User-uploaded files (created at runtime)
├── data/               # Generated data (created at runtime)
├── run.py              # Application entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── config.py           # Configuration management
```

**Technology Stack:**
- **Backend**: FastAPI (async Python)
- **Database**: SQLite (via SQLAlchemy ORM)
- **AI**: OpenAI GPT-4 API
- **Frontend**: Bootstrap 5 + vanilla JavaScript
- **File Processing**: PyPDF2, pandas

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Data Formats](#data-formats)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure OpenAI API key
cp .env.example .env
# Edit .env to add your OPENAI_API_KEY

# 3. Run the server
python run.py

# 4. Open http://localhost:8000 in your browser
```

## Installation

### Prerequisites

- **Python 3.9+** - Check with `python3 --version`
- **OpenAI API key** - Get one at [platform.openai.com](https://platform.openai.com)
- **pip** - Package installer (usually comes with Python)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd projects/pmcursor
   ```

2. **Create virtual environment (optional but recommended)**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

5. **Verify installation**
   ```bash
   python -c "import src; print('Installation successful')"
   ```

## Configuration

Environment variables are loaded via Pydantic Settings from `.env` file or environment.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENAI_API_KEY` | string | **required** | Your OpenAI API key |
| `APP_HOST` | string | `0.0.0.0` | Server host address |
| `APP_PORT` | integer | `8000` | Server port |
| `DEBUG` | boolean | `True` | Enable debug mode |
| `DATABASE_URL` | string | `sqlite:///./pmcursor.db` | Database connection URL |
| `UPLOAD_DIR` | string | `uploads` | Upload files directory |
| `DATA_DIR` | string | `data` | Generated data directory |
| `MAX_UPLOAD_SIZE_MB` | integer | `50` | Maximum file upload size in MB |

### Database Configuration

- **Development**: SQLite (default) - No setup required
- **Production**: PostgreSQL/MySQL - Update `DATABASE_URL`
  ```env
  DATABASE_URL=postgresql://user:password@localhost/pmcursor
  ```

## Usage Guide

### Getting Started

1. **Create a Project**
   - Enter a descriptive name (e.g., "SaaS Product Interviews Q1 2024")
   - Add an optional description of your product or research focus

2. **Upload Data Files**
   - Supported formats: PDF, TXT, MD, CSV, JSON
   - Upload interview transcripts, user feedback, usage logs, survey results
   - Multiple files supported - they'll be combined for analysis

3. **Run Analysis**
   - Use default query "What should we build next?" or customize
   - Examples:
     - "What are the top 3 pain points customers mention?"
     - "How could we improve onboarding experience?"
     - "What features would increase user retention?"

4. **Review Results**
   - Feature title and detailed description
   - Justification linking to specific customer feedback
   - Proposed UI changes (layout, components, UX)
   - Data model modifications (new tables, fields, relationships)
   - Workflow changes (user journey modifications)
   - Priority level (high/medium/low)
   - Development tasks with:
     - Task title and description
     - Category (backend, frontend, database, testing, devops)
     - Estimated effort in hours

### Supported Data Formats

| Format | Processing | Notes |
|--------|-----------|-------|
| `.txt` | Plain text extraction | Best for interview transcripts |
| `.md` | Markdown text | Preserves formatting |
| `.pdf` | Text extraction via PyPDF2 | Scanned PDFs not supported (no OCR) |
| `.csv` | Summary with column names + sample rows | Good for structured survey data |
| `.json` | Formatted JSON dump | For structured APIs/exports |

### Best Practices

- **File Content**: Include actual user quotes for stronger justifications
- **Multiple Sources**: Upload various data types (interviews + usage stats) for richer insights
- **Context**: In project description, include product overview and target users
- **Query Specificity**: Ask targeted questions for more focused recommendations
- **Iteration**: Run multiple analyses with different queries to explore possibilities

## API Reference

All API endpoints are prefixed with `/api`. Responses follow standard JSON format.

### Base URL

```http
http://localhost:8000
```

### Projects

#### `POST /api/projects`

Create a new project.

**Request** (form data):
```
name: string (required)
description: string (optional)
```

**Response**:
```json
{
  "id": 1,
  "name": "My Project",
  "description": "Project description"
}
```

#### `GET /api/projects`

List all projects.

**Response**:
```json
[
  {
    "id": 1,
    "name": "My Project",
    "description": "Project description",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### Uploads

#### `POST /api/projects/{project_id}/uploads`

Upload a file to a project.

**Request** (multipart/form-data):
```
file: File (required) - Supported types: pdf, txt, md, csv, json
```

**Response**:
```json
{
  "id": 1,
  "filename": "interview.pdf",
  "status": "pending"
}
```

**Status Codes**:
- `200` - Upload successful
- `400` - File type not allowed
- `404` - Project not found

#### `GET /api/projects/{project_id}/uploads`

List all uploaded files for a project.

**Response**:
```json
[
  {
    "id": 1,
    "filename": "interview.pdf",
    "file_type": "pdf",
    "status": "pending"
  }
]
```

### Analysis

#### `POST /api/projects/{project_id}/analyze`

Generate feature recommendations from uploaded data.

**Request** (form data):
```
query: string (optional, default: "What should we build next?")
```

**Response** (Success):
```json
{
  "analysis_id": 1,
  "feature": {
    "id": 1,
    "title": "Smart Notification System",
    "description": "An intelligent notification system that learns user preferences...",
    "justification": "Based on 15 customer interviews, 80% mentioned...",
    "ui_changes": "Add notification preferences panel in settings...",
    "data_model_changes": "New table: user_notification_preferences...",
    "workflow_changes": "Users will now configure notifications during onboarding...",
    "priority": "high",
    "tasks": [
      {
        "id": 1,
        "title": "Design notification preference UI",
        "description": "Create mockups and interactive prototype...",
        "task_type": "frontend",
        "estimated_hours": 12
      },
      {
        "id": 2,
        "title": "Implement preference storage",
        "description": "Add database table and backend API...",
        "task_type": "backend",
        "estimated_hours": 8
      }
    ]
  }
}
```

**Response** (No data):
```json
{
  "analysis_id": 1,
  "message": "No data to analyze"
}
```

**Status Codes**:
- `200` - Analysis completed successfully
- `404` - Project not found
- `500` - Analysis failed (check response for error details)

#### `GET /api/projects/{project_id}/analyses`

List all analysis runs for a project.

**Response**:
```json
[
  {
    "id": 1,
    "query": "What should we build next?",
    "summary": "Generated 5 development tasks",
    "status": "completed",
    "created_at": "2024-01-15T11:00:00"
  }
]
```

### Health Check

#### `GET /health`

Application health status.

**Response**:
```json
{
  "status": "healthy"
}
```

## Examples

### cURL Examples

**Create project:**
```bash
curl -X POST "http://localhost:8000/api/projects" \
  -F "name=My SaaS Product" \
  -F "description=Customer interview analysis Q1 2024"
```

**Upload file:**
```bash
curl -X POST "http://localhost:8000/api/projects/1/uploads" \
  -F "file=@./interviews.pdf"
```

**Run analysis:**
```bash
curl -X POST "http://localhost:8000/api/projects/1/analyze" \
  -F "query=What are the most requested features?"
```

**List projects:**
```bash
curl "http://localhost:8000/api/projects"
```

**List analyses:**
```bash
curl "http://localhost:8000/api/projects/1/analyses"
```

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Create project
project = requests.post(f"{BASE_URL}/api/projects", data={
    "name": "My Project",
    "description": "Product discovery analysis"
}).json()
project_id = project["id"]

# Upload file
with open("customer_interviews.pdf", "rb") as f:
    requests.post(f"{BASE_URL}/api/projects/{project_id}/uploads", files={
        "file": ("interviews.pdf", f, "application/pdf")
    })

# Run analysis
result = requests.post(f"{BASE_URL}/api/projects/{project_id}/analyze", data={
    "query": "What should we build next to reduce churn?"
}).json()

print(f"Feature: {result['feature']['title']}")
for task in result['feature']['tasks']:
    print(f"- {task['title']} ({task['estimated_hours']}h)")
```

### JavaScript Example

```javascript
// Create project
const project = await fetch('/api/projects', {
  method: 'POST',
  body: new URLSearchParams({
    name: 'My Project',
    description: 'Product discovery analysis'
  })
}).then(r => r.json());

// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
await fetch(`/api/projects/${project.id}/uploads`, {
  method: 'POST',
  body: formData
});

// Run analysis
const result = await fetch(`/api/projects/${project.id}/analyze`, {
  method: 'POST',
  body: new URLSearchParams({
    query: 'What features do power users need?'
  })
}).then(r => r.json());

console.log(`Feature: ${result.feature.title}`);
result.feature.tasks.forEach(task => {
  console.log(`- ${task.title} (${task.estimated_hours}h)`);
});
```

## Troubleshooting

### Common Issues

**"No module named 'src'"**  
Fix: Run from project root directory, or use `python -m src.api.server`

**"Invalid API key" or "Authentication error"**  
Fix: Verify `OPENAI_API_KEY` in `.env` file is correct and has credits

**"File type not allowed"**  
Fix: Check file extension is supported: pdf, txt, md, csv, json

**"413 Request Entity Too Large"**  
Fix: Increase `MAX_UPLOAD_SIZE_MB` in `.env` (default: 50MB)

**Database locked errors**  
Fix: Ensure only one server instance is running. Stop other processes using the database.

**PDF text extraction returns empty**  
Fix: PDF may be scanned image. Convert to text or use OCR tool first.

**Slow analysis (1+ minutes)**  
Fix: Normal for large datasets. GPT-4 processing takes time. Check OpenAI API status.

**"Database error: no such table"**  
Fix: Initialize database by running the application - tables auto-create on first run.

### Logs

Check `logs/` directory for detailed logs:
```bash
ls logs/
tail -f logs/latest.log
```

### Debug Mode

Enable verbose logging by setting `DEBUG=True` in `.env`. This shows:
- Request/response logs
- SQL queries
- Stack traces on errors

### Getting Help

1. Check this documentation
2. Review logs in `logs/` directory
3. Ensure all dependencies installed: `pip install -r requirements.txt`
4. Verify OpenAI API key is valid and has quota

## Deployment

### Local Production

```bash
# 1. Set production environment
cp .env.example .env
# Edit .env:
# DEBUG=False
# APP_HOST=127.0.0.1  # or your server IP

# 2. Initialize database (automatic on first run)

# 3. Run with production server
python run.py
```

### Using Gunicorn (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn src.api.server:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --access-logfile -
```

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t pmcursor .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... pmcursor
```

### HTTPS with Nginx

Configure Nginx as reverse proxy:
```nginx
server {
    listen 80;
    server_name pmcursor.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Variables for Production

```env
DEBUG=False
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=sqlite:///./pmcursor.db  # or postgresql://...
MAX_UPLOAD_SIZE_MB=100
```

### Database Backup

```bash
# SQLite backup
cp pmcursor.db pmcursor.db.backup-$(date +%Y%m%d)

# Restore
cp pmcursor.db.backup-20240115 pmcursor.db
```

## Development

### Project Structure

```
pmcursor/
├── src/
│   ├── api/              # FastAPI routes and server
│   │   ├── routes.py    # API endpoint definitions
│   │   └── server.py    # FastAPI app creation
│   ├── core/            # Business logic
│   │   ├── data_processor.py   # File parsing and extraction
│   │   └── feature_proposer.py # OpenAI integration
│   ├── models/          # SQLAlchemy models
│   │   └── database.py  # Database schema and session
│   ├── storage/         # File system operations
│   │   └── file_manager.py
│   └── utils/           # Helper functions
│       └── helpers.py
├── templates/           # HTML templates (Jinja2)
├── static/             # CSS, JavaScript
├── tests/              # Unit and integration tests
├── uploads/            # Uploaded files (gitignored)
├── data/               # Generated data (gitignored)
├── logs/               # Application logs (gitignored)
├── .env                # Environment config (gitignored)
├── pmcursor.db         # SQLite database (gitignored)
├── run.py              # Entry point
├── requirements.txt    # Dependencies
├── TASKS.md            # Project tasks tracker
└── README.md           # This file
```

### Layered Architecture

1. **API Layer** (`src/api/`)
   - HTTP request handling
   - Request validation via Pydantic
   - Response formatting

2. **Core Layer** (`src/core/`)
   - Business logic
   - Data processing
   - AI integration

3. **Models Layer** (`src/models/`)
   - Database schema
   - ORM models
   - Session management

4. **Storage Layer** (`src/storage/`)
   - File system abstraction
   - Upload management

5. **Utils Layer** (`src/utils/`)
   - Shared utilities
   - Helper functions

### Code Conventions

- **Formatting**: PEP 8, 4-space indentation
- **Type hints**: Use for all function signatures
- **Docstrings**: Google style for modules, classes, functions
- **Async**: Use `async def` for API handlers, `await` for I/O
- **Error handling**: Raise HTTPException for API errors
- **Imports**: Standard library → third-party → local packages

### Adding New Features

1. Add database models in `src/models/database.py`
2. Add business logic in `src/core/`
3. Create API endpoints in `src/api/routes.py`
4. Add tests in `tests/`
5. Update `README.md` if user-facing changes

## Testing

### Run Tests

```bash
# All tests
pytest

# With verbose output
pytest -v

# Specific test file
pytest tests/test_api.py

# With coverage report
pytest --cov=src

# Run async tests
pytest tests/integration/
```

### Test Structure

- `tests/unit/` - Unit tests for individual modules
- `tests/integration/` - End-to-end API tests
- `tests/conftest.py` - Shared fixtures

### Writing Tests

Follow existing patterns:
```python
import pytest
from src.core.data_processor import DataProcessor

def test_extract_from_text():
    processor = DataProcessor(file_manager_mock)
    result = processor._extract_from_text("sample.txt")
    assert isinstance(result, str)
    assert len(result) > 0
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Ensure tests pass: `pytest`
5. Commit: `git commit -m "Add amazing feature"`
6. Push: `git push origin feature/amazing-feature`
7. Open Pull Request

### Code Review Process

- All PRs require at least one review
- CI must pass (tests, linting)
- Documentation updates required for user-facing changes

## License

[Add license information here]

## Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: [support email if applicable]

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [OpenAI](https://openai.com/) - GPT-4 AI models
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [PyPDF2](https://pypdf2.readthedocs.io/) - PDF processing
