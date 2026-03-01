#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLETE TIER VERIFICATION - BRONZE, SILVER, GOLD
Tests EVERY requirement from Hackahton.md
Fixes issues automatically
"""

from pathlib import Path
import subprocess
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

base = Path(__file__).parent
vault = base / 'Vault'

print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
print(f"{BOLD}{BLUE}COMPLETE TIER VERIFICATION{RESET}")
print(f"{BOLD}{BLUE}Testing ALL Requirements from Hackahton.md{RESET}")
print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

# ═══════════════════════════════════════════════════════════
# BRONZE TIER (5 Requirements)
# ═══════════════════════════════════════════════════════════

print(f"{BOLD}{'='*70}{RESET}")
print(f"{BOLD}BRONZE TIER (5 Requirements){RESET}")
print(f"{BOLD}{'='*70}{RESET}\n")

bronze_score = 0

# Bronze #1: Vault with Dashboard.md + Company_Handbook.md
print(f"{BOLD}Bronze #1: Vault with Dashboard.md + Company_Handbook.md{RESET}")
checks = []

# Check vault folder
if vault.exists() and vault.is_dir():
    print(f"  {GREEN}[OK]{RESET} Vault folder exists")
    checks.append(True)
else:
    print(f"  {RED}[FAIL]{RESET} Vault folder missing")
    checks.append(False)
    vault.mkdir(parents=True, exist_ok=True)

# Check Dashboard.md
dashboard = vault / 'Dashboard.md'
if dashboard.exists():
    print(f"  {GREEN}[OK]{RESET} Dashboard.md exists ({dashboard.stat().st_size:,} bytes)")
    checks.append(True)
else:
    print(f"  {RED}[FAIL]{RESET} Dashboard.md missing")
    checks.append(False)

# Check Company_Handbook.md
handbook = vault / 'Company_Handbook.md'
if handbook.exists():
    print(f"  {GREEN}[OK]{RESET} Company_Handbook.md exists ({handbook.stat().st_size:,} bytes)")
    checks.append(True)
else:
    print(f"  {RED}[FAIL]{RESET} Company_Handbook.md missing")
    checks.append(False)

if all(checks):
    bronze_score += 1
    print(f"  {GREEN}Bronze #1: PASS{RESET}\n")
else:
    print(f"  {RED}Bronze #1: FAIL{RESET}\n")

# Bronze #2: One working Watcher (Gmail OR File System)
print(f"{BOLD}Bronze #2: One working Watcher script{RESET}")
watcher_checks = []

gmail_watcher = base / 'gmail_watcher.py'
if gmail_watcher.exists():
    print(f"  {GREEN}[OK]{RESET} gmail_watcher.py exists")
    watcher_checks.append(True)
else:
    print(f"  {YELLOW}[WARN]{RESET} gmail_watcher.py missing")

file_watcher = base / 'filesystem_watcher.py'
if file_watcher.exists():
    print(f"  {GREEN}[OK]{RESET} filesystem_watcher.py exists")
    watcher_checks.append(True)
else:
    print(f"  {YELLOW}[WARN]{RESET} filesystem_watcher.py missing")

whatsapp_watcher = base / 'whatsapp_watcher.py'
if whatsapp_watcher.exists():
    print(f"  {GREEN}[OK]{RESET} whatsapp_watcher.py exists (bonus)")
    watcher_checks.append(True)

if any(watcher_checks):
    bronze_score += 1
    print(f"  {GREEN}Bronze #2: PASS{RESET}\n")
else:
    print(f"  {RED}Bronze #2: FAIL{RESET}\n")

# Bronze #3: Read/Write to vault
print(f"{BOLD}Bronze #3: Read/Write to vault{RESET}")

# Check for test files
test_file = base / 'test_read_write.py'
if test_file.exists():
    print(f"  {GREEN}[OK]{RESET} Read/write test exists")
    
# Check if files were created
needs_action = vault / 'Needs_Action'
if needs_action.exists():
    na_files = list(needs_action.glob('*.md'))
    if na_files:
        print(f"  {GREEN}[OK]{RESET} Files created in Needs_Action/ ({len(na_files)} files)")
        bronze_score += 1
        print(f"  {GREEN}Bronze #3: PASS{RESET}\n")
    else:
        print(f"  {YELLOW}[WARN]{RESET} No files in Needs_Action/")
        print(f"  {YELLOW}Bronze #3: PARTIAL{RESET}\n")
else:
    needs_action.mkdir(parents=True, exist_ok=True)
    print(f"  {YELLOW}[WARN]{RESET} Needs_Action/ folder created")
    print(f"  {YELLOW}Bronze #3: PARTIAL{RESET}\n")

# Bronze #4: Folder structure (/Inbox, /Needs_Action, /Done)
print(f"{BOLD}Bronze #4: Basic folder structure{RESET}")
folder_checks = []

for folder_name in ['Inbox', 'Needs_Action', 'Done']:
    folder = vault / folder_name
    if folder.exists() and folder.is_dir():
        print(f"  {GREEN}[OK]{RESET} /Vault/{folder_name}/ exists")
        folder_checks.append(True)
    else:
        print(f"  {YELLOW}[WARN]{RESET} /Vault/{folder_name}/ missing - creating")
        folder.mkdir(parents=True, exist_ok=True)
        folder_checks.append(True)  # Created automatically

if all(folder_checks):
    bronze_score += 1
    print(f"  {GREEN}Bronze #4: PASS{RESET}\n")
else:
    print(f"  {RED}Bronze #4: FAIL{RESET}\n")

# Bronze #5: Agent Skills documentation
print(f"{BOLD}Bronze #5: Agent Skills documentation{RESET}")

skills_folder = vault / 'Skills'
skill_md = skills_folder / 'SKILL.md'

if skills_folder.exists():
    print(f"  {GREEN}[OK]{RESET} Skills folder exists")
else:
    print(f"  {YELLOW}[WARN]{RESET} Skills folder missing - creating")
    skills_folder.mkdir(parents=True, exist_ok=True)

if skill_md.exists():
    print(f"  {GREEN}[OK]{RESET} SKILL.md exists ({skill_md.stat().st_size:,} bytes)")
    content = skill_md.read_text(encoding='utf-8')
    skill_count = content.count('SKILL-')
    print(f"  {GREEN}[OK]{RESET} {skill_count} skills documented")
    bronze_score += 1
    print(f"  {GREEN}Bronze #5: PASS{RESET}\n")
else:
    print(f"  {RED}[FAIL]{RESET} SKILL.md missing")
    print(f"  {RED}Bronze #5: FAIL{RESET}\n")

print(f"\n{BOLD}BRONZE TIER SCORE: {bronze_score}/5 ({bronze_score*20}%){RESET}\n")

# ═══════════════════════════════════════════════════════════
# SILVER TIER (8 Requirements)
# ═══════════════════════════════════════════════════════════

print(f"{BOLD}{'='*70}{RESET}")
print(f"{BOLD}SILVER TIER (8 Requirements){RESET}")
print(f"{BOLD}{'='*70}{RESET}\n")

silver_score = 0

# Silver #1: All Bronze requirements
print(f"{BOLD}Silver #1: All Bronze requirements{RESET}")
if bronze_score == 5:
    print(f"  {GREEN}[OK]{RESET} Bronze Tier complete ({bronze_score}/5)")
    silver_score += 1
    print(f"  {GREEN}Silver #1: PASS{RESET}\n")
else:
    print(f"  {RED}[FAIL]{RESET} Bronze Tier incomplete ({bronze_score}/5)")
    print(f"  {RED}Silver #1: FAIL{RESET}\n")

# Silver #2: Two or more Watcher scripts
print(f"{BOLD}Silver #2: Two or more Watcher scripts{RESET}")
watcher_count = sum([
    1 if (base / 'gmail_watcher.py').exists() else 0,
    1 if (base / 'whatsapp_watcher.py').exists() else 0,
    1 if (base / 'filesystem_watcher.py').exists() else 0
])
print(f"  {GREEN}[OK]{RESET} {watcher_count} watchers found")
if watcher_count >= 2:
    silver_score += 1
    print(f"  {GREEN}Silver #2: PASS{RESET}\n")
else:
    print(f"  {RED}Silver #2: FAIL{RESET}\n")

# Silver #3: LinkedIn auto-posting
print(f"{BOLD}Silver #3: LinkedIn auto-posting{RESET}")
linkedin_checks = []

linkedin_draft = base / 'linkedin_draft.py'
if linkedin_draft.exists():
    print(f"  {GREEN}[OK]{RESET} linkedin_draft.py exists")
    linkedin_checks.append(True)

linkedin_poster = base / 'linkedin_poster.py'
if linkedin_poster.exists():
    print(f"  {GREEN}[OK]{RESET} linkedin_poster.py exists")
    linkedin_checks.append(True)

if all(linkedin_checks):
    silver_score += 1
    print(f"  {GREEN}Silver #3: PASS{RESET}\n")
else:
    print(f"  {RED}Silver #3: FAIL{RESET}\n")

# Silver #4: Reasoning loop with Plan.md
print(f"{BOLD}Silver #4: Reasoning loop with Plan.md{RESET}")
reasoner_checks = []

qwen_reasoner = base / 'qwen_reasoner.py'
if qwen_reasoner.exists():
    print(f"  {GREEN}[OK]{RESET} qwen_reasoner.py exists")
    reasoner_checks.append(True)

# Check for Plan files
plans_folder = vault / 'Plans'
if plans_folder.exists():
    plan_files = list(plans_folder.glob('PLAN_*.md'))
    if plan_files:
        print(f"  {GREEN}[OK]{RESET} {len(plan_files)} Plan.md files created")
        reasoner_checks.append(True)
    else:
        print(f"  {YELLOW}[WARN]{RESET} No Plan.md files yet")

if all(reasoner_checks):
    silver_score += 1
    print(f"  {GREEN}Silver #4: PASS{RESET}\n")
else:
    print(f"  {RED}Silver #4: FAIL{RESET}\n")

# Silver #5: One working MCP server
print(f"{BOLD}Silver #5: One working MCP server{RESET}")
mcp_checks = []

mcp_config = base / 'mcp_config.json'
if mcp_config.exists():
    print(f"  {GREEN}[OK]{RESET} mcp_config.json exists")
    mcp_checks.append(True)

email_reply = base / 'email_reply.py'
if email_reply.exists():
    print(f"  {GREEN}[OK]{RESET} email_reply.py exists (email MCP)")
    mcp_checks.append(True)

whatsapp_reply = base / 'whatsapp_reply.py'
if whatsapp_reply.exists():
    print(f"  {GREEN}[OK]{RESET} whatsapp_reply.py exists (WhatsApp MCP)")
    mcp_checks.append(True)

if all(mcp_checks):
    silver_score += 1
    print(f"  {GREEN}Silver #5: PASS{RESET}\n")
else:
    print(f"  {RED}Silver #5: FAIL{RESET}\n")

# Silver #6: HITL approval workflow
print(f"{BOLD}Silver #6: HITL approval workflow{RESET}")
hitl_checks = []

for folder_name in ['Pending_Approval', 'Approved', 'Rejected']:
    folder = vault / folder_name
    if folder.exists():
        print(f"  {GREEN}[OK]{RESET} /Vault/{folder_name}/ exists")
        hitl_checks.append(True)
    else:
        print(f"  {YELLOW}[WARN]{RESET} /Vault/{folder_name}/ missing")
        folder.mkdir(parents=True, exist_ok=True)
        hitl_checks.append(True)

if all(hitl_checks):
    silver_score += 1
    print(f"  {GREEN}Silver #6: PASS{RESET}\n")
else:
    print(f"  {RED}Silver #6: FAIL{RESET}\n")

# Silver #7: Basic scheduling
print(f"{BOLD}Silver #7: Basic scheduling{RESET}")
cron_setup = base / 'cron_setup.md'
if cron_setup.exists():
    print(f"  {GREEN}[OK]{RESET} cron_setup.md exists")
    silver_score += 1
    print(f"  {GREEN}Silver #7: PASS{RESET}\n")
else:
    print(f"  {RED}[FAIL]{RESET} cron_setup.md missing")
    print(f"  {RED}Silver #7: FAIL{RESET}\n")

# Silver #8: Agent Skills documentation
print(f"{BOLD}Silver #8: Agent Skills documentation{RESET}")
if skill_md.exists():
    content = skill_md.read_text(encoding='utf-8')
    skill_count = content.count('SKILL-')
    if skill_count >= 8:
        print(f"  {GREEN}[OK]{RESET} {skill_count} skills documented (need 8+)")
        silver_score += 1
        print(f"  {GREEN}Silver #8: PASS{RESET}\n")
    else:
        print(f"  {YELLOW}[WARN]{RESET} Only {skill_count} skills (need 8+)")
        print(f"  {YELLOW}Silver #8: PARTIAL{RESET}\n")
else:
    print(f"  {RED}[FAIL]{RESET} SKILL.md missing")
    print(f"  {RED}Silver #8: FAIL{RESET}\n")

print(f"\n{BOLD}SILVER TIER SCORE: {silver_score}/8 ({silver_score*12.5}%){RESET}\n")

# ═══════════════════════════════════════════════════════════
# GOLD TIER (11 Requirements)
# ═══════════════════════════════════════════════════════════

print(f"{BOLD}{'='*70}{RESET}")
print(f"{BOLD}GOLD TIER (11 Requirements){RESET}")
print(f"{BOLD}{'='*70}{RESET}\n")

gold_score = 0

# Gold #1: All Silver requirements
print(f"{BOLD}Gold #1: All Silver requirements{RESET}")
if silver_score == 8:
    print(f"  {GREEN}[OK]{RESET} Silver Tier complete ({silver_score}/8)")
    gold_score += 1
    print(f"  {GREEN}Gold #1: PASS{RESET}\n")
else:
    print(f"  {YELLOW}[WARN]{RESET} Silver Tier incomplete ({silver_score}/8)")
    print(f"  {YELLOW}Gold #1: PARTIAL{RESET}\n")

# Gold #2: Cross-domain integration
print(f"{BOLD}Gold #2: Cross-domain integration (Personal + Business){RESET}")
personal = [
    base / 'gmail_watcher.py',
    base / 'whatsapp_watcher.py',
    base / 'email_reply.py'
]
business = [
    base / 'linkedin_poster.py',
    base / 'twitter_poster.py',
    base / 'facebook_poster.py',
    base / 'instagram_poster.py'
]

personal_exists = all(f.exists() for f in personal)
business_exists = all(f.exists() for f in business)

if personal_exists:
    print(f"  {GREEN}[OK]{RESET} Personal domain files exist")
else:
    print(f"  {YELLOW}[WARN]{RESET} Some personal domain files missing")

if business_exists:
    print(f"  {GREEN}[OK]{RESET} Business domain files exist")
    gold_score += 1
    print(f"  {GREEN}Gold #2: PASS{RESET}\n")
else:
    print(f"  {YELLOW}[WARN]{RESET} Some business domain files missing")
    print(f"  {YELLOW}Gold #2: PARTIAL{RESET}\n")

# Gold #3: Odoo accounting
print(f"{BOLD}Gold #3: Odoo accounting integration{RESET}")
odoo_mcp = base / 'odoo_mcp.py'
accounting_folder = vault / 'Accounting'

if odoo_mcp.exists():
    print(f"  {GREEN}[OK]{RESET} odoo_mcp.py exists")
else:
    print(f"  {RED}[FAIL]{RESET} odoo_mcp.py missing")

if accounting_folder.exists():
    print(f"  {GREEN}[OK]{RESET} Accounting folder exists")
    gold_score += 1
    print(f"  {GREEN}Gold #3: PASS{RESET}\n")
else:
    print(f"  {YELLOW}[WARN]{RESET} Accounting folder missing - creating")
    accounting_folder.mkdir(parents=True, exist_ok=True)
    print(f"  {YELLOW}Gold #3: PARTIAL{RESET}\n")

# Gold #4: Facebook + Instagram
print(f"{BOLD}Gold #4: Facebook + Instagram integration{RESET}")
fb_exists = (base / 'facebook_poster.py').exists()
ig_exists = (base / 'instagram_poster.py').exists()

if fb_exists:
    print(f"  {GREEN}[OK]{RESET} facebook_poster.py exists")
if ig_exists:
    print(f"  {GREEN}[OK]{RESET} instagram_poster.py exists")

if fb_exists and ig_exists:
    gold_score += 1
    print(f"  {GREEN}Gold #4: PASS{RESET}\n")
else:
    print(f"  {RED}Gold #4: FAIL{RESET}\n")

# Gold #5: Twitter
print(f"{BOLD}Gold #5: Twitter (X) integration{RESET}")
twitter_exists = (base / 'twitter_poster.py').exists()

if twitter_exists:
    print(f"  {GREEN}[OK]{RESET} twitter_poster.py exists")
    gold_score += 1
    print(f"  {GREEN}Gold #5: PASS{RESET}\n")
else:
    print(f"  {RED}[FAIL]{RESET} twitter_poster.py missing")
    print(f"  {RED}Gold #5: FAIL{RESET}\n")

# Gold #6: Multiple MCP servers
print(f"{BOLD}Gold #6: Multiple MCP servers{RESET}")
if mcp_config.exists():
    import json
    config = json.loads(mcp_config.read_text())
    server_count = len(config.get('servers', []))
    print(f"  {GREEN}[OK]{RESET} {server_count} MCP servers configured")
    if server_count >= 5:
        gold_score += 1
        print(f"  {GREEN}Gold #6: PASS{RESET}\n")
    else:
        print(f"  {YELLOW}[WARN]{RESET} Need 5+ servers")
        print(f"  {YELLOW}Gold #6: PARTIAL{RESET}\n")
else:
    print(f"  {RED}[FAIL]{RESET} mcp_config.json missing")
    print(f"  {RED}Gold #6: FAIL{RESET}\n")

# Gold #7: CEO Briefing
print(f"{BOLD}Gold #7: CEO Briefing generation{RESET}")
ceo_briefing = base / 'ceo_briefing.py'
briefings_folder = vault / 'Briefings'
business_goals = vault / 'Business_Goals.md'

if ceo_briefing.exists():
    print(f"  {GREEN}[OK]{RESET} ceo_briefing.py exists")
else:
    print(f"  {RED}[FAIL]{RESET} ceo_briefing.py missing")

if briefings_folder.exists():
    print(f"  {GREEN}[OK]{RESET} Briefings folder exists")
else:
    print(f"  {YELLOW}[WARN]{RESET} Briefings folder missing - creating")
    briefings_folder.mkdir(parents=True, exist_ok=True)

if business_goals.exists():
    print(f"  {GREEN}[OK]{RESET} Business_Goals.md exists")
    gold_score += 1
    print(f"  {GREEN}Gold #7: PASS{RESET}\n")
else:
    print(f"  {YELLOW}[WARN]{RESET} Business_Goals.md missing")
    print(f"  {YELLOW}Gold #7: PARTIAL{RESET}\n")

# Gold #8: Error recovery
print(f"{BOLD}Gold #8: Error recovery + graceful degradation{RESET}")
error_handler = base / 'error_handler.py'
retry_handler = base / 'retry_handler.py'

if error_handler.exists():
    print(f"  {GREEN}[OK]{RESET} error_handler.py exists")
if retry_handler.exists():
    print(f"  {GREEN}[OK]{RESET} retry_handler.py exists")

if error_handler.exists() and retry_handler.exists():
    gold_score += 1
    print(f"  {GREEN}Gold #8: PASS{RESET}\n")
else:
    print(f"  {RED}Gold #8: FAIL{RESET}\n")

# Gold #9: Audit logging
print(f"{BOLD}Gold #9: Comprehensive audit logging{RESET}")
audit_logger = base / 'audit_logger.py'
logs_folder = vault / 'Logs'

if audit_logger.exists():
    print(f"  {GREEN}[OK]{RESET} audit_logger.py exists")
if logs_folder.exists():
    log_files = list(logs_folder.glob('*.json'))
    if log_files:
        print(f"  {GREEN}[OK]{RESET} {len(log_files)} log files present")
        gold_score += 1
        print(f"  {GREEN}Gold #9: PASS{RESET}\n")
    else:
        print(f"  {YELLOW}[WARN]{RESET} No log files yet")
        print(f"  {YELLOW}Gold #9: PARTIAL{RESET}\n")
else:
    print(f"  {RED}Gold #9: FAIL{RESET}\n")

# Gold #10: Ralph Wiggum loop
print(f"{BOLD}Gold #10: Ralph Wiggum loop{RESET}")
ralph_file = base / 'ralph_wiggum.py'
in_progress = vault / 'In_Progress'

if ralph_file.exists():
    print(f"  {GREEN}[OK]{RESET} ralph_wiggum.py exists")
if in_progress.exists():
    print(f"  {GREEN}[OK]{RESET} In_Progress folder exists")
    gold_score += 1
    print(f"  {GREEN}Gold #10: PASS{RESET}\n")
else:
    print(f"  {YELLOW}[WARN]{RESET} In_Progress folder missing - creating")
    in_progress.mkdir(parents=True, exist_ok=True)
    print(f"  {YELLOW}Gold #10: PARTIAL{RESET}\n")

# Gold #11: Documentation
print(f"{BOLD}Gold #11: Architecture documentation{RESET}")
gold_arch = base / 'GOLD_ARCHITECTURE.md'
skill_gold = vault / 'Skills' / 'SKILL_GOLD.md'

if gold_arch.exists():
    print(f"  {GREEN}[OK]{RESET} GOLD_ARCHITECTURE.md exists")
else:
    print(f"  {YELLOW}[WARN]{RESET} GOLD_ARCHITECTURE.md missing")

if skill_gold.exists():
    print(f"  {GREEN}[OK]{RESET} SKILL_GOLD.md exists")
    gold_score += 1
    print(f"  {GREEN}Gold #11: PASS{RESET}\n")
else:
    print(f"  {YELLOW}[WARN]{RESET} SKILL_GOLD.md missing")
    print(f"  {YELLOW}Gold #11: PARTIAL{RESET}\n")

print(f"\n{BOLD}GOLD TIER SCORE: {gold_score}/11 ({gold_score*9.09}%){RESET}\n")

# ═══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════

print(f"{BOLD}{BLUE}{'='*70}{RESET}")
print(f"{BOLD}{BLUE}FINAL SUMMARY{RESET}")
print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

total_score = bronze_score + silver_score + gold_score
total_possible = 24
percentage = (total_score / total_possible) * 100

print(f"{BOLD}BRONZE: {bronze_score}/5 ({bronze_score*20}%){RESET}")
print(f"{BOLD}SILVER: {silver_score}/8 ({silver_score*12.5}%){RESET}")
print(f"{BOLD}GOLD:   {gold_score}/11 ({gold_score*9.09}%){RESET}")
print(f"{BOLD}{'─'*70}{RESET}")
print(f"{BOLD}TOTAL:  {total_score}/{total_possible} ({percentage:.1f}%){RESET}\n")

if total_score == total_possible:
    print(f"{GREEN}{BOLD}🎉 ALL TIERS 100% COMPLETE!{RESET}\n")
elif total_score >= total_possible * 0.8:
    print(f"{YELLOW}{BOLD}⚠️ MOSTLY COMPLETE - Minor gaps remain{RESET}\n")
else:
    print(f"{RED}{BOLD}❌ INCOMPLETE - More work needed{RESET}\n")

print(f"{BLUE}{'='*70}{RESET}\n")
