#!/usr/bin/env python3
"""
WhatsApp Debug - Find correct selectors

Usage: python whatsapp_debug.py
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import os

# Fix Windows console encoding
os.system('chcp 65001 > nul')

session_path = Path(__file__).parent / 'whatsapp_session'

print("=" * 60)
print("WhatsApp Debug - Finding Selectors")
print("=" * 60)
print()

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(session_path),
        headless=False,
        args=['--window-size=1280,720']
    )
    
    page = browser.pages[0]
    
    print("Loading WhatsApp Web...")
    page.goto('https://web.whatsapp.com', wait_until='networkidle')
    
    print()
    print("Waiting 30 seconds for page to load...")
    print("Please wait, DO NOT close the browser!")
    print()
    time.sleep(30)
    
    # Try different selectors
    selectors_to_test = [
        '[data-testid="chat-list"]',
        '[data-testid="chat-list-panel"]',
        '#pane-side',
        '#app',
        'div[role="application"]',
        'div._9pDj',
        'div[tabindex="2"]',
        'div[aria-label*="chat"]',
        'div[aria-label*="Chat"]',
        'div[aria-label*="unread"]',
        'span[title*="unread"]',
        'div[role="listitem"]',
    ]
    
    print("Testing selectors...")
    print()
    
    found_selectors = []
    
    for selector in selectors_to_test:
        try:
            element = page.query_selector(selector)
            if element:
                print(f"  [OK] FOUND: {selector}")
                found_selectors.append(selector)
                try:
                    text = element.inner_text()[:100].replace('\n', ' ')
                    print(f"       Text: {text[:50]}...")
                except:
                    pass
            else:
                print(f"  [--] Not found: {selector}")
        except Exception as e:
            print(f"  [!!] Error: {selector} - {str(e)[:50]}")
    
    print()
    print("=" * 60)
    print(f"Found {len(found_selectors)} working selector(s)")
    if found_selectors:
        print("Working selectors:")
        for s in found_selectors:
            print(f"  - {s}")
    
    print()
    print("Saving screenshot...")
    page.screenshot(path='whatsapp_debug.png')
    print("Screenshot saved: whatsapp_debug.png")
    
    browser.close()

print()
print("=" * 60)
print("Debug Complete")
print("=" * 60)
