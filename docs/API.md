# GenAI Email Processing System - API Documentation

## Overview

This API provides AI-driven email processing capabilities including classification, sentiment analysis, automated response generation, and semantic search.

## Base URL
```
http://localhost:8000
```

## Authentication

Currently, no authentication is required for this proof-of-concept. In production, implement proper API key authentication.

## Endpoints

### Health Check

#### GET /health
Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "service": "GenAI Email Processor",
  "timestamp": "2025-06-27T10:00:00Z",
  "version": "1.0.0",
  "dependencies": {
    "database": "healthy",
    "ai_service": "healthy",
    "vector_db": "healthy"
  }
}
```

### Email Processing

#### POST /api/v1/emails/process
Process an email completely: classify, analyze, and generate response.

**Request Body:**
```json
{
  "subject": "Issue with my order",
  "body": "I received the wrong item in my order #12345. Please help me resolve this issue.",
  "sender": "customer@example.com",
  "attachments": ["receipt.pdf"],
  "metadata": {
    "source": "web_form",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Response:**
```json
{
  "email_id": "uuid-1234",
  "classification": {
    "category": "order",
    "subcategory": "wrong_item",
    "priority": "medium",
    "sentiment": "negative",
    "confidence": 0.9,
    "keywords": ["order", "wrong", "item", "help"],
    "entities": [
      {
        "type": "order_id",
        "value": "12345"
      }
    ]
  },
  "response": {
    "content": "Thank you for contacting us about your order. We sincerely apologize for the mix-up...",
    "tone": "empathetic",
    "suggested_actions": [
      "Process replacement order",
      "Arrange return pickup"
    ],
    "confidence": 0.85
  },
  "processing_time": 2.3,
  "timestamp": "2025-06-27T10:00:00Z"
}
```

#### POST /api/v1/emails/classify
Classify an email without generating a response.

**Request Body:**
```json
{
  "subject": "Can't access my account",
  "body": "I'm having trouble logging into my account.",
  "sender": "user@example.com"
}
```

**Response:**
```json
{
  "category": "support",
  "subcategory": "account_access",
  "priority": "medium",
  "sentiment": "neutral",
  "confidence": 0.92,
  "keywords": ["access", "account", "trouble", "login"],
  "entities": []
}
```

#### POST /api/v1/emails/respond
Generate a response for an email with provided classification.

**Request Body:**
```json
{
  "email": {
    "subject": "Order issue",
    "body": "My order is wrong",
    "sender": "customer@example.com"
  },
  "classification": {
    "category": "order",
    "priority": "medium",
    "sentiment": "negative",
    "confidence": 0.8,
    "keywords": ["order", "wrong"],
    "entities": []
  }
}
```

**Response:**
```json
{
  "content": "We apologize for the inconvenience with your order...",
  "tone": "empathetic",
  "suggested_actions": [
    "Escalate to fulfillment team",
    "Process replacement"
  ],
  "confidence": 0.9
}
```

### Search

#### POST /api/v1/search/
Perform semantic search through email history.

**Request Body:**
```json
{
  "query": "order problems",
  "limit": 10,
  "category_filter": "order",
  "date_from": "2025-06-01T00:00:00Z",
  "date_to": "2025-06-27T23:59:59Z"
}
```

**Response:**
```json
{
  "query": "order problems",
  "results": [
    {
      "email_id": "uuid-5678",
      "subject": "Issue with order delivery",
      "snippet": "I have a problem with my recent order delivery...",
      "similarity_score": 0.95,
      "category": "order",
      "timestamp": "2025-06-25T14:30:00Z"
    }
  ],
  "total_count": 1,
  "search_time": 0.15
}
```

#### GET /api/v1/search/similar/{email_id}
Find emails similar to the specified email ID.

**Parameters:**
- `email_id`: The ID of the reference email
- `limit`: Maximum number of similar emails to return (default: 5)

**Response:**
```json
{
  "email_id": "uuid-1234",
  "similar_emails": [
    {
      "email_id": "uuid-5678",
      "subject": "Similar order issue",
      "snippet": "Another customer with order problem...",
      "similarity_score": 0.85,
      "category": "order",
      "timestamp": "2025-06-20T09:15:00Z"
    }
  ],
  "count": 1
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400`: Bad Request - Invalid input data
- `422`: Validation Error - Request body doesn't match expected schema
- `500`: Internal Server Error - Processing failed

## Rate Limiting

Current implementation doesn't include rate limiting. For production deployment, implement appropriate rate limiting based on your requirements.

## Data Models

### Email Categories
- `support`: General customer support inquiries
- `complaint`: Customer complaints and negative feedback
- `inquiry`: Information requests and questions
- `order`: Order-related issues and inquiries
- `billing`: Billing and payment related issues
- `technical`: Technical problems and support
- `general`: General communications

### Priority Levels
- `low`: Standard priority
- `medium`: Moderate priority requiring attention
- `high`: High priority needing prompt response
- `urgent`: Critical issues requiring immediate attention

### Sentiment Types
- `positive`: Positive sentiment detected
- `neutral`: Neutral or mixed sentiment
- `negative`: Negative sentiment detected

## Examples

### cURL Examples

**Process an email:**
```bash
curl -X POST "http://localhost:8000/api/v1/emails/process" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Need help with my account",
    "body": "I cannot access my account. Please help.",
    "sender": "user@example.com"
  }'
```

**Search emails:**
```bash
curl -X POST "http://localhost:8000/api/v1/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "account access",
    "limit": 5
  }'
```

### Python Example

```python
import requests

# Process an email
response = requests.post(
    "http://localhost:8000/api/v1/emails/process",
    json={
        "subject": "Order problem",
        "body": "I have an issue with my order #12345",
        "sender": "customer@email.com"
    }
)

result = response.json()
print(f"Category: {result['classification']['category']}")
print(f"Response: {result['response']['content']}")
```

## Monitoring and Observability

The API provides structured logging and health check endpoints for monitoring:

- Use `/health` for basic health checks
- Use `/api/v1/health/detailed` for comprehensive health information
- Logs are available in JSON format for easy parsing
- Metrics can be extracted from logs for performance monitoring
