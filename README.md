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

## 🚀 Complete Command Reference

### Prerequisites

```bash
# Install all required packages
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install playwright
pip install watchdog
pip install requests
```

---

## 📋 Quick Start Commands

### First Time Setup

```bash
# Step 1: Navigate to project folder
cd C:\Code-journy\Quator-4\Hackahton-0

# Step 2: Authorize Gmail API (one-time)
python auth_setup.py

# Step 3: Setup WhatsApp QR Code (one-time)
python whatsapp_setup_qr.py

# Step 4: Verify all components are working
python test_gmail.py
python test_whatsapp_simple.py

# Step 5: Check tier compliance
python check_tier_compliance.py   # Bronze + Silver
python check_gold_compliance.py   # Gold Tier
```

---

## 👁️ Watcher Commands (Perception Layer)

### Gmail Watcher

```bash
# Start Gmail Watcher (checks every 120 seconds)
python gmail_watcher.py

# Test Gmail connection only
python test_gmail.py

# Test Gmail with live email capture
python test_live_email.py
```

**What it does:**
- Monitors your Gmail inbox for unread emails
- Creates `.md` files in `Vault/Needs_Action/` for each new email
- Extracts: From, Subject, Content, Date
- Runs continuously until you press Ctrl+C

**Output:** `Vault/Needs_Action/EMAIL_<message_id>.md`

---

### WhatsApp Watcher

```bash
# Start WhatsApp Watcher (checks every 30 seconds)
python whatsapp_watcher.py

# Setup WhatsApp QR code (first time only)
python whatsapp_setup_qr.py

# Test WhatsApp connection
python test_whatsapp_simple.py

# Debug WhatsApp selectors
python whatsapp_debug.py
```

**What it does:**
- Monitors WhatsApp Web for messages containing keywords
- Keywords: `urgent`, `asap`, `invoice`, `payment`, `help`
- Creates `.md` files in `Vault/Needs_Action/` for each message
- Runs continuously until you press Ctrl+C

**Output:** `Vault/Needs_Action/WHATSAPP_<chat_name>_<timestamp>.md`

---

### File System Watcher

```bash
# Start File System Watcher (real-time monitoring)
python filesystem_watcher.py
```

**What it does:**
- Monitors `Vault/Inbox/` folder for new files
- Automatically copies files to `Vault/Needs_Action/`
- Creates metadata `.md` file alongside each file
- Uses `watchdog` library for real-time detection

**Output:** `Vault/Needs_Action/FILE_<filename>.md`

---

## 🧠 Reasoning Commands (AI Layer)

### Qwen Reasoner

```bash
# Start AI Reasoning Loop (monitors every 10 seconds)
python qwen_reasoner.py
```

**What it does:**
- Monitors `Vault/Needs_Action/` folder for new tasks
- Reads email, WhatsApp, and file action files
- Creates action plans in `Vault/Plans/PLAN_*.md`
- Generates reply drafts for emails and WhatsApp messages
- Detects sensitive actions requiring human approval
- Moves processed files to appropriate folders

**Output:**
- `Vault/Plans/PLAN_<task_name>.md` - Action plan with checkboxes
- `Vault/Pending_Approval/APPROVAL_*.md` - Approval requests
- `Vault/Pending_Approval/EMAIL_REPLY_*.md` - Email reply drafts
- `Vault/Pending_Approval/WHATSAPP_REPLY_*.md` - WhatsApp reply drafts

---

## 🥇 GOLD TIER COMMANDS

### 📊 CEO Briefing Generator

```bash
# Generate weekly CEO briefing (last 7 days)
python ceo_briefing.py Vault 7

# Generate briefing for last 30 days
python ceo_briefing.py Vault 30
```

**Output:** `Vault/Briefings/YYYY-MM-DD_Monday_Briefing.md`

**What you'll see:**
- Executive Summary
- Revenue (This Week, MTD, Trend)
- Completed Tasks
- Bottlenecks (with delay analysis)
- Proactive Suggestions (cost optimization, subscription audit)
- Upcoming Deadlines

---

### 🔄 Ralph Wiggum Persistence Loop

```bash
# Test Ralph Wiggum loop
python ralph_wiggum.py Vault
```

**What it does:**
- Keeps AI working until multi-step tasks complete
- File-movement based completion detection
- Auto-escalates to human when stuck

**Output:** Task files move from `In_Progress/` → `Done/`

---

### 🛡️ Error Recovery & Audit Logging

```bash
# Test audit logger
python audit_logger.py Vault

# Test error handler
python error_handler.py Vault

# Test retry handler
python retry_handler.py
```

**What you'll see:**
- `Vault/Logs/YYYY-MM-DD.json` - JSON audit logs
- All actions logged with timestamps
- 90-day retention policy

---

