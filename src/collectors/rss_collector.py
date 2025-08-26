"""
RSS feed collector for news sources
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import feedparser
from urllib.parse import urljoin

from .base_collector import BaseCollector
from ..database.models import Article

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    """Collector for RSS feeds"""
    
    def collect_articles(self) -> List[Article]:
        """Collect articles from RSS feed"""
        articles = []
        
        try:
            logger.info(f"Fetching RSS feed: {self.source.url}")
            
            # Parse RSS feed
            feed = feedparser.parse(self.source.url)
            
            if feed.bozo:
                logger.warning(f"RSS feed has parsing issues: {feed.bozo_exception}")
            
            # Get recent articles from database to avoid processing duplicates
            from ..database.models import DatabaseManager
            db_path = self.config.get('database', {}).get('path', 'data/ai_news.db')
            db = DatabaseManager(db_path)
            recent_data = self._get_recent_articles_data(db)
            
            processed_count = 0
            url_skipped_count = 0
            title_skipped_count = 0
            
            # Process entries
            for entry in feed.entries:
                try:
                    # Quick URL check before processing
                    entry_url = getattr(entry, 'link', '')
                    if entry_url in recent_data['urls']:
                        url_skipped_count += 1
                        logger.debug(f"Skipping recently collected URL: {entry_url}")
                        continue
                    
                    # Quick title check before processing
                    entry_title = getattr(entry, 'title', '')
                    normalized_title = self._normalize_title(entry_title)
                    if normalized_title in recent_data['titles']:
                        title_skipped_count += 1
                        logger.debug(f"Skipping recently collected title: {entry_title}")
                        continue
                    
                    article = self._process_entry(entry)
                    if article and self._should_process_article(article):
                        articles.append(article)
                        processed_count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to process RSS entry: {e}")
                    continue
            
            total_skipped = url_skipped_count + title_skipped_count
            if total_skipped > 0:
                logger.info(f"Skipped {total_skipped} recently collected articles (URLs: {url_skipped_count}, Titles: {title_skipped_count})")
            
            logger.info(f"Collected {len(articles)} articles from RSS feed")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to collect from RSS feed {self.source.url}: {e}")
            return []
    
    def _process_entry(self, entry) -> Optional[Article]:
        """Process a single RSS entry"""
        
        # Extract basic information
        title = getattr(entry, 'title', '')
        url = getattr(entry, 'link', '')
        
        if not title or not url:
            logger.debug("Skipping entry without title or URL")
            return None
        
        # Extract content
        content = self._extract_content(entry)
        
        # Extract author
        author = self._extract_author(entry)
        
        # Extract published date
        published_date = self._extract_published_date(entry)
        
        # Extract metadata
        metadata = self._extract_metadata(entry)
        
        # Create article
        article = self._create_article(
            title=title,
            url=url,
            content=content,
            author=author,
            published_date=published_date,
            metadata=metadata
        )
        
        return article
    
    def _extract_content(self, entry) -> str:
        """Extract content from RSS entry"""
        content = ""
        
        # Try different content fields in order of preference
        content_fields = [
            'content',
            'summary',
            'description'
        ]
        
        for field in content_fields:
            if hasattr(entry, field):
                field_value = getattr(entry, field)
                
                if isinstance(field_value, list) and field_value:
                    # Handle content field which is usually a list
                    if hasattr(field_value[0], 'value'):
                        content = field_value[0].value
                    elif hasattr(field_value[0], 'get'):
                        content = field_value[0].get('value', '')
                    else:
                        content = str(field_value[0])
                elif isinstance(field_value, str):
                    content = field_value
                elif hasattr(field_value, 'value'):
                    content = field_value.value
                
                if content:
                    break
        
        # Clean HTML if present
        if content:
            content = self._extract_text_content(content)
        
        return content
    
    def _extract_author(self, entry) -> str:
        """Extract author from RSS entry"""
        author_fields = ['author', 'dc_creator', 'author_detail']
        
        for field in author_fields:
            if hasattr(entry, field):
                author = getattr(entry, field)
                
                if isinstance(author, dict):
                    return author.get('name', '')
                elif isinstance(author, str):
                    return author
        
        return ""
    
    def _extract_published_date(self, entry) -> Optional[datetime]:
        """Extract published date from RSS entry"""
        date_fields = ['published', 'updated', 'created']
        
        for field in date_fields:
            if hasattr(entry, field):
                date_str = getattr(entry, field)
                if date_str:
                    return self._parse_date(date_str)
        
        # Try parsed date fields
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                import time
                return datetime.fromtimestamp(time.mktime(entry.published_parsed))
            except (ValueError, OverflowError):
                pass
        
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            try:
                import time
                return datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            except (ValueError, OverflowError):
                pass
        
        return None
    
    def _extract_metadata(self, entry) -> Dict[str, Any]:
        """Extract metadata from RSS entry"""
        metadata = {}
        
        # Extract tags/categories
        if hasattr(entry, 'tags'):
            metadata['categories'] = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
        
        # Extract GUID
        if hasattr(entry, 'id'):
            metadata['guid'] = entry.id
        
        # Extract media content
        if hasattr(entry, 'media_content'):
            metadata['media'] = [
                {
                    'url': media.get('url', ''),
                    'type': media.get('type', ''),
                    'medium': media.get('medium', '')
                }
                for media in entry.media_content
            ]
        
        # Extract enclosures (attachments)
        if hasattr(entry, 'enclosures'):
            metadata['enclosures'] = [
                {
                    'url': enc.href,
                    'type': enc.type,
                    'length': enc.length
                }
                for enc in entry.enclosures
            ]
        
        return metadata
    
    def _should_process_article(self, article: Article) -> bool:
        """Check if article should be processed based on source-specific filters"""
        
        # Apply keyword filtering for Japanese sources
        if self.source.language == 'japanese':
            filter_keywords = self.source.config.get('filter_keywords', [])
            if filter_keywords:
                text = (article.title + ' ' + article.content).lower()
                if not any(keyword.lower() in text for keyword in filter_keywords):
                    logger.debug(f"Article filtered out by Japanese keywords: {article.title}")
                    return False
        
        return True
    
    def _get_recent_articles_data(self, db) -> Dict[str, set]:
        """Get URLs and titles of recently collected articles to avoid duplicates"""
        try:
            with db.get_connection() as conn:
                # Get URLs from articles collected in the last 24 hours
                url_rows = conn.execute("""
                    SELECT url FROM articles 
                    WHERE collected_date >= datetime('now', '-1 day')
                    AND source = ?
                """, (self.source.name,)).fetchall()
                
                # Get titles from articles collected in the last 48 hours (longer window for titles)
                title_rows = conn.execute("""
                    SELECT title FROM articles 
                    WHERE collected_date >= datetime('now', '-2 days')
                    AND source = ?
                """, (self.source.name,)).fetchall()
                
                urls = {row[0] for row in url_rows}
                titles = {self._normalize_title(row[0]) for row in title_rows}
                
                return {
                    'urls': urls,
                    'titles': titles
                }
        except Exception as e:
            logger.warning(f"Failed to get recent articles data: {e}")
            return {'urls': set(), 'titles': set()}
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for exact matching"""
        if not title:
            return ""
        
        # Remove leading/trailing whitespace and normalize unicode
        normalized = title.strip()
        
        # Normalize unicode characters
        import unicodedata
        normalized = unicodedata.normalize('NFKC', normalized)
        
        return normalized
    
    def _get_recent_urls(self, db) -> set:
        """Get URLs of recently collected articles to avoid duplicates (legacy method)"""
        try:
            with db.get_connection() as conn:
                # Get URLs from articles collected in the last 24 hours
                rows = conn.execute("""
                    SELECT url FROM articles 
                    WHERE collected_date >= datetime('now', '-1 day')
                    AND source = ?
                """, (self.source.name,)).fetchall()
                
                return {row[0] for row in rows}
        except Exception as e:
            logger.warning(f"Failed to get recent URLs: {e}")
            return set()
    
    def _fetch_full_content(self, url: str) -> str:
        """Fetch full article content from URL if RSS only provides summary"""
        try:
            response = self._make_request(url)
            html = response.text
            
            # Extract main content using common selectors
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '#content'
            ]
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    return self._extract_text_content(str(content_elem))
            
            # Fallback to body content
            body = soup.find('body')
            if body:
                return self._extract_text_content(str(body))
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to fetch full content from {url}: {e}")
            return ""
