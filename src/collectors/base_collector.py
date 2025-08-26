"""
Base collector class for news sources
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import time
import requests
from urllib.parse import urlparse

from ..database.models import Article, Source, CollectionLog
from ..utils.config import get_performance_config, get_filtering_config

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Base class for all news collectors"""
    
    def __init__(self, source: Source, config: Dict[str, Any]):
        self.source = source
        self.config = config
        self.performance_config = get_performance_config(config)
        self.filtering_config = get_filtering_config(config)
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create HTTP session with proper configuration"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'AI-News-Bot/1.0 (Educational Purpose)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Set timeout
        timeout = self.performance_config.get('request_timeout', 30)
        session.timeout = timeout
        
        return session
    
    @abstractmethod
    def collect_articles(self) -> List[Article]:
        """Collect articles from the source"""
        pass
    
    def collect_with_logging(self) -> CollectionLog:
        """Collect articles with comprehensive logging"""
        start_time = time.time()
        log = CollectionLog(source_id=self.source.id)
        
        try:
            logger.info(f"Starting collection from {self.source.name}")
            
            # Collect articles
            articles = self.collect_articles()
            
            # Filter articles
            filtered_articles = self._filter_articles(articles)
            
            # Update log
            log.articles_found = len(articles)
            log.articles_processed = len(filtered_articles)
            log.status = 'success'
            
            logger.info(
                f"Collection completed: {len(articles)} found, "
                f"{len(filtered_articles)} after filtering"
            )
            
            return log, filtered_articles
            
        except Exception as e:
            error_msg = f"Collection failed: {str(e)}"
            logger.error(error_msg)
            log.errors.append(error_msg)
            log.status = 'failed'
            return log, []
            
        finally:
            log.duration_seconds = time.time() - start_time
    
    def _filter_articles(self, articles: List[Article]) -> List[Article]:
        """Filter articles based on configuration"""
        filtered = []
        
        for article in articles:
            if self._should_include_article(article):
                filtered.append(article)
            else:
                logger.debug(f"Filtered out article: {article.title}")
        
        return filtered
    
    def _should_include_article(self, article: Article) -> bool:
        """Check if article should be included based on filters"""
        
        # Check minimum length
        min_length = self.filtering_config.get('min_article_length', 100)
        if len(article.content) < min_length:
            return False
        
        # Check age
        max_age_days = self.filtering_config.get('max_article_age_days', 7)
        if article.published_date:
            # Make both datetimes timezone-aware or timezone-naive for comparison
            now = datetime.now()
            pub_date = article.published_date
            
            # If published_date is timezone-aware, make now timezone-aware too
            if pub_date.tzinfo is not None:
                import pytz
                if now.tzinfo is None:
                    now = pytz.UTC.localize(now)
            # If published_date is timezone-naive, make sure now is also timezone-naive
            elif now.tzinfo is not None:
                now = now.replace(tzinfo=None)
            
            age = now - pub_date
            if age.days > max_age_days:
                return False
        
        # Check blocked domains
        blocked_domains = self.filtering_config.get('blocked_domains', [])
        if blocked_domains:
            domain = urlparse(article.url).netloc.lower()
            if any(blocked in domain for blocked in blocked_domains):
                return False
        
        # Check required keywords
        required_keywords = self.filtering_config.get('required_keywords', [])
        if required_keywords:
            text = (article.title + ' ' + article.content).lower()
            if not any(keyword.lower() in text for keyword in required_keywords):
                return False
        
        return True
    
    def _make_request(self, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic"""
        retry_attempts = self.performance_config.get('retry_attempts', 3)
        retry_delay = self.performance_config.get('retry_delay', 5)
        
        for attempt in range(retry_attempts):
            try:
                response = self.session.get(url, **kwargs)
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == retry_attempts - 1:
                    raise
                
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{retry_attempts}): {e}"
                )
                time.sleep(retry_delay)
        
        raise RuntimeError("All retry attempts failed")
    
    def _extract_text_content(self, html: str) -> str:
        """Extract clean text content from HTML"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.warning(f"Failed to extract text content: {e}")
            return html
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            from langdetect import detect
            detected = detect(text)
            
            # Map language codes to our standard format
            language_map = {
                'en': 'english',
                'ja': 'japanese',
                'zh': 'chinese',
                'ko': 'korean'
            }
            
            return language_map.get(detected, detected)
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return self.source.language or 'unknown'
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%d %b %Y %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            'Read more',
            'Continue reading',
            'Click here',
            'Subscribe',
            'Advertisement',
        ]
        
        for pattern in unwanted_patterns:
            text = text.replace(pattern, '')
        
        return text.strip()
    
    def _create_article(self, title: str, url: str, content: str = "", 
                       author: str = "", published_date: Optional[datetime] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Article:
        """Create Article object with common fields"""
        
        # Clean inputs
        title = self._clean_text(title)
        content = self._clean_text(content)
        author = self._clean_text(author)
        
        # Detect language if not specified
        language = self._detect_language(title + ' ' + content)
        
        # Create article
        article = Article(
            title=title,
            url=url,
            content=content,
            language=language,
            source=self.source.name,
            author=author,
            published_date=published_date,
            metadata=metadata or {},
            tags=self.source.tags.copy()
        )
        
        return article
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'session'):
            self.session.close()
