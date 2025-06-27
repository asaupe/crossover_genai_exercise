# Test configuration for pytest
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import os
import tempfile
from pathlib import Path

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["CHROMA_PERSIST_DIRECTORY"] = tempfile.mkdtemp()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    
    # Mock completion response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"category": "support", "confidence": 0.9}'
    
    mock_client.chat.completions.create.return_value = mock_response
    
    # Mock embedding response
    mock_embedding_response = Mock()
    mock_embedding_response.data = [Mock()]
    mock_embedding_response.data[0].embedding = [0.1] * 1536  # Typical embedding size
    
    mock_client.embeddings.create.return_value = mock_embedding_response
    
    return mock_client


@pytest.fixture
def sample_email_request():
    """Sample email request for testing."""
    from src.data.models import EmailRequest
    
    return EmailRequest(
        subject="Issue with my order",
        body="I received the wrong item in my order #12345. Please help me resolve this issue.",
        sender="customer@example.com",
        attachments=[],
        metadata={}
    )


@pytest.fixture
def sample_email_classification():
    """Sample email classification for testing."""
    from src.data.models import EmailClassification, EmailCategory, EmailPriority, EmailSentiment
    
    return EmailClassification(
        category=EmailCategory.ORDER,
        subcategory="wrong_item",
        priority=EmailPriority.MEDIUM,
        sentiment=EmailSentiment.NEGATIVE,
        confidence=0.9,
        keywords=["order", "wrong", "item", "help"],
        entities=[{"type": "order_id", "value": "12345"}]
    )
