#!/usr/bin/env python3
"""
WhatsApp Reply Sender - Fixed Version 2026
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys

def find_input_box(page):
    """Try multiple selectors to find WhatsApp message input box"""
    selectors = [
        'div[contenteditable="true"][data-tab="10"]',
        'div[contenteditable="true"][data-tab="6"]',
        'div[contenteditable="true"][role="textbox"]',
        'footer div[contenteditable="true"]',
        'div[contenteditable="true"][aria-placeholder]',
        'div.lexical-rich-text-input div[contenteditable="true"]',
        'div[aria-label="Type a message"]',
    ]
    for sel in selectors:
        el = page.query_selector(sel)
        if el:
            print(f"  [OK] Input found: {sel[:60]}", flush=True)
            return el
    return None

def find_search_box(page):
    """Try multiple selectors for search box"""
    selectors = [
        'input[aria-label="Search or start new chat"]',
        'div[contenteditable="true"][data-tab="3"]',
        'div[aria-label="Search or start new chat"]',
        'div[role="textbox"][data-tab="3"]',
        'input[type="text"][aria-label]',
    ]
    for sel in selectors:
        el = page.query_selector(sel)
        if el:
            print(f"  [OK] Search box found: {sel[:60]}", flush=True)
            return el
    return None

def send_message_via_clipboard(page, input_box, msg):
    """Send message by typing it (handles multiline)"""
    input_box.click()
    time.sleep(0.5)
    
    # Clear any existing text
    input_box.press('Control+a')
    time.sleep(0.2)
    
    # Type the message line by line (Shift+Enter for newlines)
    lines = msg.split('\n')
    for i, line in enumerate(lines):
        page.keyboard.type(line, delay=20)
        if i < len(lines) - 1:
            page.keyboard.press('Shift+Enter')
    
    time.sleep(0.5)
    page.keyboard.press('Enter')
    time.sleep(1)

def main():
    vault = Path(__file__).parent / 'Vault'
    approved = vault / 'Approved'
    done = vault / 'Done'
    session = vault.parent / 'whatsapp_session'

    # Create Done folder if not exists
    done.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("WhatsApp Reply Sender - FIXED VERSION 2026")
    print("=" * 60)

    files = []
    for f in approved.glob('*.md'):
        try:
            text = f.read_text(encoding='utf-8')
            if 'type: whatsapp_reply' in text:
                files.append((f, text))
        except Exception as e:
            print(f"[!] Could not read {f.name}: {e}")

    if not files:
        print("No approved WhatsApp replies found")
        print("\nTo send a reply:")
        print("1. Edit draft in Pending_Approval/")
        print("2. Move to Approved/")
        print("3. Run this script")
        return

    print(f"Found {len(files)} reply(s)\n")

    for filepath, content in files:
        # Extract recipient
        to = ''
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('to:'):
                to = stripped.split(':', 1)[1].strip().strip('"').strip("'")
                break

        # Extract message from ## Reply Message section
        msg = ''
        if '## Reply Message' in content:
            start = content.find('## Reply Message') + len('## Reply Message')
            end = content.find('\n---', start)
            if end == -1:
                end = len(content)
            msg_section = content[start:end]
            msg_lines = []
            for l in msg_section.split('\n'):
                if l.startswith('#'):
                    continue
                if '**To:**' in l or '**From:**' in l:
                    continue
                msg_lines.append(l)
            msg = '\n'.join(msg_lines).strip()

        # Validate
        if not to:
            print(f"[SKIP] No recipient found in: {filepath.name}")
            continue

        if not msg:
            print(f"[SKIP] No message found in: {filepath.name}")
            continue

        # Check if message is still a placeholder
        placeholder_hints = ['[Edit', '[Write', '[Type', 'placeholder', 'your reply here', 'edit this']
        if any(hint.lower() in msg.lower() for hint in placeholder_hints):
            print(f"[SKIP] Message not edited yet: {filepath.name}")
            print(f"       Please replace placeholder text with actual reply!")
            continue

        if len(msg.strip()) < 5:
            print(f"[SKIP] Message too short: {filepath.name}")
            continue

        print(f"{'='*40}")
        print(f"To  : {to}")
        print(f"Msg : {msg[:80]}{'...' if len(msg) > 80 else ''}")
        print(f"{'='*40}")
        print("Launching browser...", flush=True)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(session),
                    headless=False,
                    args=['--no-sandbox', '--disable-setuid-sandbox'],
                    timeout=30000
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                print("Loading WhatsApp Web...", flush=True)
                page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=30000)
                time.sleep(6)

                # Check login status
                if not page.query_selector('#pane-side'):
                    print("WhatsApp not logged in. Waiting for QR scan (60s)...", flush=True)
                    page.wait_for_selector('#pane-side', timeout=60000)
                    time.sleep(3)
                    print("Logged in!", flush=True)

                # Search for contact
                safe_to = to.strip()
                print(f"Searching for: {safe_to}", flush=True)

                search_box = find_search_box(page)

                if search_box:
                    search_box.click()
                    time.sleep(0.5)
                    search_box.press('Control+a')
                    search_box.type(safe_to, delay=50)
                    time.sleep(2.5)

                    # Try clicking first result
                    result_selectors = [
                        'div[aria-label="Search results."] div[role="listitem"]:first-child',
                        'div#pane-side div[role="listitem"]:first-child',
                        'div[data-testid="cell-frame-container"]:first-child',
                        'div[tabindex="-1"][role="listitem"]:first-child',
                    ]
                    clicked = False
                    for sel in result_selectors:
                        result = page.query_selector(sel)
                        if result:
                            result.click()
                            clicked = True
                            print(f"  Clicked result with: {sel[:50]}", flush=True)
                            break

                    if not clicked:
                        page.keyboard.press('Enter')
                        print("  Pressed Enter on search result", flush=True)

                    time.sleep(2)
                else:
                    print("[!] Search box not found! Cannot proceed.", flush=True)
                    browser.close()
                    continue

                # Verify chat opened
                chat_header = page.query_selector('header')
                if chat_header:
                    print(f"Chat opened successfully", flush=True)
                else:
                    print("[!] Chat may not have opened correctly", flush=True)

                # Find and use message input
                print("Finding message input...", flush=True)
                time.sleep(1)
                input_box = find_input_box(page)

                if input_box:
                    print("Sending message...", flush=True)
                    send_message_via_clipboard(page, input_box, msg)
                    time.sleep(2)

                    print("[OK] Message sent successfully!", flush=True)
                    browser.close()

                    # Move file to Done
                    dest = done / filepath.name
                    filepath.rename(dest)
                    print(f"[OK] Moved to Done: {dest.name}\n")

                else:
                    print("[!] Message input box NOT FOUND", flush=True)
                    print("    Screenshot saved as debug_screenshot.png", flush=True)
                    page.screenshot(path=str(vault.parent / 'debug_screenshot.png'))
                    browser.close()

        except Exception as e:
            print(f"[!] Error processing {filepath.name}: {e}\n")
            import traceback
            traceback.print_exc()

    print("\nDone!")

if __name__ == '__main__':
    main()