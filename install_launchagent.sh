#!/bin/bash
# Install Stand Reminder LaunchAgent for auto-start on login

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.khayab.standreminder.plist"
PYTHON_PATH="/usr/bin/python3"

echo "🔧 Stand Reminder — LaunchAgent Setup"
echo "────────────────────────────────────"

# Create LaunchAgents directory if not exists
mkdir -p "$HOME/Library/LaunchAgents"

# Create plist file
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.khayab.standreminder</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPT_DIR/stand_reminder.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/standreminder.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/standreminder.error.log</string>
</dict>
</plist>
EOF

echo "✓ สร้างไฟล์ plist: $PLIST_PATH"

# Load LaunchAgent
launchctl load "$PLIST_PATH" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ โหลด LaunchAgent สำเร็จ"
else
    echo "⚠ LaunchAgent อาจโหลดไปแล้ว ลองสั่ง:"
    echo "  launchctl unload $PLIST_PATH"
    echo "  launchctl load $PLIST_PATH"
fi

echo ""
echo "✓ ติดตั้งเสร็จ! Stand Reminder จะเปิดโดยอัตโนมัติตอนเข้า macOS"
echo ""
echo "ตรวจสอบสถานะ:"
echo "  launchctl list | grep standreminder"
echo ""
echo "ดูประวัติ:"
echo "  tail -f /tmp/standreminder.log"
echo ""
echo "ปิด (ถ้าอยากหยุด):"
echo "  launchctl unload $PLIST_PATH"
