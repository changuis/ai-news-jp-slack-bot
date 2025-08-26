#!/bin/bash

# AI News JP Slack Bot - macOS Service Setup Script - 日本のAIニュース配信ボット
# This script sets up the Japanese AI news bot to run as a background service on macOS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOT_NAME="ai-news-jp-slack-bot"
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.user.${BOT_NAME}"
PLIST_FILE="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
PYTHON_PATH=$(which python3)
LOG_DIR="$BOT_DIR/logs"

echo -e "${BLUE}🇯🇵 AI News JP Slack Bot - macOS Service Setup${NC}"
echo "=================================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ This script is designed for macOS only${NC}"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to create the plist file
create_plist() {
    echo -e "${YELLOW}📝 Creating Launch Agent plist file...${NC}"
    
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${BOT_DIR}/main.py</string>
        <string>--interactive</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${BOT_DIR}</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/service.log</string>
    
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/service_error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
EOF

    echo -e "${GREEN}✅ Created plist file: ${PLIST_FILE}${NC}"
}

# Function to install the service
install_service() {
    echo -e "${YELLOW}🔧 Installing Launch Agent...${NC}"
    
    # Load the service
    launchctl load "$PLIST_FILE"
    
    # Enable the service to start at login
    launchctl enable "gui/$(id -u)/${PLIST_NAME}"
    
    echo -e "${GREEN}✅ Service installed and enabled${NC}"
}

# Function to start the service
start_service() {
    echo -e "${YELLOW}🚀 Starting service...${NC}"
    
    launchctl start "$PLIST_NAME"
    
    echo -e "${GREEN}✅ Service started${NC}"
}

# Function to check service status
check_status() {
    echo -e "${YELLOW}📊 Checking service status...${NC}"
    
    if launchctl list | grep -q "$PLIST_NAME"; then
        echo -e "${GREEN}✅ Service is running${NC}"
        
        # Show recent logs
        echo -e "\n${BLUE}📋 Recent logs:${NC}"
        if [[ -f "$LOG_DIR/service.log" ]]; then
            tail -10 "$LOG_DIR/service.log"
        else
            echo "No logs found yet"
        fi
    else
        echo -e "${RED}❌ Service is not running${NC}"
    fi
}

# Function to show usage
show_usage() {
    echo -e "\n${BLUE}📖 Service Management Commands:${NC}"
    echo "  Start service:   launchctl start $PLIST_NAME"
    echo "  Stop service:    launchctl stop $PLIST_NAME"
    echo "  Restart service: launchctl stop $PLIST_NAME && launchctl start $PLIST_NAME"
    echo "  Check status:    launchctl list | grep $PLIST_NAME"
    echo "  View logs:       tail -f $LOG_DIR/service.log"
    echo "  View errors:     tail -f $LOG_DIR/service_error.log"
    echo ""
    echo -e "${BLUE}🗑️  To uninstall:${NC}"
    echo "  launchctl stop $PLIST_NAME"
    echo "  launchctl unload $PLIST_FILE"
    echo "  rm $PLIST_FILE"
}

# Main installation process
main() {
    echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"
    
    # Check if Python exists
    if [[ ! -f "$PYTHON_PATH" ]]; then
        echo -e "${RED}❌ Python3 not found. Please install Python3 first.${NC}"
        exit 1
    fi
    
    # Check if bot directory exists
    if [[ ! -f "$BOT_DIR/main.py" ]]; then
        echo -e "${RED}❌ Bot main.py not found in $BOT_DIR${NC}"
        exit 1
    fi
    
    # Check if config exists (check both .yaml and .yml extensions)
    if [[ ! -f "$BOT_DIR/config/config.yaml" ]] && [[ ! -f "$BOT_DIR/config/config.yml" ]]; then
        echo -e "${RED}❌ Configuration file not found. Please set up config/config.yaml or config/config.yml first.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
    
    # Stop existing service if running
    if launchctl list | grep -q "$PLIST_NAME"; then
        echo -e "${YELLOW}🛑 Stopping existing service...${NC}"
        launchctl stop "$PLIST_NAME" 2>/dev/null || true
        launchctl unload "$PLIST_FILE" 2>/dev/null || true
    fi
    
    # Create and install service
    create_plist
    install_service
    start_service
    
    # Wait a moment for service to start
    sleep 3
    
    # Check status
    check_status
    
    # Show usage information
    show_usage
    
    echo -e "\n${GREEN}🎉 AI News JP Slack Bot service setup complete!${NC}"
    echo -e "${BLUE}The Japanese AI news bot will now run automatically in the background and start on login.${NC}"
}

# Handle command line arguments
case "${1:-install}" in
    "install")
        main
        ;;
    "status")
        check_status
        ;;
    "start")
        start_service
        ;;
    "stop")
        echo -e "${YELLOW}🛑 Stopping service...${NC}"
        launchctl stop "$PLIST_NAME"
        echo -e "${GREEN}✅ Service stopped${NC}"
        ;;
    "restart")
        echo -e "${YELLOW}🔄 Restarting service...${NC}"
        launchctl stop "$PLIST_NAME" 2>/dev/null || true
        sleep 2
        launchctl start "$PLIST_NAME"
        echo -e "${GREEN}✅ Service restarted${NC}"
        ;;
    "uninstall")
        echo -e "${YELLOW}🗑️  Uninstalling service...${NC}"
        launchctl stop "$PLIST_NAME" 2>/dev/null || true
        launchctl unload "$PLIST_FILE" 2>/dev/null || true
        rm -f "$PLIST_FILE"
        echo -e "${GREEN}✅ Service uninstalled${NC}"
        ;;
    "logs")
        echo -e "${BLUE}📋 Service logs:${NC}"
        tail -f "$LOG_DIR/service.log"
        ;;
    "errors")
        echo -e "${BLUE}📋 Service error logs:${NC}"
        tail -f "$LOG_DIR/service_error.log"
        ;;
    *)
        echo -e "${BLUE}Usage: $0 {install|status|start|stop|restart|uninstall|logs|errors}${NC}"
        exit 1
        ;;
esac
