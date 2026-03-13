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

## Setup

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. **Clone and navigate**:
   ```bash
   cd projects/pmcursor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your `OPENAI_API_KEY`.

4. **Run the application**:
   ```bash
   python run.py
   ```

5. **Open your browser**:
   Navigate to http://localhost:8000

## Usage

1. **Create a Project**: Enter a name and description for your product project
2. **Upload Data**: Select or drag-drop interview transcripts, usage logs, or feedback data
3. **Analyze**: Ask a question like "What should we build next?" and let the AI analyze
4. **Review Results**: Get feature proposals with justifications, proposed changes, and development tasks

## API Endpoints

- `GET /` - Web interface
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `POST /api/projects/{id}/uploads` - Upload file to project
- `GET /api/projects/{id}/uploads` - List project uploads
- `POST /api/projects/{id}/analyze` - Generate feature recommendations
- `GET /api/projects/{id}/analyses` - List analysis history
- `GET /health` - Health check

## Development

### Running Tests
```bash
pytest tests/
```

### Project Structure
The codebase follows clean architecture principles with separation of concerns:
- API layer handles HTTP requests/responses
- Core layer contains business logic
- Models layer defines data structures
- Storage layer manages file operations

## Current Status

✅ **Phase 1 Complete**: Architecture designed and project structure implemented with core functionality

- Web interface with project management
- File upload system supporting multiple formats
- AI-powered analysis engine
- Comprehensive feature proposal generation
- Development task breakdown
