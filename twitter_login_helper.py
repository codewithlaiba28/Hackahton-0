#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter Manual Login Helper - Gives you time to login
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

session_path = Path('twitter_session')

print("\n" + "="*70)
print("TWITTER LOGIN HELPER")
print("="*70)
print("\nThis will open Twitter and give you 3 minutes to login.")
print("After login, the session will be saved for future use.")
print("\nOpening Twitter in 3 seconds...")
time.sleep(3)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(session_path),
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox'],
        timeout=60000
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("\nOpening Twitter...")
    page.goto('https://twitter.com', wait_until='domcontentloaded', timeout=30000)
    
    print("\n" + "="*70)
    print("LOGIN INSTRUCTIONS:")
    print("="*70)
    print("\n1. You have 3 MINUTES to login")
    print("2. Enter your username/email")
    print("3. Enter your password")
    print("4. Complete any verification")
    print("5. Wait for home timeline to load")
    print("\nThe browser will stay open. Login at your own pace.")
    print("After successful login, just close the browser.")
    print("\nSession will be saved to: twitter_session/")
    print("="*70)
    
    # Wait for 3 minutes
    for i in range(90):
        time.sleep(2)
        
        # Check if logged in
        tweet_button = page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
        if tweet_button:
            print("\n[OK] Login detected! Twitter is ready.")
            print("You can now close the browser or continue using Twitter.")
            break
        
        if i % 15 == 0 and i > 0:
            print(f"  Still waiting... ({(i+1)*2}s/180s)")
    
    browser.close()

print("\n" + "="*70)
print("SESSION SAVED")
print("="*70)
print("\nNext time you run twitter_poster.py, you'll be automatically logged in!")
print("\nNow test posting with:")
print('  python twitter_poster.py --text "Test tweet" --vault Vault')
print()
