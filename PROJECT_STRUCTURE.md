# Project Structure Documentation

## Overview

This document provides a detailed overview of the Question Answer Generator project structure, explaining the purpose of each directory and key files.

## Directory Structure

```
question-answer-generator/
│
├── .kiro/                          # Kiro specification files
│   └── specs/
│       └── question-answer-generator/
│           ├── requirements.md     # Feature requirements
│           ├── design.md          # Design document
│           └── tasks.md           # Implementation tasks
│
├── backend/                        # Python backend application
│   ├── config/                    # Configuration modules
│   │   ├── __init__.py
│   │   ├── settings.py           # Application settings (env vars)
│   │   └── logging_config.py     # Logging configuration
│   │
│   ├── src/                       # Source code
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application entry point
│   │   ├── tasks.py              # Celery async tasks
│   │   └── utils/                # Utility functions
│   │       ├── __init__.py
│   │       └── setup.py          # Directory setup utilities
│   │
│   ├── tests/                     # Test files
│   │   └── __init__.py
│   │
│   ├── .env.example              # Example environment variables
│   ├── Dockerfile                # Docker image for backend
│   ├── pytest.ini                # Pytest configuration
│   └── requirements.txt          # Python dependencies
│
├── frontend/                      # React frontend application
│   ├── src/                      # Source code
│   │   ├── App.jsx              # Main application component
│   │   ├── main.jsx             # Application entry point
│   │   ├── index.css            # Global styles (Tailwind)
│   │   └── setupTests.js        # Jest test setup
│   │
│   ├── .babelrc                 # Babel configuration
│   ├── Dockerfile               # Docker image for frontend
│   ├── index.html               # HTML template
│   ├── jest.config.js           # Jest test configuration
│   ├── package.json             # Node dependencies and scripts
│   ├── postcss.config.js        # PostCSS configuration
│   ├── tailwind.config.js       # Tailwind CSS configuration
│   └── vite.config.js           # Vite build tool configuration
│
├── .gitignore                    # Git ignore patterns
├── docker-compose.yml            # Docker Compose orchestration
├── README.md                     # Main project documentation
├── QUICKSTART.md                 # Quick start guide
├── PROJECT_STRUCTURE.md          # This file
├── setup.bat                     # Setup script for Windows
└── run.bat                       # Command runner for Windows
```

## Key Files Explained

### Backend Configuration

#### `backend/config/settings.py`
- Manages all application settings using Pydantic
- Loads configuration from environment variables
- Includes settings for API, storage, LLM APIs, Redis, Celery, and more

#### `backend/config/logging_config.py`
- Configures application logging
- Sets up console and file handlers with rotation
- Creates log directory automatically

#### `backend/.env.example`
- Template for environment variables
- Copy to `.env` and fill in actual values
- Contains API keys, paths, and configuration options

### Backend Application

#### `backend/src/main.py`
- FastAPI application entry point
- Defines API endpoints
- Configures CORS middleware
- Creates necessary directories on startup

#### `backend/src/tasks.py`
- Celery task definitions
- Handles asynchronous processing
- Will contain question paper processing logic

#### `backend/requirements.txt`
- All Python dependencies
- Includes FastAPI, ReportLab, Graphviz, ChromaDB, Hypothesis, pytest, etc.

### Frontend Application

#### `frontend/src/main.jsx`
- React application entry point
- Renders the root App component

#### `frontend/src/App.jsx`
- Main application component
- Will contain the UI for file upload, language selection, etc.

#### `frontend/package.json`
- Node.js dependencies
- NPM scripts for development, build, and testing
- Includes React, Vite, Tailwind CSS, Axios, Jest

#### `frontend/vite.config.js`
- Vite build tool configuration
- Proxy configuration for API calls
- Development server settings

### Docker Configuration

#### `docker-compose.yml`
- Orchestrates all services (backend, frontend, Redis, Celery)
- Defines volumes for data persistence
- Sets up networking between services
- Configures health checks

#### `backend/Dockerfile`
- Docker image for Python backend
- Installs system dependencies (Graphviz, Tesseract OCR)
- Installs Python packages
- Creates necessary directories

#### `frontend/Dockerfile`
- Docker image for React frontend
- Based on Node.js Alpine
- Installs npm dependencies

### Testing Configuration

#### `backend/pytest.ini`
- Pytest configuration
- Defines test markers (unit, integration, property)
- Sets test discovery patterns

#### `frontend/jest.config.js`
- Jest test configuration
- Sets up jsdom environment
- Configures test coverage

### Utility Scripts

#### `setup.bat`
- Initial setup script for Windows
- Checks Docker installation
- Creates .env file from template

#### `run.bat`
- Command runner for common tasks
- Provides shortcuts for starting, stopping, testing
- Simplifies Docker Compose commands

## Data Directories (Created at Runtime)

These directories are created automatically when the application starts:

- `backend/uploads/` - Uploaded question papers
- `backend/outputs/` - Generated PDF files
- `backend/logs/` - Application logs
- `backend/data/chromadb/` - Vector database storage

## Development Workflow

### Adding New Features

1. **Backend Components**: Add to `backend/src/`
2. **Frontend Components**: Add to `frontend/src/`
3. **Tests**: Add to `backend/tests/` or `frontend/src/` (co-located)
4. **Configuration**: Update `backend/config/settings.py` if needed

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Adding Dependencies

```bash
# Backend
cd backend
pip install <package>
pip freeze > requirements.txt

# Frontend
cd frontend
npm install <package>
```

## Environment Variables

All environment variables are defined in `backend/.env`. Key variables:

- `OPENAI_API_KEY` - Required for answer generation
- `REDIS_HOST` - Redis server host
- `UPLOAD_DIR` - Where uploaded files are stored
- `OUTPUT_DIR` - Where generated PDFs are saved
- `LOG_LEVEL` - Logging verbosity

## Port Assignments

- `3000` - Frontend development server
- `8000` - Backend API server
- `6379` - Redis server

## Next Steps

After setting up the project structure:

1. Implement data models (Task 2)
2. Implement Language Service (Task 3)
3. Implement Educational Knowledge Base (Task 4)
4. Continue with remaining tasks in `tasks.md`

## Additional Resources

- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [requirements.md](.kiro/specs/question-answer-generator/requirements.md) - Feature requirements
- [design.md](.kiro/specs/question-answer-generator/design.md) - System design
- [tasks.md](.kiro/specs/question-answer-generator/tasks.md) - Implementation plan
