#!/usr/bin/env python3
"""
AI News JP Slack Bot - Main application entry point
Japanese AI News Bot for Railway deployment
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

# Import health check for Railway
from health_check import start_health_check, stop_health_check

from src.utils.config import load_config, setup_logging, create_example_config
from src.database.models import DatabaseManager
from src.collectors.rss_collector import RSSCollector
from src.processors.summarizer import ArticleSummarizer, TagGenerator
from src.slack.bot import AINewsSlackBot
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logger = logging.getLogger(__name__)


class AINewsBot:
    """Main AI News Bot application"""
    
    def __init__(self, config_path: str = None):
        # Load configuration
        self.config = load_config(config_path)
        
        # Setup logging
        setup_logging(self.config)
        
        # Initialize components
        db_path = self.config['database']['path']
        self.db = DatabaseManager(db_path)
        
        self.summarizer = ArticleSummarizer(self.config)
        self.tag_generator = TagGenerator(self.config)
        self.slack_bot = AINewsSlackBot(self.config, self.db)
        
        # Initialize scheduler
        timezone = self.config.get('schedule', {}).get('timezone', 'UTC')
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(timezone))
        
        logger.info("AI News Bot initialized successfully")
    
    def collect_news(self, language: str = None, source_name: str = None):
        """Collect news from configured sources"""
        logger.info("Starting news collection...")
        
        # Get sources to collect from
        sources = self.db.get_sources(enabled_only=True)
        
        if language:
            sources = [s for s in sources if s.language == language]
        
        if source_name:
            sources = [s for s in sources if s.name.lower() == source_name.lower()]
        
        if not sources:
            logger.warning("No sources found for collection")
            return
        
        total_new_articles = 0
        
        for source in sources:
            try:
                logger.info(f"Collecting from source: {source.name}")
                
                # Create appropriate collector
                if source.source_type == 'rss':
                    collector = RSSCollector(source, self.config)
                else:
                    logger.warning(f"Unsupported source type: {source.source_type}")
                    continue
                
                # Collect articles with logging
                collection_log, articles = collector.collect_with_logging()
                
                # Save collection log
                self.db.save_collection_log(collection_log)
                
                # Process new articles (check for duplicates first to avoid unnecessary processing)
                new_articles = []
                url_duplicate_count = 0
                title_duplicate_count = 0
                
                for article in articles:
                    # Check if article already exists by URL (early duplicate detection)
                    existing_by_url = self.db.get_article_by_url(article.url)
                    if existing_by_url:
                        url_duplicate_count += 1
                        logger.debug(f"Skipping duplicate URL: {article.title}")
                        continue
                    
                    # Check if article already exists by title (additional duplicate detection)
                    existing_by_title = self.db.get_article_by_title(article.title)
                    if existing_by_title:
                        title_duplicate_count += 1
                        logger.debug(f"Skipping duplicate title: {article.title}")
                        continue
                    
                    # Only process new articles
                    try:
                        # Generate summary
                        try:
                            article.summary = self.summarizer.summarize_article(article)
                        except Exception as e:
                            logger.warning(f"Failed to summarize article: {e}")
                            article.summary = article.content[:200] + "..." if len(article.content) > 200 else article.content
                        
                        # Generate tags
                        try:
                            generated_tags = self.tag_generator.generate_tags(article)
                            article.tags.extend(generated_tags)
                            article.tags = list(set(article.tags))  # Remove duplicates
                        except Exception as e:
                            logger.warning(f"Failed to generate tags: {e}")
                        
                        # Save article
                        self.db.save_article(article)
                        new_articles.append(article)
                        
                        logger.info(f"Saved new article: {article.title}")
                        
                    except Exception as e:
                        logger.error(f"Failed to process article '{article.title}': {e}")
                        continue
                
                total_duplicate_count = url_duplicate_count + title_duplicate_count
                if total_duplicate_count > 0:
                    logger.info(f"Skipped {total_duplicate_count} duplicate articles from {source.name} (URLs: {url_duplicate_count}, Titles: {title_duplicate_count})")
                
                total_new_articles += len(new_articles)
                
                # Update source statistics
                source.last_collected = datetime.now()
                source.collection_count += 1
                if collection_log.status == 'failed':
                    source.error_count += 1
                else:
                    source.error_count = 0  # Reset on success
                
                self.db.save_source(source)
                
                logger.info(f"Collected {len(new_articles)} new articles from {source.name}")
                
            except Exception as e:
                logger.error(f"Failed to collect from {source.name}: {e}")
                continue
        
        logger.info(f"Collection completed. Total new articles: {total_new_articles}")
        
        # Post to Slack if there are new articles
        if total_new_articles > 0:
            recent_articles = self.db.get_articles(limit=5)
            self.slack_bot.post_articles_summary(
                recent_articles, 
                f"🤖 AI News Update - {total_new_articles} New Articles"
            )
    
    def setup_scheduler(self):
        """Setup scheduled jobs"""
        schedule_config = self.config.get('schedule', {})
        
        if not schedule_config.get('enabled', True):
            logger.info("Scheduler disabled in configuration")
            return
        
        jobs = schedule_config.get('jobs', [])
        
        for job_config in jobs:
            try:
                job_name = job_config['name']
                cron_expr = job_config['cron']
                
                if job_config.get('task') == 'cleanup_old_articles':
                    # Cleanup job
                    retention_days = job_config.get('retention_days', 30)
                    self.scheduler.add_job(
                        func=lambda: self.cleanup_old_articles(retention_days),
                        trigger=CronTrigger.from_crontab(cron_expr),
                        id=job_name,
                        name=job_name
                    )
                else:
                    # Collection job
                    sources = job_config.get('sources', [])
                    languages = job_config.get('languages', [])
                    
                    self.scheduler.add_job(
                        func=lambda: self.scheduled_collection(sources, languages),
                        trigger=CronTrigger.from_crontab(cron_expr),
                        id=job_name,
                        name=job_name
                    )
                
                logger.info(f"Scheduled job '{job_name}' with cron: {cron_expr}")
                
            except Exception as e:
                logger.error(f"Failed to schedule job {job_config.get('name', 'unknown')}: {e}")
    
    def scheduled_collection(self, source_types: list, languages: list):
        """Run scheduled collection"""
        logger.info(f"Running scheduled collection for {source_types} in {languages}")
        
        for language in languages:
            self.collect_news(language=language)
    
    def cleanup_old_articles(self, days: int = 30):
        """Clean up old articles"""
        logger.info(f"Cleaning up articles older than {days} days")
        
        try:
            deleted_count = self.db.cleanup_old_articles(days)
            logger.info(f"Cleaned up {deleted_count} old articles")
            
            if deleted_count > 0:
                self.slack_bot.send_alert(
                    f"Cleaned up {deleted_count} articles older than {days} days",
                    level="info"
                )
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            self.slack_bot.send_alert(f"Cleanup failed: {e}", level="error")
    
    def start_scheduler(self):
        """Start the scheduler"""
        logger.info("Starting scheduler...")
        
        try:
            self.setup_scheduler()
            
            # Print scheduled jobs
            jobs = self.scheduler.get_jobs()
            if jobs:
                logger.info("Scheduled jobs:")
                for job in jobs:
                    logger.info(f"  - {job.name}: {job.trigger}")
            else:
                logger.warning("No jobs scheduled")
            
            # Start scheduler
            self.scheduler.start()
            
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            raise
    
    def test_connections(self):
        """Test all connections"""
        logger.info("Testing connections...")
        
        # Test Slack connection
        if self.slack_bot.test_connection():
            logger.info("✅ Slack connection successful")
        else:
            logger.error("❌ Slack connection failed")
            return False
        
        # Test OpenAI connection
        try:
            from src.database.models import Article
            test_article = Article(
                title="Test Article",
                content="This is a test article for AI news summarization.",
                language="english"
            )
            summary = self.summarizer.summarize_article(test_article)
            if summary:
                logger.info("✅ OpenAI connection successful")
            else:
                logger.error("❌ OpenAI connection failed")
                return False
        except Exception as e:
            logger.error(f"❌ OpenAI connection failed: {e}")
            return False
        
        # Test database
        try:
            stats = self.db.get_collection_stats(days=1)
            logger.info("✅ Database connection successful")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
        
        logger.info("All connections successful!")
        return True
    
    def run_interactive_mode(self):
        """Run in interactive mode with scheduler"""
        logger.info("Starting interactive mode for Railway deployment...")
        
        # Start health check server for Railway
        start_health_check()
        
        # Setup and start scheduler in background
        self.setup_scheduler()
        
        # Print scheduled jobs
        jobs = self.scheduler.get_jobs()
        if jobs:
            logger.info("Scheduled jobs:")
            for job in jobs:
                logger.info(f"  - {job.name}: {job.trigger}")
        else:
            logger.warning("No jobs scheduled")
        
        # Start scheduler in background (non-blocking)
        from apscheduler.schedulers.background import BackgroundScheduler
        import pytz
        
        # Replace blocking scheduler with background scheduler
        timezone = self.config.get('schedule', {}).get('timezone', 'UTC')
        bg_scheduler = BackgroundScheduler(timezone=pytz.timezone(timezone))
        
        # Copy jobs from blocking scheduler to background scheduler
        for job in self.scheduler.get_jobs():
            bg_scheduler.add_job(
                func=job.func,
                trigger=job.trigger,
                id=job.id,
                name=job.name
            )
        
        bg_scheduler.start()
        logger.info("Background scheduler started")
        
        # Start Slack socket mode if configured
        if self.slack_bot.socket_client:
            self.slack_bot.start_socket_mode()
        
        # Keep running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interactive mode stopped by user")
            bg_scheduler.shutdown()
            stop_health_check()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI News Slack Bot")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--collect-now", action="store_true", help="Collect news immediately")
    parser.add_argument("--language", help="Collect from specific language sources")
    parser.add_argument("--source", help="Collect from specific source")
    parser.add_argument("--schedule", action="store_true", help="Run with scheduler")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--test", action="store_true", help="Test connections")
    parser.add_argument("--init-config", action="store_true", help="Create example configuration")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Create example config if requested
    if args.init_config:
        create_example_config()
        return
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize bot
        bot = AINewsBot(args.config)
        
        # Test connections
        if args.test:
            success = bot.test_connections()
            sys.exit(0 if success else 1)
        
        # Collect news immediately
        if args.collect_now:
            bot.collect_news(language=args.language, source_name=args.source)
            return
        
        # Run with scheduler
        if args.schedule:
            bot.start_scheduler()
            return
        
        # Run in interactive mode
        if args.interactive:
            bot.run_interactive_mode()
            return
        
        # Default: show help
        parser.print_help()
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
