# AI News Slack Bot - Troubleshooting Guide

This guide covers common issues and their solutions for the AI News Slack Bot.

## Table of Contents

- [Slack Token and Scope Issues](#slack-token-and-scope-issues)
- [Slash Commands Not Working](#slash-commands-not-working)
- [Bot Can't Post Messages](#bot-cant-post-messages)
- [Service Management Issues](#service-management-issues)
- [General Troubleshooting](#general-troubleshooting)

---

## Slack Token and Scope Issues

### Problem: Missing `chat:write` Scope

**Error seen in logs:**
```
'error': 'missing_scope', 'needed': 'chat:write:bot'
```

**Symptoms:**
- Slash commands work but bot can't respond
- Bot receives commands but no messages appear in Slack

### Solution: Add Missing Scope and Regenerate Token

#### Step 1: Add the Missing Scope

1. **Go to your Slack app**: https://api.slack.com/apps
2. **Select your AI News Bot app**
3. **Click "OAuth & Permissions"** in the left sidebar
4. **Scroll down to "Bot Token Scopes"**
5. **Click "Add an OAuth Scope"**
6. **Add `chat:write`** (this is the missing scope)

#### Step 2: Force Token Regeneration

The key issue is that when you add new scopes to a Slack app, existing tokens don't automatically get the new permissions. You need to regenerate the token.

**Method 1: Reinstall the App**
1. **Scroll up to the top of the OAuth & Permissions page**
2. **Click "Reinstall to Workspace"** (this is the key step!)
3. **Authorize the app** with the new permissions
4. **Copy the NEW Bot User OAuth Token** (starts with `xoxb-`)

**Method 2: Remove and Re-add a Scope**
1. **Remove the `chat:write` scope** (click the X next to it)
2. **Click "Save Changes"**
3. **Add `chat:write` scope back** (click "Add an OAuth Scope")
4. **Click "Reinstall to Workspace"** (should appear now)
5. **Authorize the app**
6. **Copy the NEW token** (should be different now)

**Method 3: Add Another Scope to Force Regeneration**
1. **Add `chat:write.public` scope** (this will force regeneration)
2. **Click "Reinstall to Workspace"**
3. **Authorize the app**
4. **Copy the NEW token**

#### Step 3: Update Your Configuration

1. **Edit your config file**:
```bash
nano config/config.yaml
```

2. **Replace the old bot token** with the new one:
```yaml
slack:
  bot_token: "xoxb-your-new-token-here"  # Replace with NEW token
  app_token: "xapp-your-app-token"       # Keep this the same
  # ... rest of config
```

**Important**: The new token should be different from your current one. If it's the same, the regeneration didn't work.

#### Step 4: Restart the Bot

1. **Stop the current bot** (Ctrl+C in terminal)
2. **Start it again**:
```bash
python3 main.py --interactive
```

### How to Verify the Fix

After updating the token, test your slash commands:
- `/ai-news latest 5`
- `/ai-news sources`

You should now see responses in Slack! 🎉

The error should change from:
```
'provided': 'channels:history,channels:read,users:read,groups:read'
```

To something that includes:
```
'provided': 'chat:write,channels:read,commands,app_mentions:read'
```

---

## Required Scopes Checklist

Make sure your bot has these scopes:

✅ **`chat:write`** - **REQUIRED** - Send messages  
✅ `chat:write.public` - Send messages to channels bot isn't in  
✅ `channels:read` - View basic information about public channels  
✅ `commands` - Add shortcuts and/or slash commands  
✅ `app_mentions:read` - View messages that directly mention your bot  

---

## Slash Commands Not Working

### Problem: Commands Not Responding

If your slash commands aren't working at all:

1. **Check Socket Mode Configuration**:
   - Go to your Slack app → "Socket Mode"
   - Ensure "Enable Socket Mode" is On
   - Make sure you have an App-Level Token with `connections:write` scope

2. **Verify Slash Command Setup**:
   - Go to "Slash Commands" in your app
   - Ensure `/ai-news` command exists
   - **Important**: For Socket Mode, you can leave the Request URL blank or use a placeholder like `https://example.com`

3. **Check Bot is Running in Interactive Mode**:
```bash
python3 main.py --interactive
```

### Problem: Commands Recognized but No Response

This is usually the `chat:write` scope issue covered above.

---

## Bot Can't Post Messages

### Problem: Bot Posts Nothing to Channels

1. **Check Channel Permissions**:
   - Make sure the bot is added to the target channels
   - In each channel, type: `/invite @AI News Bot`

2. **Verify Channel Names in Config**:
```yaml
slack:
  channels:
    main: "#ai-news"        # Make sure these channels exist
    alerts: "#ai-news-alerts"
```

3. **Check Bot Token Scopes** (see above section)

---

## Service Management Issues

### macOS Service Problems

#### Service Won't Start

1. **Check configuration exists**:
```bash
ls -la config/config.yaml
```

2. **Check Python path**:
```bash
which python3
```

3. **Check permissions**:
```bash
ls -la setup_macos_service.sh
chmod +x setup_macos_service.sh  # If needed
```

#### Service Keeps Crashing

1. **Check error logs**:
```bash
./setup_macos_service.sh errors
```

2. **Test manually**:
```bash
python3 main.py --test
```

3. **Check API keys and tokens in config**

#### No News Being Collected

1. **Check service logs**:
```bash
./setup_macos_service.sh logs
```

2. **Test collection manually**:
```bash
python3 main.py --collect-now
```

3. **Check schedule configuration in config.yaml**

### Service Management Commands

| Command | Description |
|---------|-------------|
| `./setup_macos_service.sh install` | Install and start the service |
| `./setup_macos_service.sh status` | Check service status |
| `./setup_macos_service.sh start` | Start the service |
| `./setup_macos_service.sh stop` | Stop the service |
| `./setup_macos_service.sh restart` | Restart the service |
| `./setup_macos_service.sh logs` | View service logs (live) |
| `./setup_macos_service.sh errors` | View error logs (live) |
| `./setup_macos_service.sh uninstall` | Remove the service completely |

---

## General Troubleshooting

### Common Issues

1. **"Configuration file not found"**
   - Make sure you copied `config.example.yaml` to `config.yaml`
   - Check the file path and permissions

2. **"Slack connection failed"**
   - Verify your bot token is correct
   - Make sure the bot is installed in your workspace
   - Check that the bot has the required scopes

3. **"OpenAI connection failed"**
   - Verify your API key is correct
   - Check your OpenAI account has credits
   - Ensure you have access to the specified model (GPT-4)

4. **"No articles collected"**
   - Check your internet connection
   - Verify RSS feed URLs are accessible
   - Review the logs in `logs/` directory

5. **"Permission denied" errors**
   - Make sure the bot is added to the channels
   - Check channel permissions
   - Verify bot scopes include `chat:write`

### Debug Mode

Run with debug logging to see detailed information:

```bash
python3 main.py --collect-now --debug
```

### Log Files

Check these log files for detailed information:
- `logs/ai_news_bot.log` - Main application log
- `logs/errors.log` - Error messages only
- `logs/collection.log` - Collection-specific logs
- `logs/service.log` - Service logs (if running as service)
- `logs/service_error.log` - Service error logs

### Testing Connections

Test all connections before troubleshooting:

```bash
python3 main.py --test
```

This will test:
- ✅ Slack connection
- ✅ OpenAI connection  
- ✅ Database connection

### Getting Help

If you're still having issues:

1. Check the troubleshooting section above
2. Review log files in the `logs/` directory
3. Run with `--debug` flag for detailed output
4. Ensure all prerequisites are met
5. Verify your API keys and tokens are correct

---

## Quick Reference

### Most Common Fix: Token Regeneration

If slash commands work but bot can't respond:

1. Go to https://api.slack.com/apps → Your App → OAuth & Permissions
2. Click "Reinstall to Workspace"
3. Copy the NEW bot token
4. Update `config/config.yaml` with the new token
5. Restart the bot: `python3 main.py --interactive`

### Emergency Reset

If everything is broken:

1. **Create a new Slack app** from scratch
2. **Add all required scopes**:
   - `chat:write`
   - `chat:write.public`
   - `channels:read`
   - `commands`
   - `app_mentions:read`
3. **Set up slash command** `/ai-news`
4. **Enable Socket Mode** with `connections:write`
5. **Install to workspace**
6. **Copy both tokens** (bot token and app token)
7. **Update config** with new tokens
8. **Restart bot**

This should resolve most issues! 🚀
