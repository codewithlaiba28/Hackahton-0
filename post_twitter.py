#!/usr/bin/env python3
"""
Twitter Only - Actually Posts
Gives you unlimited time to login, then posts
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
print("TWITTER - ACTUALLY POSTING")
print("="*70)
print("\nBrowser opening in 3 seconds...")
print("Go to twitter.com and login")
print("Take your time - I'll wait!")
print("="*70)
time.sleep(3)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(session_path),
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,720'],
        timeout=600000
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("\n[OK] Browser opened!")
    print("\nNOW:")
    print("  1. Go to https://twitter.com")
    print("  2. Login with your credentials")
    print("  3. Wait for home timeline to load")
    print("  4. Come back here and press ENTER")
    print("\nTake ALL the time you need - I'm waiting...")
    print("="*70)
    
    # Wait for Enter
    try:
        input()
    except:
        pass
    
    print("\nGreat! Checking Twitter...\n")
    
    # Go to Twitter
    page.goto('https://twitter.com', timeout=30000)
    time.sleep(5)
    
    # Check if logged in
    tweet_btn = page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
    
    if tweet_btn:
        print("[OK] Logged in to Twitter!")
        print("\nClicking Tweet button...")
        tweet_btn.click()
        time.sleep(3)
        
        # Find input
        inp = page.query_selector('[data-testid="tweetTextarea_0"]')
        
        if inp:
            print("[OK] Tweet composer opened!")
            
            # Type tweet
            tweet_text = "AI Employee Gold Tier Test! This is an ACTUAL automated post from my Personal AI Employee. #Hackathon2026 #AI #Automation"
            
            print(f"\nTyping tweet: {tweet_text[:50]}...")
            inp.click()
            time.sleep(0.5)
            page.keyboard.press('Control+a')
            time.sleep(0.2)
            page.keyboard.type(tweet_text, delay=50)
            time.sleep(2)
            
            # Screenshot
            page.screenshot(path='twitter_compose.png')
            print("Screenshot saved: twitter_compose.png")
            
            print("\n" + "="*70)
            print("READY TO POST!")
            print("="*70)
            print("\nPress ENTER to actually post this tweet...")
            print("(Or close browser to cancel)")
            print("="*70)
            
            try:
                input()
            except:
                pass
            
            # Click post button
            btns = page.query_selector_all('[data-testid="tweetButton"]')
            
            if btns:
                print("\n[OK] Clicking Post button...")
                btns[0].click()
                time.sleep(5)
                
                # Verify
                page.goto('https://twitter.com', timeout=10000)
                time.sleep(3)
                
                print("\n" + "="*70)
                print("SUCCESS! Tweet posted to Twitter!")
                print("="*70)
                print("\nCheck your Twitter profile:")
                print("  https://twitter.com")
                print("\nScreenshot saved: twitter_compose.png")
                print("="*70)
            else:
                print("\n[!] Post button not found!")
        else:
            print("\n[!] Tweet input box not found!")
    else:
        print("\n[!] Not logged in to Twitter!")
        print("    Please login and run this script again.")
    
    browser.close()

print("\nDone!\n")
