# Stand Up Reminder 🧍

แอพ macOS Menu Bar แจ้งเตือนให้ลุกยืนระหว่างวันทำงาน รองรับ macOS 12 ขึ้นไป

## ติดตั้ง

```bash
pip3 install -r requirements.txt
```

## รัน

```bash
python3 stand_reminder.py
```

ไอคอน 🧍 จะปรากฏบน Menu Bar

**หมายเหตุ:** ครั้งแรกที่รัน macOS จะขอสิทธิ์แจ้งเตือน กด Allow ด้วย

## ฟีเจอร์

- แจ้งเตือนพร้อมเสียงทุก N นาที (default 30 นาที)
- กำหนดช่วงเวลาทำงาน เช่น 09:00–18:00
- ยกเว้นหลายช่วงเวลา เช่น พักเที่ยง ประชุม
- Snooze ผ่าน Menu Bar เพื่อเลื่อนการแจ้งเตือนออกไป
- นับสถิติรายวัน ว่าลุกไปกี่ครั้งแล้ว
- เลือกเสียงแจ้งเตือนได้ (Glass, Ping, Tink, Pop และอื่นๆ)

## ตั้งค่า

ปรับได้ผ่าน Menu Bar โดยตรง หรือแก้ไฟล์ `config.json`:

```json
{
  "interval_minutes": 30,
  "work_start": "09:00",
  "work_end": "18:00",
  "excluded_ranges": [["12:00", "13:00"]],
  "sound": "Glass",
  "snooze_minutes": 5,
  "enabled": true
}
```

## รันอัตโนมัติตอนเปิดเครื่อง

**วิธีที่ 1: ใช้ script ติดตั้ง (แนะนำ)**

```bash
bash install_launchagent.sh
```

**วิธีที่ 2: ติดตั้งด้วยมือ**

1. สร้างไฟล์ `~/Library/LaunchAgents/com.khayab.standreminder.plist` แทน `PATH_TO_REPO` ด้วย path ของโฟลเดอร์นี้:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.khayab.standreminder</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>PATH_TO_REPO/stand_reminder.py</string>
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
```

2. โหลด LaunchAgent:

```bash
launchctl load ~/Library/LaunchAgents/com.khayab.standreminder.plist
```

**จัดการ LaunchAgent**

| คำสั่ง | ความหมาย |
|--------|----------|
| `launchctl list \| grep standreminder` | ตรวจสอบสถานะ |
| `tail -f /tmp/standreminder.log` | ดู log |
| `tail -f /tmp/standreminder.error.log` | ดู error log |
| `launchctl unload ~/Library/LaunchAgents/com.khayab.standreminder.plist` | หยุดรันอัตโนมัติ |
| `launchctl load ~/Library/LaunchAgents/com.khayab.standreminder.plist` | เปิดใหม่ |
