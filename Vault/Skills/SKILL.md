---
skill_version: 3.0
created: 2026-02-27
updated: 2026-02-27
tier: SILVER (COMPLETE)
---

# 🧠 AI Employee Skills Documentation

This document catalogs all Agent Skills implemented in this Personal AI Employee system, following the [Claude Agent Skills framework](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

---

## 📋 Skill Overview

### BRONZE TIER Skills (Foundation)

| Skill ID | Name | Category | Status |
|----------|------|----------|--------|
| SKILL-001 | Gmail Watching | Perception | ✅ Active |
| SKILL-002 | File Read/Write | Action | ✅ Active |
| SKILL-003 | Folder Management | Action | ✅ Active |
| SKILL-004 | Dashboard Updates | Reporting | ✅ Active |

### SILVER TIER Skills (NEW)

| Skill ID | Name | Category | Status |
|----------|------|----------|--------|
| SKILL-005 | WhatsApp Watching | Perception | ✅ Active |
| SKILL-006 | File System Watching | Perception | ✅ Active |
| SKILL-007 | Qwen Reasoning | Reasoning | ✅ Active |
| SKILL-008 | Plan Generation | Reasoning | ✅ Active |
| SKILL-009 | HITL Approval Workflow | Action | ✅ Active |
| SKILL-010 | LinkedIn Draft Generation | Action | ✅ Active |
| SKILL-011 | MCP Configuration | Integration | ✅ Active |
| SKILL-012 | Cron Scheduling | Orchestration | ✅ Active |
| SKILL-013 | Email Reply Sending | Action | ✅ Active |
| SKILL-014 | WhatsApp Reply Sending | Action | ✅ Active |
| SKILL-015 | LinkedIn Auto-Posting | Action | ✅ Active |

---

## 🔍 SKILL-001: Gmail Watching (BRONZE)

**Status:** ✅ Active  
**File:** `gmail_watcher.py`

Monitors Gmail inbox for unread messages and creates actionable files.

### Functions
- `check_for_updates()` - Query Gmail API every 120 seconds
- `create_action_file()` - Create markdown file in Needs_Action

---

## 📱 SKILL-005: WhatsApp Watching (SILVER)

**Status:** ✅ Active  
**File:** `whatsapp_watcher.py`

Monitors WhatsApp Web for unread messages containing keywords.

### Implementation

```python
class WhatsAppWatcher(BaseWatcher):
    """
    Agent Skill: WhatsApp Monitoring
    
    Monitors WhatsApp Web for messages containing:
    - urgent, asap, invoice, payment, help
    """
```

### Functions

#### `check_for_updates() -> list`
- **Purpose**: Query WhatsApp Web for unread messages
- **Interval**: Every 30 seconds
- **Filter**: Messages containing keywords
- **Returns**: List of message objects

#### `create_action_file(message) -> Path`
- **Purpose**: Create markdown file in Needs_Action folder
- **Format**: YAML frontmatter + message content + suggested actions
- **Output**: `WHATSAPP_<contact>_<timestamp>.md`

### Usage Example

```bash
# Start WhatsApp Watcher
python whatsapp_watcher.py

# First run requires QR code scan
# Subsequent runs use saved session
```

### Agent Skill Pattern
**Perception Skill** - Monitors external system and creates internal files.

---

## 📁 SKILL-006: File System Watching (SILVER)

**Status:** ✅ Active  
**File:** `filesystem_watcher.py`

Monitors a drop folder for new files and creates action files.

### Implementation

```python
class FileSystemWatcher:
    """
    Agent Skill: File System Monitoring
    
    Uses watchdog library for efficient file monitoring.
    Watches /Vault/Inbox for new files.
    """
```

### Functions

#### `on_created(event)` - Handle file creation events
#### `process_file(source)` - Copy file and create metadata

### Usage Example

```bash
# Start File System Watcher
python filesystem_watcher.py

# Drop files in Vault/Inbox/
# Metadata files created in Needs_Action/
```

---

## 🧠 SKILL-007: Qwen Reasoning (SILVER)

**Status:** ✅ Active  
**File:** `qwen_reasoner.py`

AI reasoning engine that analyzes tasks and creates action plans.

### Implementation

```python
class QwenReasoner:
    """
    Agent Skill: AI Reasoning
    
    Analyzes tasks from Needs_Action folder
    Creates plans and determines approval requirements
    """
```

### Functions

#### `check_for_new_tasks() -> List[Path]`
- **Purpose**: Find unprocessed task files
- **Returns**: List of new file paths

#### `read_task_file(filepath) -> Dict`
- **Purpose**: Parse task file content and frontmatter
- **Returns**: Task data dictionary

#### `analyze_task(task_data) -> Dict`
- **Purpose**: Determine required actions and approval needs
- **Returns**: Analysis with category, urgency, actions

#### `create_plan(task_data, analysis) -> Path`
- **Purpose**: Generate Plan.md with step-by-step checklist
- **Output**: `Vault/Plans/PLAN_<task>.md`

#### `create_approval_request(task_data, analysis) -> Path`
- **Purpose**: Create approval file for sensitive actions
- **Output**: `Vault/Pending_Approval/APPROVAL_<task>.md`

### Usage Example

```bash
# Start Qwen Reasoner
python qwen_reasoner.py

# Monitors Needs_Action folder
# Creates plans automatically
```

---

## 📋 SKILL-008: Plan Generation (SILVER)

**Status:** ✅ Active  
**File:** `qwen_reasoner.py`

Automatically generates action plans with checkboxes.

### Plan Template

```markdown
---
type: action_plan
task_source: EMAIL_abc123.md
created: 2026-02-27 16:00:00
category: communication
urgency: normal
approval_required: Not Required
status: pending
---

# Action Plan: EMAIL_abc123

## Objective
Process and complete the task

## Required Actions
- [ ] Reply To Sender
- [ ] Draft Response
- [ ] Review Before Sending

## Approval Status
- **Human Approval:** Not Required
```

---

## ✅ SKILL-009: HITL Approval Workflow (SILVER)

**Status:** ✅ Active  
**File:** `qwen_reasoner.py`

Human-in-the-loop approval system for sensitive actions.

### Implementation

```python
# Approval file structure
{
    "type": "approval_request",
    "action": "payment",
    "amount": "$750.00",
    "recipient": "Client ABC",
    "status": "pending"
}
```

### Workflow

```
1. Sensitive action detected
2. Approval file created in Pending_Approval/
3. Human reviews file
4. Move to Approved/ → Action executes
5. Move to Rejected/ → Action cancelled
```

### Approval Thresholds

| Action Type | Threshold | Approval Required |
|-------------|-----------|-------------------|
| Payment | > $500 | ✅ Yes |
| Email Send | Any | ✅ Yes (draft only) |
| Social Post | Any | ✅ Yes (draft only) |
| File Processing | Any | ❌ No |

---

## 💼 SKILL-010: LinkedIn Draft Generation (SILVER)

**Status:** ✅ Active  
**File:** `linkedin_draft.py`

Creates LinkedIn post drafts from business data.

### Implementation

```python
class LinkedInDraftGenerator:
    """
    Agent Skill: Social Media Content Generation
    
    Reads Dashboard.md for business metrics
    Creates engaging LinkedIn post drafts
    """
```

### Functions

#### `read_dashboard() -> dict`
- **Purpose**: Extract business metrics from Dashboard.md
- **Returns**: Revenue, tasks, projects data

#### `generate_post(data) -> str`
- **Purpose**: Create engaging LinkedIn post content
- **Includes**: Milestones, achievements, call-to-action

#### `create_draft_file(post_content) -> Path`
- **Purpose**: Save draft with metadata and checklist
- **Output**: `Vault/Plans/LINKEDIN_draft_*.md`

### Usage Example

```bash
# Generate new LinkedIn draft
python linkedin_draft.py

# Draft saved to Plans folder
# Requires human approval before posting
```

---

## 🔌 SKILL-011: MCP Configuration (SILVER)

**Status:** ✅ Active  
**File:** `mcp_config.json`

Configuration for Model Context Protocol servers.

### Configuration

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"]
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"]
    }
  ],
  "human_in_the_loop": {
    "enabled": true,
    "approval_folder": "Vault/Pending_Approval"
  }
}
```

### Supported MCP Servers

| Server | Purpose | Status |
|--------|---------|--------|
| filesystem | File operations | ✅ Built-in |
| email-mcp | Send emails | ⏳ Ready |
| browser-mcp | Web automation | ⏳ Ready |
| calendar-mcp | Schedule events | ⏳ Ready |

---

## ⏰ SKILL-012: Cron Scheduling (SILVER)

**Status:** ✅ Active  
**File:** `cron_setup.md`

Automated task scheduling via cron or Task Scheduler.

### Default Schedule

| Task | Schedule | Cron Expression |
|------|----------|-----------------|
| Daily Briefing | 8:00 AM | `0 8 * * *` |
| Weekly Audit | Sunday 11 PM | `0 23 * * 0` |
| Gmail Check | Every 2 min | Continuous |
| WhatsApp Check | Every 30 sec | Continuous |

### Windows Task Scheduler Commands

```batch
# Daily Briefing
python "C:\Code-journy\Quator-4\Hackahton-0\qwen_reasoner.py"

