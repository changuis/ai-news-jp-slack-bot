#!/usr/bin/env python3
"""
Debug script to check configuration loading on Railway
"""

import os
import json
import sys
from pathlib import Path

def debug_config():
    """Debug configuration loading issues"""
    
    print("🔍 AI News JP Bot - Configuration Debug")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables Check:")
    
    config_json = os.getenv('CONFIG_JSON')
    if config_json:
        print(f"✅ CONFIG_JSON exists (length: {len(config_json)} characters)")
        print(f"📝 First 100 characters: {config_json[:100]}...")
        
        # Try to parse JSON
        try:
            config_data = json.loads(config_json)
            print("✅ CONFIG_JSON is valid JSON")
            
            # Check for sources section
            if 'sources' in config_data:
                print("✅ 'sources' section found in config")
                
                if 'japanese' in config_data['sources']:
                    japanese_sources = config_data['sources']['japanese']
                    print("✅ 'japanese' sources found")
                    
                    if 'rss_feeds' in japanese_sources:
                        rss_count = len(japanese_sources['rss_feeds'])
                        print(f"✅ Found {rss_count} RSS feeds")
                        
                        # List first few sources
                        for i, feed in enumerate(japanese_sources['rss_feeds'][:3]):
                            print(f"   {i+1}. {feed.get('name', 'Unknown')} - {feed.get('enabled', False)}")
                    else:
                        print("❌ No 'rss_feeds' in japanese sources")
                    
                    if 'websites' in japanese_sources:
                        website_count = len(japanese_sources['websites'])
                        print(f"✅ Found {website_count} websites")
                else:
                    print("❌ No 'japanese' section in sources")
            else:
                print("❌ No 'sources' section in config")
                print("📋 Available sections:", list(config_data.keys()))
                
        except json.JSONDecodeError as e:
            print(f"❌ CONFIG_JSON is invalid JSON: {e}")
            print(f"📝 Content around error: {config_json[max(0, e.pos-50):e.pos+50]}")
            
    else:
        print("❌ CONFIG_JSON environment variable not found")
    
    # Check other environment variables
    other_vars = [
        'SLACK_BOT_TOKEN',
        'SLACK_APP_TOKEN', 
        'OPENAI_API_KEY',
        'DATABASE_PATH',
        'TZ',
        'PYTHONPATH'
    ]
    
    print("\n📋 Other Environment Variables:")
    for var in other_vars:
        value = os.getenv(var)
        if value:
            if 'TOKEN' in var or 'KEY' in var:
                print(f"✅ {var}: {value[:20]}... (length: {len(value)})")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
    
    # Check if we can import the config module
    print("\n🔧 Testing Configuration Loading:")
    try:
        # Add src directory to path
        sys.path.append(str(Path(__file__).parent / 'src'))
        
        from src.utils.config import load_config
        print("✅ Config module imported successfully")
        
        try:
            config = load_config()
            print("✅ Configuration loaded successfully")
            
            # Check sources in loaded config
            sources = config.get('sources', {})
            if sources:
                japanese_sources = sources.get('japanese', {})
                rss_feeds = japanese_sources.get('rss_feeds', [])
                websites = japanese_sources.get('websites', [])
                
                print(f"✅ Loaded {len(rss_feeds)} RSS feeds and {len(websites)} websites")
                
                # List sources
                print("\n📡 Loaded Sources:")
                for feed in rss_feeds[:5]:  # Show first 5
                    print(f"   • {feed.get('name', 'Unknown')} ({'enabled' if feed.get('enabled') else 'disabled'})")
                    
            else:
                print("❌ No sources found in loaded configuration")
                print("📋 Available config sections:", list(config.keys()))
                
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Failed to import config module: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎯 Debug complete!")

if __name__ == "__main__":
    debug_config()
