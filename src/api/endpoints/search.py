"""
Search endpoints for semantic search functionality.
"""

import time
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger

from src.data.models import SearchQuery, SearchResponse
from src.ai.semantic_search import SemanticSearchEngine

router = APIRouter()


def get_search_engine() -> SemanticSearchEngine:
    """Dependency to get semantic search engine instance."""
    return SemanticSearchEngine()


@router.post("/", response_model=SearchResponse)
async def search_emails(
    query: SearchQuery,
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Perform semantic search through email history.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Performing search for query: '{query.query}'")
        
        results = await search_engine.search(query)
        search_time = time.time() - start_time
        
        response = SearchResponse(
            query=query.query,
            results=results.results,
            total_count=results.total_count,
            search_time=search_time
        )
        
        logger.info(f"Search completed in {search_time:.2f}s, found {len(results.results)} results")
        
        return response
        
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/similar/{email_id}")
async def find_similar_emails(
    email_id: str,
    limit: int = 5,
    search_engine: SemanticSearchEngine = Depends(get_search_engine)
):
    """
    Find emails similar to the specified email ID.
    """
    try:
        logger.info(f"Finding similar emails to {email_id}")
        
        similar_emails = await search_engine.find_similar(email_id, limit)
        
        return {
            "email_id": email_id,
            "similar_emails": similar_emails,
            "count": len(similar_emails)
        }
        
    except Exception as e:
        logger.error(f"Error finding similar emails: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error finding similar emails: {str(e)}")
