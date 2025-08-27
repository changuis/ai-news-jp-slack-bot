# AI News JP Slack Bot 🇯🇵🤖

A comprehensive Japanese AI News Slack Bot that automatically collects, summarizes, and shares AI-related news from Japanese sources.

## 🚀 Quick Start

**For complete setup instructions, troubleshooting, and all features, see:**
**[📖 COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)**

## ⚡ Railway Deployment (Recommended)

1. **Deploy to Railway**: Connect this repo to [railway.app](https://railway.app)
2. **Set CONFIG_JSON**: Add the complete configuration JSON in Railway Variables
3. **Deploy**: Bot will automatically start collecting Japanese AI news
4. **Test**: Use `/ai-news sources` in Slack

## 🎯 Features

- **12 Japanese AI News Sources** (ITmedia, ASCII, 日経xTECH, etc.)
- **Automated Collection** at 9 AM and 3 PM JST
- **AI Summarization** in Japanese using OpenAI GPT
- **Slack Integration** with slash commands
- **Duplicate Detection** and smart filtering
- **Railway Cloud Deployment** ready

## 📱 Slack Commands

- `/ai-news sources` - List all news sources
- `/ai-news latest [count]` - Show recent articles
- `/ai-news search <keyword>` - Search articles
- `/ai-news tags` - List available tags
- `/ai-news stats` - Collection statistics

## 🔧 Quick Troubleshooting

**"No sources configured"** → Check CONFIG_JSON variable in Railway
**Bot not responding** → Verify Slack scopes include `chat:write`
**Deployment fails** → Check Railway logs for specific errors

## 📚 Documentation

- **[COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)** - Full setup, configuration, and troubleshooting
- **[config.json](config.json)** - Example configuration file
- **[debug_config.py](debug_config.py)** - Configuration debugging tool
- **[view_database.py](view_database.py)** - Database inspection tool

## 🏗️ Architecture

```
ai-news-jp-slack-bot/
├── main.py                 # Main application
├── health_check.py         # Railway health check
├── src/
│   ├── collectors/         # RSS and web scraping
│   ├── processors/         # AI summarization & tagging
│   ├── database/           # SQLite database operations
│   ├── slack/              # Slack bot integration
│   └── utils/              # Configuration and utilities
├── config/                 # Configuration files
└── COMPLETE_GUIDE.md       # Full documentation
```

## 🇯🇵 Japanese AI Sources

**RSS Feeds (8):**
- ITmedia AI+, ASCII.jp AI, 日経xTECH AI, Impress Watch AI
- マイナビニュース AI, CNET Japan AI, ZDNet Japan AI, 週刊アスキー AI

**Websites (4):**
- Preferred Networks Blog, RIKEN AIP, リンナ株式会社, 東京大学 AI研究

## 🚂 Railway Ready

This bot is optimized for Railway deployment with:
- ✅ Health check endpoint
- ✅ Environment variable configuration
- ✅ Automatic source population
- ✅ Background scheduling
- ✅ Persistent SQLite database

---

**For detailed setup instructions, see [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)**

**Your Japanese AI News Bot is ready to keep your team updated with the latest AI developments from Japan!** 🇯🇵🤖🚂
