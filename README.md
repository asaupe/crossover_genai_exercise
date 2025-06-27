# 🎓 GenAI Email Processing System
AI-powered customer email processing using RAG, embeddings, and intelligent response generation

A sophisticated email processing system that automatically categorizes, analyzes, and generates responses to customer emails. Built with cutting-edge AI technologies including Retrieval-Augmented Generation (RAG), OpenAI embeddings, and intelligent validation systems.

## ✨ Features
🤖 **AI-Powered Email Processing** - Uses GPT and embeddings for intelligent email categorization and response generation
🔍 **Semantic Search** - Vector-based similarity search with ChromaDB indexing
🛡️ **Smart Guardrails** - Validates responses and prevents hallucinations
🎨 **Modern API Interface** - RESTful FastAPI with automatic documentation
🔄 **Batch Processing** - Handle multiple emails efficiently
📊 **Analytics Dashboard** - Email processing metrics and insights
🌐 **Multi-language Support** - Process emails in multiple languages (en, es, fr, de)
⚡ **Real-time Processing** - Fast response times with async operations

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- OpenAI API key
- 4GB+ RAM (for embeddings)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/asaupe/crossover_genai_exercise.git

pytest --cov=src

# Verbose output
pytest -v

# Specific test file
pytest tests/test_email_processor.py
```

### Test Categories
- **Unit tests** for all core modules
- **Integration tests** for end-to-end workflows
- **API tests** for endpoint validation
- **Performance benchmarks**

### Validation Scripts
```bash
# Pre-assessment validation
python pre_assessment_check.py

# API key testing
python test_openai_key.py

# API key format validation
python validate_api_key.py
```

## 📁 Project Structure

```
crossover_genai_assessment/
├── 📄 README.md                 # This file
├── 📄 QUICK_REFERENCE.md        # Quick command reference
├── 📄 requirements.txt          # Python dependencies
├── 📄 .env.example             # Environment template
├── 📄 Dockerfile              # Container configuration
├── 📄 docker-compose.yml      # Multi-container setup
├── 📄 Makefile                # Build automation
├── 🗂️ src/                     # Core application modules
│   ├── main.py                 # FastAPI application entry
│   ├── api/                    # API routes and endpoints
│   │   ├── routes.py           # Main router
│   │   └── endpoints/          # Individual endpoint modules
│   ├── core/                   # Business logic
│   │   └── email_processor.py  # Main email processing logic
│   ├── ai/                     # AI/ML components
│   │   ├── llm_client.py       # OpenAI integration
│   │   ├── text_analyzer.py    # Text analysis utilities
│   │   └── semantic_search.py  # Vector search implementation
│   ├── data/                   # Data layer
│   │   ├── models.py           # Pydantic models
│   │   └── database.py         # Database operations
│   ├── config/                 # Configuration
│   │   └── settings.py         # Application settings
│   └── utils/                  # Utilities
│       └── logging.py          # Logging configuration
├── 🗂️ tests/                   # Test suite
│   ├── test_email_processor.py # Core logic tests
│   ├── test_llm_client.py      # AI component tests
│   ├── test_api_endpoints.py   # API tests
│   └── test_integration.py     # End-to-end tests
├── 🗂️ docs/                    # Documentation
│   └── API.md                  # API documentation
├── 🗂️ examples/                # Usage examples
│   └── demo.py                 # Demo script
├── 🗂️ scripts/                 # Utility scripts
│   ├── test_client.py          # API test client
│   ├── generate_sample_data.py # Sample data generator
│   └── benchmark.py            # Performance benchmarks
├── 📄 pre_assessment_check.py  # Setup validation
├── 📄 test_openai_key.py       # API key testing
├── 📄 validate_api_key.py      # Key format validation
└── 🗂️ logs/                    # Application logs
```

## 📊 Implementation Features

### Core Capabilities
✅ **Email Classification** - Automatic categorization by type and urgency
✅ **Sentiment Analysis** - Emotion detection and scoring
✅ **Response Generation** - Context-aware automated responses
✅ **Semantic Search** - Vector-based email similarity search
✅ **Batch Processing** - Efficient multi-email handling
✅ **Multi-language Support** - Process emails in multiple languages
✅ **RAG Integration** - Enhanced responses with relevant context

### Technical Features
✅ **FastAPI Framework** - Modern async web framework
✅ **OpenAI Integration** - GPT-3.5/4 for text processing
✅ **Vector Embeddings** - Semantic search with ChromaDB
✅ **Pydantic Validation** - Strong data validation and serialization
✅ **Comprehensive Testing** - Unit, integration, and API tests
✅ **Logging System** - Structured logging with configurable levels
✅ **Environment Management** - Flexible configuration system

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Application
APP_NAME=GenAI Email Processor
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000

# OpenAI Configuration
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=1000
TEMPERATURE=0.7

# Database
DATABASE_URL=sqlite:///./emails.db

# Vector Database
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=text-embedding-ada-002

# Email Processing
MAX_EMAIL_LENGTH=10000
MAX_RESPONSE_LENGTH=2000
SUPPORTED_LANGUAGES=en,es,fr,de

# Security
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🐛 Troubleshooting

### Common Issues

**"OpenAI API Key not found"**
```bash
# Solution: Set environment variable
export OPENAI_API_KEY=your_key_here
# Or edit .env file
```

**"ChromaDB connection failed"**
```bash
# Solution: Check disk space and permissions
# ChromaDB creates local database files
```

**"FastAPI app won't start"**
```bash
# Solution: Check port availability
python -m src.main --port 8001
```

**"Import errors"**
```bash
# Solution: Activate virtual environment
source .venv/bin/activate
pip install -r requirements.txt
```

### Validation Tools
```bash
# Complete system check
python pre_assessment_check.py

# API key validation
python test_openai_key.py

# Key format check
python validate_api_key.py
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -e .`)
4. Run tests (`pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests
- Update documentation
- Use conventional commit messages

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing GPT and embedding APIs
- **FastAPI** for the excellent web framework
- **ChromaDB** for vector database capabilities
- **LangChain** for LLM application framework
- **Crossover** for the assessment opportunity
cd crossover_genai_exercise
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python -m src.main
```

## Usage

### API Endpoints

- `POST /api/v1/emails/process` - Process and categorize an email
- `POST /api/v1/emails/respond` - Generate automated response
- `GET /api/v1/emails/search` - Semantic search through emails
- `GET /api/v1/health` - Health check endpoint

### Example Usage

```python
import requests

# Process an email
response = requests.post("http://localhost:8000/api/v1/emails/process", json={
    "subject": "Issue with order #12345",
    "body": "I received the wrong item in my order...",
    "sender": "customer@example.com"
})

# Search emails
response = requests.get("http://localhost:8000/api/v1/emails/search", params={
    "query": "order issues",
    "limit": 10
})
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Development

### Code Style
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run all checks:
```bash
make lint
```

### Logging
The application uses structured logging with different levels:
- INFO: General application flow
- WARNING: Potential issues
- ERROR: Error conditions
- DEBUG: Detailed debugging information

## Configuration

Key configuration options in `.env`:

```
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./emails.db
LOG_LEVEL=INFO
CHROMA_PERSIST_DIRECTORY=./chroma_db
MAX_EMAIL_LENGTH=10000
```

## License

This project is for assessment purposes.
