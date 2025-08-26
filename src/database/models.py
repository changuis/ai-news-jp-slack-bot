"""
Database models for the AI News Slack Bot
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class Article:
    """Article data model"""
    id: Optional[int] = None
    title: str = ""
    url: str = ""
    content: str = ""
    summary: str = ""
    language: str = ""
    source: str = ""
    author: str = ""
    published_date: Optional[datetime] = None
    collected_date: Optional[datetime] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.collected_date is None:
            self.collected_date = datetime.now()


@dataclass
class Source:
    """News source data model"""
    id: Optional[int] = None
    name: str = ""
    url: str = ""
    source_type: str = ""  # rss, website, twitter, reddit
    language: str = ""
    enabled: bool = True
    last_collected: Optional[datetime] = None
    collection_count: int = 0
    error_count: int = 0
    tags: List[str] = None
    config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.config is None:
            self.config = {}


@dataclass
class Tag:
    """Tag data model"""
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    description: str = ""
    color: str = "#000000"
    usage_count: int = 0
    created_date: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()


@dataclass
class CollectionLog:
    """Collection log data model"""
    id: Optional[int] = None
    source_id: int = 0
    collection_date: Optional[datetime] = None
    articles_found: int = 0
    articles_processed: int = 0
    articles_new: int = 0
    errors: List[str] = None
    duration_seconds: float = 0.0
    status: str = "success"  # success, partial, failed
    
    def __post_init__(self):
        if self.collection_date is None:
            self.collection_date = datetime.now()
        if self.errors is None:
            self.errors = []


class DatabaseManager:
    """Database manager for SQLite operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            # Articles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    content TEXT,
                    summary TEXT,
                    language TEXT,
                    source TEXT,
                    author TEXT,
                    published_date TIMESTAMP,
                    collected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT,  -- JSON array
                    metadata TEXT  -- JSON object
                )
            """)
            
            # Sources table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    language TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    last_collected TIMESTAMP,
                    collection_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    tags TEXT,  -- JSON array
                    config TEXT  -- JSON object
                )
            """)
            
            # Tags table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    category TEXT,
                    description TEXT,
                    color TEXT DEFAULT '#000000',
                    usage_count INTEGER DEFAULT 0,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Collection logs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collection_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER,
                    collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    articles_found INTEGER DEFAULT 0,
                    articles_processed INTEGER DEFAULT 0,
                    articles_new INTEGER DEFAULT 0,
                    errors TEXT,  -- JSON array
                    duration_seconds REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'success',
                    FOREIGN KEY (source_id) REFERENCES sources (id)
                )
            """)
            
            # Article-Tag relationship table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_tags (
                    article_id INTEGER,
                    tag_id INTEGER,
                    confidence REAL DEFAULT 1.0,
                    PRIMARY KEY (article_id, tag_id),
                    FOREIGN KEY (article_id) REFERENCES articles (id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_title ON articles(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_published_date ON articles(published_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_collected_date ON articles(collected_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_language ON articles(language)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sources_enabled ON sources(enabled)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_collection_logs_date ON collection_logs(collection_date)")
            
            conn.commit()
    
    def save_article(self, article: Article) -> int:
        """Save article to database"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO articles 
                (title, url, content, summary, language, source, author, 
                 published_date, collected_date, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.title,
                article.url,
                article.content,
                article.summary,
                article.language,
                article.source,
                article.author,
                article.published_date,
                article.collected_date,
                json.dumps(article.tags),
                json.dumps(article.metadata)
            ))
            return cursor.lastrowid
    
    def get_article_by_url(self, url: str) -> Optional[Article]:
        """Get article by URL"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM articles WHERE url = ?", (url,)).fetchone()
            if row:
                return self._row_to_article(row)
            return None
    
    def get_article_by_title(self, title: str, source: str = None) -> Optional[Article]:
        """Get article by title (optionally filtered by source)"""
        with self.get_connection() as conn:
            if source:
                row = conn.execute("SELECT * FROM articles WHERE title = ? AND source = ?", (title, source)).fetchone()
            else:
                row = conn.execute("SELECT * FROM articles WHERE title = ?", (title,)).fetchone()
            if row:
                return self._row_to_article(row)
            return None
    
    def get_articles(self, limit: int = 50, offset: int = 0, 
                    language: Optional[str] = None,
                    source: Optional[str] = None,
                    tags: Optional[List[str]] = None) -> List[Article]:
        """Get articles with filters"""
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if tags:
            # Simple tag filtering - could be improved with proper JOIN
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f'%"{tag}"%')
        
        query += " ORDER BY published_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_article(row) for row in rows]
    
    def search_articles(self, query: str, limit: int = 50) -> List[Article]:
        """Search articles by title and content"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM articles 
                WHERE title LIKE ? OR content LIKE ? OR summary LIKE ?
                ORDER BY published_date DESC 
                LIMIT ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%', limit)).fetchall()
            return [self._row_to_article(row) for row in rows]
    
    def save_source(self, source: Source) -> int:
        """Save source to database"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO sources 
                (name, url, source_type, language, enabled, last_collected,
                 collection_count, error_count, tags, config)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source.name,
                source.url,
                source.source_type,
                source.language,
                source.enabled,
                source.last_collected,
                source.collection_count,
                source.error_count,
                json.dumps(source.tags),
                json.dumps(source.config)
            ))
            return cursor.lastrowid
    
    def get_sources(self, enabled_only: bool = True) -> List[Source]:
        """Get all sources"""
        query = "SELECT * FROM sources"
        if enabled_only:
            query += " WHERE enabled = 1"
        
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [self._row_to_source(row) for row in rows]
    
    def save_tag(self, tag: Tag) -> int:
        """Save tag to database"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO tags 
                (name, category, description, color, usage_count, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tag.name,
                tag.category,
                tag.description,
                tag.color,
                tag.usage_count,
                tag.created_date
            ))
            return cursor.lastrowid
    
    def get_tags(self) -> List[Tag]:
        """Get all tags"""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM tags ORDER BY usage_count DESC").fetchall()
            return [self._row_to_tag(row) for row in rows]
    
    def save_collection_log(self, log: CollectionLog) -> int:
        """Save collection log"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO collection_logs 
                (source_id, collection_date, articles_found, articles_processed,
                 articles_new, errors, duration_seconds, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log.source_id,
                log.collection_date,
                log.articles_found,
                log.articles_processed,
                log.articles_new,
                json.dumps(log.errors),
                log.duration_seconds,
                log.status
            ))
            return cursor.lastrowid
    
    def get_collection_stats(self, days: int = 7) -> Dict[str, Any]:
        """Get collection statistics"""
        with self.get_connection() as conn:
            # Total articles collected in the last N days
            total_articles = conn.execute("""
                SELECT COUNT(*) FROM articles 
                WHERE collected_date >= datetime('now', '-{} days')
            """.format(days)).fetchone()[0]
            
            # Articles by language
            lang_stats = conn.execute("""
                SELECT language, COUNT(*) as count FROM articles 
                WHERE collected_date >= datetime('now', '-{} days')
                GROUP BY language
            """.format(days)).fetchall()
            
            # Articles by source
            source_stats = conn.execute("""
                SELECT source, COUNT(*) as count FROM articles 
                WHERE collected_date >= datetime('now', '-{} days')
                GROUP BY source
                ORDER BY count DESC
                LIMIT 10
            """.format(days)).fetchall()
            
            # Collection success rate
            success_rate = conn.execute("""
                SELECT 
                    COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*) as rate
                FROM collection_logs 
                WHERE collection_date >= datetime('now', '-{} days')
            """.format(days)).fetchone()[0] or 0
            
            return {
                'total_articles': total_articles,
                'languages': dict(lang_stats),
                'top_sources': dict(source_stats),
                'success_rate': round(success_rate, 2),
                'period_days': days
            }
    
    def cleanup_old_articles(self, days: int = 30) -> int:
        """Remove articles older than specified days"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM articles 
                WHERE collected_date < datetime('now', '-{} days')
            """.format(days))
            return cursor.rowcount
    
    def _row_to_article(self, row) -> Article:
        """Convert database row to Article object"""
        return Article(
            id=row['id'],
            title=row['title'],
            url=row['url'],
            content=row['content'],
            summary=row['summary'],
            language=row['language'],
            source=row['source'],
            author=row['author'],
            published_date=datetime.fromisoformat(row['published_date']) if row['published_date'] else None,
            collected_date=datetime.fromisoformat(row['collected_date']) if row['collected_date'] else None,
            tags=json.loads(row['tags']) if row['tags'] else [],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def _row_to_source(self, row) -> Source:
        """Convert database row to Source object"""
        return Source(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            source_type=row['source_type'],
            language=row['language'],
            enabled=bool(row['enabled']),
            last_collected=datetime.fromisoformat(row['last_collected']) if row['last_collected'] else None,
            collection_count=row['collection_count'],
            error_count=row['error_count'],
            tags=json.loads(row['tags']) if row['tags'] else [],
            config=json.loads(row['config']) if row['config'] else {}
        )
    
    def _row_to_tag(self, row) -> Tag:
        """Convert database row to Tag object"""
        return Tag(
            id=row['id'],
            name=row['name'],
            category=row['category'],
            description=row['description'],
            color=row['color'],
            usage_count=row['usage_count'],
            created_date=datetime.fromisoformat(row['created_date']) if row['created_date'] else None
        )
