# Stand Up Reminder 🧍

แอพ macOS Menu Bar แจ้งเตือนให้ลุกยืนระหว่างวันทำงาน

## ติดตั้ง

```bash
pip3 install -r requirements.txt
```

## รัน

```bash
python3 stand_reminder.py
```

จะเห็นไอคอน 🧍 ขึ้นบน Menu Bar

## ฟีเจอร์

- **แจ้งเตือนพร้อมเสียง** ทุก N นาที (default 30 นาที)
- **กำหนดช่วงเวลาทำงาน** เช่น 09:00–18:00
- **ยกเว้นหลายช่วงเวลา** เช่น พักเที่ยง ประชุม
- **ปุ่ม Snooze** เลื่อนการแจ้งเตือนออกไป 5 นาที
- **นับสถิติรายวัน** ดูว่าลุกไปกี่ครั้งแล้ว
- **เลือกเสียงได้** Glass, Ping, Tink, Pop และอื่นๆ

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

**วิธีที่ 1: ใช้ script ติดตั้ง (ง่ายสุด)**

```bash
bash install_launchagent.sh
```

จะสร้าง LaunchAgent และเปิดให้อัตโนมัติ โปรแกรมจะรันใหม่ทุกครั้งที่ log in

**วิธีที่ 2: ติดตั้งด้วยมือ**

1. สร้างไฟล์ `~/Library/LaunchAgents/com.khayab.standreminder.plist` ด้วยเนื้อหา:
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
        <string>/Users/mtb730773/Documents/khayab/stand_reminder.py</string>
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

2. โหลด:
```bash
launchctl load ~/Library/LaunchAgents/com.khayab.standreminder.plist
```

**จัดการ LaunchAgent**

ตรวจสอบสถานะ:
```bash
launchctl list | grep standreminder
```

ดูประวัติ log:
```bash
tail -f /tmp/standreminder.log
tail -f /tmp/standreminder.error.log
```

ปิด (หยุดรันอัตโนมัติ):
```bash
launchctl unload ~/Library/LaunchAgents/com.khayab.standreminder.plist
```

เปิดใหม่:
```bash
launchctl load ~/Library/LaunchAgents/com.khayab.standreminder.plist
```
