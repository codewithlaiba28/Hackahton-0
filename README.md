# 🤖 Personal AI Employee - SILVER TIER

A local-first, agent-driven automation system that acts as your digital full-time employee (FTE). This is the **SILVER TIER** implementation of the Personal AI Employee Hackathon.

---

## 📋 What's New in SILVER TIER

This SILVER TIER implementation includes **all BRONZE features** plus:

- ✅ **WhatsApp Watcher** - Monitors WhatsApp Web for urgent messages
- ✅ **File System Watcher** - Watches drop folder for new files
- ✅ **Qwen Reasoner** - AI reasoning loop that creates action plans
- ✅ **Human-in-the-Loop (HITL)** - Approval workflow for sensitive actions
- ✅ **LinkedIn Draft Generator** - Creates social media post drafts
- ✅ **MCP Configuration** - Ready for external action servers
- ✅ **Cron Scheduling** - Automated task scheduling

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER (Watchers)                   │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Gmail Watcher  │  WhatsApp Watcher│  File System Watcher        │
│  (120s interval)│  (30s interval)  │  (Real-time)                │
└────────┬────────┴────────┬─────────┴────────────┬────────────────┘
         │                 │                       │
         ▼                 ▼                       ▼
         └─────────────────┴───────────────────────┘
                          │
                          ▼
              /Vault/Needs_Action/ Folder
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REASONING LAYER (Qwen)                        │
│                                                                  │
│  1. Read task files from Needs_Action                           │
│  2. Analyze content and determine actions                        │
│  3. Create Plan.md with step-by-step checklist                   │
│  4. Flag sensitive actions for approval                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              /Vault/Plans/ Folder
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ACTION LAYER (HITL + MCP)                     │
│                                                                  │
│  ┌─────────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │ Pending Approval│────▶│   Approved   │────▶│   Execute    │ │
│  │   (Human)       │     │   (Move)     │     │   (MCP)      │ │
│  └─────────────────┘     └──────────────┘     └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Complete Folder Structure

```
Hackahton-0/
├── Vault/
│   ├── Inbox/                    # Drop folder for files
│   ├── Needs_Action/             # Items requiring attention
│   ├── Done/                     # Completed tasks
│   ├── Plans/                    # Action plans and drafts
│   │   ├── PLAN_*.md             # Auto-generated plans
│   │   └── LINKEDIN_draft_*.md   # Social media drafts
│   ├── Pending_Approval/         # Awaiting human approval
│   ├── Approved/                 # Approved actions
│   ├── Rejected/                 # Rejected actions
│   ├── Skills/
│   │   └── SKILL.md              # Agent skills documentation
│   ├── Dashboard.md              # Real-time status overview
│   └── Company_Handbook.md       # Rules of engagement
├── Watchers (Bronze + Silver):
│   ├── base_watcher.py           # Base class for all watchers
│   ├── gmail_watcher.py          # Gmail monitoring
│   ├── whatsapp_watcher.py       # WhatsApp monitoring (NEW)
│   └── filesystem_watcher.py     # File drop monitoring (NEW)
├── Reasoning:
│   └── qwen_reasoner.py          # AI reasoning loop (NEW)
├── Actions:
│   └── linkedin_draft.py         # LinkedIn draft generator (NEW)
├── Configuration:
│   ├── mcp_config.json           # MCP server config (NEW)
│   ├── cron_setup.md             # Scheduling guide (NEW)
│   └── credentials.json          # OAuth credentials
│   └── token.json                # Auth token
├── Documentation:
│   ├── README.md                 # This file
│   ├── SETUP_QUICK.md            # Quick setup guide
│   └── BRONZE_CERTIFICATE.md     # Bronze tier completion
└── Logs/                         # Activity logs (auto-created)
```

---

## 🚀 How to Run the Scripts

### Prerequisites

```bash
# Install all required packages
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install playwright
pip install watchdog
```

### Step 1: Authorize Gmail (If Not Done)

```bash
cd C:\Code-journy\Quator-4\Hackahton-0
python auth_setup.py
```

### Step 2: Start Watchers

**Option A: Run Individual Watchers**

```bash
# Gmail Watcher (runs continuously)
python gmail_watcher.py

# WhatsApp Watcher (in new terminal)
python whatsapp_watcher.py

# File System Watcher (in new terminal)
python filesystem_watcher.py
```

**Option B: Run All Watchers**

Create `start_all_watchers.bat`:
```batch
@echo off
start cmd /k "cd /d %~dp0 && python gmail_watcher.py"
start cmd /k "cd /d %~dp0 && python whatsapp_watcher.py"
start cmd /k "cd /d %~dp0 && python filesystem_watcher.py"
```

### Step 3: Start Reasoning Loop

```bash
# Qwen Reasoner (monitors Needs_Action folder)
python qwen_reasoner.py
```

