#!/usr/bin/env python3
"""
Simple Social Media Poster - Auto opens browser, waits for login, then posts
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

session_path = Path('social_session')
vault_path = Path('Vault')
image_path = Path('image.png')

print("\n" + "="*70)
print("SOCIAL MEDIA AUTO-POSTER")
print("="*70)
print("\nBrowser will open in 3 seconds...")
print("Login to Twitter, Facebook, and Instagram")
print("Then come back and press ENTER")
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
    print("\nNOW LOGIN:")
    print("  1. Go to twitter.com and login")
    print("  2. Go to facebook.com and login")
    print("  3. Go to instagram.com and login")
    print("\nTake your time - I'm waiting...")
    print("\nWhen done, press ENTER in this terminal...")
    
    # Wait for Enter
    try:
        input()
    except:
        pass
    
    print("\nGreat! Starting to post...\n")
    
    # TWITTER
    print("="*60)
    print("TWITTER")
    print("="*60)
    page.goto('https://twitter.com', timeout=30000)
    time.sleep(3)
    
    tweet_btn = page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
    if tweet_btn:
        print("[OK] Twitter logged in!")
        tweet_btn.click()
        time.sleep(2)
        
        inp = page.query_selector('[data-testid="tweetTextarea_0"]')
        if inp:
            inp.click()
            time.sleep(0.5)
            page.keyboard.press('Control+a')
            time.sleep(0.2)
            page.keyboard.type("AI Employee Gold Tier Test! ACTUAL automated post from Personal AI Employee. #Hackathon2026 #AI", delay=50)
            time.sleep(2)
            
            page.screenshot(path='twitter_ready.png')
            print("Screenshot: twitter_ready.png")
            
            print("\nPress ENTER to post this tweet...")
            try:
                input()
            except:
                pass
            
            btns = page.query_selector_all('[data-testid="tweetButton"]')
            if btns:
                btns[0].click()
                time.sleep(5)
                print("[OK] Tweet posted!")
                page.screenshot(path='twitter_posted.png')
            else:
                print("[!] Post button not found")
        else:
            print("[!] Tweet input not found")
    else:
        print("[!] Not logged in to Twitter")
    
    time.sleep(2)
    
    # FACEBOOK
    print("\n" + "="*60)
    print("FACEBOOK")
    print("="*60)
    page.goto('https://facebook.com', timeout=30000)
    time.sleep(3)
    
    menu = page.query_selector('[aria-label="Menu"]')
    if menu:
        print("[OK] Facebook logged in!")
        
        post_box = page.query_selector('[aria-label="What\'s on your mind?"]')
        if post_box:
            post_box.click()
            time.sleep(2)
            
            page.keyboard.type("AI Employee Gold Tier Test! ACTUAL automated post. #Hackathon2026 #AI", delay=50)
            time.sleep(2)
            
            page.screenshot(path='facebook_ready.png')
            print("Screenshot: facebook_ready.png")
            
            print("\nPress ENTER to post to Facebook...")
            try:
                input()
            except:
                pass
            
            btns = page.query_selector_all('[aria-label="Post"]')
            if btns:
                btns[0].click()
                time.sleep(5)
                print("[OK] Facebook posted!")
                page.screenshot(path='facebook_posted.png')
            else:
                print("[!] Post button not found")
        else:
            print("[!] Post box not found")
    else:
        print("[!] Not logged in to Facebook")
    
    time.sleep(2)
    
    # INSTAGRAM
    print("\n" + "="*60)
    print("INSTAGRAM")
    print("="*60)
    page.goto('https://instagram.com', timeout=30000)
    time.sleep(3)
    
    profile = page.query_selector('[aria-label="See profile"]')
    if profile:
        print("[OK] Instagram logged in!")
        
        new_post = page.query_selector('[aria-label="New post"]')
        if new_post:
            new_post.click()
            time.sleep(2)
            
            if image_path.exists():
                file_inp = page.query_selector('input[type="file"]')
                if file_inp:
                    file_inp.set_input_files(str(image_path))
                    time.sleep(5)
                    print("[OK] Image uploaded!")
                    
                    btns = page.query_selector_all('button:has-text("Next")')
                    for i, btn in enumerate(btns[:2]):
                        btn.click()
                        time.sleep(2)
                    
                    cap = page.query_selector('textarea[aria-label="Write a caption..."]')
                    if cap:
                        cap.fill("AI Employee Gold Tier Test! #Hackathon2026 #AI #Automation")
                        time.sleep(1)
                    
                    page.screenshot(path='instagram_ready.png')
                    print("Screenshot: instagram_ready.png")
                    
                    print("\nPress ENTER to post to Instagram...")
                    try:
                        input()
                    except:
                        pass
                    
                    share_btns = page.query_selector_all('button:has-text("Share")')
                    if share_btns:
                        share_btns[0].click()
                        time.sleep(5)
                        print("[OK] Instagram posted!")
                        page.screenshot(path='instagram_posted.png')
                    else:
                        print("[!] Share button not found")
            else:
                print(f"[!] Image not found: {image_path}")
        else:
            print("[!] New post button not found")
    else:
        print("[!] Not logged in to Instagram")
    
    browser.close()

print("\n" + "="*70)
print("DONE! All posts complete!")
print("="*70)
print("\nScreenshots:")
print("  - twitter_ready.png, twitter_posted.png")
print("  - facebook_ready.png, facebook_posted.png")
print("  - instagram_ready.png, instagram_posted.png")
print("\nCheck your profiles to see the posts!")
print("="*70)
