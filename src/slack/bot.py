"""
Slack bot integration for AI News Bot
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
import json

from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

from ..database.models import DatabaseManager, Article
from ..utils.config import get_slack_config

logger = logging.getLogger(__name__)


class AINewsSlackBot:
    """Slack bot for AI news sharing and interaction"""
    
    def __init__(self, config: Dict[str, Any], db: DatabaseManager):
        self.config = get_slack_config(config)
        self.db = db
        
        # Initialize Slack clients
        self.web_client = WebClient(token=self.config['bot_token'])
        
        # Socket mode for slash commands (optional)
        if self.config.get('app_token'):
            self.socket_client = SocketModeClient(
                app_token=self.config['app_token'],
                web_client=self.web_client
            )
            self._setup_socket_handlers()
        else:
            self.socket_client = None
        
        # Configuration
        self.main_channel = self.config.get('channels', {}).get('main', '#ai-news')
        self.alerts_channel = self.config.get('channels', {}).get('alerts', '#ai-news-alerts')
        self.max_articles_per_post = self.config.get('posting', {}).get('max_articles_per_post', 5)
        
    def start_socket_mode(self):
        """Start socket mode for real-time interactions"""
        if self.socket_client:
            logger.info("Starting Slack bot in socket mode...")
            # Clear any existing listeners to avoid conflicts
            self.socket_client.socket_mode_request_listeners.clear()
            # Add only our custom handler
            self.socket_client.socket_mode_request_listeners.append(self._handle_socket_request)
            self.socket_client.connect()
        else:
            logger.warning("Socket mode not available - app_token not configured")
    
    def _setup_socket_handlers(self):
        """Setup socket mode event handlers"""
        if not self.socket_client:
            return
        
        # All socket mode requests are handled by the main handler
        # No need for separate handlers since we handle different types in _handle_socket_request
        pass
    
    def _handle_socket_request(self, client: SocketModeClient, req: SocketModeRequest):
        """Handle incoming socket mode requests"""
        try:
            if req.type == "slash_commands":
                # Handle slash command and respond directly via Socket Mode ONLY
                self._handle_slash_command_with_response(req, client)
                # Do NOT call the old _handle_slash_command method
            elif req.type == "events_api":
                self._handle_event(req)
            else:
                # Acknowledge the request
                response = SocketModeResponse(envelope_id=req.envelope_id)
                client.send_socket_mode_response(response)
            
        except Exception as e:
            logger.error(f"Error handling socket request: {e}")
            # Still acknowledge even on error
            response = SocketModeResponse(envelope_id=req.envelope_id)
            client.send_socket_mode_response(response)
    
    def _handle_slash_command_with_response(self, req: SocketModeRequest, client: SocketModeClient):
        """Handle slash commands and respond directly via Socket Mode"""
        command = req.payload.get("command", "")
        text = req.payload.get("text", "")
        channel_id = req.payload.get("channel_id", "")
        user_id = req.payload.get("user_id", "")
        
        logger.info(f"Received slash command: {command} {text}")
        
        # Generate response content
        response_text = ""
        
        if command == "/ai-news":
            try:
                response_text = self._generate_ai_news_response(text)
                logger.info(f"Generated response for {command} {text}")
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                response_text = f"Sorry, there was an error processing your request: {str(e)}"
        else:
            response_text = "Unknown command"
        
        # Send response via Socket Mode
        try:
            response = SocketModeResponse(
                envelope_id=req.envelope_id,
                payload={
                    "text": response_text,
                    "response_type": "in_channel"  # Make response visible to everyone
                }
            )
            client.send_socket_mode_response(response)
            logger.info(f"Sent Socket Mode response for {command}")
        except Exception as e:
            logger.error(f"Failed to send Socket Mode response: {e}")
    
    def _handle_slash_command(self, req: SocketModeRequest):
        """Handle slash commands"""
        command = req.payload.get("command", "")
        text = req.payload.get("text", "")
        channel_id = req.payload.get("channel_id", "")
        user_id = req.payload.get("user_id", "")
        
        logger.info(f"Received slash command: {command} {text}")
        
        if command == "/ai-news":
            self._handle_ai_news_command(text, channel_id, user_id)
    
    def _handle_event(self, req: SocketModeRequest):
        """Handle events API requests"""
        event = req.payload.get("event", {})
        event_type = event.get("type", "")
        
        logger.info(f"Received event: {event_type}")
        
        if event_type == "app_mention":
            # Handle app mentions if needed
            pass
        elif event_type == "message":
            # Handle messages if needed
            pass
    
    def _handle_ai_news_command(self, text: str, channel_id: str, user_id: str):
        """Handle /ai-news slash command"""
        parts = text.strip().split() if text else []
        
        if not parts:
            self._send_help_message(channel_id)
            return
        
        subcommand = parts[0].lower()
        
        if subcommand == "search":
            query = " ".join(parts[1:]) if len(parts) > 1 else ""
            self._handle_search_command(query, channel_id)
        
        elif subcommand == "latest":
            count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
            self._handle_latest_command(count, channel_id)
        
        elif subcommand == "tags":
            self._handle_tags_command(channel_id)
        
        elif subcommand == "sources":
            self._handle_sources_command(channel_id)
        
        elif subcommand == "stats":
            self._handle_stats_command(channel_id)
        
        else:
            self._send_help_message(channel_id)
    
    def _handle_search_command(self, query: str, channel_id: str):
        """Handle search command"""
        if not query:
            self._send_message(channel_id, "Please provide a search query. Example: `/ai-news search GPT`")
            return
        
        try:
            articles = self.db.search_articles(query, limit=10)
            
            if not articles:
                self._send_message(channel_id, f"No articles found for query: '{query}'")
                return
            
            # Format search results
            blocks = self._format_search_results(articles, query)
            self._send_blocks(channel_id, blocks)
            
        except Exception as e:
            logger.error(f"Search command failed: {e}")
            self._send_message(channel_id, "Search failed. Please try again later.")
    
    def _handle_latest_command(self, count: int, channel_id: str):
        """Handle latest articles command"""
        try:
            articles = self.db.get_articles(limit=min(count, 10))
            
            if not articles:
                self._send_message(channel_id, "No recent articles found.")
                return
            
            blocks = self._format_articles_summary(articles, f"Latest {len(articles)} Articles")
            self._send_blocks(channel_id, blocks)
            
        except Exception as e:
            logger.error(f"Latest command failed: {e}")
            self._send_message(channel_id, "Failed to fetch latest articles.")
    
    def _handle_tags_command(self, channel_id: str):
        """Handle tags listing command"""
        try:
            tags = self.db.get_tags()
            
            if not tags:
                self._send_message(channel_id, "No tags found.")
                return
            
            # Group tags by category
            tag_text = "📋 *Available Tags:*\n\n"
            
            categories = {}
            for tag in tags[:20]:  # Limit to top 20 tags
                category = tag.category or 'general'
                if category not in categories:
                    categories[category] = []
                categories[category].append(f"`{tag.name}` ({tag.usage_count})")
            
            for category, tag_list in categories.items():
                tag_text += f"*{category.title()}:* {', '.join(tag_list)}\n"
            
            self._send_message(channel_id, tag_text)
            
        except Exception as e:
            logger.error(f"Tags command failed: {e}")
            self._send_message(channel_id, "Failed to fetch tags.")
    
    def _handle_sources_command(self, channel_id: str):
        """Handle sources listing command"""
        try:
            sources = self.db.get_sources(enabled_only=False)
            
            if not sources:
                self._send_message(channel_id, "No sources configured.")
                return
            
            source_text = "📰 *News Sources:*\n\n"
            
            # Group by language
            languages = {}
            for source in sources:
                lang = source.language or 'unknown'
                if lang not in languages:
                    languages[lang] = []
                
                status = "✅" if source.enabled else "❌"
                languages[lang].append(f"{status} {source.name} ({source.source_type})")
            
            for lang, source_list in languages.items():
                source_text += f"*{lang.title()}:*\n"
                source_text += "\n".join(source_list) + "\n\n"
            
            self._send_message(channel_id, source_text)
            
        except Exception as e:
            logger.error(f"Sources command failed: {e}")
            self._send_message(channel_id, "Failed to fetch sources.")
    
    def _handle_stats_command(self, channel_id: str):
        """Handle statistics command"""
        try:
            stats = self.db.get_collection_stats(days=7)
            
            stats_text = "📊 *Collection Statistics (Last 7 Days):*\n\n"
            stats_text += f"• Total Articles: {stats['total_articles']}\n"
            stats_text += f"• Success Rate: {stats['success_rate']}%\n\n"
            
            if stats['languages']:
                stats_text += "*By Language:*\n"
                for lang, count in stats['languages'].items():
                    stats_text += f"• {lang}: {count}\n"
                stats_text += "\n"
            
            if stats['top_sources']:
                stats_text += "*Top Sources:*\n"
                for source, count in list(stats['top_sources'].items())[:5]:
                    stats_text += f"• {source}: {count}\n"
            
            self._send_message(channel_id, stats_text)
            
        except Exception as e:
            logger.error(f"Stats command failed: {e}")
            self._send_message(channel_id, "Failed to fetch statistics.")
    
    def _generate_ai_news_response(self, text: str) -> str:
        """Generate response for AI news commands"""
        parts = text.strip().split() if text else []
        
        if not parts:
            return """🤖 *AI News Bot Commands:*

