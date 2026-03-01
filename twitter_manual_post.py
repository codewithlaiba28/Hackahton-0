#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TWITTER MANUAL POST - GUARANTEED TO WORK
Opens browser, you handle overlays, script types content
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys
import codecs

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

VAULT = Path(__file__).parent / 'Vault'
SESSION = VAULT.parent / 'twitter_session'

# Read the approved post
approved_file = VAULT / 'Approved' / 'TWITTER_GOLD_TIER_TEST.md'
if not approved_file.exists():
    print("No approved post found!")
    exit(1)

content = approved_file.read_text(encoding='utf-8')

# Extract tweet text
tweet_text = ""
if '## Tweet Content' in content:
    tweet_text = content.split('## Tweet Content')[1].split('##')[0].strip()

if len(tweet_text) > 280:
    tweet_text = tweet_text[:280]

print("\n" + "="*70)
print("TWITTER MANUAL POST")
print("="*70)
print(f"\nTweet content ({len(tweet_text)} chars):")
print("-"*70)
print(tweet_text)
print("-"*70)

print("\nOpening Twitter in browser...")
print("STEP 1: Login if needed")
print("STEP 2: Dismiss any overlays/cookies")
print("STEP 3: Press 't' for new tweet (or click Tweet button)")
print("STEP 4: Script will auto-type the content")
print("STEP 5: You click 'Post'")
print("="*70)
print("\nBrowser opening in 3 seconds...")
time.sleep(3)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        SESSION,
        headless=False,
        args=['--start-maximized']
    )
    page = browser.pages[0]
    
    # Go to Twitter
    page.goto('https://twitter.com')
    
    print("\n" + "="*70)
    print("BROWSER OPENED!")
    print("="*70)
    print("\nINSTRUCTIONS:")
    print("  1. Login to Twitter (if not already)")
    print("  2. Dismiss any overlays/cookies (press Escape or X)")
    print("  3. Press 't' key for new tweet OR click Tweet button")
    print("  4. Come back to this window and press Enter")
    print("\nScript will auto-type the content when you press Enter!")
    print("="*70)
    
    # Wait for user to login and open composer
    input("\nPress Enter when composer is open...")
    
    # Type content
    print("\nTyping content...")
    page.keyboard.type(tweet_text, delay=50)
    print("Content typed!")
    
    print("\n" + "="*70)
    print("CLICK 'Post' BUTTON NOW!")
    print("="*70)
    print("Waiting 60 seconds...")
    time.sleep(60)
    
    browser.close()

print("\nDone!")
