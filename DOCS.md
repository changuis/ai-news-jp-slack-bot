# AI News JP Slack Bot - Documentation Index - 日本のAIニュース配信ボット

This document provides an overview of all available documentation for the AI News JP Slack Bot (Japanese AI News Bot).

## 📚 Documentation Structure

| Document | Purpose | Content |
|----------|---------|---------|
| **[README.md](README.md)** | Main project overview | Features, quick start, architecture, and basic usage (Japanese focus) |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Complete setup instructions | Step-by-step configuration, Slack app creation, API keys |
| **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** | Problem solving guide | Common issues, Slack token problems, service management |
| **[MACOS_SERVICE_GUIDE.md](MACOS_SERVICE_GUIDE.md)** | macOS service management | Background service setup, monitoring, and control |
| **[IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)** | Technical details | Duplicate detection, performance optimizations, database schema |

## 🇯🇵 Japanese AI News Bot Specifics

### Key Differences from Original Bot:
- **Language Focus**: Japanese AI news sources only
- **Channel**: Posts to `#times-mayo`
- **Sources**: 8+ Japanese tech news sites + Japanese AI companies
- **Summarization**: All summaries in Japanese
- **Keywords**: Japanese AI terminology and company names

### Japanese Sources Covered:
- **News Sites**: ITmedia AI+, ASCII.jp, 日経xTECH, Impress Watch, マイナビニュース, CNET Japan, ZDNet Japan
- **Companies**: Preferred Networks, リンナ株式会社, RIKEN AIP
- **Universities**: 東京大学 AI研究
- **Social**: Japanese AI company Twitter accounts

## 🚀 Quick Navigation

### Getting Started
1. **New Users**: Start with [README.md](README.md) for overview
2. **Setup**: Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete installation
3. **macOS Users**: Use [MACOS_SERVICE_GUIDE.md](MACOS_SERVICE_GUIDE.md) for background service

### Having Issues?
1. **Common Problems**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. **Slack Issues**: See [Slack Token and Scope Issues](TROUBLESHOOTING.md#slack-token-and-scope-issues)
3. **Service Problems**: See [Service Management Issues](TROUBLESHOOTING.md#service-management-issues)

### Technical Details
1. **Implementation**: Read [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)
2. **Performance**: See [Performance Optimizations](IMPLEMENTATION_NOTES.md#performance-optimizations)
3. **Database**: See [Database Schema](IMPLEMENTATION_NOTES.md#database-schema)

## 📋 Japanese Configuration Highlights

### Slack Configuration:
```yaml
slack:
  channels:
    main: "#times-mayo"  # Your specified channel
    alerts: "#times-mayo"  # Same channel for alerts
```

### Japanese Sources:
```yaml
sources:
  japanese:
    rss_feeds:
      - name: "ITmedia AI+"
      - name: "ASCII.jp AI"
      - name: "日経xTECH AI"
      - name: "Impress Watch AI"
      # ... and more
```

### Japanese Keywords:
```yaml
tagging:
  categories:
    technology:
      keywords: ["人工知能", "機械学習", "深層学習", "生成AI", "ChatGPT"]
    companies:
      keywords: ["プリファード", "リンナ", "ソフトバンク", "NTT"]
```

## 🔧 Utility Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `check_duplicates.py` | Monitor duplicate detection | `python check_duplicates.py` |
| `view_database.py` | View database contents | `python view_database.py` |
| `setup_macos_service.sh` | macOS service management | `./setup_macos_service.sh [command]` |

## 📊 Quick Commands Reference

```bash
# Setup and Testing
python main.py --test                    # Test all connections
python main.py --init-config            # Create example config

# Collection (Japanese only)
python main.py --collect-now             # Collect Japanese AI news immediately
python main.py --collect-now --debug    # Collect with debug logging
python main.py --language japanese      # Collect Japanese (default)

# Running
python main.py --interactive             # Interactive mode with Slack
python main.py --schedule               # Run with scheduler

# Monitoring
python check_duplicates.py              # Check for duplicates
python view_database.py                 # View database contents
python view_database.py search "AI"     # Search articles

# Service Management (macOS)
./setup_macos_service.sh install        # Install Japanese AI news service
./setup_macos_service.sh status         # Check status
./setup_macos_service.sh logs           # View logs
```

## 🎌 Japanese-Specific Features

### Language Processing:
- **Encoding**: UTF-8 optimized for Japanese text
- **Text Length**: Shorter minimum length (50 chars) for Japanese
- **Keywords**: Comprehensive Japanese AI terminology
- **Tokenization**: MeCab support for Japanese morphological analysis

### Content Filtering:
- **Required Keywords**: Japanese AI terms (人工知能, 機械学習, etc.)
- **Company Focus**: Japanese AI companies and research institutions
- **Cultural Context**: Japanese business and research environment

### Scheduling:
- **Timezone**: Asia/Tokyo
- **Business Hours**: 9 AM and 3 PM weekdays (Japanese business hours)
- **Weekend Cleanup**: Sunday 2 AM JST

## 🔄 Migration from Original Bot

If migrating from the original `ai-news-slack-bot`:

1. **Different Database**: Uses `ai_news_jp.db` (separate from original)
2. **Different Service**: `com.user.ai-news-jp-slack-bot` (can run alongside original)
3. **Different Channel**: Posts to `#times-mayo` instead of `#ai-news`
4. **Language Focus**: Only Japanese sources and summaries

## 📈 Expected Performance

### Collection Efficiency:
- **Sources**: 8-12 Japanese AI news sources
- **Articles per Day**: 10-30 Japanese AI articles
- **Processing Time**: 1-2 minutes per collection
- **Duplicate Rate**: 70-80% (typical for established sources)

### Database Growth:
- **Daily Articles**: 5-15 new articles
- **Monthly Growth**: ~150-450 articles
- **Storage**: ~10-50MB per month

---

**Need help?** Start with the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide for the most common issues and solutions.

**日本のAIエコシステムの最新情報をお楽しみください！** 🇯🇵🤖
