#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick test to check if WhatsApp session is still valid"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

session_path = Path(__file__).parent / 'whatsapp_session'

print("=" * 60)
print("WhatsApp Login Status Check")
print("=" * 60)
print()

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(session_path),
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox'],
        timeout=30000
    )

    page = browser.pages[0] if browser.pages else browser.new_page()

    print("Loading WhatsApp Web...")
    page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)

    # Check if logged in (chat list visible)
    pane_side = page.query_selector('#pane-side')
    
    if pane_side:
        print()
        print("SUCCESS! WhatsApp is already logged in!")
        print()
        print("Session is valid. You can now run:")
        print("  python whatsapp_reply.py")
        print()
        time.sleep(3)
    else:
        # Check for QR code
        qr_code = page.query_selector('[data-icon="qr-phone"]')
        if qr_code:
            print()
            print("NOT LOGGED IN - QR Code is visible")
            print()
            print("Please scan QR code within next 120 seconds...")
            print()
            
            # Wait for login
            for i in range(60):
                time.sleep(2)
                if page.query_selector('#pane-side'):
                    print()
                    print("SUCCESS! Logged in!")
                    print()
                    print("Now run: python whatsapp_reply.py")
                    break
            else:
                print()
                print("Timeout - QR code expired")
                print("Run this script again to retry")
        else:
            print()
            print("Loading... or unknown state")
            time.sleep(10)
            
            if page.query_selector('#pane-side'):
                print("Logged in!")
            else:
                print("Still not logged in")
                print("May need to clear session and re-authenticate")

    browser.close()

print()
print("Done!")
