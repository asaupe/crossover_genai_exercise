"""
Tests for email processing functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.core.email_processor import EmailProcessor
from src.data.models import EmailRequest, EmailCategory, EmailPriority, EmailSentiment


class TestEmailProcessor:
    """Test cases for EmailProcessor class."""
    
    @pytest.fixture
    def email_processor(self):
        """Create EmailProcessor instance for testing."""
        with patch('src.core.email_processor.LLMClient'), \
             patch('src.core.email_processor.TextAnalyzer'), \
             patch('src.core.email_processor.EmailDatabase'):
            return EmailProcessor()
    
    @pytest.mark.asyncio
    async def test_classify_email_support(self, email_processor, sample_email_request):
        """Test email classification for support category."""
        # Mock the dependencies
        email_processor.llm_client.classify_email = AsyncMock(return_value={
            "category": EmailCategory.SUPPORT,
            "confidence": 0.9
        })
        
        email_processor.text_analyzer.analyze_sentiment = AsyncMock(
            return_value=EmailSentiment.NEUTRAL
        )
        
        email_processor.text_analyzer.extract_keywords = AsyncMock(
            return_value=["help", "support", "question"]
        )
        
        email_processor.text_analyzer.extract_entities = AsyncMock(
            return_value=[]
        )
        
        # Test classification
        classification = await email_processor.classify_email(sample_email_request)
        
        assert classification.category == EmailCategory.SUPPORT
        assert classification.confidence == 0.9
        assert classification.sentiment == EmailSentiment.NEUTRAL
        assert "help" in classification.keywords
    
    @pytest.mark.asyncio
    async def test_classify_email_urgent_priority(self, email_processor):
        """Test urgent priority detection."""
        urgent_email = EmailRequest(
            subject="URGENT: System is down!",
            body="Our production system is completely broken and not working. Please help immediately!",
            sender="admin@company.com"
        )
        
        # Mock the dependencies
        email_processor.llm_client.classify_email = AsyncMock(return_value={
            "category": EmailCategory.TECHNICAL,
            "confidence": 0.95
        })
        
        email_processor.text_analyzer.analyze_sentiment = AsyncMock(
            return_value=EmailSentiment.NEGATIVE
        )
        
        email_processor.text_analyzer.extract_keywords = AsyncMock(
            return_value=["urgent", "system", "broken", "immediately"]
        )
        
        email_processor.text_analyzer.extract_entities = AsyncMock(
            return_value=[]
        )
        
        classification = await email_processor.classify_email(urgent_email)
        
        assert classification.priority == EmailPriority.URGENT
        assert classification.category == EmailCategory.TECHNICAL
    
    @pytest.mark.asyncio
    async def test_determine_priority_complaint(self, email_processor):
        """Test priority determination for complaints."""
        complaint_email = EmailRequest(
            subject="Terrible service",
            body="I am very disappointed with your service. This is unacceptable!",
            sender="angry@customer.com"
        )
        
        ai_classification = {"category": EmailCategory.COMPLAINT}
        priority = email_processor._determine_priority(complaint_email, ai_classification)
        
        assert priority == EmailPriority.HIGH
    
    def test_determine_priority_urgent_keywords(self, email_processor):
        """Test priority determination with urgent keywords."""
        urgent_email = EmailRequest(
            subject="Critical issue",
            body="We have a critical system failure that needs immediate attention.",
            sender="user@company.com"
        )
        
        ai_classification = {"category": EmailCategory.TECHNICAL}
        priority = email_processor._determine_priority(urgent_email, ai_classification)
        
        assert priority == EmailPriority.URGENT
    
    @pytest.mark.asyncio
    async def test_store_email(self, email_processor, sample_email_request, sample_email_classification):
        """Test email storage functionality."""
        from src.data.models import EmailResponse, EmailProcessingResult
        
        # Create sample response and result
        response = EmailResponse(
            content="Thank you for contacting us. We'll look into your order issue.",
            tone="professional",
            suggested_actions=["Check order status", "Contact shipping"],
            confidence=0.8
        )
        
        result = EmailProcessingResult(
            email_id="test-123",
            classification=sample_email_classification,
            response=response,
            processing_time=1.5
        )
        
        # Mock database store method
        email_processor.database.store_email = AsyncMock()
        
        await email_processor.store_email("test-123", sample_email_request, result)
        
        # Verify store_email was called
        email_processor.database.store_email.assert_called_once_with(
            "test-123", sample_email_request, result
        )
    
    @pytest.mark.asyncio
    async def test_get_email_context(self, email_processor, sample_email_request):
        """Test email context retrieval."""
        # Mock database methods
        email_processor.database.get_emails_by_sender = AsyncMock(
            return_value=[{"id": "prev-1", "subject": "Previous order"}]
        )
        
        email_processor.database.search_knowledge_base = AsyncMock(
            return_value=[{"title": "Order Issues", "content": "How to handle orders"}]
        )
        
        context = await email_processor.get_email_context(sample_email_request)
        
        assert "previous_emails" in context
        assert "knowledge_base" in context
        assert "sender_history" in context
        assert context["sender_history"] == 1
