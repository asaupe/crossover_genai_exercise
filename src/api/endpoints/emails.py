"""
Email processing endpoints.
"""

import time
import uuid
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from src.data.models import (
    EmailRequest, 
    EmailProcessingResult, 
    EmailResponse,
    EmailClassification
)
from src.core.email_processor import EmailProcessor
from src.ai.llm_client import LLMClient

router = APIRouter()


def get_email_processor() -> EmailProcessor:
    """Dependency to get email processor instance."""
    return EmailProcessor()


def get_llm_client() -> LLMClient:
    """Dependency to get LLM client instance."""
    return LLMClient()


@router.post("/process", response_model=EmailProcessingResult)
async def process_email(
    email: EmailRequest,
    processor: EmailProcessor = Depends(get_email_processor),
    llm_client: LLMClient = Depends(get_llm_client)
):
    """
    Process an incoming email: classify, analyze, and generate response.
    """
    start_time = time.time()
    email_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Processing email {email_id} from {email.sender}")
        
        # Classify the email
        classification = await processor.classify_email(email)
        logger.info(f"Email {email_id} classified as {classification.category}")
        
        # Generate response
        response = await llm_client.generate_response(email, classification)
        logger.info(f"Generated response for email {email_id}")
        
        processing_time = time.time() - start_time
        
        result = EmailProcessingResult(
            email_id=email_id,
            classification=classification,
            response=response,
            processing_time=processing_time
        )
        
        # Store the processed email (implement storage logic)
        await processor.store_email(email_id, email, result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing email {email_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing email: {str(e)}")


@router.post("/respond", response_model=EmailResponse)
async def generate_response(
    email: EmailRequest,
    classification: EmailClassification,
    llm_client: LLMClient = Depends(get_llm_client)
):
    """
    Generate a response for an email with provided classification.
    """
    try:
        logger.info(f"Generating response for email from {email.sender}")
        
        response = await llm_client.generate_response(email, classification)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@router.post("/classify", response_model=EmailClassification)
async def classify_email(
    email: EmailRequest,
    processor: EmailProcessor = Depends(get_email_processor)
):
    """
    Classify an email without generating a response.
    """
    try:
        logger.info(f"Classifying email from {email.sender}")
        
        classification = await processor.classify_email(email)
        
        return classification
        
    except Exception as e:
        logger.error(f"Error classifying email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error classifying email: {str(e)}")
