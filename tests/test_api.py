"""
Tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.main import create_app
from src.data.models import EmailRequest, EmailCategory, EmailPriority, EmailSentiment


class TestEmailEndpoints:
    """Test cases for email API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    @pytest.fixture
    def mock_email_processor(self):
        """Mock EmailProcessor for testing."""
        with patch('src.api.endpoints.emails.EmailProcessor') as mock:
            processor = mock.return_value
            processor.classify_email = AsyncMock()
            processor.store_email = AsyncMock()
            yield processor
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLMClient for testing."""
        with patch('src.api.endpoints.emails.LLMClient') as mock:
            client = mock.return_value
            client.generate_response = AsyncMock()
            yield client
    
    def test_process_email_endpoint(self, client, mock_email_processor, mock_llm_client):
        """Test email processing endpoint."""
        from src.data.models import EmailClassification, EmailResponse
        
        # Setup mocks
        mock_email_processor.classify_email.return_value = EmailClassification(
            category=EmailCategory.SUPPORT,
            priority=EmailPriority.MEDIUM,
            sentiment=EmailSentiment.NEUTRAL,
            confidence=0.9,
            keywords=["help", "support"],
            entities=[]
        )
        
        mock_llm_client.generate_response.return_value = EmailResponse(
            content="Thank you for your message. We'll help you with your request.",
            tone="professional",
            suggested_actions=["Follow up in 24 hours"],
            confidence=0.8
        )
        
        # Test request
        email_data = {
            "subject": "Need help with account",
            "body": "I'm having trouble accessing my account. Can you help?",
            "sender": "user@example.com",
            "attachments": [],
            "metadata": {}
        }
        
        response = client.post("/api/v1/emails/process", json=email_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "email_id" in data
        assert data["classification"]["category"] == "support"
        assert data["response"]["content"] is not None
        assert data["processing_time"] > 0
    
    def test_classify_email_endpoint(self, client, mock_email_processor):
        """Test email classification endpoint."""
        from src.data.models import EmailClassification
        
        # Setup mock
        mock_email_processor.classify_email.return_value = EmailClassification(
            category=EmailCategory.COMPLAINT,
            priority=EmailPriority.HIGH,
            sentiment=EmailSentiment.NEGATIVE,
            confidence=0.95,
            keywords=["terrible", "disappointed"],
            entities=[]
        )
        
        email_data = {
            "subject": "Terrible service",
            "body": "I am very disappointed with your service quality.",
            "sender": "complaint@example.com"
        }
        
        response = client.post("/api/v1/emails/classify", json=email_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["category"] == "complaint"
        assert data["priority"] == "high"
        assert data["sentiment"] == "negative"
        assert data["confidence"] == 0.95
    
    def test_generate_response_endpoint(self, client, mock_llm_client):
        """Test response generation endpoint."""
        from src.data.models import EmailResponse
        
        # Setup mock
        mock_llm_client.generate_response.return_value = EmailResponse(
            content="We apologize for the inconvenience. We'll resolve this issue promptly.",
            tone="empathetic",
            suggested_actions=["Escalate to manager", "Follow up in 2 hours"],
            confidence=0.9
        )
        
        request_data = {
            "email": {
                "subject": "Order issue",
                "body": "My order is wrong",
                "sender": "customer@example.com"
            },
            "classification": {
                "category": "order",
                "subcategory": "wrong_item",
                "priority": "medium",
                "sentiment": "negative",
                "confidence": 0.8,
                "keywords": ["order", "wrong"],
                "entities": []
            }
        }
        
        response = client.post("/api/v1/emails/respond", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["content"] is not None
        assert data["tone"] == "empathetic"
        assert len(data["suggested_actions"]) > 0
    
    def test_invalid_email_request(self, client):
        """Test invalid email request handling."""
        invalid_data = {
            "subject": "",  # Empty subject
            "body": "Test body",
            # Missing sender
        }
        
        response = client.post("/api/v1/emails/process", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestSearchEndpoints:
    """Test cases for search API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    @pytest.fixture
    def mock_search_engine(self):
        """Mock SemanticSearchEngine for testing."""
        with patch('src.api.endpoints.search.SemanticSearchEngine') as mock:
            engine = mock.return_value
            engine.search = AsyncMock()
            engine.find_similar = AsyncMock()
            yield engine
    
    def test_search_emails_endpoint(self, client, mock_search_engine):
        """Test email search endpoint."""
        from src.data.models import SearchResult
        from datetime import datetime
        
        # Setup mock
        mock_results = {
            "results": [
                SearchResult(
                    email_id="email-1",
                    subject="Order issue",
                    snippet="Customer has problem with order...",
                    similarity_score=0.9,
                    category=EmailCategory.ORDER,
                    timestamp=datetime.now()
                )
            ],
            "total_count": 1
        }
        
        mock_search_engine.search.return_value = type('MockResult', (), mock_results)()
        
        search_data = {
            "query": "order problem",
            "limit": 10
        }
        
        response = client.post("/api/v1/search/", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["query"] == "order problem"
        assert len(data["results"]) == 1
        assert data["results"][0]["similarity_score"] == 0.9
        assert data["total_count"] == 1
    
    def test_find_similar_emails_endpoint(self, client, mock_search_engine):
        """Test find similar emails endpoint."""
        from src.data.models import SearchResult
        from datetime import datetime
        
        # Setup mock
        similar_emails = [
            SearchResult(
                email_id="similar-1",
                subject="Similar order issue",
                snippet="Another customer with order problem...",
                similarity_score=0.85,
                category=EmailCategory.ORDER,
                timestamp=datetime.now()
            )
        ]
        
        mock_search_engine.find_similar.return_value = similar_emails
        
        response = client.get("/api/v1/search/similar/email-123?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email_id"] == "email-123"
        assert len(data["similar_emails"]) == 1
        assert data["count"] == 1


class TestHealthEndpoints:
    """Test cases for health check endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        app = create_app()
        return TestClient(app)
    
    def test_health_check_endpoint(self, client):
        """Test basic health check endpoint."""
        response = client.get("/api/v1/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] is not None
        assert data["version"] is not None
        assert "dependencies" in data
    
    def test_detailed_health_check_endpoint(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/api/v1/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "timestamp" in data
        assert "service" in data
        assert "version" in data
        assert "components" in data
        assert "environment" in data