# Weekly Audit
python "C:\Code-journy\Quator-4\Hackahton-0\linkedin_draft.py"
```

---

## 📧 SKILL-013: Email Reply Sending (SILVER)

**Status:** ✅ Active
**File:** `email_reply.py`

Sends email replies via Gmail API with Human-in-the-Loop approval.

### Implementation

```python
class EmailReplySender:
    """
    Agent Skill: Email Reply Sending

    Sends emails via Gmail API after human approval.
    Uses OAuth 2.0 for authentication.
    """
```

### Functions

#### `check_approved_replies() -> list`
- **Purpose**: Check Approved folder for email reply files
- **Location**: `Vault/Approved/`
- **Returns**: List of approved reply files

#### `parse_reply_file(filepath: Path) -> dict`
- **Purpose**: Parse email reply file and extract details
- **Extracts**: to, subject, body, in_reply_to
- **Returns**: Dictionary with email data

#### `send_reply(reply_data: dict) -> bool`
- **Purpose**: Send email via Gmail API
- **Method**: `service.users().messages().send()`
- **Returns**: True if successful

### Usage Example

```bash
# Send approved email replies
python email_reply.py

# Workflow:
# 1. Reply draft created in Pending_Approval/
# 2. Human moves to Approved/
# 3. Script sends email automatically
# 4. File moved to Done/
```

### Agent Skill Pattern
**Action Skill** - Executes external action (sending email) after human approval.

### Security
- OAuth 2.0 authentication
- Scopes: `gmail.send`, `gmail.readonly`, `gmail.modify`
- Credentials stored in `token.json` (git-ignored)

---

## 💬 SKILL-014: WhatsApp Reply Sending (SILVER)

**Status:** ✅ Active
**File:** `whatsapp_reply.py`

Sends WhatsApp messages via browser automation (Playwright).

### Implementation

```python
class WhatsAppReplySender:
    """
    Agent Skill: WhatsApp Reply Sending

    Sends WhatsApp messages via Playwright browser automation.
    Uses persistent session for authentication.
    """
