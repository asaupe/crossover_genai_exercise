"""
Semantic search engine using ChromaDB for vector similarity search.
"""

import asyncio
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from loguru import logger
import openai

from src.config.settings import settings
from src.data.models import SearchQuery, SearchResult, EmailCategory


class SemanticSearchEngine:
    """Vector-based semantic search for emails."""
    
    def __init__(self):
        self.logger = logger.bind(name="SemanticSearchEngine")
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="emails",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.logger.info("Semantic search engine initialized")
    
    async def add_email(
        self, 
        email_id: str, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> None:
        """
        Add an email to the vector database.
        """
        try:
            # Generate embedding
            embedding = await self._get_embedding(content)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
                ids=[email_id]
            )
            
            self.logger.info(f"Added email {email_id} to vector database")
            
        except Exception as e:
            self.logger.error(f"Error adding email to vector database: {str(e)}")
            raise
    
    async def search(self, query: SearchQuery) -> Dict[str, Any]:
        """
        Perform semantic search for emails.
        """
        try:
            self.logger.info(f"Searching for: '{query.query}'")
            
            # Generate query embedding
            query_embedding = await self._get_embedding(query.query)
            
            # Build where clause for filtering
            where_clause = {}
            if query.category_filter:
                where_clause["category"] = query.category_filter.value
            
            if query.date_from or query.date_to:
                # Add date filtering logic
                pass
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=query.limit,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert to SearchResult objects
            search_results = []
            if results["ids"][0]:
                for i, email_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    document = results["documents"][0][i]
                    distance = results["distances"][0][i]
                    
                    # Convert distance to similarity score (1 - distance for cosine)
                    similarity_score = max(0.0, 1.0 - distance)
                    
                    search_result = SearchResult(
                        email_id=email_id,
                        subject=metadata.get("subject", ""),
                        snippet=self._create_snippet(document, query.query),
                        similarity_score=similarity_score,
                        category=EmailCategory(metadata.get("category", "general")),
                        timestamp=metadata.get("timestamp", "")
                    )
                    search_results.append(search_result)
            
            # Get total count (simplified)
            total_count = len(search_results)
            
            return {
                "results": search_results,
                "total_count": total_count
            }
            
        except Exception as e:
            self.logger.error(f"Error performing search: {str(e)}")
            raise
    
    async def find_similar(self, email_id: str, limit: int = 5) -> List[SearchResult]:
        """
        Find emails similar to the given email ID.
        """
        try:
            # Get the email document
            result = self.collection.get(
                ids=[email_id],
                include=["documents", "embeddings"]
            )
            
            if not result["ids"]:
                return []
            
            # Use the email's embedding to find similar emails
            embedding = result["embeddings"][0]
            
            similar_results = self.collection.query(
                query_embeddings=[embedding],
                n_results=limit + 1,  # +1 because the original email will be included
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert to SearchResult objects, excluding the original email
            search_results = []
            for i, found_id in enumerate(similar_results["ids"][0]):
                if found_id != email_id:  # Exclude the original email
                    metadata = similar_results["metadatas"][0][i]
                    document = similar_results["documents"][0][i]
                    distance = similar_results["distances"][0][i]
                    
                    similarity_score = max(0.0, 1.0 - distance)
                    
                    search_result = SearchResult(
                        email_id=found_id,
                        subject=metadata.get("subject", ""),
                        snippet=document[:200] + "..." if len(document) > 200 else document,
                        similarity_score=similarity_score,
                        category=EmailCategory(metadata.get("category", "general")),
                        timestamp=metadata.get("timestamp", "")
                    )
                    search_results.append(search_result)
            
            return search_results[:limit]
            
        except Exception as e:
            self.logger.error(f"Error finding similar emails: {str(e)}")
            return []
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using OpenAI's embedding model.
        """
        try:
            response = self.openai_client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def _create_snippet(self, document: str, query: str, max_length: int = 200) -> str:
        """
        Create a relevant snippet from the document based on the query.
        """
        try:
            # Simple approach: find the query terms in the document
            query_terms = query.lower().split()
            document_lower = document.lower()
            
            # Find the best position to start the snippet
            best_pos = 0
            best_score = 0
            
            for i in range(len(document) - max_length + 1):
                snippet = document_lower[i:i + max_length]
                score = sum(1 for term in query_terms if term in snippet)
                
                if score > best_score:
                    best_score = score
                    best_pos = i
            
            # Extract snippet
            snippet = document[best_pos:best_pos + max_length]
            
            # Clean up snippet boundaries (try to end at word boundaries)
            if len(snippet) == max_length and best_pos + max_length < len(document):
                last_space = snippet.rfind(' ')
                if last_space > max_length * 0.8:  # Only if we don't lose too much
                    snippet = snippet[:last_space] + "..."
                else:
                    snippet += "..."
            
            return snippet
            
        except Exception as e:
            self.logger.error(f"Error creating snippet: {str(e)}")
            return document[:max_length] + "..." if len(document) > max_length else document
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the email collection.
        """
        try:
            count = self.collection.count()
            
            return {
                "total_emails": count,
                "collection_name": "emails"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}