• `/ai-news search <keyword>` - Search for articles
• `/ai-news latest [count]` - Show latest articles (default: 5)
• `/ai-news tags` - List available tags
• `/ai-news sources` - List news sources
• `/ai-news stats` - Show collection statistics

*Examples:*
• `/ai-news search GPT-4`
• `/ai-news latest 10`"""
        
        subcommand = parts[0].lower()
        
        try:
            if subcommand == "search":
                query = " ".join(parts[1:]) if len(parts) > 1 else ""
                if not query:
                    return "Please provide a search query. Example: `/ai-news search GPT`"
                
                articles = self.db.search_articles(query, limit=5)
                if not articles:
                    return f"No articles found for query: '{query}'"
                
                response = f"🔍 *Search Results for '{query}':*\n\n"
                for i, article in enumerate(articles, 1):
                    response += f"{i}. *{article.title}*\n"
                    response += f"   📰 {article.source} | 📅 {article.published_date.strftime('%Y-%m-%d') if article.published_date else 'Unknown'}\n"
                    response += f"   {article.summary[:150]}...\n"
                    response += f"   🔗 {article.url}\n\n"
                return response
            
            elif subcommand == "latest":
                count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 5
                articles = self.db.get_articles(limit=min(count, 10))
                
                if not articles:
                    return "No recent articles found."
                
                response = f"📰 *Latest {len(articles)} Articles:*\n\n"
                for i, article in enumerate(articles, 1):
                    response += f"{i}. *{article.title}*\n"
                    response += f"   📰 {article.source} | 📅 {article.published_date.strftime('%Y-%m-%d') if article.published_date else 'Unknown'}\n"
                    response += f"   {article.summary[:150]}...\n"
                    response += f"   🔗 {article.url}\n\n"
                return response
            
            elif subcommand == "sources":
                sources = self.db.get_sources(enabled_only=False)
                if not sources:
                    return "No sources configured."
                
                response = "📰 *News Sources:*\n\n"
                languages = {}
                for source in sources:
                    lang = source.language or 'unknown'
                    if lang not in languages:
                        languages[lang] = []
                    
                    status = "✅" if source.enabled else "❌"
                    languages[lang].append(f"{status} {source.name} ({source.source_type})")
                
                for lang, source_list in languages.items():
                    response += f"*{lang.title()}:*\n"
                    response += "\n".join(source_list) + "\n\n"
                
                return response
            
            elif subcommand == "tags":
                tags = self.db.get_tags()
                if not tags:
                    return "No tags found."
                
                response = "📋 *Available Tags:*\n\n"
                categories = {}
                for tag in tags[:20]:
                    category = tag.category or 'general'
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(f"`{tag.name}` ({tag.usage_count})")
                
                for category, tag_list in categories.items():
                    response += f"*{category.title()}:* {', '.join(tag_list)}\n"
                
                return response
            
            elif subcommand == "stats":
                stats = self.db.get_collection_stats(days=7)
                
                response = "📊 *Collection Statistics (Last 7 Days):*\n\n"
                response += f"• Total Articles: {stats['total_articles']}\n"
                response += f"• Success Rate: {stats['success_rate']}%\n\n"
                
                if stats['languages']:
                    response += "*By Language:*\n"
                    for lang, count in stats['languages'].items():
                        response += f"• {lang}: {count}\n"
                    response += "\n"
                
                if stats['top_sources']:
                    response += "*Top Sources:*\n"
                    for source, count in list(stats['top_sources'].items())[:5]:
                        response += f"• {source}: {count}\n"
                
                return response
            
            else:
                return """🤖 *AI News Bot Commands:*