### 📱 Social Media Posting (Gold Tier)

#### **Twitter (X)**
```bash
# Post text only
python twitter_poster.py --text "Your tweet here"

# Post with image
python twitter_poster.py --text "Tweet" --image "path/to/image.png"

# Post all approved drafts
python twitter_poster.py

# With edit mode
python twitter_poster.py --edit
```

**Output:** Tweet posted to Twitter.com, file moved to `Vault/Done/`

---

#### **Facebook**
```bash
# Post text only
python facebook_poster.py --text "Your Facebook post"

# Post with image
python facebook_poster.py --text "Post" --image "path/to/image.jpg"

# Post all approved drafts
python facebook_poster.py
```

**Output:** Post on Facebook, file moved to `Vault/Done/`

---

#### **Instagram**
```bash
# Post with image (REQUIRED)
python instagram_poster.py --text "Caption here" --image "path/to/image.jpg"

# Post all approved drafts
python instagram_poster.py --image "path/to/image.jpg"
```

**Output:** Instagram post with caption + image, file moved to `Vault/Done/`

---

#### **LinkedIn**
```bash
# Post text only
python linkedin_poster.py --text "Professional update"

# Post with image
python linkedin_poster.py --text "Update" --image "path/to/image.png"

# Post all approved drafts
python linkedin_poster.py

# With edit mode
python linkedin_poster.py --edit
```

**Output:** LinkedIn post, file moved to `Vault/Done/`

---

### 💰 Odoo Accounting Integration

```bash
# Create invoice
python odoo_mcp.py --action create_invoice --customer "Client Name" --amount 1000

# Get financial report
python odoo_mcp.py --action get_report

# Record payment
python odoo_mcp.py --action record_payment --amount 500
```

**Environment Variables:**
```
ODOO_URL=http://localhost:8069
ODOO_DB=hackathon
ODOO_USERNAME=antigravityuser18@gmail.com
ODOO_PASSWORD=Laiba@28july2007
```

**Output:**
- Invoice created in Odoo (Draft status)
- Saved to `Vault/Accounting/Invoices/INVOICE_<id>.md`
- Logged to `Vault/Logs/YYYY-MM-DD.json`

---

### ✅ Compliance Checking

```bash
# Check Bronze + Silver compliance
python check_tier_compliance.py

# Check Gold Tier compliance
python check_gold_compliance.py
```

**Output:**
- Tier-by-tier compliance report
- Pass/Fail for each requirement
- Overall score (e.g., 24/24 = 100%)

---

### 📋 GOLD TIER QUICK REFERENCE TABLE

| Command | What It Does | Output Location |
|---------|--------------|-----------------|
| `python ceo_briefing.py Vault 7` | Generate weekly CEO briefing | `Vault/Briefings/` |
| `python ralph_wiggum.py Vault` | Test persistence loop | `Vault/Done/` |
| `python audit_logger.py Vault` | Test audit logging | `Vault/Logs/` |
| `python error_handler.py Vault` | Test error recovery | Console output |
| `python retry_handler.py` | Test retry logic | Console output |
| `python twitter_poster.py` | Post to Twitter | Twitter.com + `Vault/Done/` |
| `python facebook_poster.py` | Post to Facebook | Facebook.com + `Vault/Done/` |
| `python instagram_poster.py --image X` | Post to Instagram | Instagram.com + `Vault/Done/` |
| `python linkedin_poster.py` | Post to LinkedIn | LinkedIn.com + `Vault/Done/` |
| `python odoo_mcp.py --action create_invoice` | Create invoice in Odoo | Odoo + `Vault/Accounting/` |
| `python check_gold_compliance.py` | Check Gold Tier status | Console report |

---

### 🎯 GOLD TIER WORKFLOW EXAMPLES

#### **Example 1: Generate Weekly CEO Briefing**
```bash
# Run every Sunday at 11 PM via cron
python ceo_briefing.py Vault 7

# View the generated briefing
type Vault\Briefings\*.md
```

#### **Example 2: Post to All Social Media**
```bash
# Create approved posts in Vault/Approved/
# Then run all posters:
python twitter_poster.py
python facebook_poster.py
python instagram_poster.py --image image.png
python linkedin_poster.py
```

#### **Example 3: Create Invoice for Client**
```bash
# Create $1500 invoice for "ABC Corp"
python odoo_mcp.py --action create_invoice --customer "ABC Corp" --amount 1500

# View created invoice
type Vault\Accounting\Invoices\INVOICE_*.md
```

