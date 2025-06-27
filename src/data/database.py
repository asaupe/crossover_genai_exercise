"""
Database operations for email storage and retrieval.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import sqlite3
from pathlib import Path
from loguru import logger

from src.config.settings import settings
from src.data.models import EmailRequest, EmailProcessingResult


class EmailDatabase:
    """Database operations for email storage."""
    
    def __init__(self):
        self.logger = logger.bind(name="EmailDatabase")
        self.db_path = self._get_db_path()
        self._init_database()
    
    def _get_db_path(self) -> str:
        """Get database path from settings."""
        if settings.DATABASE_URL.startswith("sqlite:///"):
            return settings.DATABASE_URL[10:]  # Remove sqlite:/// prefix
        return "emails.db"
    
    def _init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create emails table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS emails (
                        id TEXT PRIMARY KEY,
                        subject TEXT NOT NULL,
                        body TEXT NOT NULL,
                        sender TEXT NOT NULL,
                        category TEXT,
                        priority TEXT,
                        sentiment TEXT,
                        confidence REAL,
                        keywords TEXT,
                        entities TEXT,
                        response_content TEXT,
                        response_tone TEXT,
                        suggested_actions TEXT,
                        processing_time REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """)
                
                # Create knowledge base table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        category TEXT,
                        tags TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails(sender)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_category ON emails(category)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_emails_created_at ON emails(created_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_kb_category ON knowledge_base(category)")
                
                conn.commit()
                
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise
    
    async def store_email(
        self, 
        email_id: str, 
        email: EmailRequest, 
        result: EmailProcessingResult
    ) -> None:
        """
        Store processed email in database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO emails (
                        id, subject, body, sender, category, priority, sentiment,
                        confidence, keywords, entities, response_content, response_tone,
                        suggested_actions, processing_time, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    email_id,
                    email.subject,
                    email.body,
                    email.sender,
                    result.classification.category.value,
                    result.classification.priority.value,
                    result.classification.sentiment.value,
                    result.classification.confidence,
                    json.dumps(result.classification.keywords),
                    json.dumps(result.classification.entities),
                    result.response.content,
                    result.response.tone,
                    json.dumps(result.response.suggested_actions),
                    result.processing_time,
                    json.dumps(email.metadata)
                ))
                
                conn.commit()
                
            self.logger.info(f"Stored email {email_id} in database")
            
        except Exception as e:
            self.logger.error(f"Error storing email: {str(e)}")
            raise
    
    async def get_email(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve email by ID.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving email {email_id}: {str(e)}")
            return None
    
    async def get_emails_by_sender(
        self, 
        sender: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get emails from a specific sender.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT * FROM emails WHERE sender = ? ORDER BY created_at DESC LIMIT ?",
                    (sender, limit)
                )
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Error getting emails by sender {sender}: {str(e)}")
            return []
    
    async def search_emails(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search emails by text content.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = """
                    SELECT * FROM emails 
                    WHERE (subject LIKE ? OR body LIKE ?)
                """
                params = [f"%{query}%", f"%{query}%"]
                
                if category:
                    sql += " AND category = ?"
                    params.append(category)
                
                sql += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Error searching emails: {str(e)}")
            return []
    
    async def search_knowledge_base(
        self, 
        query: str, 
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base articles.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                sql = """
                    SELECT * FROM knowledge_base 
                    WHERE (title LIKE ? OR content LIKE ?)
                """
                params = [f"%{query}%", f"%{query}%"]
                
                if category:
                    sql += " AND category = ?"
                    params.append(category)
                
                sql += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Error searching knowledge base: {str(e)}")
            return []
    
    async def get_email_stats(self) -> Dict[str, Any]:
        """
        Get email statistics.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total emails
                cursor.execute("SELECT COUNT(*) FROM emails")
                total_emails = cursor.fetchone()[0]
                
                # Emails by category
                cursor.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM emails 
                    GROUP BY category
                """)
                category_stats = dict(cursor.fetchall())
                
                # Recent activity (last 24 hours)
                cursor.execute("""
                    SELECT COUNT(*) FROM emails 
                    WHERE created_at >= datetime('now', '-1 day')
                """)
                recent_emails = cursor.fetchone()[0]
                
                return {
                    "total_emails": total_emails,
                    "category_breakdown": category_stats,
                    "recent_emails_24h": recent_emails
                }
                
        except Exception as e:
            self.logger.error(f"Error getting email stats: {str(e)}")
            return {"error": str(e)}
    
    async def add_knowledge_article(
        self, 
        title: str, 
        content: str, 
        category: str,
        tags: List[str]
    ) -> int:
        """
        Add an article to the knowledge base.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO knowledge_base (title, content, category, tags)
                    VALUES (?, ?, ?, ?)
                """, (title, content, category, json.dumps(tags)))
                
                article_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Added knowledge base article {article_id}")
                return article_id
                
        except Exception as e:
            self.logger.error(f"Error adding knowledge article: {str(e)}")
            raise
