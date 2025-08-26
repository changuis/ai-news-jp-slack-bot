"""
AI-powered article summarization using OpenAI GPT
"""

from typing import Dict, Any, Optional
import logging
import openai
from openai import OpenAI

from ..database.models import Article
from ..utils.config import get_openai_config

logger = logging.getLogger(__name__)


class ArticleSummarizer:
    """AI-powered article summarizer using OpenAI GPT"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = get_openai_config(config)
        self.client = OpenAI(api_key=self.config['api_key'])
        
        # Configuration
        self.model = self.config.get('model', 'gpt-4')
        self.max_tokens = self.config.get('max_tokens', 500)
        self.temperature = self.config.get('temperature', 0.3)
        
        # Prompts
        self.prompts = self.config.get('prompts', {})
        
    def summarize_article(self, article: Article) -> str:
        """Generate summary for an article"""
        try:
            logger.info(f"Generating summary for article: {article.title}")
            
            # Choose appropriate prompt based on language
            prompt_template = self._get_prompt_template(article.language)
            
            # Prepare content for summarization
            content = self._prepare_content(article)
            
            # Generate prompt
            prompt = prompt_template.format(article_text=content)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(article.language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"Summary generated successfully for: {article.title}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary for {article.title}: {e}")
            return self._generate_fallback_summary(article)
    
    def _get_prompt_template(self, language: str) -> str:
        """Get appropriate prompt template for language"""
        if language == 'japanese':
            return self.prompts.get('japanese_summary', """
以下のAI関連記事を2-3文で要約してください。
主要な技術的発展とその影響に焦点を当ててください：

{article_text}
""")
        else:
            return self.prompts.get('english_summary', """
Summarize the following AI-related article in 2-3 sentences. 
Focus on the key technical developments and their implications:

{article_text}
""")
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt for the language"""
        if language == 'japanese':
            return """あなたはAI技術の専門家です。記事を簡潔で分かりやすく要約し、
技術的な重要性と実用的な影響を強調してください。専門用語は適切に説明してください。"""
        else:
            return """You are an AI technology expert. Provide concise, clear summaries that 
highlight technical significance and practical implications. Explain technical terms appropriately."""
    
    def _prepare_content(self, article: Article) -> str:
        """Prepare article content for summarization"""
        # Combine title and content
        content = f"Title: {article.title}\n\n"
        
        if article.content:
            # Truncate content if too long (to stay within token limits)
            max_content_length = 3000  # Approximate token limit
            if len(article.content) > max_content_length:
                content += article.content[:max_content_length] + "..."
            else:
                content += article.content
        
        # Add metadata if available
        if article.author:
            content += f"\n\nAuthor: {article.author}"
        
        if article.published_date:
            content += f"\nPublished: {article.published_date.strftime('%Y-%m-%d')}"
        
        return content
    
    def _generate_fallback_summary(self, article: Article) -> str:
        """Generate a simple fallback summary when AI fails"""
        # Extract first few sentences as fallback
        sentences = article.content.split('.')[:3]
        summary = '. '.join(sentences).strip()
        
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        if not summary:
            summary = article.title
        
        logger.info(f"Using fallback summary for: {article.title}")
        return summary
    
    def batch_summarize(self, articles: list[Article]) -> Dict[str, str]:
        """Summarize multiple articles in batch"""
        summaries = {}
        
        for article in articles:
            try:
                summary = self.summarize_article(article)
                summaries[article.url] = summary
            except Exception as e:
                logger.error(f"Failed to summarize article {article.url}: {e}")
                summaries[article.url] = self._generate_fallback_summary(article)
        
        return summaries
    
    def get_summary_length_config(self, length_type: str = "medium") -> Dict[str, int]:
        """Get token limits based on summary length preference"""
        length_configs = {
            "short": {"max_tokens": 150, "sentences": 1},
            "medium": {"max_tokens": 300, "sentences": 2-3},
            "long": {"max_tokens": 500, "sentences": 3-5}
        }
        
        return length_configs.get(length_type, length_configs["medium"])


class TagGenerator:
    """AI-powered tag generation for articles"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = get_openai_config(config)
        self.client = OpenAI(api_key=self.config['api_key'])
        self.model = self.config.get('model', 'gpt-4')
    
    def generate_tags(self, article: Article, max_tags: int = 5) -> list[str]:
        """Generate relevant tags for an article"""
        try:
            logger.info(f"Generating tags for article: {article.title}")
            
            # Prepare content
            content = f"Title: {article.title}\n\nContent: {article.content[:1000]}"
            
            # Create prompt
            prompt = self._get_tagging_prompt(article.language, max_tags)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_tagging_system_prompt(article.language)
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n{content}"
                    }
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            # Parse tags from response
            tags_text = response.choices[0].message.content.strip()
            tags = self._parse_tags(tags_text)
            
            logger.info(f"Generated {len(tags)} tags for: {article.title}")
            return tags[:max_tags]
            
        except Exception as e:
            logger.error(f"Failed to generate tags for {article.title}: {e}")
            return self._generate_fallback_tags(article)
    
    def _get_tagging_prompt(self, language: str, max_tags: int) -> str:
        """Get tagging prompt for language"""
        if language == 'japanese':
            return f"""以下のAI関連記事に最も関連性の高いタグを{max_tags}個生成してください。
タグはカンマ区切りで出力してください。技術分野、応用領域、企業名などを含めてください。"""
        else:
            return f"""Generate {max_tags} most relevant tags for the following AI-related article.
Output tags separated by commas. Include technical fields, application domains, company names, etc."""
    
    def _get_tagging_system_prompt(self, language: str) -> str:
        """Get system prompt for tagging"""
        if language == 'japanese':
            return """あなたはAI技術の専門家です。記事の内容を分析し、
検索や分類に有用な適切なタグを生成してください。"""
        else:
            return """You are an AI technology expert. Analyze the article content and 
generate appropriate tags that would be useful for search and categorization."""
    
    def _parse_tags(self, tags_text: str) -> list[str]:
        """Parse tags from AI response"""
        # Split by common separators
        separators = [',', ';', '\n', '|']
        
        tags = [tags_text]
        for sep in separators:
            new_tags = []
            for tag in tags:
                new_tags.extend(tag.split(sep))
            tags = new_tags
        
        # Clean and filter tags
        cleaned_tags = []
        for tag in tags:
            tag = tag.strip().lower()
            if tag and len(tag) > 1 and len(tag) < 30:
                cleaned_tags.append(tag)
        
        return list(set(cleaned_tags))  # Remove duplicates
    
    def _generate_fallback_tags(self, article: Article) -> list[str]:
        """Generate simple fallback tags"""
        tags = ['ai', 'artificial intelligence']
        
        # Add language tag
        if article.language:
            tags.append(article.language)
        
        # Add source tag
        if article.source:
            tags.append(article.source.lower().replace(' ', '-'))
        
        return tags
