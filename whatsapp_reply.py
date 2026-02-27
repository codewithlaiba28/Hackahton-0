#!/usr/bin/env python3
"""
WhatsApp Reply Sender - Final Working Version
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys

def main():
    vault = Path(__file__).parent / 'Vault'
    approved = vault / 'Approved'
    done = vault / 'Done'
    session = vault.parent / 'whatsapp_session'
    
    print("=" * 60)
    print("WhatsApp Reply Sender - SILVER TIER")
    print("=" * 60)
    
    files = [f for f in approved.glob('*.md') if 'type: whatsapp_reply' in f.read_text()]
    
    if not files:
        print("No approved WhatsApp replies found")
        print("\nTo send a reply:")
        print("1. Edit draft in Pending_Approval/")
        print("2. Move to Approved/")
        print("3. Run this script")
        return
    
    print(f"Found {len(files)} reply(s)\n")
    
    for filepath in files:
        content = filepath.read_text()
        
        # Extract recipient and message
        to = ''
        msg = ''
        
        for line in content.split('\n'):
            if line.strip().startswith('to:'):
                to = line.split(':', 1)[1].strip()
        
        if '## Reply Message' in content:
            start = content.find('## Reply Message') + 18
            end = content.find('---', start)
            if end == -1:
                end = len(content)
            msg_section = content[start:end]
            msg_lines = [l for l in msg_section.split('\n') if not l.startswith('#') and '**To:**' not in l and l.strip()]
            msg = '\n'.join(msg_lines).strip()
        
        if not to:
            print(f"[SKIP] No recipient: {filepath.name}")
            continue
        
        if not msg or '[Edit' in msg or 'placeholder' in msg.lower():
            print(f"[SKIP] Message not edited: {filepath.name}")
            print(f"       Please edit the file first!")
            continue
        
        print(f"To: {to}")
        print(f"Msg: {msg[:50]}...")
        print(f"Sending...", flush=True)
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(session),
                    headless=False,
                    args=['--no-sandbox', '--disable-setuid-sandbox'],
                    timeout=30000
                )
                
                page = browser.pages[0]
                
                print("Loading WhatsApp...", flush=True)
                page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=30000)
                time.sleep(5)
                
                # Check if loaded
                if not page.query_selector('#pane-side'):
                    print("Waiting for QR scan (30s)...", flush=True)
                    time.sleep(30)
                
                # Search for contact
                print(f"Searching: {to}...", flush=True)
                
                # Try search box
                search = page.query_selector('input[aria-label="Search or start new chat"]')
                if search:
                    search.click()
                    time.sleep(1)
                    search.fill(to)
                    time.sleep(2)
                    page.keyboard.press('Enter')
                    time.sleep(2)
                    print("Chat opened", flush=True)
                else:
                    print("Search not found, trying keyboard...", flush=True)
                    page.keyboard.press('Tab')
                    time.sleep(0.5)
                    page.keyboard.type(to)
                    time.sleep(2)
                    page.keyboard.press('Enter')
                    time.sleep(2)
                
                # Send message
                print("Sending message...", flush=True)
                
                # Find input
                input_box = page.query_selector('div[contenteditable="true"][data-tab="10"]')
                if input_box:
                    input_box.click()
                    time.sleep(0.5)
                    input_box.fill(msg)
                    time.sleep(0.5)
                    page.keyboard.press('Enter')
                    time.sleep(1)
                    print("[OK] Message sent!", flush=True)
                    
                    time.sleep(2)
                    browser.close()
                    
                    # Move to Done
                    dest = done / filepath.name
                    filepath.rename(dest)
                    print(f"[OK] Moved to Done: {dest.name}\n")
                else:
                    print("[!] Input box not found", flush=True)
                    browser.close()
                    
        except Exception as e:
            print(f"[!] Error: {e}\n")

if __name__ == '__main__':
    main()
