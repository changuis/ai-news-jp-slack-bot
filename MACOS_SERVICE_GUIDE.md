# macOS Service Setup - Quick Reference

## 🚀 Quick Start

1. **Install the service:**
```bash
./setup_macos_service.sh install
```

2. **Check if it's running:**
```bash
./setup_macos_service.sh status
```

## 📋 Service Management Commands

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

## 📁 Service Files

 **Service Definition**: `~/Library/LaunchAgents/com.user.ai-news-slack-bot.plist`
 **Service Logs**: `logs/service.log`
 **Error Logs**: `logs/service_error.log`

## 🔧 Manual Service Control

If you prefer using `launchctl` directly:

```bash
# Start service
launchctl start com.user.ai-news-slack-bot

# Stop service
launchctl stop com.user.ai-news-slack-bot

# Check if running
launchctl list | grep ai-news-slack-bot

# View logs
tail -f logs/service.log
tail -f logs/service_error.log
```

## ✅ What the Service Does

When installed, the service will:
 ✅ **Auto-start** when you log in to your Mac
 ✅ **Run in background** (no terminal window needed)
 ✅ **Auto-restart** if it crashes
 ✅ **Collect news** according to your schedule
 ✅ **Post to Slack** automatically
 ✅ **Log everything** to files for monitoring

## 📊 Monitoring

### Check Service Status
```bash
./setup_macos_service.sh status
```

### View Recent Activity
```bash
# Last 20 lines of logs
tail -20 logs/service.log

# Follow logs in real-time
tail -f logs/service.log
```

### Check for Errors
```bash
# View error logs
./setup_macos_service.sh errors

# Or manually
tail -f logs/service_error.log
```

## 🛠️ Troubleshooting

### Service Won't Start
1. Check configuration: `config/config.yaml` exists and is valid
2. Check Python path: `which python3`
3. Check permissions: `ls -la setup_macos_service.sh`

### Service Keeps Crashing
1. Check error logs: `./setup_macos_service.sh errors`
2. Test manually: `python3 main.py --test`
3. Check API keys and tokens

### No News Being Collected
1. Check logs: `./setup_macos_service.sh logs`
2. Test collection: `python3 main.py --collect-now`
3. Check schedule configuration

## 🔄 Updating the Bot

When you update the bot code:

1. **Stop the service:**
```bash
./setup_macos_service.sh stop
```

2. **Update your code** (git pull, etc.)

3. **Restart the service:**
```bash
./setup_macos_service.sh start
```

## 🗑️ Uninstalling

To completely remove the service:

```bash
./setup_macos_service.sh uninstall
```

This will:
 Stop the service
 Remove the plist file
 Clean up all service configurations

## 📝 Notes

 The service runs with your user permissions
 Logs are rotated automatically by macOS
 The service will survive system reboots
 You can run multiple instances with different configurations by changing the service name

## 🎯 Pro Tips

1. **Monitor regularly**: Check logs weekly to ensure everything is working
2. **Test changes**: Always test manually before updating the service
3. **Backup config**: Keep a backup of your `config/config.yaml`
4. **Use status command**: Quick way to check if the bot is running
5. **Follow logs**: Use `./setup_macos_service.sh logs` to watch real-time activity

--

**Need help?** Check the main `SETUP_GUIDE.md` for detailed configuration instructions.
