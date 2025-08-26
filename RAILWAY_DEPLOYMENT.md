# Railway Deployment Guide - AI News JP Slack Bot 🚂

Complete guide to deploy your Japanese AI News Bot on Railway for 24/7 operation.

## 📋 Prerequisites

✅ GitHub account  
✅ OpenAI API key  
✅ Slack workspace access  
⏳ Slack bot tokens (we'll create these)  

## 🎯 Deployment Overview

1. **Create Slack App & Get Tokens**
2. **Push Code to GitHub**
3. **Deploy to Railway**
4. **Configure Environment Variables**
5. **Test & Monitor**

---

## 📱 Step 1: Create Slack App & Get Tokens

### 1.1 Create New Slack App

1. Go to **https://api.slack.com/apps**
2. Click **"Create New App"** → **"From scratch"**
3. **App Name**: `AI News JP Bot` (or your preference)
4. **Pick a workspace**: Select your Japanese workspace
5. Click **"Create App"**

### 1.2 Configure Bot Permissions

1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll down to **"Bot Token Scopes"**
3. Click **"Add an OAuth Scope"** and add these scopes:

**Required Scopes:**
- `chat:write` - Send messages (REQUIRED)
- `chat:write.public` - Send messages to channels bot isn't in
- `channels:read` - View basic information about public channels
- `commands` - Add shortcuts and/or slash commands
- `app_mentions:read` - View messages that directly mention your bot

### 1.3 Enable Socket Mode

1. In the left sidebar, click **"Socket Mode"**
2. Toggle **"Enable Socket Mode"** to **On**
3. Click **"Generate Token and Scopes"**
4. **Token Name**: `AI News JP Socket`
5. **Add Scope**: `connections:write`
6. Click **"Generate"**
7. **📝 COPY THE APP-LEVEL TOKEN** (starts with `xapp-`)
8. Click **"Done"**

### 1.4 Create Slash Command

1. In the left sidebar, click **"Slash Commands"**
2. Click **"Create New Command"**
3. Fill in:
   - **Command**: `/ai-news`
   - **Request URL**: `https://example.com` (not used with Socket Mode)
   - **Short Description**: `Japanese AI News Bot commands`
   - **Usage Hint**: `search <keyword> | latest | sources | tags | stats`
4. Click **"Save"**

### 1.5 Install App to Workspace

1. In the left sidebar, click **"OAuth & Permissions"**
2. Scroll up and click **"Install to Workspace"**
3. Click **"Allow"**
4. **📝 COPY THE BOT USER OAUTH TOKEN** (starts with `xoxb-`)

### 1.6 Add Bot to Channel

1. Go to your Slack workspace
2. Navigate to **#times-mayo** channel
3. Type: `/invite @AI News JP Bot`
4. Press Enter

**✅ Tokens Ready!** You now have:
- **Bot Token**: `xoxb-...` 
- **App Token**: `xapp-...`

---

## 🐙 Step 2: Push Code to GitHub

### 2.1 Create GitHub Repository

1. Go to **https://github.com**
2. Click **"New repository"**
3. **Repository name**: `ai-news-jp-slack-bot`
4. **Description**: `Japanese AI News Slack Bot - 24/7 Railway Deployment`
5. Set to **Public** (required for Railway free tier)
6. ✅ **Add a README file**
7. Click **"Create repository"**

### 2.2 Push Your Code

```bash
# Navigate to your bot directory
cd ai-news-jp-slack-bot

# Initialize git (if not already done)
git init

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ai-news-jp-slack-bot.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: Japanese AI News Bot for Railway deployment"

# Push to GitHub
git push -u origin main
```

**✅ Code on GitHub!** Your repository is ready for Railway.

---

## 🚂 Step 3: Deploy to Railway

### 3.1 Create Railway Account

1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Sign up with **GitHub** (recommended)
4. Authorize Railway to access your repositories

### 3.2 Deploy from GitHub

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **`ai-news-jp-slack-bot`** repository
4. Click **"Deploy Now"**

Railway will automatically:
- ✅ Detect Python project
- ✅ Install dependencies from `requirements.txt`
- ✅ Use `Procfile` to start the bot
- ✅ Set up persistent storage

### 3.3 Wait for Initial Build

- **Build time**: 2-5 minutes
- **Status**: Watch the build logs in Railway dashboard
- **Expected**: Build will complete but bot won't start (missing environment variables)

---

## ⚙️ Step 4: Configure Environment Variables

### 4.1 Set Environment Variables

In Railway dashboard:

1. Click on your **project**
2. Click **"Variables"** tab
3. Add these variables:

```
CONFIG_YAML=[Copy entire config/config.example.yaml content here]
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token-here
SLACK_APP_TOKEN=xapp-your-actual-app-token-here
OPENAI_API_KEY=sk-your-actual-openai-key-here
DATABASE_PATH=/app/data/ai_news_jp.db
TZ=Asia/Tokyo
PYTHONPATH=/app
```

**Important**: For the `CONFIG_YAML` variable, copy the entire YAML configuration from your `config/config.example.yaml` file. The bot will read this configuration directly from the environment variable instead of looking for a config file.

### 4.2 Deploy with Environment Variables

1. Click **"Deploy"** button
2. Railway will redeploy with your environment variables
3. **Build time**: 1-2 minutes

---

## 🧪 Step 5: Test & Monitor

### 5.1 Check Deployment Status

In Railway dashboard:
1. **Status**: Should show "Active" with green indicator
2. **Logs**: Click "View Logs" to see bot activity
3. **Resources**: Monitor CPU and memory usage

### 5.2 Test Bot Functionality

In your Slack workspace (#times-mayo):

```
/ai-news latest
/ai-news sources
/ai-news stats
```

**Expected Results:**
- ✅ Bot responds to commands
- ✅ Shows Japanese news sources
- ✅ Displays collection statistics

### 5.3 Test News Collection

**Manual Test:**
```bash
# In Railway logs, you should see:
# "Starting news collection..."
# "Collected X articles from [Japanese sources]"
# "Posted articles summary to #times-mayo"
```

**Scheduled Test:**
- **9 AM JST**: Morning collection
- **3 PM JST**: Afternoon collection
- Check #times-mayo for automated posts

---

## 📊 Monitoring & Maintenance

### Railway Dashboard Monitoring

**Metrics to Watch:**
- **CPU Usage**: Should be <10% most of the time
- **Memory Usage**: Should be <200MB
- **Network**: Outbound requests for RSS feeds and APIs
- **Uptime**: Should be 99%+

### Log Monitoring

**Key Log Messages:**
```
✅ "AI News Bot initialized successfully"
✅ "Slack connection successful"
✅ "OpenAI connection successful"
✅ "Database connection successful"
✅ "Collected X new articles from [source]"
✅ "Posted articles summary to #times-mayo"
```

**Error Messages to Watch:**
```
❌ "Slack connection failed"
❌ "OpenAI connection failed"
❌ "Failed to collect from [source]"
❌ "Database error"
```

### Railway Commands

**View Logs:**
```bash
# In Railway dashboard
Click "View Logs" → See real-time logs
```

**Restart Service:**
```bash
# In Railway dashboard
Click "Deploy" → Redeploy service
```

**Update Code:**
```bash
# Push to GitHub
git add .
git commit -m "Update bot"
git push

# Railway auto-deploys from GitHub
```

---

## 💰 Cost & Usage

### Railway Free Tier

**Included:**
- **500 hours/month** execution time
- **$5 monthly credit** for overages
- **1GB RAM, 1 vCPU** resources
- **100GB network** transfer

**Your Bot Usage:**
- **~2-3 hours/day** active time
- **~60-90 hours/month** total
- **Well within free tier** ✅

### If You Exceed Free Tier

**Pricing:**
- **$0.000463/GB-hour** for compute
- **$0.25/GB-month** for storage
- **Estimated cost**: $2-5/month maximum

---

## 🔧 Troubleshooting

### Common Issues

**1. Bot Not Responding to Commands**
```
Problem: /ai-news commands don't work
Solution: Check SLACK_BOT_TOKEN and SLACK_APP_TOKEN
Verify: Bot has chat:write scope
```

**2. No News Collection**
```
Problem: No articles being collected
Solution: Check OpenAI API key and internet connectivity
Verify: Japanese RSS feeds are accessible
```

**3. Database Issues**
```
Problem: Articles not saving
Solution: Check DATABASE_PATH=/app/data/ai_news_jp.db
Verify: Persistent storage is working
```

**4. Timezone Issues**
```
Problem: Wrong collection times
Solution: Ensure TZ=Asia/Tokyo is set
Verify: Logs show correct JST times
```

### Debug Commands

**Check Environment Variables:**
```bash
# In Railway logs, look for:
"Environment variables loaded successfully"
```

**Test Database:**
```bash
# In Railway logs, look for:
"Database initialized successfully"
"Articles table created"
```

**Test API Connections:**
```bash
# In Railway logs, look for:
"✅ Slack connection successful"
"✅ OpenAI connection successful"
```

---

## 🎉 Success Checklist

After deployment, verify:

- ✅ **Railway Status**: Active and running
- ✅ **Slack Commands**: `/ai-news` responds
- ✅ **News Collection**: Articles collected from Japanese sources
- ✅ **Channel Posts**: Updates posted to #times-mayo
- ✅ **Scheduling**: 9 AM and 3 PM JST collections work
- ✅ **Database**: Articles persist between deployments
- ✅ **Logs**: Clean logs with no errors
- ✅ **Resources**: Within Railway free tier limits

---

## 🚀 Your Bot is Live!

**Congratulations!** Your Japanese AI News Bot is now running 24/7 on Railway, collecting the latest AI news from Japan and posting updates to your #times-mayo channel.

**What happens next:**
- **Daily Collections**: 9 AM and 3 PM JST
- **Japanese Sources**: 12+ Japanese AI news sources
- **Smart Filtering**: Only Japanese AI-related articles
- **Automatic Summaries**: Japanese summaries via OpenAI
- **Slack Integration**: Posts directly to #times-mayo

**日本のAIエコシステムの最新情報をお楽しみください！** 🇯🇵🤖

---

## 📞 Support

**Need Help?**
- **Railway Issues**: Check Railway documentation
- **Slack Issues**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Bot Issues**: Check Railway logs and GitHub issues

**Updates:**
- **Code Updates**: Push to GitHub → Railway auto-deploys
- **Configuration**: Update environment variables in Railway dashboard
- **Monitoring**: Use Railway dashboard for metrics and logs