• `/ai-news search <keyword>` - Search for articles
• `/ai-news latest [count]` - Show latest articles (default: 5)
• `/ai-news tags` - List available tags
• `/ai-news sources` - List news sources
• `/ai-news stats` - Show collection statistics

*Examples:*
• `/ai-news search GPT-4`
• `/ai-news latest 10`"""
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, there was an error processing your request: {str(e)}"
    
    def _send_help_message(self, channel_id: str):
        """Send help message"""
        help_text = """
🤖 *AI News Bot Commands:*

• `/ai-news search <keyword>` - Search for articles
• `/ai-news latest [count]` - Show latest articles (default: 5)
• `/ai-news tags` - List available tags
• `/ai-news sources` - List news sources
• `/ai-news stats` - Show collection statistics

*Examples:*
• `/ai-news search GPT-4`
• `/ai-news latest 10`
"""
        self._send_message(channel_id, help_text)
    
    def post_articles_summary(self, articles: List[Article], title: str = "AI News Update") -> bool:
        """Post articles summary to main channel"""
        try:
            if not articles:
                logger.info("No articles to post")
                return True
            
            # Limit articles per post
            articles_to_post = articles[:self.max_articles_per_post]
            
            # Format articles
            blocks = self._format_articles_summary(articles_to_post, title)
            
            # Post to main channel
            response = self._send_blocks(self.main_channel, blocks)
            
            if response:
                logger.info(f"Posted {len(articles_to_post)} articles to {self.main_channel}")
                return True
            else:
                logger.error("Failed to post articles to Slack")
                return False
                
        except Exception as e:
            logger.error(f"Failed to post articles summary: {e}")
            return False
    
    def send_alert(self, message: str, level: str = "info") -> bool:
        """Send alert message to alerts channel"""
        try:
            emoji_map = {
                "info": "ℹ️",
                "warning": "⚠️",
                "error": "❌",
                "success": "✅"
            }
            
            emoji = emoji_map.get(level, "ℹ️")
            formatted_message = f"{emoji} *Alert:* {message}"
            
            response = self._send_message(self.alerts_channel, formatted_message)
            
            if response:
                logger.info(f"Sent alert to {self.alerts_channel}: {message}")
                return True
            else:
                logger.error("Failed to send alert to Slack")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False
    
    def _format_articles_summary(self, articles: List[Article], title: str) -> List[Dict]:
        """Format articles as Slack blocks"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            },
            {
                "type": "divider"
            }
        ]
        
        for article in articles:
            # Article block
            article_block = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{article.url}|{article.title}>*\n{article.summary or 'No summary available'}"
                }
            }
            
            # Add metadata
            metadata_text = []
            if article.source:
                metadata_text.append(f"📰 {article.source}")
            if article.language:
                metadata_text.append(f"🌐 {article.language}")
            if article.published_date:
                metadata_text.append(f"📅 {article.published_date.strftime('%Y-%m-%d')}")
            
            if metadata_text:
                article_block["fields"] = [
                    {
                        "type": "mrkdwn",
                        "text": " | ".join(metadata_text)
                    }
                ]
            
            blocks.append(article_block)
            
            # Add tags if available
            if article.tags:
                tags_text = " ".join([f"`{tag}`" for tag in article.tags[:5]])
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"🏷️ {tags_text}"
                        }
                    ]
                })
            
            blocks.append({"type": "divider"})
        
        return blocks
    
    def _format_search_results(self, articles: List[Article], query: str) -> List[Dict]:
        """Format search results as Slack blocks"""
        return self._format_articles_summary(articles, f"Search Results for '{query}'")
    
    def _send_message(self, channel: str, text: str) -> bool:
        """Send simple text message"""
        try:
            response = self.web_client.chat_postMessage(
                channel=channel,
                text=text
            )
            return response["ok"]
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def _send_blocks(self, channel: str, blocks: List[Dict]) -> bool:
        """Send message with blocks"""
        try:
            response = self.web_client.chat_postMessage(
                channel=channel,
                text="AI News Update",  # Fallback text for accessibility
                blocks=blocks
            )
            return response["ok"]
        except Exception as e:
            logger.error(f"Failed to send blocks: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Slack connection"""
        try:
            response = self.web_client.auth_test()
            if response["ok"]:
                logger.info(f"Slack connection successful. Bot user: {response['user']}")
                return True
            else:
                logger.error("Slack connection failed")
                return False
        except Exception as e:
            logger.error(f"Slack connection test failed: {e}")
            return False