```

### Functions

#### `check_approved_replies() -> list`
- **Purpose**: Check Approved folder for WhatsApp reply files
- **Location**: `Vault/Approved/`
- **Returns**: List of approved reply files

#### `parse_reply_file(filepath: Path) -> dict`
- **Purpose**: Parse WhatsApp reply file
- **Extracts**: contact, message, reply_to
- **Returns**: Dictionary with message data

#### `send_reply(reply_data: dict) -> bool`
- **Purpose**: Send WhatsApp message via browser automation
- **Method**: Playwright + WhatsApp Web
- **Returns**: True if successful

### Usage Example

```bash
# Send approved WhatsApp replies
python whatsapp_reply.py

# Workflow:
# 1. Reply draft created in Pending_Approval/
# 2. Human moves to Approved/
# 3. Script sends message automatically
# 4. File moved to Done/
```

### Agent Skill Pattern
**Action Skill** - Executes external action (sending WhatsApp message) after human approval.

### Security
- Session stored in `whatsapp_session/` (git-ignored)
- Browser automation via Playwright
- No credentials stored in code

---

## 📱 SKILL-015: LinkedIn Auto-Posting (SILVER)

**Status:** ✅ Active
**File:** `linkedin_poster.py`

Posts content to LinkedIn via browser automation with HITL approval.

### Implementation

```python
class LinkedInPoster:
    """
    Agent Skill: LinkedIn Auto-Posting

    Posts content to LinkedIn via browser automation.
    Requires human approval before posting.
    """
```

### Functions

#### `check_approved_posts() -> list`
- **Purpose**: Check Approved folder for LinkedIn post files
- **Location**: `Vault/Approved/`
- **Returns**: List of approved post files

#### `parse_post_file(filepath: Path) -> dict`
- **Purpose**: Parse LinkedIn post file
- **Extracts**: content, hashtags, metadata
- **Returns**: Dictionary with post data

#### `post_to_linkedin(post_data: dict) -> bool`
- **Purpose**: Post content to LinkedIn
- **Method**: Playwright + LinkedIn Web
- **Steps**:
  1. Navigate to linkedin.com/feed
  2. Click "Start a post"
  3. Type content into editor
  4. Click "Post" button
- **Returns**: True if successful

### Usage Example

```bash
# Generate LinkedIn draft
python linkedin_draft.py

# Post approved content
python linkedin_poster.py

