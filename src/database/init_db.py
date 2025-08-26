#!/usr/bin/env python3
"""
Database initialization script for AI News Slack Bot
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import DatabaseManager, Source, Tag
from utils.config import load_config


def init_database():
    """Initialize the database with tables and default data"""
    print("Initializing AI News Slack Bot database...")
    
    # Load configuration
    config = load_config()
    db_path = config.get('database', {}).get('path', 'data/ai_news.db')
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Initialize database
    db = DatabaseManager(db_path)
    print(f"Database initialized at: {db_path}")
    
    # Add default sources from config
    sources_config = config.get('sources', {})
    
    # Add English RSS sources
    english_rss = sources_config.get('english', {}).get('rss_feeds', [])
    for source_config in english_rss:
        if source_config.get('enabled', True):
            source = Source(
                name=source_config['name'],
                url=source_config['url'],
                source_type='rss',
                language='english',
                enabled=True,
                tags=source_config.get('tags', [])
            )
            db.save_source(source)
            print(f"Added English RSS source: {source.name}")
    
    # Add English website sources
    english_websites = sources_config.get('english', {}).get('websites', [])
    for source_config in english_websites:
        if source_config.get('enabled', True):
            source = Source(
                name=source_config['name'],
                url=source_config['url'],
                source_type='website',
                language='english',
                enabled=True,
                tags=source_config.get('tags', []),
                config={'selector': source_config.get('selector', '')}
            )
            db.save_source(source)
            print(f"Added English website source: {source.name}")
    
    # Add Japanese RSS sources
    japanese_rss = sources_config.get('japanese', {}).get('rss_feeds', [])
    for source_config in japanese_rss:
        if source_config.get('enabled', True):
            source = Source(
                name=source_config['name'],
                url=source_config['url'],
                source_type='rss',
                language='japanese',
                enabled=True,
                tags=source_config.get('tags', []),
                config={'filter_keywords': source_config.get('filter_keywords', [])}
            )
            db.save_source(source)
            print(f"Added Japanese RSS source: {source.name}")
    
    # Add Japanese website sources
    japanese_websites = sources_config.get('japanese', {}).get('websites', [])
    for source_config in japanese_websites:
        if source_config.get('enabled', True):
            source = Source(
                name=source_config['name'],
                url=source_config['url'],
                source_type='website',
                language='japanese',
                enabled=True,
                tags=source_config.get('tags', []),
                config={'selector': source_config.get('selector', '')}
            )
            db.save_source(source)
            print(f"Added Japanese website source: {source.name}")
    
    # Add default tags from config
    tagging_config = config.get('tagging', {}).get('categories', {})
    for category_name, category_config in tagging_config.items():
        tag = Tag(
            name=category_name,
            category='auto',
            description=f"Auto-generated tag for {category_name}",
            color=get_category_color(category_name)
        )
        db.save_tag(tag)
        print(f"Added tag: {tag.name}")
    
    print("Database initialization completed successfully!")
    
    # Print statistics
    sources = db.get_sources(enabled_only=False)
    tags = db.get_tags()
    print(f"\nDatabase summary:")
    print(f"- Sources: {len(sources)}")
    print(f"- Tags: {len(tags)}")
    print(f"- Database file: {db_path}")


def get_category_color(category: str) -> str:
    """Get color for category"""
    colors = {
        'technology': '#007bff',
        'business': '#28a745',
        'research': '#6f42c1',
        'products': '#fd7e14',
        'regulation': '#dc3545'
    }
    return colors.get(category, '#6c757d')


if __name__ == "__main__":
    init_database()