#### **Example 4: Check Gold Tier Status**
```bash
# Run compliance check
python check_gold_compliance.py

# Expected output:
# Gold #1: PASS
# Gold #2: PASS
# ...
# Gold #11: PASS
# Score: 11/11 (100%)
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

## 🔄 Complete End-to-End Workflows

### Workflow 1: Email Processing

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL PROCESSING FLOW                         │
└─────────────────────────────────────────────────────────────────┘

Step 1: EMAIL ARRIVES
    │
    ▼
┌──────────────────┐
│  Gmail Server    │
│  (New Email)     │
└────────┬─────────┘
         │
         ▼
Step 2: GMAIL WATCHER DETECTS
    Command: python gmail_watcher.py (running)
    Interval: Every 120 seconds
    Action: Creates EMAIL_<id>.md in Needs_Action/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Needs_Action/EMAIL_<id>.md    │
│ ---                                  │
│ type: email                          │
│ from: client@example.com             │
│ subject: Invoice Request             │
│ ---                                  │
└─────────────┬───────────────────────┘
              │
              ▼
Step 3: QWEN REASONER PROCESSES
    Command: python qwen_reasoner.py (running)
    Interval: Every 10 seconds
    Actions:
    - Reads email content
    - Creates PLAN_<task>.md in Plans/
    - Creates EMAIL_REPLY_<id>.md in Pending_Approval/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Pending_Approval/             │
│ EMAIL_REPLY_<timestamp>.md          │
│ ---                                  │
│ type: email_reply                    │
│ to: client@example.com               │
│ subject: Re: Invoice Request         │
│ ---                                  │
│ ## Reply Message                     │
│ [Edit this draft]                    │
└─────────────┬───────────────────────┘
              │
              ▼
Step 4: HUMAN REVIEW (YOU)
    1. Open file in Pending_Approval/
    2. Edit reply message
    3. Move file to Approved/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Approved/                     │
│ EMAIL_REPLY_<timestamp>.md          │
│ (Ready to send)                     │
└─────────────┬───────────────────────┘
              │
              ▼
Step 5: EMAIL REPLY SENT
    Command: python email_reply.py
    Action:
    - Scans Approved/ folder
    - Sends email via Gmail API
    - Moves file to Done/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Done/                         │
│ EMAIL_REPLY_<timestamp>.md          │
│ (Sent successfully)                 │
└─────────────────────────────────────┘
```

---

### Workflow 2: WhatsApp Message Processing

```
┌─────────────────────────────────────────────────────────────────┐
│               WHATSAPP MESSAGE PROCESSING FLOW                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: WHATSAPP MESSAGE ARRIVES
    │
    ▼
┌──────────────────┐
│  WhatsApp Web    │
│  (Keyword Match) │
│  urgent, asap,   │
│  invoice, etc.   │
└────────┬─────────┘
         │
         ▼
Step 2: WHATSAPP WATCHER DETECTS
    Command: python whatsapp_watcher.py (running)
    Interval: Every 30 seconds
    Action: Creates WHATSAPP_<chat>.md in Needs_Action/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Needs_Action/                 │
│ WHATSAPP_<chat>_<timestamp>.md      │
│ ---                                  │
│ type: whatsapp                       │
│ from: John Doe                       │
│ received: 2026-02-28T14:30:00        │
│ ---                                  │
│ ## WhatsApp Message                  │
│ "Urgent: Need invoice ASAP"          │
└─────────────┬───────────────────────┘
              │
              ▼
Step 3: QWEN REASONER PROCESSES
    Command: python qwen_reasoner.py (running)
    Interval: Every 10 seconds
    Actions:
    - Reads message content
    - Creates PLAN_<task>.md in Plans/
    - Creates WHATSAPP_REPLY_<id>.md in Pending_Approval/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Pending_Approval/             │
│ WHATSAPP_REPLY_<timestamp>.md       │
│ ---                                  │
│ type: whatsapp_reply                 │
│ to: John Doe                         │
│ ---                                  │
│ ## Reply Message                     │
│ [Edit this draft]                    │
└─────────────┬───────────────────────┘
              │
              ▼
Step 4: HUMAN REVIEW (YOU)
    1. Open file in Pending_Approval/
    2. Edit reply message
    3. Move file to Approved/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Approved/                     │
│ WHATSAPP_REPLY_<timestamp>.md       │
│ (Ready to send)                     │
└─────────────┬───────────────────────┘
              │
              ▼
Step 5: WHATSAPP REPLY SENT
    Command: python whatsapp_reply.py
    Action:
    - Scans Approved/ folder
    - Opens WhatsApp Web
    - Searches contact and sends message
    - Moves file to Done/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Done/                         │
│ WHATSAPP_REPLY_<timestamp>.md       │
│ (Sent successfully)                 │
└─────────────────────────────────────┘
```

---

### Workflow 3: LinkedIn Auto-Posting

