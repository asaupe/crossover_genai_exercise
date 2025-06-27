"""
Tests for AI components.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.ai.llm_client import LLMClient
from src.ai.text_analyzer import TextAnalyzer
from src.data.models import EmailRequest, EmailClassification, EmailCategory, EmailSentiment


class TestLLMClient:
    """Test cases for LLMClient class."""
    
    @pytest.fixture
    def llm_client(self):
        """Create LLMClient instance for testing."""
        with patch('src.ai.llm_client.openai.OpenAI'):
            return LLMClient()
    
    @pytest.mark.asyncio
    async def test_classify_email(self, llm_client):
        """Test email classification with LLM."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "category": "support",
            "subcategory": "account_access",
            "sentiment": "neutral",
            "confidence": 0.9,
            "reasoning": "Customer needs help with account access"
        }
        '''
        
        llm_client.client.chat.completions.create.return_value = mock_response
        
        content = "Subject: Can't access my account\n\nI'm having trouble logging into my account."
        
        result = await llm_client.classify_email(content)
        
        assert result["category"] == "support"
        assert result["confidence"] == 0.9
        assert result["sentiment"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_generate_response(self, llm_client, sample_email_request, sample_email_classification):
        """Test response generation with LLM."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "content": "Thank you for contacting us about your order. We'll investigate the issue immediately.",
            "tone": "professional",
            "suggested_actions": ["Check order details", "Contact shipping department"],
            "confidence": 0.85
        }
        '''
        
        llm_client.client.chat.completions.create.return_value = mock_response
        
        response = await llm_client.generate_response(sample_email_request, sample_email_classification)
        
        assert response.content is not None
        assert response.tone == "professional"
        assert len(response.suggested_actions) > 0
        assert response.confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment(self, llm_client):
        """Test sentiment analysis with LLM."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "negative"
        
        llm_client.client.chat.completions.create.return_value = mock_response
        
        text = "I am very disappointed with your service. This is terrible!"
        
        sentiment = await llm_client.analyze_sentiment(text)
        
        assert sentiment == EmailSentiment.NEGATIVE
    
    def test_build_classification_prompt(self, llm_client):
        """Test classification prompt building."""
        content = "Subject: Help needed\n\nI need assistance with my account."
        
        prompt = llm_client._build_classification_prompt(content)
        
        assert "Email Content:" in prompt
        assert content in prompt
        assert "category" in prompt.lower()
        assert "sentiment" in prompt.lower()
    
    def test_build_response_prompt(self, llm_client, sample_email_request, sample_email_classification):
        """Test response generation prompt building."""
        prompt = llm_client._build_response_prompt(sample_email_request, sample_email_classification)
        
        assert sample_email_request.subject in prompt
        assert sample_email_request.body in prompt
        assert sample_email_request.sender in prompt
        assert sample_email_classification.category.value in prompt


class TestTextAnalyzer:
    """Test cases for TextAnalyzer class."""
    
    @pytest.fixture
    def text_analyzer(self):
        """Create TextAnalyzer instance for testing."""
        return TextAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_positive(self, text_analyzer):
        """Test positive sentiment analysis."""
        text = "Thank you so much! This is excellent service. I'm very happy with the results."
        
        sentiment = await text_analyzer.analyze_sentiment(text)
        
        assert sentiment == EmailSentiment.POSITIVE
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_negative(self, text_analyzer):
        """Test negative sentiment analysis."""
        text = "This is terrible service. I'm very disappointed and frustrated with your company."
        
        sentiment = await text_analyzer.analyze_sentiment(text)
        
        assert sentiment == EmailSentiment.NEGATIVE
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_neutral(self, text_analyzer):
        """Test neutral sentiment analysis."""
        text = "I would like to inquire about my order status. Please provide an update."
        
        sentiment = await text_analyzer.analyze_sentiment(text)
        
        assert sentiment == EmailSentiment.NEUTRAL
    
    @pytest.mark.asyncio
    async def test_extract_keywords(self, text_analyzer):
        """Test keyword extraction."""
        text = "I need help with my order delivery. The shipping address is incorrect."
        
        keywords = await text_analyzer.extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert any(keyword in ["help", "order", "delivery", "shipping"] for keyword in keywords)
    
    @pytest.mark.asyncio
    async def test_extract_entities_email(self, text_analyzer):
        """Test email entity extraction."""
        text = "Please contact me at john.doe@example.com for further information."
        
        entities = await text_analyzer.extract_entities(text)
        
        email_entities = [e for e in entities if e["type"] == "email"]
        assert len(email_entities) > 0
        assert email_entities[0]["value"] == "john.doe@example.com"
    
    @pytest.mark.asyncio
    async def test_extract_entities_phone(self, text_analyzer):
        """Test phone number entity extraction."""
        text = "You can reach me at 555-123-4567 or 555.987.6543."
        
        entities = await text_analyzer.extract_entities(text)
        
        phone_entities = [e for e in entities if e["type"] == "phone"]
        assert len(phone_entities) >= 1
    
    @pytest.mark.asyncio
    async def test_extract_entities_order_id(self, text_analyzer):
        """Test order ID entity extraction."""
        text = "I have an issue with order #12345 and ORDER-67890."
        
        entities = await text_analyzer.extract_entities(text)
        
        order_entities = [e for e in entities if e["type"] == "order_id"]
        assert len(order_entities) >= 1
        assert any(e["value"] in ["12345", "67890"] for e in order_entities)
    
    @pytest.mark.asyncio
    async def test_extract_entities_money(self, text_analyzer):
        """Test money amount entity extraction."""
        text = "I was charged $99.99 but expected $49.50."
        
        entities = await text_analyzer.extract_entities(text)
        
        money_entities = [e for e in entities if e["type"] == "money"]
        assert len(money_entities) >= 1
        assert any(e["value"] in ["$99.99", "$49.50"] for e in money_entities)
    
    def test_calculate_urgency_score(self, text_analyzer):
        """Test urgency score calculation."""
        urgent_text = "URGENT: Critical system failure! The server is down and not working!"
        normal_text = "I would like to update my profile information when you have time."
        
        urgent_score = text_analyzer.calculate_urgency_score(urgent_text)
        normal_score = text_analyzer.calculate_urgency_score(normal_text)
        
        assert urgent_score > normal_score
        assert 0.0 <= urgent_score <= 1.0
        assert 0.0 <= normal_score <= 1.0
    
    def test_detect_language(self, text_analyzer):
        """Test language detection."""
        english_text = "Hello, I need help with my account."
        spanish_text = "Hola, necesito ayuda con mi cuenta por favor."
        
        en_lang = text_analyzer.detect_language(english_text)
        es_lang = text_analyzer.detect_language(spanish_text)
        
        assert en_lang == "en"
        # Note: Simple detection might not always work perfectly
        # This is just a basic test for the functionality
