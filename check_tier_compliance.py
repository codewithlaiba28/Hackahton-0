#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRONZE & SILVER TIER COMPLIANCE CHECKER
Personal AI Employee Hackathon 0
Based on requirements from Hackahton.md (Lines 118-150)
"""

from pathlib import Path
import json
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Use ASCII-safe icons for Windows
CHECK_PASS = '[OK]'
CHECK_FAIL = '[FAIL]'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(70)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_check(name, status, details=""):
    icon = CHECK_PASS if status else CHECK_FAIL
    color = GREEN if status else RED
    print(f"{icon} {color}{name}{RESET}")
    if details:
        print(f"   {YELLOW}-> {details}{RESET}")

def check_file_exists(filepath, description=""):
    """Check if a file exists"""
    exists = filepath.exists()
    if exists:
        size = filepath.stat().st_size
        details = f"{size:,} bytes" if description else ""
    else:
        details = "File not found"
    return exists, details

def check_folder_exists(folderpath):
    """Check if a folder exists"""
    exists = folderpath.exists() and folderpath.is_dir()
    details = "Folder exists" if exists else "Folder not found"
    return exists, details

def count_files(folder, pattern="*.md"):
    """Count files matching pattern in folder"""
    if not folder.exists():
        return 0
    return len(list(folder.glob(pattern)))

def check_file_contains(filepath, search_text):
    """Check if file contains specific text"""
    if not filepath.exists():
        return False, "File not found"
    try:
        content = filepath.read_text(encoding='utf-8')
        found = search_text.lower() in content.lower()
        details = f"Found '{search_text}'" if found else f"'{search_text}' not found"
        return found, details
    except:
        return False, "Error reading file"

def main():
    base = Path(__file__).parent
    vault = base / 'Vault'
    
    print_header("BRONZE & SILVER TIER COMPLIANCE CHECK")
    print(f"Base Directory: {base}")
    print(f"Vault Directory: {vault}")
    
    # ═══════════════════════════════════════════════════════════
    # BRONZE TIER REQUIREMENTS
    # ═══════════════════════════════════════════════════════════
    
    print_header("BRONZE TIER REQUIREMENTS (5 Total)")
    
    bronze_score = 0
    
    # Bronze Requirement 1: Obsidian vault with Dashboard.md and Company_Handbook.md
    print(f"{BOLD}Bronze #1: Obsidian vault with Dashboard.md and Company_Handbook.md{RESET}")
    
    vault_exists, _ = check_folder_exists(vault)
    print_check("Vault folder exists", vault_exists)
    
    dashboard_exists, dashboard_details = check_file_exists(vault / 'Dashboard.md')
    print_check("Dashboard.md exists", dashboard_exists, dashboard_details)
    
    handbook_exists, handbook_details = check_file_exists(vault / 'Company_Handbook.md')
    print_check("Company_Handbook.md exists", handbook_exists, handbook_details)
    
    # Check Dashboard sections
    if dashboard_exists:
        content = (vault / 'Dashboard.md').read_text(encoding='utf-8')
        has_bank = 'Bank Balance' in content or 'bank' in content.lower()
        has_messages = 'Pending Messages' in content or 'messages' in content.lower()
        has_projects = 'Active Projects' in content or 'projects' in content.lower()
        print_check("Dashboard has required sections", has_bank and has_messages and has_projects)
    
    bronze_1_pass = vault_exists and dashboard_exists and handbook_exists
    if bronze_1_pass:
        bronze_score += 1
    print(f"\n{YELLOW}Bronze #1 Status: {'PASS' if bronze_1_pass else 'FAIL'}{RESET}\n")
    
    # Bronze Requirement 2: One working Watcher script
    print(f"{BOLD}Bronze #2: One working Watcher script (Gmail OR file system){RESET}")
    
    gmail_watcher = base / 'gmail_watcher.py'
    file_watcher = base / 'filesystem_watcher.py'
    whatsapp_watcher = base / 'whatsapp_watcher.py'
    
    gmail_exists, gmail_details = check_file_exists(gmail_watcher)
    print_check("gmail_watcher.py exists", gmail_exists, gmail_details)
    
    file_watcher_exists, file_watcher_details = check_file_exists(file_watcher)
    print_check("filesystem_watcher.py exists", file_watcher_exists, file_watcher_details)
    
    whatsapp_exists, whatsapp_details = check_file_exists(whatsapp_watcher)
    print_check("whatsapp_watcher.py exists", whatsapp_exists, whatsapp_details)
    
    # Check for base class
    base_watcher = base / 'base_watcher.py'
    base_exists, _ = check_file_exists(base_watcher)
    print_check("base_watcher.py exists (base class)", base_exists)
    
    bronze_2_pass = gmail_exists or file_watcher_exists or whatsapp_exists
    if bronze_2_pass:
        bronze_score += 1
    print(f"\n{YELLOW}Bronze #2 Status: {'PASS' if bronze_2_pass else 'FAIL'}{RESET}\n")

    # Bronze Requirement 3: Claude Code reading/writing to vault
    print(f"{BOLD}Bronze #3: Read/Write capability to vault{RESET}")

    # Check if Needs_Action folder has files (evidence of writing)
    needs_action = vault / 'Needs_Action'
    na_count = count_files(needs_action)
    print_check(f"Files in Needs_Action/", na_count > 0, f"{na_count} files found")

    # Check if Done folder has files (evidence of processing)
    done_folder = vault / 'Done'
    done_count = count_files(done_folder)
    print_check(f"Files in Done/", done_count > 0, f"{done_count} files processed")

    # Check for test files
    test_file = base / 'test_read_write.py'
    test_exists, _ = check_file_exists(test_file)
    print_check("test_read_write.py exists (read/write test)", test_exists)

    bronze_3_pass = na_count > 0 or done_count > 0
    if bronze_3_pass:
        bronze_score += 1
    print(f"\n{YELLOW}Bronze #3 Status: {'PASS' if bronze_3_pass else 'FAIL'}{RESET}\n")

    # Bronze Requirement 4: Basic folder structure
    print(f"{BOLD}Bronze #4: Basic folder structure (/Inbox, /Needs_Action, /Done){RESET}")

    inbox = vault / 'Inbox'
    inbox_exists, _ = check_folder_exists(inbox)
    print_check("/Vault/Inbox exists", inbox_exists)

    na_exists, _ = check_folder_exists(needs_action)
    print_check("/Vault/Needs_Action exists", na_exists)

    done_exists, _ = check_folder_exists(done_folder)
    print_check("/Vault/Done exists", done_exists)

    # Additional folders (bonus)
    plans = vault / 'Plans'
    plans_exists, _ = check_folder_exists(plans)
    print_check("/Vault/Plans exists (bonus)", plans_exists)

    pending = vault / 'Pending_Approval'
    pending_exists, _ = check_folder_exists(pending)
    print_check("/Vault/Pending_Approval exists (bonus)", pending_exists)

    approved = vault / 'Approved'
    approved_exists, _ = check_folder_exists(approved)
    print_check("/Vault/Approved exists (bonus)", approved_exists)

    bronze_4_pass = inbox_exists and na_exists and done_exists
    if bronze_4_pass:
        bronze_score += 1
    print(f"\n{YELLOW}Bronze #4 Status: {'PASS' if bronze_4_pass else 'FAIL'}{RESET}\n")

    # Bronze Requirement 5: Agent Skills documentation
    print(f"{BOLD}Bronze #5: Agent Skills documentation{RESET}")

    skills_folder = vault / 'Skills'
    skills_exists, _ = check_folder_exists(skills_folder)
    print_check("/Vault/Skills folder exists", skills_exists)

    skill_md = skills_folder / 'SKILL.md'
    skill_exists, skill_details = check_file_exists(skill_md)
    print_check("SKILL.md exists", skill_exists, skill_details)

    if skill_exists:
        # Check for skill documentation
        content = skill_md.read_text(encoding='utf-8')
        has_skill_pattern = 'SKILL-' in content or 'skill' in content.lower()
        print_check("Skills documented (SKILL- pattern)", has_skill_pattern)

        # Count skills
        skill_count = content.count('SKILL-')
        print_check(f"Number of skills documented", skill_count > 0, f"{skill_count} skills found")

    bronze_5_pass = skills_exists and skill_exists
    if bronze_5_pass:
        bronze_score += 1
    print(f"\n{YELLOW}Bronze #5 Status: {'PASS' if bronze_5_pass else 'FAIL'}{RESET}\n")

    # ═══════════════════════════════════════════════════════════
    # SILVER TIER REQUIREMENTS
    # ═══════════════════════════════════════════════════════════

    print_header("SILVER TIER REQUIREMENTS (8 Total)")
    print("(All Bronze requirements must also be met)\n")

    silver_score = 0

    # Silver Requirement 1: All Bronze requirements
    print(f"{BOLD}Silver #1: All Bronze requirements{RESET}")
    bronze_all_pass = bronze_score == 5
    print_check(f"Bronze Tier complete ({bronze_score}/5)", bronze_all_pass)
    if bronze_all_pass:
        silver_score += 1
    print(f"\n{YELLOW}Silver #1 Status: {'PASS' if bronze_all_pass else 'FAIL'}{RESET}\n")

    # Silver Requirement 2: Two or more Watcher scripts
    print(f"{BOLD}Silver #2: Two or more Watcher scripts{RESET}")

    watcher_count = sum([gmail_exists, whatsapp_exists, file_watcher_exists])
    print_check(f"Number of watchers", watcher_count >= 2, f"{watcher_count} watchers found")

    if gmail_exists:
        print_check("  - Gmail Watcher", True)
    if whatsapp_exists:
        print_check("  - WhatsApp Watcher", True)
    if file_watcher_exists:
        print_check("  - File System Watcher", True)

    if watcher_count >= 2:
        silver_score += 1
    print(f"\n{YELLOW}Silver #2 Status: {'PASS' if watcher_count >= 2 else 'FAIL'}{RESET}\n")

    # Silver Requirement 3: Automatically Post on LinkedIn
    print(f"{BOLD}Silver #3: LinkedIn auto-posting{RESET}")

    linkedin_draft = base / 'linkedin_draft.py'
    ld_exists, ld_details = check_file_exists(linkedin_draft)
    print_check("linkedin_draft.py exists", ld_exists, ld_details)

    linkedin_poster = base / 'linkedin_poster.py'
    lp_exists, lp_details = check_file_exists(linkedin_poster)
    print_check("linkedin_poster.py exists", lp_exists, lp_details)

    # Check for LinkedIn drafts
    linkedin_drafts = count_files(vault / 'Plans', 'LINKEDIN*.md')
    print_check(f"LinkedIn drafts created", linkedin_drafts > 0, f"{linkedin_drafts} drafts found")

    if ld_exists and lp_exists:
        silver_score += 1
    print(f"\n{YELLOW}Silver #3 Status: {'PASS' if ld_exists and lp_exists else 'FAIL'}{RESET}\n")

    # Silver Requirement 4: Claude reasoning loop with Plan.md
    print(f"{BOLD}Silver #4: Reasoning loop that creates Plan.md files{RESET}")

    reasoner = base / 'qwen_reasoner.py'
    reasoner_exists, reasoner_details = check_file_exists(reasoner)
    print_check("qwen_reasoner.py exists", reasoner_exists, reasoner_details)

    # Check for Plan files
    plan_count = count_files(plans, 'PLAN_*.md')
    print_check(f"Plan.md files created", plan_count > 0, f"{plan_count} plans found")

    if reasoner_exists and plan_count > 0:
        silver_score += 1
    print(f"\n{YELLOW}Silver #4 Status: {'PASS' if reasoner_exists and plan_count > 0 else 'FAIL'}{RESET}\n")

    # Silver Requirement 5: One working MCP server
    print(f"{BOLD}Silver #5: One working MCP server for external action{RESET}")

    mcp_config = base / 'mcp_config.json'
    mcp_exists, mcp_details = check_file_exists(mcp_config)
    print_check("mcp_config.json exists", mcp_exists, mcp_details)

    # Check for reply scripts (MCP-like actions)
    email_reply = base / 'email_reply.py'
    er_exists, _ = check_file_exists(email_reply)
    print_check("email_reply.py exists (email action)", er_exists)

    whatsapp_reply = base / 'whatsapp_reply.py'
    wr_exists, _ = check_file_exists(whatsapp_reply)
    print_check("whatsapp_reply.py exists (WhatsApp action)", wr_exists)

    if mcp_exists and (er_exists or wr_exists):
        silver_score += 1
    print(f"\n{YELLOW}Silver #5 Status: {'PASS' if mcp_exists and (er_exists or wr_exists) else 'FAIL'}{RESET}\n")

    # Silver Requirement 6: Human-in-the-loop approval workflow
    print(f"{BOLD}Silver #6: HITL approval workflow{RESET}")

    # Check folders
    pending_exists, _ = check_folder_exists(vault / 'Pending_Approval')
    print_check("/Vault/Pending_Approval exists", pending_exists)

    approved_exists, _ = check_folder_exists(vault / 'Approved')
    print_check("/Vault/Approved exists", approved_exists)

    rejected = vault / 'Rejected'
    rejected_exists, _ = check_folder_exists(rejected)
    print_check("/Vault/Rejected exists", rejected_exists)

    # Check for approval files
    approval_count = count_files(vault / 'Pending_Approval')
    print_check(f"Approval files exist", approval_count > 0, f"{approval_count} pending approvals")

    approved_count = count_files(vault / 'Approved')
    print_check(f"Approved files exist", approved_count > 0, f"{approved_count} approved actions")

    if pending_exists and approved_exists and (approval_count > 0 or approved_count > 0):
        silver_score += 1
    print(f"\n{YELLOW}Silver #6 Status: {'PASS' if pending_exists and approved_exists else 'FAIL'}{RESET}\n")

    # Silver Requirement 7: Basic scheduling via cron or Task Scheduler
    print(f"{BOLD}Silver #7: Basic scheduling{RESET}")

    cron_setup = base / 'cron_setup.md'
    cron_exists, cron_details = check_file_exists(cron_setup)
    print_check("cron_setup.md exists", cron_exists, cron_details)

    if cron_exists:
        # Check for scheduling content
        content = (base / 'cron_setup.md').read_text(encoding='utf-8')
        has_cron = 'cron' in content.lower() or 'schedule' in content.lower()
        print_check("Contains scheduling instructions", has_cron)

    if cron_exists:
        silver_score += 1
    print(f"\n{YELLOW}Silver #7 Status: {'PASS' if cron_exists else 'FAIL'}{RESET}\n")

    # Silver Requirement 8: All AI functionality as Agent Skills
    print(f"{BOLD}Silver #8: Agent Skills documentation (continued from Bronze){RESET}")

    if skill_exists:
        content = skill_md.read_text(encoding='utf-8')

        # Check for Silver tier skills
        has_whatsapp = 'whatsapp' in content.lower()
        print_check("WhatsApp skills documented", has_whatsapp)

        has_linkedin = 'linkedin' in content.lower()
        print_check("LinkedIn skills documented", has_linkedin)

        has_reasoning = 'reason' in content.lower() or 'plan' in content.lower()
        print_check("Reasoning skills documented", has_reasoning)

        has_hitl = 'approval' in content.lower() or 'HITL' in content
        print_check("HITL skills documented", has_hitl)

        skill_count = content.count('SKILL-')
        print_check(f"Total skills documented", skill_count >= 8, f"{skill_count} skills (need 8+)")

    silver_8_pass = skill_exists and skill_count >= 8
    if silver_8_pass:
        silver_score += 1
    print(f"\n{YELLOW}Silver #8 Status: {'PASS' if silver_8_pass else 'FAIL'}{RESET}\n")

    # ═══════════════════════════════════════════════════════════
    # FINAL SUMMARY
    # ═══════════════════════════════════════════════════════════

    print_header("FINAL SUMMARY")

    print(f"{BOLD}BRONZE TIER:{RESET}")
    print(f"  Score: {bronze_score}/5 ({bronze_score*20}%)")
    bronze_status = "COMPLETE" if bronze_score == 5 else "INCOMPLETE"
    bronze_color = GREEN if bronze_score == 5 else RED
    print(f"  Status: {bronze_color}{bronze_status}{RESET}")

    print(f"\n{BOLD}SILVER TIER:{RESET}")
    print(f"  Score: {silver_score}/8 ({silver_score*12.5}%)")
    silver_status = "COMPLETE" if silver_score == 8 else "INCOMPLETE"
    silver_color = GREEN if silver_score == 8 else RED
    print(f"  Status: {silver_color}{silver_status}{RESET}")

    print(f"\n{BOLD}OVERALL:{RESET}")
    total_score = bronze_score + silver_score
    total_possible = 13
    percentage = (total_score / total_possible) * 100

    print(f"  Total Score: {total_score}/{total_possible} ({percentage:.1f}%)")

    if bronze_score == 5 and silver_score == 8:
        print(f"\n{GREEN}{BOLD}CONGRATULATIONS! BOTH TIERS COMPLETE!{RESET}")
    elif bronze_score == 5:
        print(f"\n{YELLOW}{BOLD}BRONZE TIER COMPLETE - Work on Silver Tier{RESET}")
    else:
        print(f"\n{RED}{BOLD}BRONZE TIER INCOMPLETE - Complete Bronze first{RESET}")

    print(f"\n{BLUE}{'='*70}{RESET}\n")

if __name__ == '__main__':
    main()
