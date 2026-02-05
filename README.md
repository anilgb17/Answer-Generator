# Question Answer Generator

A web-based system that accepts questions or question papers as input and produces comprehensive answers in PDF format with supporting visual elements in multiple languages.

## Project Structure

```
.
├── backend/                    # Python backend
│   ├── src/                   # Source code
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   └── tasks.py          # Celery tasks
│   ├── tests/                # Test files
│   │   └── __init__.py
│   ├── config/               # Configuration modules
│   │   ├── __init__.py
│   │   ├── settings.py       # Application settings
│   │   └── logging_config.py # Logging configuration
│   ├── requirements.txt      # Python dependencies
│   ├── pytest.ini           # Pytest configuration
│   ├── Dockerfile           # Backend Docker image
│   └── .env.example         # Example environment variables
│
├── frontend/                 # React frontend
│   ├── src/                 # Source code
│   │   ├── main.jsx        # Application entry point
│   │   ├── App.jsx         # Main App component
│   │   ├── index.css       # Global styles
│   │   └── setupTests.js   # Test setup
│   ├── package.json        # Node dependencies
│   ├── vite.config.js      # Vite configuration
│   ├── tailwind.config.js  # Tailwind CSS configuration
│   ├── postcss.config.js   # PostCSS configuration
│   ├── jest.config.js      # Jest configuration
│   ├── .babelrc            # Babel configuration
│   ├── Dockerfile          # Frontend Docker image
│   └── index.html          # HTML template
│
└── docker-compose.yml       # Docker Compose configuration

```

## Features

- Multi-format input support (text, PDF, images)
- Multi-language answer generation (10+ languages)
- Educational knowledge base integration
- Automatic visual element generation (diagrams, flowcharts)
- Professional PDF output with table of contents
- Asynchronous processing with progress tracking
- Web-based interface with drag-and-drop upload

## Technology Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Web framework
- **Celery** - Asynchronous task queue
- **Redis** - Caching and message broker
- **ReportLab** - PDF generation
- **Graphviz** - Diagram generation
- **ChromaDB** - Vector database for knowledge base
- **Hypothesis** - Property-based testing
- **pytest** - Testing framework

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Jest** - Testing framework

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)
- At least one AI provider API key (Gemini recommended - FREE)

### Quick Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/anilgb17/Answer-Generator.git
   cd Answer-Generator
   ```

2. **Setup environment file**
   ```bash
   # Run the automated setup script
   python setup_env.py
   ```
   
   Or manually:
   ```bash
   # Windows
   copy backend\.env.example backend\.env
   
   # Linux/Mac
   cp backend/.env.example backend/.env
   ```

3. **Add your API keys**
   
   Open `backend/.env` and add at least ONE API key:
   
   - **Gemini (FREE - Recommended)**: Get from https://makersuite.google.com/app/apikey
   - **Perplexity (FREE tier)**: Get from https://www.perplexity.ai/settings/api
   - **OpenAI (PAID)**: Get from https://platform.openai.com/api-keys
   - **Anthropic (PAID)**: Get from https://console.anthropic.com/
   
   Example:
   ```bash
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Start the application**
   ```bash
   # Windows
   start-project.bat
   
   # Linux/Mac
   docker-compose up -d
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Setup with Docker (Recommended)

1. Clone the repository
2. Run the setup script:
   ```bash
   python setup_env.py
   ```
3. Add your API keys to `backend/.env` (at least one required)
4. Start all services:
   ```bash
   docker-compose up -d
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development Setup

#### Backend

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy and configure environment:
   ```bash
   copy .env.example .env
   ```

5. Start Redis (required):
   ```bash
   docker run -p 6379:6379 redis:7-alpine
   ```

6. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

7. Run Celery worker (in separate terminal):
   ```bash
   celery -A src.tasks worker --loglevel=info
   ```

8. Run tests:
   ```bash
   pytest
   ```

#### Frontend

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

4. Run tests:
   ```bash
   npm test
   ```

## Configuration

Configuration is managed through environment variables. See `backend/.env.example` for all available options.

Key configuration options:
- `OPENAI_API_KEY` - OpenAI API key for answer generation
- `ANTHROPIC_API_KEY` - Anthropic API key (alternative)
- `MAX_FILE_SIZE_MB` - Maximum upload file size
- `PDF_RETENTION_DAYS` - How long to keep generated PDFs
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## Testing

### Backend Tests
```bash
cd backend
pytest                    # Run all tests
pytest -m unit           # Run unit tests only
pytest -m property       # Run property-based tests only
pytest -m integration    # Run integration tests only
```

### Frontend Tests
```bash
cd frontend
npm test                 # Run all tests
npm test -- --coverage   # Run with coverage
```

## Deployment

For production deployment, see the comprehensive guides:

- **[Quick Start Guide](QUICKSTART.md)** - Get started in minutes with Docker
- **[Deployment Guide](DEPLOYMENT.md)** - Complete deployment documentation
- **[Deployment Checklist](DEPLOYMENT_CHECKLIST.md)** - Pre-deployment checklist
- **[Kubernetes Guide](k8s/README.md)** - Kubernetes deployment instructions

### Deployment Options

1. **Docker Compose (Recommended for small-scale)**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Kubernetes (Recommended for production)**
   ```bash
   cd k8s
   ./deploy.sh
   ```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Documentation

- [Quick Start Guide](QUICKSTART.md) - Get up and running quickly
- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md) - Pre-deployment verification
- [Requirements Document](.kiro/specs/question-answer-generator/requirements.md) - System requirements
- [Design Document](.kiro/specs/question-answer-generator/design.md) - Architecture and design
- [Tasks Document](.kiro/specs/question-answer-generator/tasks.md) - Implementation plan
- [Kubernetes Guide](k8s/README.md) - Kubernetes deployment

## License

MIT
