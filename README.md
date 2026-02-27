# 🤖 Personal AI Employee - BRONZE TIER

A local-first, agent-driven automation system that acts as your digital full-time employee (FTE). This is the **BRONZE TIER** implementation of the Personal AI Employee Hackathon.

## 📋 What Was Built

This BRONZE TIER implementation includes:

- ✅ **Obsidian Vault** with Dashboard.md and Company_Handbook.md
- ✅ **Folder Structure**: `/Inbox`, `/Needs_Action`, `/Done`, `/Skills`
- ✅ **Base Watcher**: Abstract base class for all watcher scripts
- ✅ **Gmail Watcher**: Monitors Gmail for important unread messages
- ✅ **Agent Skills Documentation**: SKILL.md documenting all capabilities

## 🏗️ Architecture

```
Perception (Watchers) → Reasoning (You/Qwen) → Action (MCP Servers)
```

The Watcher scripts run continuously in the background, monitoring external systems (Gmail, WhatsApp, etc.) and creating actionable `.md` files in the `Needs_Action` folder for processing.

## 📁 Folder Structure

```
Hackahton-0/
├── Vault/
│   ├── Inbox/              # Raw incoming items
│   ├── Needs_Action/       # Items requiring attention
│   ├── Done/               # Completed tasks
│   ├── Skills/             # Agent skills documentation
│   ├── Dashboard.md        # Real-time status overview
│   └── Company_Handbook.md # Rules of engagement
├── base_watcher.py         # Base class for all watchers
├── gmail_watcher.py        # Gmail monitoring script
└── README.md               # This file
```

### Folder Descriptions

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming items before processing |
| `/Needs_Action` | Items that require attention or action |
| `/Done` | Completed and archived tasks |
| `/Skills` | Agent skills documentation (SKILL.md files) |

## 🚀 How to Run the Scripts

### Prerequisites

Ensure you have the following installed:
- Python 3.13 or higher
- Google Gmail API credentials (for Gmail watcher)

### Install Required Packages

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Running the Watchers

**1. Run the Base Watcher (Template):**
```bash
python base_watcher.py
```
*Note: This is an abstract class and cannot be run directly. Use it as a template.*

**2. Run the Gmail Watcher:**
```bash
python gmail_watcher.py
```

*Note: Gmail Watcher requires Google API credentials setup. See below.*

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to your project directory
6. Update `gmail_watcher.py` with your credentials path

## 📖 Using Your AI Employee

### Daily Workflow

1. **Morning**: Check `Dashboard.md` for overview
2. **Throughout Day**: Watchers create files in `Needs_Action/`
3. **Processing**: Review items in `Needs_Action/` and take action
4. **Completion**: Move processed items to `Done/`

### Company Handbook Rules

Key rules defined in `Company_Handbook.md`:
- ✉️ Reply to emails within 24 hours
- 💰 Flag any payment over $500 for approval
- 💬 Always be polite on WhatsApp
- 🔒 Never share sensitive information

## 🛠️ Extending Your AI Employee

### Adding a New Watcher

1. Create a new Python file (e.g., `whatsapp_watcher.py`)
2. Inherit from `BaseWatcher` class
3. Implement `check_for_updates()` and `create_action_file()`
4. Run the new watcher script

### Example: File System Watcher

```python
from base_watcher import BaseWatcher
from pathlib import Path

class FileSystemWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Your monitoring logic here
        return []
    
    def create_action_file(self, item) -> Path:
        # Create .md file in Needs_Action
        pass
```

## 📊 BRONZE TIER Checklist

- [x] Obsidian vault with Dashboard.md
- [x] Company_Handbook.md with rules
- [x] One working Watcher script (Gmail)
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] File read/write capability verified

## 🔜 Next Steps (SILVER TIER)

To advance to SILVER TIER, add:
- [ ] WhatsApp Watcher
- [ ] MCP server for sending emails
- [ ] Human-in-the-loop approval workflow
- [ ] Scheduled tasks via cron/Task Scheduler
- [ ] Plan.md creation logic

## 📝 License

This project is part of the Personal AI Employee Hackathon 2026.

## 🆘 Support

For questions or issues:
- Check `Company_Handbook.md` for rules
- Review `Vault/Skills/SKILL.md` for capabilities
- Join Wednesday Research Meeting on Zoom

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*
