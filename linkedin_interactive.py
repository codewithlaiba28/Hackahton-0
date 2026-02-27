#!/usr/bin/env python3
"""
LinkedIn Interactive Poster - Manual login + auto post

Usage: python linkedin_interactive.py --image image.png
"""

import sys
import codecs
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

vault_path = Path(__file__).parent / 'Vault'
session_path = vault_path.parent / 'linkedin_session'
image_path = Path('image.png')

print("=" * 60)
print("LinkedIn Interactive Poster")
print("=" * 60)
print()
print("Step 1: Opening LinkedIn in browser...")
print("Step 2: LOGIN to your account")
print("Step 3: Close browser when ready")
print()

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        session_path,
        headless=False,
        args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("Opening LinkedIn... Please LOGIN now!")
    page.goto('https://www.linkedin.com/feed/')
    
    print("\nBrowser is open. Login to LinkedIn and stay logged in.")
    print("Close browser when done - session will be saved.")
    print("\nPress Ctrl+C when done...")
    
    try:
        input()  # Wait for user to close
    except KeyboardInterrupt:
        pass
    
    browser.close()

print("\n✅ Session saved!")
print("\nNow run: python linkedin_poster.py --image image.png")