# Workflow:
# 1. Draft created in Plans/
# 2. Human reviews and moves to Approved/
# 3. Script posts to LinkedIn automatically
# 4. File moved to Done/
```

### Agent Skill Pattern
**Action Skill** - Executes external action (posting to social media) after human approval.

### Security
- Session stored in `linkedin_session/` (git-ignored)
- Browser automation via Playwright
- Human approval required before posting

---

## 🔗 Skill Integration Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    SKILL LAYERS                              │
├─────────────────────────────────────────────────────────────┤
│  PERCEPTION (Watchers)                                       │
│  ├── SKILL-001: Gmail Watching                               │
│  ├── SKILL-005: WhatsApp Watching                            │
│  └── SKILL-006: File System Watching                         │
├─────────────────────────────────────────────────────────────┤
│  REASONING (AI Analysis)                                     │
│  ├── SKILL-007: Qwen Reasoning                               │
│  └── SKILL-008: Plan Generation                              │
├─────────────────────────────────────────────────────────────┤
│  ACTION (Execution)                                          │
│  ├── SKILL-002: File Read/Write                              │
│  ├── SKILL-003: Folder Management                            │
│  ├── SKILL-009: HITL Approval                                │
│  └── SKILL-010: LinkedIn Draft                               │
├─────────────────────────────────────────────────────────────┤
│  INTEGRATION (External)                                      │
│  ├── SKILL-011: MCP Configuration                            │
│  └── SKILL-012: Cron Scheduling                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📈 Skill Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Gmail Check Interval | 120 seconds | ✅ 120s |
| WhatsApp Check Interval | 30 seconds | ✅ 30s |
| File System Response | < 1 second | ✅ Real-time |
| Reasoning Loop | 10 seconds | ✅ 10s |
| Plan Generation | < 5 seconds | ✅ <1s |
| Approval Detection | 100% accurate | ✅ Active |

---

## 🚀 Future Skills (GOLD TIER)

| Skill ID | Name | Tier | Description |
|----------|------|------|-------------|
| SKILL-013 | Odoo Integration | GOLD | Accounting system via MCP |
| SKILL-014 | Facebook/Instagram | GOLD | Social media posting |
| SKILL-015 | Twitter (X) | GOLD | Twitter integration |
| SKILL-016 | CEO Briefing | GOLD | Weekly business audit |
| SKILL-017 | Ralph Wiggum Loop | GOLD | Persistence pattern |
| SKILL-018 | Error Recovery | GOLD | Graceful degradation |

---

## 📝 Skill Development Guide

### Creating a New Agent Skill

1. **Define Purpose**: What problem does it solve?
2. **Choose Pattern**: Perception, Reasoning, Action, or Integration
3. **Implement**: Create Python class/function
4. **Document**: Add to this SKILL.md file
5. **Test**: Verify with sample data
6. **Deploy**: Add to watcher rotation or reasoner

### Skill Template

```python
class NewSkill:
    """
    Agent Skill: [Skill Name]
    
    Description: [What it does]
    Pattern: [Perception/Reasoning/Action/Integration]
    Tier: [BRONZE/SILVER/GOLD]
    """
    
    def __init__(self):
        pass
    
    def execute(self, input_data) -> output:
        """Execute the skill"""
        pass
```

---

## 📊 Complete Skill Matrix

| ID | Name | Tier | Category | File | Status |
|----|------|------|----------|------|--------|
| 001 | Gmail Watching | BRONZE | Perception | gmail_watcher.py | ✅ |
| 002 | File Read/Write | BRONZE | Action | base_watcher.py | ✅ |
| 003 | Folder Management | BRONZE | Action | base_watcher.py | ✅ |
| 004 | Dashboard Updates | BRONZE | Reporting | qwen_reasoner.py | ✅ |
| 005 | WhatsApp Watching | SILVER | Perception | whatsapp_watcher.py | ✅ |
| 006 | File System Watching | SILVER | Perception | filesystem_watcher.py | ✅ |
| 007 | Qwen Reasoning | SILVER | Reasoning | qwen_reasoner.py | ✅ |
| 008 | Plan Generation | SILVER | Reasoning | qwen_reasoner.py | ✅ |
| 009 | HITL Approval | SILVER | Action | qwen_reasoner.py | ✅ |
| 010 | LinkedIn Draft | SILVER | Action | linkedin_draft.py | ✅ |
| 011 | MCP Configuration | SILVER | Integration | mcp_config.json | ✅ |
| 012 | Cron Scheduling | SILVER | Orchestration | cron_setup.md | ✅ |
| 013 | Email Reply Sending | SILVER | Action | email_reply.py | ✅ |
| 014 | WhatsApp Reply Sending | SILVER | Action | whatsapp_reply.py | ✅ |
| 015 | LinkedIn Auto-Posting | SILVER | Action | linkedin_poster.py | ✅ |

---

*This SKILL.md file serves as the official documentation for all Agent Skills in the Personal AI Employee system. Update when new skills are added.*
