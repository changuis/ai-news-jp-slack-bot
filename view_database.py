#!/usr/bin/env python3
"""
Database viewer for AI News Slack Bot
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.database.models import DatabaseManager
from src.utils.config import load_config
from datetime import datetime
import json

def view_database():
    """View database contents"""
    try:
        # Load configuration
        config = load_config()
        db_path = config.get('database', {}).get('path', 'data/ai_news.db')
        
        # Initialize database
        db = DatabaseManager(db_path)
        
        print("🤖 AI News Slack Bot - Database Viewer")
        print("=" * 50)
        
        # Show articles
        print("\n📰 ARTICLES:")
        articles = db.get_articles(limit=50)
        
        if not articles:
            print("No articles found in database.")
        else:
            print(f"Found {len(articles)} articles:\n")
            
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article.title}")
                print(f"   Source: {article.source}")
                print(f"   Language: {article.language}")
                print(f"   Published: {article.published_date.strftime('%Y-%m-%d %H:%M') if article.published_date else 'Unknown'}")
                print(f"   URL: {article.url}")
                if article.summary:
                    print(f"   Summary: {article.summary[:100]}...")
                if article.tags:
                    print(f"   Tags: {', '.join(article.tags[:5])}")
                print()
        
        # Show sources
        print("\n📡 NEWS SOURCES:")
        sources = db.get_sources(enabled_only=False)
        
        if sources:
            for source in sources:
                status = "✅ Enabled" if source.enabled else "❌ Disabled"
                print(f"• {source.name} ({source.source_type}) - {source.language} - {status}")
                print(f"  URL: {source.url}")
                if source.last_collected:
                    print(f"  Last collected: {source.last_collected.strftime('%Y-%m-%d %H:%M')}")
                print(f"  Collection count: {source.collection_count}, Errors: {source.error_count}")
                print()
        
        # Show tags
        print("\n🏷️ TAGS:")
        tags = db.get_tags()
        
        if tags:
            for tag in tags:
                print(f"• {tag.name} ({tag.category}) - Used {tag.usage_count} times")
        
        # Show statistics
        print("\n📊 STATISTICS:")
        stats = db.get_collection_stats(days=7)
        print(f"• Total articles (last 7 days): {stats['total_articles']}")
        print(f"• Success rate: {stats['success_rate']}%")
        
        if stats['languages']:
            print("• By language:")
            for lang, count in stats['languages'].items():
                print(f"  - {lang}: {count}")
        
        if stats['top_sources']:
            print("• Top sources:")
            for source, count in list(stats['top_sources'].items())[:5]:
                print(f"  - {source}: {count}")
        
    except Exception as e:
        print(f"Error viewing database: {e}")

def view_article_details(article_id: int):
    """View detailed information about a specific article"""
    try:
        config = load_config()
        db_path = config.get('database', {}).get('path', 'data/ai_news.db')
        db = DatabaseManager(db_path)
        
        # Get article by ID (we'll need to modify the database model for this)
        articles = db.get_articles(limit=1000)  # Get all articles
        
        if article_id <= len(articles):
            article = articles[article_id - 1]
            
            print(f"\n📰 ARTICLE DETAILS #{article_id}")
            print("=" * 50)
            print(f"Title: {article.title}")
            print(f"Source: {article.source}")
            print(f"Language: {article.language}")
            print(f"Author: {article.author or 'Unknown'}")
            print(f"Published: {article.published_date.strftime('%Y-%m-%d %H:%M:%S') if article.published_date else 'Unknown'}")
            print(f"Collected: {article.collected_date.strftime('%Y-%m-%d %H:%M:%S') if article.collected_date else 'Unknown'}")
            print(f"URL: {article.url}")
            print(f"\nSummary:\n{article.summary}")
            print(f"\nTags: {', '.join(article.tags) if article.tags else 'None'}")
            print(f"\nContent:\n{article.content[:500]}{'...' if len(article.content) > 500 else ''}")
            
            if article.metadata:
                print(f"\nMetadata:\n{json.dumps(article.metadata, indent=2)}")
        else:
            print(f"Article #{article_id} not found. Available articles: 1-{len(articles)}")
            
    except Exception as e:
        print(f"Error viewing article details: {e}")

def search_articles(query: str):
    """Search articles by keyword"""
    try:
        config = load_config()
        db_path = config.get('database', {}).get('path', 'data/ai_news.db')
        db = DatabaseManager(db_path)
        
        articles = db.search_articles(query, limit=20)
        
        print(f"\n🔍 SEARCH RESULTS for '{query}':")
        print("=" * 50)
        
        if not articles:
            print("No articles found matching your search.")
        else:
            print(f"Found {len(articles)} articles:\n")
            
            for i, article in enumerate(articles, 1):
                print(f"{i}. {article.title}")
                print(f"   Source: {article.source} | Language: {article.language}")
                print(f"   Published: {article.published_date.strftime('%Y-%m-%d') if article.published_date else 'Unknown'}")
                if article.summary:
                    print(f"   Summary: {article.summary[:150]}...")
                print()
                
    except Exception as e:
        print(f"Error searching articles: {e}")

def main():
    """Main function with interactive menu"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "search" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            search_articles(query)
        elif command == "article" and len(sys.argv) > 2:
            try:
                article_id = int(sys.argv[2])
                view_article_details(article_id)
            except ValueError:
                print("Please provide a valid article number.")
        else:
            print("Usage:")
            print("  python3 view_database.py                    # View all data")
            print("  python3 view_database.py search <keyword>   # Search articles")
            print("  python3 view_database.py article <number>   # View specific article")
    else:
        view_database()

if __name__ == "__main__":
    main()
