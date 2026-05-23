#!/usr/bin/env python3
"""Stand Up Reminder — macOS Menu Bar App"""

import json
import os
import subprocess
import uuid
from datetime import datetime, date, timedelta

import rumps
from UserNotifications import (
    UNUserNotificationCenter,
    UNMutableNotificationContent,
    UNNotificationRequest,
    UNTimeIntervalNotificationTrigger,
)

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "interval_minutes": 30,
    "work_start": "09:00",
    "work_end": "18:00",
    "excluded_ranges": [["12:00", "13:00"]],
    "sound": "Glass",
    "snooze_minutes": 5,
    "enabled": True,
}

SOUNDS = ["Glass", "Ping", "Tink", "Pop", "Purr", "Submarine", "Blow", "Basso", "Funk"]
INTERVALS = [15, 20, 30, 45, 60]


def parse_hm(s):
    h, m = s.split(":")
    return int(h), int(m)


def time_in_range(now, start_str, end_str):
    sh, sm = parse_hm(start_str)
    eh, em = parse_hm(end_str)
    start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end = now.replace(hour=eh, minute=em, second=0, microsecond=0)
    return start <= now < end


class StandReminderApp(rumps.App):
    def __init__(self):
        super().__init__("🧍", quit_button=None)
        self.config = self._load_config()
        self.snooze_until = None
        self.last_alert_slot = None
        self.stats_date = date.today()
        self.stats_count = 0
        self._rebuild_menu()

    # ── Config ────────────────────────────────────────────────────────────────

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH) as f:
                    cfg = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    cfg.setdefault(k, v)
                return cfg
            except Exception:
                pass
        return dict(DEFAULT_CONFIG)

    def _save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    # ── Time logic ────────────────────────────────────────────────────────────

    def _is_work_time(self, now=None):
        now = now or datetime.now()
        if not time_in_range(now, self.config["work_start"], self.config["work_end"]):
            return False
        for start_s, end_s in self.config["excluded_ranges"]:
            if time_in_range(now, start_s, end_s):
                return False
        return True

    def _current_slot(self, now):
        minutes = now.hour * 60 + now.minute
        return minutes // self.config["interval_minutes"]

    def _should_alert(self, now):
        if not self.config["enabled"]:
            return False
        if not self._is_work_time(now):
            return False
        if self.snooze_until and now < self.snooze_until:
            return False
        return self._current_slot(now) != self.last_alert_slot

    # ── Timer ──────────────────────────────────────────────────────────────────

    @rumps.timer(30)
    def tick(self, _):
        now = datetime.now()

        # Reset daily stats at midnight
        today = date.today()
        if today != self.stats_date:
            self.stats_date = today
            self.stats_count = 0

        # Update icon / snooze state
        if self.snooze_until and now >= self.snooze_until:
            self.snooze_until = None
            self.title = "🧍"

        if self._should_alert(now):
            self.last_alert_slot = self._current_slot(now)
            self._send_alert(now)

        self._update_stats_item()

    # ── Alert ──────────────────────────────────────────────────────────────────

    def _send_alert(self, now):
        self._play_sound()
        time_str = now.strftime("%H:%M")
        content = UNMutableNotificationContent.alloc().init()
        content.setTitle_("ลุกขึ้นยืนสักครู่! 🧍")
        content.setSubtitle_(f"เวลา {time_str}")
        content.setBody_("นั่งนานแล้ว ลุกยืดเส้นยืดสายหน่อยนะ")
        trigger = UNTimeIntervalNotificationTrigger.triggerWithTimeInterval_repeats_(1, False)
        req = UNNotificationRequest.requestWithIdentifier_content_trigger_(
            str(uuid.uuid4()), content, trigger
        )
        UNUserNotificationCenter.currentNotificationCenter().addNotificationRequest_withCompletionHandler_(req, None)
        self.stats_count += 1
        self._update_stats_item()

    def _play_sound(self):
        sound = self.config.get("sound", "Glass")
        path = f"/System/Library/Sounds/{sound}.aiff"
        if os.path.exists(path):
            subprocess.Popen(["afplay", path])

    # ── Snooze ─────────────────────────────────────────────────────────────────

    def _do_snooze(self):
        minutes = self.config["snooze_minutes"]
        self.snooze_until = datetime.now() + timedelta(minutes=minutes)
        self.title = "💤"

    @rumps.clicked("💤 Snooze")
    def snooze_clicked(self, _):
        self._do_snooze()

    # ── Enable / Disable ───────────────────────────────────────────────────────

    @rumps.clicked("▶ เปิดใช้งาน / ⏸ หยุด")
    def toggle_enabled(self, _):
        self.config["enabled"] = not self.config["enabled"]
        self._save_config()
        self.title = "🧍" if self.config["enabled"] else "⏸"
        if self.config["enabled"]:
            self.last_alert_slot = self._current_slot(datetime.now())

    # ── Interval submenu ───────────────────────────────────────────────────────

    def _interval_item(self, minutes):
        current = self.config["interval_minutes"]
        label = f"{'✓ ' if minutes == current else '  '}{minutes} นาที"
        item = rumps.MenuItem(label)
        item.set_callback(lambda _: self._set_interval(minutes))
        return item

    def _set_interval(self, minutes):
        self.config["interval_minutes"] = minutes
        now = datetime.now()
        self.last_alert_slot = (now.hour * 60 + now.minute) // minutes
        self._save_config()
        self._rebuild_menu()

    # ── Work hours ─────────────────────────────────────────────────────────────

    @rumps.clicked("🕒 ตั้งเวลาทำงาน")
    def set_work_hours(self, _):
        current = f"{self.config['work_start']} - {self.config['work_end']}"
        window = rumps.Window(
            title="ตั้งเวลาทำงาน",
            message="ใส่เวลาเริ่ม - สิ้นสุด เช่น 09:00 - 18:00",
            default_text=current,
            ok="บันทึก",
            cancel="ยกเลิก",
            dimensions=(280, 24),
        )
        resp = window.run()
        if resp.clicked:
            try:
                parts = [p.strip() for p in resp.text.split("-")]
                s, e = parts[0], parts[1]
                parse_hm(s)
                parse_hm(e)
                self.config["work_start"] = s
                self.config["work_end"] = e
                self._save_config()
                self._rebuild_menu()
            except Exception:
                rumps.alert("รูปแบบไม่ถูกต้อง", "ใช้รูปแบบ HH:MM - HH:MM เช่น 09:00 - 18:00")

    # ── Excluded ranges ────────────────────────────────────────────────────────

    @rumps.clicked("🚫 เพิ่มช่วงเว้น")
    def add_exclusion(self, _):
        window = rumps.Window(
            title="เพิ่มช่วงเว้น",
            message="ใส่ช่วงเวลาที่ไม่ต้องแจ้งเตือน เช่น 12:00 - 13:00",
            default_text="12:00 - 13:00",
            ok="เพิ่ม",
            cancel="ยกเลิก",
            dimensions=(280, 24),
        )
        resp = window.run()
        if resp.clicked:
            try:
                parts = [p.strip() for p in resp.text.split("-")]
                s, e = parts[0], parts[1]
                parse_hm(s)
                parse_hm(e)
                self.config["excluded_ranges"].append([s, e])
                self._save_config()
                self._rebuild_menu()
            except Exception:
                rumps.alert("รูปแบบไม่ถูกต้อง", "ใช้รูปแบบ HH:MM - HH:MM เช่น 12:00 - 13:00")

    @rumps.clicked("🗑 ลบช่วงเว้นทั้งหมด")
    def clear_exclusions(self, _):
        if rumps.alert("ลบช่วงเว้นทั้งหมด?", ok="ลบ", cancel="ยกเลิก"):
            self.config["excluded_ranges"] = []
            self._save_config()
            self._rebuild_menu()

    # ── Sound submenu ──────────────────────────────────────────────────────────

    def _sound_item(self, sound):
        current = self.config["sound"]
        label = f"{'✓ ' if sound == current else '  '}{sound}"
        item = rumps.MenuItem(label)
        item.set_callback(lambda _: self._set_sound(sound))
        return item

    def _set_sound(self, sound):
        self.config["sound"] = sound
        self._save_config()
        self._play_sound()
        self._rebuild_menu()

    # ── Stats ──────────────────────────────────────────────────────────────────

    def _update_stats_item(self):
        if "📊 สถิติ" in self.menu:
            self.menu["📊 สถิติ"].title = f"📊 วันนี้ลุกแล้ว: {self.stats_count} ครั้ง"

    # ── Menu builder ───────────────────────────────────────────────────────────

    def _rebuild_menu(self):
        self.menu.clear()

        self.menu.add(rumps.MenuItem("▶ เปิดใช้งาน / ⏸ หยุด"))
        self.menu.add(rumps.MenuItem("💤 Snooze"))
        self.menu.add(rumps.separator)

        # Interval submenu
        interval_menu = rumps.MenuItem(f"⏱ แจ้งทุก: {self.config['interval_minutes']} นาที")
        for m in INTERVALS:
            interval_menu.add(self._interval_item(m))
        self.menu.add(interval_menu)

        # Work hours
        wh = f"🕒 ตั้งเวลาทำงาน  ({self.config['work_start']}–{self.config['work_end']})"
        self.menu.add(rumps.MenuItem(wh, callback=self.set_work_hours))

        # Excluded ranges
        exc = self.config["excluded_ranges"]
        exc_label = "🚫 ช่วงเว้น: " + (", ".join(f"{s}–{e}" for s, e in exc) if exc else "ไม่มี")
        exc_menu = rumps.MenuItem(exc_label)
        exc_menu.add(rumps.MenuItem("🚫 เพิ่มช่วงเว้น", callback=self.add_exclusion))
        exc_menu.add(rumps.MenuItem("🗑 ลบช่วงเว้นทั้งหมด", callback=self.clear_exclusions))
        self.menu.add(exc_menu)

        # Sound submenu
        sound_menu = rumps.MenuItem(f"🔊 เสียง: {self.config['sound']}")
        for s in SOUNDS:
            sound_menu.add(self._sound_item(s))
        self.menu.add(sound_menu)

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem(f"📊 วันนี้ลุกแล้ว: {self.stats_count} ครั้ง"))
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))


if __name__ == "__main__":
    StandReminderApp().run()
