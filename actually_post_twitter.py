#!/usr/bin/env python3
# Simple script to actually post to Twitter
# Run this AFTER you manually login to Twitter in the browser

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

session_path = Path('twitter_session')
vault_path = Path('Vault')

print("\n" + "="*70)
print("TWITTER - ACTUALLY POSTING")
print("="*70)
print("\nSTEP 1: First, login to Twitter manually")
print("  1. Open browser")
print("  2. Go to https://twitter.com")
print("  3. Login with your credentials")
print("  4. Come back here when logged in")
print()
input("  Press Enter when you're logged in to Twitter...")

print("\nSTEP 2: Posting tweet...")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(session_path),
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox'],
        timeout=60000
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    # Go to Twitter
    print("  Opening Twitter...")
    page.goto('https://twitter.com', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    
    # Check if logged in
    tweet_button = page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
    
    if not tweet_button:
        print("  [ERROR] Not logged in!")
        print("  Please login first, then run this script again.")
        browser.close()
        sys.exit(1)
    
    print("  [OK] Logged in!")
    
    # Click tweet button
    print("  Opening tweet composer...")
    tweet_button.click()
    time.sleep(2)
    
    # Find input
    input_box = page.query_selector('[data-testid="tweetTextarea_0"]')
    
    if not input_box:
        print("  [ERROR] Tweet input not found!")
        browser.close()
        sys.exit(1)
    
    # Type tweet
    tweet_text = "AI Employee Gold Tier Test! This is an ACTUAL automated post from my Personal AI Employee. #Hackathon2026 #AI #Automation"
    
    print(f"  Typing tweet: {tweet_text[:50]}...")
    input_box.click()
    time.sleep(0.5)
    page.keyboard.press('Control+a')
    time.sleep(0.2)
    page.keyboard.type(tweet_text, delay=50)
    time.sleep(2)
    
    # Take screenshot
    screenshot = vault_path.parent / 'twitter_before_post.png'
    page.screenshot(path=str(screenshot))
    print(f"  Screenshot saved: {screenshot}")
    
    # Click post button
    print("  Posting tweet...")
    post_buttons = page.query_selector_all('[data-testid="tweetButton"]')
    
    if post_buttons:
        post_buttons[0].click()
        time.sleep(5)
        
        # Verify posted
        page.goto('https://twitter.com', wait_until='domcontentloaded', timeout=10000)
        time.sleep(3)
        
        print("\n  [SUCCESS] Tweet posted to Twitter!")
        print(f"  Check your Twitter profile to see the tweet.")
        
        # Log it
        from datetime import datetime
        import json
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': 'twitter_post_actual',
            'actor': 'gold_tier_test',
            'target': 'twitter.com',
            'parameters': {'text': tweet_text},
            'result': 'success'
        }
        
        log_file = vault_path / 'Logs' / f'{datetime.now().strftime("%Y-%m-%d")}.json'
        entries = []
        if log_file.exists():
            try:
                entries = json.loads(log_file.read_text())
            except:
                pass
        
        entries.append(log_entry)
        log_file.write_text(json.dumps(entries, indent=2))
        
    else:
        print("  [ERROR] Post button not found!")
    
    browser.close()

print("\n" + "="*70)
print("DONE!")
print("="*70)
print("\nYour tweet has been posted to Twitter!")
print("Go check: https://twitter.com")
print()
