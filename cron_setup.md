# Cron Setup Guide - Personal AI Employee

This guide shows how to schedule automated tasks for your AI Employee.

---

## 📅 Cron Expressions Explained

```
* * * * *
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sunday=0 or 7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

---

## 🖥️ Windows Task Scheduler

### Setup Daily 8 AM Briefing

1. Open **Task Scheduler** (search in Start menu)
2. Click **"Create Basic Task"** in right panel
3. **Name:** `AI Employee - Daily Briefing`
4. **Trigger:** Daily
5. **Time:** 8:00 AM
6. **Action:** Start a program
7. **Program/script:** `python`
8. **Arguments:** `"C:\Code-journy\Quator-4\Hackahton-0\qwen_reasoner.py"`
9. **Start in:** `C:\Code-journy\Quator-4\Hackahton-0`
10. Click **Finish**

### Setup Sunday Night Weekly Audit

1. Open **Task Scheduler**
2. Click **"Create Basic Task"**
3. **Name:** `AI Employee - Weekly Audit`
4. **Trigger:** Weekly
5. **Day:** Sunday
6. **Time:** 11:00 PM
7. **Action:** Start a program
8. **Program/script:** `python`
9. **Arguments:** `"C:\Code-journy\Quator-4\Hackahton-0\linkedin_draft.py"`
10. **Start in:** `C:\Code-journy\Quator-4\Hackahton-0`
11. Click **Finish**

---

## 🍎 macOS / Linux Cron

### Open Crontab Editor

```bash
crontab -e
```

### Add These Entries

```cron
# ========================================
# Personal AI Employee - Scheduled Tasks
# ========================================

# Daily 8 AM Briefing - Process overnight tasks
0 8 * * * cd /path/to/Hackahton-0 && python qwen_reasoner.py >> Logs/briefing.log 2>&1

# Sunday 11 PM Weekly Audit - Generate LinkedIn draft
0 23 * * 0 cd /path/to/Hackahton-0 && python linkedin_draft.py >> Logs/audit.log 2>&1

# Every hour - Check for new emails (if not running continuously)
0 * * * * cd /path/to/Hackahton-0 && timeout 60 python gmail_watcher.py >> Logs/gmail.log 2>&1

# Every 30 minutes - Check WhatsApp (if not running continuously)
*/30 * * * * cd /path/to/Hackahton-0 && timeout 30 python whatsapp_watcher.py >> Logs/whatsapp.log 2>&1

# Daily 9 AM - File system cleanup
0 9 * * * cd /path/to/Hackahton-0 && python filesystem_watcher.py >> Logs/filesystem.log 2>&1
```

### Verify Cron Jobs

```bash
# List all cron jobs
crontab -l

# View cron logs (macOS)
log show --predicate 'process == "cron"' --last 1h

# View cron logs (Linux)
grep CRON /var/log/syslog
```

---

## 📝 Cron Job Templates

### Template 1: Continuous Watcher with Restart

```bash
# Restart Gmail Watcher every 6 hours (prevents memory leaks)
0 */6 * * * cd /path/to/Hackahton-0 && pkill -f gmail_watcher.py && python gmail_watcher.py >> Logs/watcher.log 2>&1
```

### Template 2: Health Check

```bash
# Check if watchers are running, restart if not
*/5 * * * * pgrep -f gmail_watcher.py || (cd /path/to/Hackahton-0 && python gmail_watcher.py >> Logs/watcher.log 2>&1)
```

### Template 3: Log Rotation

```bash
# Rotate logs daily at midnight
0 0 * * * cd /path/to/Hackahton-0/Logs && find . -name "*.log" -size +10M -exec mv {} {}.old \;
```

---

## 🔧 Systemd Service (Linux)

### Create Service File

```bash
sudo nano /etc/systemd/system/ai-employee.service
```

### Add This Content

```ini
[Unit]
Description=Personal AI Employee Watcher
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Hackahton-0
ExecStart=/usr/bin/python3 gmail_watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable ai-employee

# Start service
sudo systemctl start ai-employee

# Check status
sudo systemctl status ai-employee

# View logs
journalctl -u ai-employee -f
```

---

## 📊 Scheduled Tasks Summary

| Task | Schedule | Cron Expression | Script |
|------|----------|-----------------|--------|
| Daily Briefing | 8:00 AM Daily | `0 8 * * *` | `qwen_reasoner.py` |
| Weekly Audit | 11:00 PM Sunday | `0 23 * * 0` | `linkedin_draft.py` |
| Hourly Email Check | Every hour | `0 * * * *` | `gmail_watcher.py` |
| WhatsApp Check | Every 30 min | `*/30 * * * *` | `whatsapp_watcher.py` |
| File System Check | 9:00 AM Daily | `0 9 * * *` | `filesystem_watcher.py` |

---

## ⚠️ Important Notes

1. **Path Adjustment:** Replace `/path/to/Hackahton-0` with your actual path:
   - Windows: `C:\Code-journy\Quator-4\Hackahton-0`
   - macOS/Linux: `/home/user/projects/Hackahton-0`

2. **Python Path:** If `python` command doesn't work, use full path:
   - Windows: `C:\Python313\python.exe`
   - macOS: `/usr/bin/python3`
   - Linux: `/usr/bin/python3` or `/usr/local/bin/python3`

3. **Log Files:** Ensure Logs folder exists:
   ```bash
   mkdir -p /path/to/Hackahton-0/Logs
   ```

4. **Permissions:** Make scripts executable (Linux/macOS):
   ```bash
   chmod +x *.py
   ```

5. **Environment:** Some systems need explicit PATH in cron:
   ```bash
   PATH=/usr/local/bin:/usr/bin:/bin
   ```

---

## 🧪 Testing Cron Jobs

### Test Immediately (Manual Run)

```bash
# Test the command manually first
cd /path/to/Hackahton-0
python qwen_reasoner.py
```

### Test Cron Environment

```bash
# Add this to crontab to test
* * * * * echo "$(date): Cron is working" >> /tmp/cron_test.log
```

### Check if Job Ran

```bash
# Check log file
cat Logs/briefing.log

# Check system logs
grep CRON /var/log/syslog | tail -20
```

---

## 📱 Windows Batch File Alternative

Create `run_daily_briefing.bat`:

```batch
@echo off
cd /d C:\Code-journy\Quator-4\Hackahton-0
python qwen_reasoner.py >> Logs\briefing.log 2>&1
```

Then schedule this batch file in Task Scheduler.

---

## ✅ Verification Checklist

- [ ] Cron/Task Scheduler configured
- [ ] Test run completed successfully
- [ ] Logs folder exists and is writable
- [ ] Python path is correct
- [ ] Scripts have execute permissions (Linux/macOS)
- [ ] Email notifications enabled (optional)
- [ ] Error handling in place

---

*Last updated: 2026-02-27*
