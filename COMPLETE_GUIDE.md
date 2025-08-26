# AI News JP Slack Bot - Complete Guide 🇯🇵🤖

A comprehensive Japanese AI News Slack Bot that collects, summarizes, and shares AI-related news from Japanese sources.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Railway Deployment](#railway-deployment)
3. [Configuration](#configuration)
4. [Troubleshooting](#troubleshooting)
5. [Features](#features)
6. [Development](#development)
7. [Maintenance](#maintenance)

---

## 🚀 Quick Start

### Prerequisites
- Slack workspace with bot permissions
- OpenAI API key
- Railway account (for deployment)

### 1. Slack App Setup
1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name: "AI News JP Bot", select your workspace

#### Required Scopes
Add these Bot Token Scopes:
- `chat:write` - Send messages (REQUIRED)
- `chat:write.public` - Send to channels bot isn't in
- `channels:read` - View channel info
- `commands` - Slash commands
- `app_mentions:read` - Handle mentions

#### Slash Commands
1. Go to "Slash Commands" → "Create New Command"
2. Command: `/ai-news`
3. Request URL: `https://example.com` (not used with Socket Mode)
4. Description: "Japanese AI News Bot commands"

#### Socket Mode (Required)
1. Go to "Socket Mode" → Enable
2. Generate App-Level Token with `connections:write` scope
3. Copy both Bot Token (`xoxb-...`) and App Token (`xapp-...`)

### 2. OpenAI Setup
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create new secret key
3. Copy the key (`sk-...`)

---

## 🚂 Railway Deployment

### Step 1: Deploy to Railway
1. **Fork/Clone this repository**
2. **Connect to Railway:**
   - Go to [railway.app](https://railway.app)
   - "New Project" → "Deploy from GitHub repo"
   - Select your forked repository

### Step 2: Configure Environment Variables
In Railway Dashboard → Your Project → Variables tab, add:

**CONFIG_JSON** (most important):
```json
{"SLACK_BOT_TOKEN":"xoxb-your-bot-token","OPENAI_API_KEY":"sk-your-openai-key","slack":{"bot_token":"xoxb-your-bot-token","app_token":"xapp-your-app-token","signing_secret":"your-signing-secret","channels":{"main":"#times-mayo","alerts":"#times-mayo"},"posting":{"frequency":"hourly","max_articles_per_post":5,"summary_length":"medium"}},"openai":{"api_key":"sk-your-openai-key","model":"gpt-4","max_tokens":500,"temperature":0.3,"prompts":{"japanese_summary":"以下のAI関連記事を2-3文で要約してください。\n主要な技術的発展とその影響に焦点を当て、日本語で簡潔にまとめてください：\n\n{article_text}\n","japanese_tagging":"以下の記事に適切な日本語タグを付けてください。\n技術分野、企業名、研究機関、応用分野などを含めてください：\n\n{article_text}\n"}},"sources":{"japanese":{"rss_feeds":[{"name":"ITmedia AI+","url":"https://www.itmedia.co.jp/aiplus/rss/news.xml","enabled":true,"tags":["tech","japanese","ai","itmedia"]},{"name":"ASCII.jp AI","url":"https://ascii.jp/rss.xml","enabled":true,"tags":["tech","japanese","ai","ascii"],"filter_keywords":["AI","人工知能","機械学習","深層学習","生成AI"]},{"name":"日経xTECH AI","url":"https://xtech.nikkei.com/rss/index.rdf","enabled":true,"tags":["business","nikkei","ai","japanese"],"filter_keywords":["AI","人工知能","機械学習","DX","デジタル変革"]},{"name":"Impress Watch AI","url":"https://www.watch.impress.co.jp/data/rss/1.0/ipw/feed.rdf","enabled":true,"tags":["tech","impress","ai","japanese"],"filter_keywords":["AI","人工知能","機械学習","深層学習","ChatGPT","生成AI"]},{"name":"マイナビニュース AI","url":"https://news.mynavi.jp/rss/techplus","enabled":true,"tags":["tech","mynavi","ai","japanese"],"filter_keywords":["AI","人工知能","機械学習","深層学習"]},{"name":"CNET Japan AI","url":"https://japan.cnet.com/rss/index.rdf","enabled":true,"tags":["tech","cnet","ai","japanese"],"filter_keywords":["AI","人工知能","機械学習","ChatGPT","生成AI"]},{"name":"ZDNet Japan AI","url":"https://japan.zdnet.com/rss/index.rdf","enabled":true,"tags":["business","zdnet","ai","japanese"],"filter_keywords":["AI","人工知能","機械学習","DX"]},{"name":"週刊アスキー AI","url":"https://weekly.ascii.jp/rss.xml","enabled":true,"tags":["tech","ascii","ai","japanese"],"filter_keywords":["AI","人工知能","機械学習","深層学習","生成AI"]}],"websites":[{"name":"Preferred Networks Blog","url":"https://preferred.jp/ja/news/","selector":".news-item","enabled":true,"tags":["preferred","research","ai","japanese","company"]},{"name":"RIKEN AIP","url":"https://aip.riken.jp/news/","selector":".news-list-item","enabled":true,"tags":["riken","research","academic","ai","japanese"]},{"name":"リンナ株式会社","url":"https://rinna.co.jp/news/","selector":".news-item","enabled":true,"tags":["rinna","company","ai","japanese","nlp"]},{"name":"東京大学 AI研究","url":"https://www.u-tokyo.ac.jp/focus/ja/topics/","selector":".topics-item","enabled":true,"tags":["university","tokyo","research","academic","ai","japanese"],"filter_keywords":["AI","人工知能","機械学習","データサイエンス"]}],"social":{"twitter_accounts":["@PreferredNet","@rinna_inc","@RIKEN_AIP","@UTokyo_News","@SoftBank_News","@NTTcom_news","@Fujitsu_Global","@NEC_corp"]}}},"tagging":{"auto_tag":true,"confidence_threshold":0.7,"categories":{"technology":{"keywords":["人工知能","機械学習","深層学習","ニューラルネットワーク","トランスフォーマー","大規模言語モデル","LLM","生成AI","ChatGPT","GPT","自然言語処理","画像認識","音声認識"],"weight":1.0},"business":{"keywords":["スタートアップ","資金調達","投資","IPO","買収","企業","ビジネス","DX","デジタル変革","デジタル化"],"weight":0.8},"research":{"keywords":["研究","論文","大学","学術","理化学研究所","産総研","東大","京大","研究開発","R&D"],"weight":0.9},"companies":{"keywords":["プリファード","リンナ","ソフトバンク","NTT","富士通","NEC","パナソニック","トヨタ","ホンダ","ソニー"],"weight":0.8},"applications":{"keywords":["自動運転","医療AI","画像認識","音声認識","自然言語処理","ロボット","IoT","スマートシティ","フィンテック","EdTech"],"weight":0.7},"regulation":{"keywords":["規制","政策","政府","法律","倫理","ガイドライン","AI倫理","プライバシー","データ保護"],"weight":0.7}}},"database":{"type":"sqlite","path":"data/ai_news_jp.db","backup":{"enabled":true,"frequency":"daily","retention_days":30}},"schedule":{"enabled":true,"timezone":"Asia/Tokyo","jobs":[{"name":"morning_jp_collection","cron":"0 9 * * 1-5","sources":["rss_feeds","websites","social"],"languages":["japanese"]},{"name":"afternoon_rss_check","cron":"0 15 * * 1-5","sources":["rss_feeds"],"languages":["japanese"]},{"name":"weekly_cleanup","cron":"0 2 * * 0","task":"cleanup_old_articles","retention_days":30}]},"logging":{"level":"INFO","format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s","files":{"main":"logs/ai_news_jp_bot.log","errors":"logs/errors.log","collection":"logs/collection.log"},"rotation":{"max_size":"10MB","backup_count":5}},"performance":{"max_concurrent_requests":10,"request_timeout":30,"retry_attempts":3,"retry_delay":5,"rate_limiting":{"requests_per_minute":60,"burst_limit":10}},"filtering":{"min_article_length":50,"max_article_age_days":7,"duplicate_detection":{"enabled":true,"similarity_threshold":0.8},"blocked_domains":["spam-site.com","low-quality-news.com"],"required_keywords":["AI","人工知能","機械学習","深層学習","生成AI","ChatGPT","大規模言語モデル","LLM"]},"language":{"default":"japanese","supported":["japanese"],"text_processing":{"japanese":{"encoding":"utf-8","tokenizer":"mecab","stop_words":true}}},"notifications":{"email":{"enabled":false,"smtp_server":"smtp.gmail.com","smtp_port":587,"username":"your-email@gmail.com","password":"your-app-password","recipients":["admin@yourcompany.com"]},"slack_alerts":{"enabled":true,"error_threshold":5,"daily_summary":true,"language":"japanese"}}}
```

**DATABASE_PATH**: `/app/data/ai_news_jp.db`

**TZ**: `Asia/Tokyo`

### Step 3: Deploy and Test
1. Click "Deploy" in Railway
2. Wait for deployment to complete
3. Check logs for successful startup
4. Test `/ai-news sources` in Slack

---

## ⚙️ Configuration

### Japanese News Sources (12 total)

#### RSS Feeds (8):
- **ITmedia AI+** - Tech news and AI developments
- **ASCII.jp AI** - Technology and AI articles
- **日経xTECH AI** - Business and digital transformation
- **Impress Watch AI** - Tech industry news
- **マイナビニュース AI** - Technology and development news
- **CNET Japan AI** - Tech and AI coverage
- **ZDNet Japan AI** - Business technology news
- **週刊アスキー AI** - Weekly tech and AI updates

#### Websites (4):
- **Preferred Networks Blog** - AI research company
- **RIKEN AIP** - Research institute
- **リンナ株式会社** - AI company news
- **東京大学 AI研究** - University research

### Schedule
- **Morning Collection**: 9 AM JST (Monday-Friday)
- **Afternoon Check**: 3 PM JST (Monday-Friday)
- **Weekly Cleanup**: 2 AM JST (Sunday)

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "No sources configured"
**Cause**: CONFIG_JSON variable missing or corrupted
**Solution**: 
- Check Railway Variables tab for CONFIG_JSON
- Ensure it's the complete JSON (4000+ characters)
- Redeploy after fixing

#### 2. Bot not responding to commands
**Cause**: Missing Slack scopes or Socket Mode issues
**Solution**:
- Verify `chat:write` scope is added
- Reinstall Slack app to regenerate token
- Check app_token is set correctly

#### 3. Railway deployment fails
**Cause**: Missing environment variables or configuration
**Solution**:
- Ensure CONFIG_JSON is properly set
- Check Railway logs for specific errors
- Verify all required files are present

### Debug Commands

**Check configuration loading:**
```bash
python debug_config.py
```

**View database contents:**
```bash
python view_database.py
```

**Check for duplicates:**
```bash
python check_duplicates.py
```

### Log Monitoring

**Railway logs to watch for:**
```
✅ Configuration loaded from CONFIG_JSON environment variable
✅ Populating database with sources from configuration...
✅ Added RSS source: ITmedia AI+
✅ Database now contains 12 sources
✅ AI News Bot initialized successfully
✅ Health check server started on port 8080
✅ Background scheduler started
✅ Slack connection successful
```

---

## 🎯 Features

### Slack Commands
- `/ai-news sources` - List all configured news sources
- `/ai-news latest [count]` - Show recent articles (default: 5)
- `/ai-news search <keyword>` - Search articles by keyword
- `/ai-news tags` - List available tags
- `/ai-news stats` - Show collection statistics

### Automated Features
- **Duplicate Detection** - URL and title-based deduplication
- **AI Summarization** - Japanese summaries using OpenAI GPT
- **Smart Tagging** - Automatic categorization
- **Scheduled Collection** - Automatic news gathering
- **Slack Integration** - Real-time notifications

### Content Filtering
- **Keyword Filtering** - AI-related content only
- **Length Filtering** - Minimum article length
- **Age Filtering** - Recent articles only
- **Domain Blocking** - Spam prevention

---

## 💻 Development

### Local Setup
```bash
# Clone repository
git clone <repository-url>
cd ai-news-jp-slack-bot

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your API keys

# Initialize database
python src/database/init_db.py

# Run locally
python main.py --interactive
```

### Testing
```bash
# Test connections
python main.py --test

# Collect news immediately
python main.py --collect-now

# Run with debug logging
python main.py --collect-now --debug
```

### File Structure
```
ai-news-jp-slack-bot/
├── main.py                 # Main application
├── health_check.py         # Railway health check
├── requirements.txt        # Dependencies
├── Procfile               # Railway process definition
├── src/
│   ├── collectors/        # News collection modules
│   ├── processors/        # AI processing (summarization, tagging)
│   ├── database/          # Database models and operations
│   ├── slack/             # Slack bot integration
│   └── utils/             # Utility functions
├── config/                # Configuration files
├── data/                  # Database storage
├── logs/                  # Log files
└── tests/                 # Unit tests
```

---

## 🔄 Maintenance

### Regular Tasks
- **Monitor Railway logs** for errors
- **Check Slack channel** for bot activity
- **Review collection statistics** weekly
- **Update news sources** as needed

### Database Management
- **Automatic cleanup** runs weekly (30-day retention)
- **Manual cleanup**: `python main.py --cleanup-days 30`
- **View database**: `python view_database.py`

### Updates and Scaling
- **Update dependencies**: Edit `requirements.txt` and redeploy
- **Add news sources**: Update CONFIG_JSON and redeploy
- **Scale collection**: Adjust cron schedules in configuration

---

## 📊 Expected Performance

### Collection Metrics
- **12 Japanese sources** monitored
- **~50-100 articles/day** collected
- **Duplicate detection** 80-90% efficiency
- **Processing time** ~2-3 minutes per collection

### Resource Usage
- **Memory**: ~200MB Railway usage
- **Storage**: ~50MB database growth/month
- **API Calls**: ~100-200 OpenAI requests/day

---

## 🆘 Support

### Getting Help
1. **Check this guide** for common solutions
2. **Review Railway logs** for specific errors
3. **Test individual components** using debug scripts
4. **Verify configuration** using debug tools

### Key Success Indicators
- ✅ Railway deployment successful
- ✅ CONFIG_JSON loads correctly
- ✅ 12 sources populated in database
- ✅ Slack commands respond properly
- ✅ Scheduled collections run automatically
- ✅ Japanese AI news posted to Slack

---

**Your Japanese AI News Bot is now ready to keep your team updated with the latest AI developments from Japan!** 🇯🇵🤖🚂
