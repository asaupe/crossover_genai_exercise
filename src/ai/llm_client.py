"""
LLM client for OpenAI integration.
"""

from typing import Dict, Any, List
import openai
from loguru import logger

from src.config.settings import settings
from src.data.models import (
    EmailRequest, 
    EmailClassification, 
    EmailResponse, 
    EmailCategory, 
    EmailSentiment
)


class LLMClient:
    """OpenAI LLM client for email processing."""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.logger = logger.bind(name="LLMClient")
    
    async def classify_email(self, content: str) -> Dict[str, Any]:
        """
        Classify email using OpenAI API.
        """
        try:
            classification_prompt = self._build_classification_prompt(content)
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert email classifier. Analyze the email and provide accurate classification."
                    },
                    {
                        "role": "user",
                        "content": classification_prompt
                    }
                ],
                temperature=settings.TEMPERATURE,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            import json
            classification = json.loads(result)
            
            self.logger.info(f"Email classified as: {classification.get('category')}")
            
            return classification
            
        except Exception as e:
            self.logger.error(f"Error classifying email: {str(e)}")
            raise
    
    async def generate_response(
        self, 
        email: EmailRequest, 
        classification: EmailClassification
    ) -> EmailResponse:
        """
        Generate email response using OpenAI API.
        """
        try:
            response_prompt = self._build_response_prompt(email, classification)
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional customer service assistant. Generate helpful, empathetic, and actionable email responses."
                    },
                    {
                        "role": "user",
                        "content": response_prompt
                    }
                ],
                temperature=settings.TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            import json
            response_data = json.loads(result)
            
            email_response = EmailResponse(
                content=response_data["content"],
                tone=response_data["tone"],
                suggested_actions=response_data.get("suggested_actions", []),
                confidence=response_data.get("confidence", 0.8)
            )
            
            self.logger.info(f"Generated response for {classification.category} email")
            
            return email_response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _build_classification_prompt(self, content: str) -> str:
        """
        Build prompt for email classification.
        """
        categories = [cat.value for cat in EmailCategory]
        sentiments = [sent.value for sent in EmailSentiment]
        
        prompt = f"""
        Please analyze the following email and provide a classification in JSON format.

        Email Content:
        {content}

        Please provide the classification with the following structure:
        {{
            "category": "one of {categories}",
            "subcategory": "specific subcategory if applicable",
            "sentiment": "one of {sentiments}",
            "confidence": "confidence score between 0.0 and 1.0",
            "reasoning": "brief explanation of the classification"
        }}

        Consider the content, tone, and intent of the email when classifying.
        """
        
        return prompt
    
    def _build_response_prompt(
        self, 
        email: EmailRequest, 
        classification: EmailClassification
    ) -> str:
        """
        Build prompt for response generation.
        """
        prompt = f"""
        Generate a professional email response based on the following information:

        Original Email:
        Subject: {email.subject}
        From: {email.sender}
        Content: {email.body}

        Classification:
        Category: {classification.category}
        Priority: {classification.priority}
        Sentiment: {classification.sentiment}
        Keywords: {", ".join(classification.keywords)}

        Please generate a response in JSON format:
        {{
            "content": "professional email response content",
            "tone": "tone of the response (professional, friendly, empathetic, etc.)",
            "suggested_actions": ["list", "of", "suggested", "follow-up", "actions"],
            "confidence": "confidence score between 0.0 and 1.0"
        }}

        Guidelines:
        - Be professional and courteous
        - Address the customer's concerns directly
        - Provide helpful information or next steps
        - Match the tone to the email category and sentiment
        - Keep response concise but complete
        - Include relevant contact information if needed
        """
        
        return prompt
    
    async def analyze_sentiment(self, text: str) -> EmailSentiment:
        """
        Analyze sentiment of text using OpenAI.
        """
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze the sentiment of this text and respond with only one word - either 'positive', 'neutral', or 'negative':\n\n{text}"
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            sentiment_str = response.choices[0].message.content.strip().lower()
            
            if sentiment_str in ["positive", "neutral", "negative"]:
                return EmailSentiment(sentiment_str)
            else:
                return EmailSentiment.NEUTRAL
                
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return EmailSentiment.NEUTRAL
