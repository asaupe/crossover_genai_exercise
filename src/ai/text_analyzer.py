"""
Text analysis utilities for email processing.
"""

import re
from typing import List, Dict
from loguru import logger

from src.config.settings import settings
from src.data.models import EmailSentiment


class TextAnalyzer:
    """Text analysis utilities for email content."""
    
    def __init__(self):
        self.logger = logger.bind(name="TextAnalyzer")
        
        # Common keywords for different categories
        self.category_keywords = {
            "support": ["help", "support", "assistance", "question", "how to"],
            "complaint": ["complaint", "unhappy", "disappointed", "terrible", "awful", "bad"],
            "technical": ["error", "bug", "broken", "not working", "technical", "system"],
            "billing": ["bill", "charge", "payment", "invoice", "refund", "money"],
            "order": ["order", "purchase", "delivery", "shipping", "product"]
        }
        
        # Sentiment keywords
        self.positive_keywords = [
            "thank", "great", "excellent", "wonderful", "amazing", "love",
            "perfect", "satisfied", "happy", "pleased"
        ]
        
        self.negative_keywords = [
            "terrible", "awful", "bad", "horrible", "disappointed", "angry",
            "frustrated", "upset", "unhappy", "hate", "worst"
        ]
    
    async def analyze_sentiment(self, text: str) -> EmailSentiment:
        """
        Analyze sentiment using keyword-based approach.
        """
        try:
            text_lower = text.lower()
            
            positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
            negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
            
            if positive_count > negative_count:
                return EmailSentiment.POSITIVE
            elif negative_count > positive_count:
                return EmailSentiment.NEGATIVE
            else:
                return EmailSentiment.NEUTRAL
                
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return EmailSentiment.NEUTRAL
    
    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """
        Extract important keywords from text.
        """
        try:
            # Simple keyword extraction using frequency
            text_lower = text.lower()
            
            # Remove common stop words
            stop_words = {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                "of", "with", "by", "from", "up", "about", "into", "through", "during",
                "before", "after", "above", "below", "between", "among", "is", "are",
                "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
                "did", "will", "would", "could", "should", "may", "might", "can", "am"
            }
            
            # Extract words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)
            
            # Filter out stop words and count frequency
            word_freq = {}
            for word in words:
                if word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and return top keywords
            keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            return [word for word, _ in keywords[:max_keywords]]
            
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    async def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extract named entities from text (simplified approach).
        """
        try:
            entities = []
            
            # Email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            for email in emails:
                entities.append({"type": "email", "value": email})
            
            # Phone numbers (simple pattern)
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones = re.findall(phone_pattern, text)
            for phone in phones:
                entities.append({"type": "phone", "value": phone})
            
            # Order numbers (assuming format like #12345 or ORDER-12345)
            order_pattern = r'(?:order|#)\s*[-:]?\s*([a-zA-Z0-9]+)'
            orders = re.findall(order_pattern, text, re.IGNORECASE)
            for order in orders:
                entities.append({"type": "order_id", "value": order})
            
            # Money amounts
            money_pattern = r'\$\d+(?:\.\d{2})?'
            amounts = re.findall(money_pattern, text)
            for amount in amounts:
                entities.append({"type": "money", "value": amount})
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    def calculate_urgency_score(self, text: str) -> float:
        """
        Calculate urgency score based on text content.
        """
        try:
            urgent_indicators = [
                "urgent", "emergency", "critical", "asap", "immediately",
                "broken", "down", "not working", "crashed", "failed"
            ]
            
            text_lower = text.lower()
            urgency_count = sum(1 for indicator in urgent_indicators if indicator in text_lower)
            
            # Normalize score (0.0 to 1.0)
            max_score = len(urgent_indicators)
            return min(urgency_count / max_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating urgency score: {str(e)}")
            return 0.0
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection (placeholder for more sophisticated detection).
        """
        # This is a very basic implementation
        # In production, use a proper language detection library
        
        if not text:
            return "en"
        
        # Simple heuristics based on common words
        spanish_words = ["el", "la", "es", "en", "de", "que", "por", "con"]
        french_words = ["le", "la", "est", "en", "de", "que", "pour", "avec"]
        german_words = ["der", "die", "ist", "in", "von", "dass", "für", "mit"]
        
        text_lower = text.lower()
        
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        french_count = sum(1 for word in french_words if word in text_lower)
        german_count = sum(1 for word in german_words if word in text_lower)
        
        if spanish_count > 2:
            return "es"
        elif french_count > 2:
            return "fr"
        elif german_count > 2:
            return "de"
        else:
            return "en"