### Step 4: Generate LinkedIn Drafts

```bash
# Create a new LinkedIn post draft
python linkedin_draft.py
```

---

## 🔄 Human-in-the-Loop (HITL) Approval Workflow

### How It Works

1. **Sensitive Action Detected** → Qwen Reasoner creates approval file
2. **File Saved** → `/Vault/Pending_Approval/APPROVAL_*.md`
3. **Human Reviews** → Opens file and reviews details
4. **To Approve** → Move file to `/Vault/Approved/`
5. **To Reject** → Move file to `/Vault/Rejected/`
6. **System Acts** → Processes approved actions automatically

### Approval File Example

```markdown
---
type: approval_request
action: payment
amount: $750.00
recipient: Client ABC
reason: Invoice #12345
created: 2026-02-27T14:30:00
status: pending
---

# Approval Required

## Payment Details
- **Amount:** $750.00
- **To:** Client ABC
- **Reference:** Invoice #12345

## Why Approval is Required
Payment over $500 threshold

## To Approve
Move this file to /Vault/Approved folder

## To Reject
Move this file to /Vault/Rejected folder
```

### Approval Workflow Diagram

```
┌──────────────────────┐
│  Sensitive Action    │
│  Detected by Qwen    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Create Approval     │
│  File in Pending/    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Human Reviews       │
│  File Contents       │
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐ ┌──────────┐
│ Approve │ │  Reject  │
│ Move to │ │  Move to │
│Approved/│ │Rejected/ │
└────┬────┘ └────┬─────┘
     │           │
     ▼           ▼
┌─────────┐ ┌──────────┐
│ Execute │ │  Log &   │
│  Action │ │  Notify  │
└─────────┘ └──────────┘
```

---

## 📅 Scheduled Tasks (Cron)

### Quick Setup

See `cron_setup.md` for detailed instructions.

### Default Schedule

| Task | Schedule | Command |
|------|----------|---------|
| Daily Briefing | 8:00 AM | `python qwen_reasoner.py` |
| Weekly Audit | Sunday 11 PM | `python linkedin_draft.py` |
| Gmail Check | Every 2 min | `python gmail_watcher.py` (continuous) |
| WhatsApp Check | Every 30 sec | `python whatsapp_watcher.py` (continuous) |

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 8:00 AM)
4. Action: `python` with args `"C:\Code-journy\Quator-4\Hackahton-0\qwen_reasoner.py"`
5. Start in: `C:\Code-journy\Quator-4\Hackahton-0`

---

## 📊 SILVER TIER Features Checklist

### Watchers (Perception)
- [x] Gmail Watcher - Monitors unread emails
- [x] WhatsApp Watcher - Monitors urgent messages
- [x] File System Watcher - Monitors drop folder

### Reasoning
- [x] Qwen Reasoner - Analyzes tasks
- [x] Plan Generation - Creates Plan.md files
- [x] Approval Detection - Flags sensitive actions

### Actions
- [x] HITL Approval Workflow - Human-in-the-loop
- [x] LinkedIn Draft Generator - Social media drafts
- [x] MCP Configuration - Ready for external actions

### Scheduling
- [x] Cron Setup Guide - Task scheduling
- [x] Windows Task Scheduler - Windows automation
- [x] Systemd Service - Linux service

---

## 🛠️ Extending Your AI Employee

### Adding a New Watcher

```python
from base_watcher import BaseWatcher
from pathlib import Path

class MyNewWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Your monitoring logic
        return []
    
    def create_action_file(self, item) -> Path:
        # Create .md file in Needs_Action
        pass
```

### Adding a New Action

1. Create script in project root
2. Implement action logic
3. Add to Qwen Reasoner's action list
4. Configure in `mcp_config.json`

---

## 🔜 Next Steps (GOLD TIER)

To advance to GOLD TIER, add:
- [ ] Odoo accounting integration via MCP
- [ ] Facebook/Instagram posting
- [ ] Twitter (X) integration
- [ ] Multiple MCP servers
- [ ] Weekly CEO Briefing generation
- [ ] Error recovery and graceful degradation
- [ ] Comprehensive audit logging
- [ ] Ralph Wiggum persistence loop

---

## 📝 License

This project is part of the Personal AI Employee Hackathon 2026.

---

## 🆘 Support

For questions or issues:
- Check `Company_Handbook.md` for rules
- Review `Vault/Skills/SKILL.md` for capabilities
- Check `cron_setup.md` for scheduling help
- Join Wednesday Research Meeting on Zoom

---

## 📈 Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 (Silver) | 2026-02-27 | Added WhatsApp, File watchers, Reasoning, HITL |
| 1.0 (Bronze) | 2026-02-27 | Initial Gmail watcher, Dashboard, Handbook |

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*
