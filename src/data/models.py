"""
Data models for the GenAI Email Processing System.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class EmailCategory(str, Enum):
    """Email categories for classification."""
    SUPPORT = "support"
    COMPLAINT = "complaint"
    INQUIRY = "inquiry"
    ORDER = "order"
    BILLING = "billing"
    TECHNICAL = "technical"
    GENERAL = "general"


class EmailPriority(str, Enum):
    """Email priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EmailSentiment(str, Enum):
    """Email sentiment analysis results."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class EmailRequest(BaseModel):
    """Request model for processing emails."""
    subject: str = Field(..., description="Email subject line", max_length=200)
    body: str = Field(..., description="Email body content", max_length=10000)
    sender: EmailStr = Field(..., description="Sender email address")
    attachments: Optional[List[str]] = Field(default=[], description="List of attachment filenames")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class EmailClassification(BaseModel):
    """Email classification results."""
    category: EmailCategory = Field(..., description="Primary email category")
    subcategory: Optional[str] = Field(None, description="More specific subcategory")
    priority: EmailPriority = Field(..., description="Email priority level")
    sentiment: EmailSentiment = Field(..., description="Email sentiment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence score")
    keywords: List[str] = Field(default=[], description="Extracted keywords")
    entities: List[Dict[str, str]] = Field(default=[], description="Named entities found")


class EmailResponse(BaseModel):
    """Generated email response."""
    content: str = Field(..., description="Response content", max_length=2000)
    tone: str = Field(..., description="Response tone (professional, friendly, etc.)")
    suggested_actions: List[str] = Field(default=[], description="Suggested follow-up actions")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Response quality confidence")


class EmailProcessingResult(BaseModel):
    """Complete email processing result."""
    email_id: str = Field(..., description="Unique email identifier")
    classification: EmailClassification = Field(..., description="Email classification results")
    response: EmailResponse = Field(..., description="Generated response")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Processing timestamp")


class SearchQuery(BaseModel):
    """Search query model."""
    query: str = Field(..., description="Search query text", min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    category_filter: Optional[EmailCategory] = Field(None, description="Filter by email category")
    date_from: Optional[datetime] = Field(None, description="Filter emails from this date")
    date_to: Optional[datetime] = Field(None, description="Filter emails until this date")


class SearchResult(BaseModel):
    """Search result item."""
    email_id: str = Field(..., description="Email identifier")
    subject: str = Field(..., description="Email subject")
    snippet: str = Field(..., description="Relevant text snippet")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    category: EmailCategory = Field(..., description="Email category")
    timestamp: datetime = Field(..., description="Email timestamp")


class SearchResponse(BaseModel):
    """Search response with results."""
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total number of matching emails")
    search_time: float = Field(..., description="Search execution time in seconds")


class HealthCheck(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Service version")
    dependencies: Dict[str, str] = Field(default={}, description="Dependency status")
