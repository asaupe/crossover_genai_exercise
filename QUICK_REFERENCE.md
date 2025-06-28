# 🚀 Quick Reference Guide - GenAI Email Processor

## 📋 Choose Your Implementation

### 📓 Jupyter Notebook (Interactive Analysis)
```bash
# Best for: Learning, experimentation, one-time processing

# Google Colab (Recommended)
1. Upload fashion_store_email_processor.ipynb to colab.research.google.com
2. Set OPENAI_API_KEY in Colab Secrets (🔑 icon)
3. Runtime → Run all

# Local Jupyter
jupyter notebook fashion_store_email_processor.ipynb
```

### 🚀 FastAPI Production (Scalable API)
```bash
# Best for: Production deployment, real-time processing

# Start server
python -m src.main
# Access: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Essential Commands

### 📓 Jupyter Notebook Quick Start
```bash
# Install notebook dependencies (if running locally)
pip install pandas numpy openai langchain langchain-openai chromadb

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Launch Jupyter
jupyter notebook

# Expected output: Excel file with processed results
```

### 🚀 FastAPI Server
```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Start the FastAPI server
python -m src.main

# Server will be available at: http://localhost:8000
# API documentation: http://localhost:8000/docs
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_email_processor.py

# Run tests with verbose output
pytest -v
```

### Development Tools
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run pre-assessment check
python pre_assessment_check.py

# Test OpenAI API key
python test_openai_key.py
```

## Project Structure Overview

```
/
├── src/                    # Main application code
│   ├── api/               # FastAPI routes and endpoints
│   ├── core/              # Business logic (EmailProcessor)
│   ├── ai/                # AI components (LLM, embeddings, search)
│   ├── data/              # Data models and database
│   ├── config/            # Configuration and settings
│   └── utils/             # Utilities (logging, etc.)
├── tests/                 # Test files
├── docs/                  # Documentation
├── examples/              # Example usage scripts
├── scripts/               # Utility scripts
└── .env                   # Environment variables
```

## Key API Endpoints

### Email Processing
- `POST /api/v1/emails/process` - Process a single email
- `POST /api/v1/emails/batch` - Process multiple emails
- `GET /api/v1/emails/{email_id}` - Get processed email details

### Search
- `POST /api/v1/search/semantic` - Semantic search through emails
- `POST /api/v1/search/query` - Query processed emails

### Health
- `GET /health` - Health check
- `GET /health/detailed` - Detailed health information

## Environment Variables

Key variables in `.env`:
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - Model to use (default: gpt-3.5-turbo)
- `DATABASE_URL` - Database connection string
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)
- `SUPPORTED_LANGUAGES` - Comma-separated language codes

## Sample Usage

### Process an Email
```python
import httpx

# Start the server first: python -m src.main

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/emails/process",
        json={
            "subject": "Customer Complaint",
            "content": "I'm not happy with my recent order...",
            "sender": "customer@example.com",
            "language": "en"
        }
    )
    result = response.json()
    print(f"Sentiment: {result['sentiment']}")
    print(f"Category: {result['category']}")
    print(f"Response: {result['response']}")
```

## Troubleshooting

### Common Issues
1. **API Key Issues**: Run `python test_openai_key.py` to validate
2. **Import Errors**: Ensure virtual environment is activated
3. **Database Issues**: Check `DATABASE_URL` in `.env`
4. **Port Conflicts**: Change `PORT` in `.env` if 8000 is taken

### Logs
- Application logs are in `logs/` directory
- Set `LOG_LEVEL=DEBUG` for detailed logging

### Getting Help
- Check the API documentation at `/docs` when server is running
- Review test files in `tests/` for usage examples
- Run `python pre_assessment_check.py` to validate setup

## Assessment Tips

1. **Read the requirements carefully** - Focus on what's being asked
2. **Use the existing structure** - Build upon the provided framework
3. **Test your changes** - Run tests frequently with `pytest`
4. **Check logs** - Use the logging system for debugging
5. **API-first approach** - Test endpoints with `/docs` interface
6. **Document your work** - Update README.md with your changes

Good luck with your assessment! 🍀
