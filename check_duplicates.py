#!/usr/bin/env python3
"""
Check for duplicate articles in the AI News database
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.database.models import DatabaseManager

def check_duplicates():
    """Check for duplicate articles"""
    db = DatabaseManager('data/ai_news.db')
    
    print("🔍 AI News Duplicate Detection Report")
    print("=" * 50)
    
    with db.get_connection() as conn:
        # Check for exact URL duplicates (should be 0 due to UNIQUE constraint)
        url_duplicates = conn.execute("""
            SELECT url, COUNT(*) as count 
            FROM articles 
            GROUP BY url 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
        """).fetchall()
        
        print(f"📊 Exact URL duplicates: {len(url_duplicates)}")
        if url_duplicates:
            for url, count in url_duplicates[:5]:
                print(f"  {count}x: {url}")
        
        # Check for exact title duplicates
        title_duplicates = conn.execute("""
            SELECT title, COUNT(*) as count, GROUP_CONCAT(source, ', ') as sources
            FROM articles 
            GROUP BY title 
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """).fetchall()
        
        print(f"\n📰 Exact title duplicates: {len(title_duplicates)}")
        if title_duplicates:
            for title, count, sources in title_duplicates:
                print(f"  {count}x: {title[:70]}...")
                print(f"      Sources: {sources}")
        else:
            print("  No exact title duplicates found ✅")
        
        # Check collection efficiency (articles skipped vs processed)
        recent_collections = conn.execute("""
            SELECT 
                s.name,
                cl.collection_date,
                cl.articles_found,
                cl.articles_processed,
                cl.articles_new,
                ROUND((cl.articles_found - cl.articles_processed) * 100.0 / cl.articles_found, 1) as skip_rate
            FROM collection_logs cl
            JOIN sources s ON cl.source_id = s.id
            WHERE cl.collection_date >= datetime('now', '-1 day')
            AND cl.articles_found > 0
            ORDER BY cl.collection_date DESC
            LIMIT 10
        """).fetchall()
        
        print(f"\n⚡ Recent Collection Efficiency:")
        print("Source | Date | Found | Processed | New | Skip Rate")
        print("-" * 60)
        for name, date, found, processed, new, skip_rate in recent_collections:
            print(f"{name[:15]:<15} | {date[11:16]} | {found:5} | {processed:9} | {new:3} | {skip_rate:7}%")
        
        # Overall statistics
        total_articles = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        sources_count = conn.execute("SELECT COUNT(*) FROM sources WHERE enabled = 1").fetchone()[0]
        
        print(f"\n📈 Database Statistics:")
        print(f"  Total articles: {total_articles}")
        print(f"  Active sources: {sources_count}")
        
        # Recent activity
        recent_count = conn.execute("""
            SELECT COUNT(*) FROM articles 
            WHERE collected_date >= datetime('now', '-1 day')
        """).fetchone()[0]
        
        print(f"  Articles collected (24h): {recent_count}")

if __name__ == "__main__":
    check_duplicates()
