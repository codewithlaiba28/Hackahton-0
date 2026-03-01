#!/usr/bin/env python3
"""
Twitter Poster - Simple & Working
Opens browser, you login, then it posts
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
print("TWITTER POSTER - ACTUALLY WORKING")
print("="*70)
print("\nThis will:")
print("  1. Open browser")
print("  2. Wait for you to login")
print("  3. Post tweet automatically")
print("\nPress Enter to start...")
input()

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(session_path),
        headless=False,
        args=['--no-sandbox', '--disable-setuid-sandbox'],
        timeout=300000
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    # Go to Twitter
    print("\nOpening Twitter...")
    page.goto('https://twitter.com', timeout=30000)
    time.sleep(5)
    
    print("\n" + "="*70)
    print("LOGIN NOW!")
    print("="*70)
    print("\nIn the browser window:")
    print("  1. Login to Twitter if not already logged in")
    print("  2. Wait for home timeline to load")
    print("  3. Come back here and press Enter")
    print("\nTake your time - I'm waiting...")
    print("="*70)
    
    # Wait for user to login
    input("\nPress Enter when you're logged in...")
    
    # Check if logged in
    print("\nChecking login status...")
    page.goto('https://twitter.com', timeout=30000)
    time.sleep(5)
    
    tweet_btn = page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
    
    if tweet_btn:
        print("[OK] Logged in!")
        
        # Click tweet
        print("\nOpening tweet composer...")
        tweet_btn.click()
        time.sleep(3)
        
        # Find input
        inp = page.query_selector('[data-testid="tweetTextarea_0"]')
        
        if inp:
            # Type tweet
            tweet_text = "AI Employee Gold Tier Test! This is an ACTUAL automated post from my Personal AI Employee. #Hackathon2026 #AI #Automation"
            
            print(f"\nTyping: {tweet_text[:50]}...")
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
            print("\nPress Enter to actually post this tweet...")
            input()
            
            # Click post
            btns = page.query_selector_all('[data-testid="tweetButton"]')
            
            if btns:
                print("\n[OK] Clicking Post button...")
                btns[0].click()
                time.sleep(5)
                
                print("\n" + "="*70)
                print("SUCCESS! Tweet posted!")
                print("="*70)
                print("\nCheck: https://twitter.com")
                print("="*70)
            else:
                print("\n[!] Post button not found!")
        else:
            print("\n[!] Tweet input not found!")
    else:
        print("\n[!] Not logged in!")
    
    browser.close()

print("\nDone!\n")