```
┌─────────────────────────────────────────────────────────────────┐
│                  LINKEDIN POSTING FLOW                          │
└─────────────────────────────────────────────────────────────────┘

Step 1: GENERATE DRAFT
    Command: python linkedin_draft.py
    Action:
    - Reads Vault/Dashboard.md
    - Extracts business metrics
    - Creates professional post draft
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Plans/                        │
│ LINKEDIN_draft_<timestamp>.md       │
│ ---                                  │
│ type: linkedin_post                  │
│ topic: Weekly Business Update        │
│ ---                                  │
│ 🚀 Exciting updates from our         │
│ company this week!                   │
│                                      │
│ #business #growth #success           │
└─────────────┬───────────────────────┘
              │
              ▼
Step 2: HUMAN REVIEW (YOU)
    1. Review draft in Plans/
    2. Edit if needed
    3. Move file to Approved/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Approved/                     │
│ LINKEDIN_draft_<timestamp>.md       │
│ (Ready to post)                     │
└─────────────┬───────────────────────┘
              │
              ▼
Step 3: POST TO LINKEDIN
    Command: python linkedin_poster.py
    Options:
    - Auto: Posts all approved drafts
    - Manual: --text "custom message"
    - With Image: --image "path/to/image.png"
    Action:
    - Opens LinkedIn
    - Creates new post
    - Uploads image (if provided)
    - Moves file to Done/
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Done/                         │
│ LINKEDIN_draft_<timestamp>.md       │
│ (Posted successfully)               │
└─────────────────────────────────────┘
```

---

### Workflow 4: File Drop Processing

```
┌─────────────────────────────────────────────────────────────────┐
│                   FILE DROP PROCESSING FLOW                     │
└─────────────────────────────────────────────────────────────────┘

Step 1: FILE DROPPED
    │
    ▼
┌──────────────────┐
│ Vault/Inbox/     │
│ invoice.pdf      │
└────────┬─────────┘
         │
         ▼
Step 2: FILESYSTEM WATCHER DETECTS
    Command: python filesystem_watcher.py (running)
    Trigger: Real-time (watchdog)
    Action:
    - Copies file to Needs_Action/
    - Creates metadata .md file
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Needs_Action/                 │
│ FILE_invoice.pdf.md                 │
│ ---                                  │
│ type: file_drop                      │
│ original_name: invoice.pdf           │
│ size: 45678                          │
│ ---                                  │
│ New file dropped for processing.     │
└─────────────┬───────────────────────┘
              │
              ▼
Step 3: QWEN REASONER PROCESSES
    Command: python qwen_reasoner.py (running)
    Interval: Every 10 seconds
    Actions:
    - Reads file metadata
    - Creates PLAN_<task>.md in Plans/
    - Determines required actions
    │
    ▼
┌─────────────────────────────────────┐
│ Vault/Plans/                        │
│ PLAN_process_invoice.md             │
│ ---                                  │
│ Objective: Process invoice file      │
│ Steps:                               │
│ - [ ] Review invoice content         │
│ - [ ] Extract key details            │
│ - [ ] Forward to accounting          │
│ - [ ] Archive in records             │
└─────────────────────────────────────┘
```

---

## 🎯 Quick Start Cheat Sheet

```bash
# ═══════════════════════════════════════════════════════════
# PERSONAL AI EMPLOYEE - QUICK START
# ═══════════════════════════════════════════════════════════

# 1. FIRST TIME SETUP (One-time)
cd C:\Code-journy\Quator-4\Hackahton-0
python auth_setup.py              # Gmail OAuth
python whatsapp_setup_qr.py       # WhatsApp QR scan

# 2. START ALL WATCHERS (4 terminals)
# Terminal 1:
python gmail_watcher.py

# Terminal 2:
python whatsapp_watcher.py

# Terminal 3:
python filesystem_watcher.py

# Terminal 4:
python qwen_reasoner.py

# 3. SEND REPLIES (When files in Approved/)
python email_reply.py             # Send email replies
python whatsapp_reply.py          # Send WhatsApp replies

# 4. LINKEDIN POSTING
python linkedin_draft.py          # Generate draft
# (Move draft to Approved/)
python linkedin_poster.py         # Post to LinkedIn

# 5. TESTING
python test_gmail.py              # Test Gmail
python test_whatsapp_login.py     # Test WhatsApp login
python test_read_write.py         # Test vault

# ═══════════════════════════════════════════════════════════
```

---

## 📊 System Status Dashboard

Check system health anytime:

```bash
# Check what's waiting for attention
dir Vault\Needs_Action

# Check what's approved and ready to send
dir Vault\Approved

# Check what's pending your review
dir Vault\Pending_Approval

# Check completed tasks
dir Vault\Done

# Check WhatsApp login status
python test_whatsapp_login.py
```

---

*Built with ❤️ for the Personal AI Employee Hackathon 2026*

*Last Updated: 2026-02-28*
