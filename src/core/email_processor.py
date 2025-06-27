"""
Email processing core logic.
"""

from typing import Dict, Any
from loguru import logger

from src.data.models import (
    EmailRequest, 
    EmailClassification, 
    EmailCategory, 
    EmailPriority, 
    EmailSentiment,
    EmailProcessingResult
)
from src.ai.llm_client import LLMClient
from src.ai.text_analyzer import TextAnalyzer
from src.data.database import EmailDatabase


class EmailProcessor:
    """Core email processing logic."""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.text_analyzer = TextAnalyzer()
        self.database = EmailDatabase()
        self.logger = logger.bind(name="EmailProcessor")
    
    async def classify_email(self, email: EmailRequest) -> EmailClassification:
        """
        Classify an email using AI and rule-based approaches.
        """
        try:
            self.logger.info(f"Classifying email from {email.sender}")
            
            # Combine subject and body for analysis
            content = f"Subject: {email.subject}\n\nBody: {email.body}"
            
            # Get AI-based classification
            ai_classification = await self.llm_client.classify_email(content)
            
            # Perform sentiment analysis
            sentiment = await self.text_analyzer.analyze_sentiment(content)
            
            # Extract keywords and entities
            keywords = await self.text_analyzer.extract_keywords(content)
            entities = await self.text_analyzer.extract_entities(content)
            
            # Determine priority based on content and rules
            priority = self._determine_priority(email, ai_classification)
            
            classification = EmailClassification(
                category=ai_classification["category"],
                subcategory=ai_classification.get("subcategory"),
                priority=priority,
                sentiment=sentiment,
                confidence=ai_classification["confidence"],
                keywords=keywords,
                entities=entities
            )
            
            self.logger.info(f"Email classified: {classification.category}, priority: {classification.priority}")
            
            return classification
            
        except Exception as e:
            self.logger.error(f"Error classifying email: {str(e)}")
            raise
    
    async def store_email(
        self, 
        email_id: str, 
        email: EmailRequest, 
        result: EmailProcessingResult
    ) -> None:
        """
        Store processed email in database and vector store.
        """
        try:
            await self.database.store_email(email_id, email, result)
            self.logger.info(f"Stored email {email_id} in database")
            
        except Exception as e:
            self.logger.error(f"Error storing email {email_id}: {str(e)}")
            raise
    
    def _determine_priority(
        self, 
        email: EmailRequest, 
        ai_classification: Dict[str, Any]
    ) -> EmailPriority:
        """
        Determine email priority based on content and rules.
        """
        content_lower = f"{email.subject} {email.body}".lower()
        
        # High priority indicators
        urgent_keywords = [
            "urgent", "emergency", "critical", "asap", "immediately",
            "broken", "down", "not working", "error", "failed"
        ]
        
        # Check for urgent keywords
        if any(keyword in content_lower for keyword in urgent_keywords):
            return EmailPriority.URGENT
        
        # Category-based priority
        category = ai_classification.get("category")
        if category == EmailCategory.COMPLAINT:
            return EmailPriority.HIGH
        elif category in [EmailCategory.TECHNICAL, EmailCategory.BILLING]:
            return EmailPriority.MEDIUM
        
        # Default priority
        return EmailPriority.LOW
    
    async def get_email_context(self, email: EmailRequest) -> Dict[str, Any]:
        """
        Get relevant context for email processing (previous conversations, etc.).
        """
        try:
            # Search for previous emails from the same sender
            previous_emails = await self.database.get_emails_by_sender(
                email.sender, 
                limit=5
            )
            
            # Get relevant knowledge base articles
            kb_articles = await self.database.search_knowledge_base(
                f"{email.subject} {email.body}",
                limit=3
            )
            
            return {
                "previous_emails": previous_emails,
                "knowledge_base": kb_articles,
                "sender_history": len(previous_emails)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting email context: {str(e)}")
            return {}
