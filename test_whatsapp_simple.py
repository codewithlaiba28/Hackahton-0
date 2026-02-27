#!/usr/bin/env python3
"""
Simple WhatsApp Test - Just check if session works

Usage: python test_whatsapp_simple.py
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time

session_path = Path(__file__).parent / 'whatsapp_session'

print("=" * 60)
print("WhatsApp Simple Test")
print("=" * 60)
print()
print(f"Session folder: {session_path}")
print()

with sync_playwright() as p:
    print("Launching browser...")
    browser = p.chromium.launch_persistent_context(
        str(session_path),
        headless=False,
        args=['--window-size=1280,720']
    )
    
    page = browser.pages[0]
    
    print("Going to WhatsApp Web...")
    page.goto('https://web.whatsapp.com', wait_until='domcontentloaded')
    
    print()
    print("Waiting 60 seconds...")
    print("If QR code shows, scan it with your phone.")
    print("If chats show, you're already connected!")
    print()
    
    # Wait and check
    for i in range(60):
        time.sleep(1)
        
        # Check for chat list
        chat_list = page.query_selector('[data-testid="chat-list"]')
        if chat_list:
            print()
            print("✅ SUCCESS! WhatsApp is connected!")
            print()
            print("Session is working. Now run:")
            print("  python whatsapp_watcher.py")
            print()
            time.sleep(5)
            break
        
        if i % 10 == 0:
            print(f"  Waiting... ({i}s)")
    
    browser.close()

print("=" * 60)
print("Test Complete")
print("=" * 60)
