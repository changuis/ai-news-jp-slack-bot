# AI News JP Slack Bot - Quick Start Guide - 日本のAIニュース配信ボット

## 🚀 Ready to Use!

Your Japanese AI News Slack Bot has been successfully created and configured. Here's how to get it running quickly.

## 📋 What's Been Set Up

✅ **Project Duplicated**: Complete copy of original bot with Japanese focus  
✅ **Configuration Updated**: Japanese sources only, #times-mayo channel  
✅ **Documentation Updated**: All docs reflect Japanese focus  
✅ **Service Scripts Updated**: macOS service ready for Japanese bot  
✅ **Database Separated**: Uses `ai_news_jp.db` (won't conflict with original)  

## 🎯 Key Differences from Original Bot

| Aspect | Original Bot | Japanese Bot |
|--------|-------------|--------------|
| **Sources** | English + Japanese | Japanese Only |
| **Channel** | #ai-news | #times-mayo |
| **Database** | ai_news.db | ai_news_jp.db |
| **Service** | ai-news-slack-bot | ai-news-jp-slack-bot |
| **Summaries** | English/Japanese | Japanese Only |
| **Keywords** | Mixed | Japanese AI terms |

## 🔧 Next Steps to Get Running

### 1. Configure Your Bot

```bash
cd ai-news-jp-slack-bot
cp config/config.example.yaml config/config.yaml
```

Edit `config/config.yaml` and update:
- `slack.bot_token`: Your Japanese workspace bot token
- `slack.app_token`: Your Japanese workspace app token  
- `openai.api_key`: Your OpenAI API key
- `slack.channels.main`: "#times-mayo" (already set)

### 2. Create Slack App for Japanese Workspace

1. Go to https://api.slack.com/apps
2. Create new app for your Japanese workspace
3. Add required scopes: `chat:write`, `commands`, `channels:read`
4. Enable Socket Mode with `connections:write`
5. Create slash command `/ai-news`
6. Install to workspace and copy tokens

### 3. Test the Setup

```bash
# Test all connections
python main.py --test

# Test Japanese news collection
python main.py --collect-now --debug
```

### 4. Run the Bot

```bash
# Interactive mode (for slash commands)
python main.py --interactive

# Or install as macOS service
./setup_macos_service.sh install
```

## 📰 Japanese Sources Configured

### News Sites (8 sources):
- ITmedia AI+
- ASCII.jp AI  
- 日経xTECH AI
- Impress Watch AI
- マイナビニュース AI
- CNET Japan AI
- ZDNet Japan AI
- 週刊アスキー AI

### Companies & Research (4 sources):
- Preferred Networks
- RIKEN AIP (理化学研究所)
- リンナ株式会社
- 東京大学 AI研究

### Social Media (8 accounts):
- @PreferredNet, @rinna_inc, @RIKEN_AIP
- @UTokyo_News, @SoftBank_News, @NTTcom_news
- @Fujitsu_Global, @NEC_corp

## 🎌 Japanese Keywords Configured

**Technology**: 人工知能, 機械学習, 深層学習, 生成AI, ChatGPT, LLM, 自然言語処理, 画像認識, 音声認識

**Companies**: プリファード, リンナ, ソフトバンク, NTT, 富士通, NEC, パナソニック, トヨタ, ソニー

**Applications**: 自動運転, 医療AI, ロボット, IoT, スマートシティ, フィンテック, EdTech

## ⏰ Collection Schedule

- **Morning Collection**: 9 AM weekdays (Japanese business hours)
- **Afternoon Check**: 3 PM weekdays (additional RSS check)
- **Weekly Cleanup**: Sunday 2 AM JST

## 🔍 Monitoring Commands

```bash
# Check for duplicates
python check_duplicates.py

# View collected articles
python view_database.py

# Search articles
python view_database.py search "生成AI"

# Service status (if installed)
./setup_macos_service.sh status
./setup_macos_service.sh logs
```

## 📱 Slack Commands Available

Once running in interactive mode:

- `/ai-news latest` - Show latest Japanese AI articles
- `/ai-news search 機械学習` - Search for articles about machine learning
- `/ai-news sources` - List Japanese news sources
- `/ai-news tags` - Show available Japanese tags
- `/ai-news stats` - Collection statistics

## 🆘 Need Help?

- **Setup Issues**: Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Slack Problems**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Service Management**: See [MACOS_SERVICE_GUIDE.md](MACOS_SERVICE_GUIDE.md)
- **Technical Details**: See [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)

## 🎉 You're Ready!

Your Japanese AI News Bot is configured and ready to collect the latest AI news from Japan's top sources and post them to your #times-mayo channel.

**日本のAIエコシステムの最新情報をお楽しみください！** 🇯🇵🤖

---

**Pro Tip**: You can run both the original English bot and this Japanese bot simultaneously since they use different databases, services, and channels!
