#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Social Media Auto-Poster with Manual Login
Gives you UNLIMITED time to login, then automatically posts
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
print("SOCIAL MEDIA - ACTUALLY POSTING (WITH MANUAL LOGIN)")
print("="*70)
print("\nThis will:")
print("  1. Open browser")
print("  2. Give you UNLIMITED time to login to all 3 platforms")
print("  3. Then automatically post to each platform")
print("\nTake your time - browser will stay open until you login!")
print("="*70)
input("\nPress Enter to open browser...")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        str(session_path),
        headless=False,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--window-size=1280,720'
        ],
        timeout=300000  # 5 minutes timeout
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    # ============ LOGIN PHASE ============
    print("\n" + "="*70)
    print("LOGIN PHASE")
    print("="*70)
    print("\nPlease login to ALL THREE platforms:")
    print("  1. Twitter:  https://twitter.com")
    print("  2. Facebook: https://facebook.com")
    print("  3. Instagram: https://instagram.com")
    print("\nTake your time - I'll wait here!")
    print("Type 'done' when you've logged in to all three.\n")
    
    # Wait for user to say they're done
    while True:
        user_input = input("Are you logged in to all three? (type 'done'): ").lower().strip()
        if user_input == 'done':
            print("\nGreat! Starting to post...")
            break
        else:
            print("  Type 'done' when ready...")
    
    # ============ TWITTER ============
    print("\n" + "="*70)
    print("POSTING TO TWITTER")
    print("="*70)
    
    page.goto('https://twitter.com', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    
    # Check if logged in
    tweet_button = page.query_selector('[data-testid="SideNav_NewTweet_Button"]')
    
    if tweet_button:
        print("  [OK] Twitter logged in!")
        
        # Click tweet button
        tweet_button.click()
        time.sleep(2)
        
        # Find input
        input_box = page.query_selector('[data-testid="tweetTextarea_0"]')
        
        if input_box:
            # Type tweet
            tweet_text = "AI Employee Gold Tier Test! This is an ACTUAL automated post from my Personal AI Employee. #Hackathon2026 #AI #Automation"
            
            input_box.click()
            time.sleep(0.5)
            page.keyboard.press('Control+a')
            time.sleep(0.2)
            page.keyboard.type(tweet_text, delay=50)
            time.sleep(2)
            
            print(f"  Tweet typed: {tweet_text[:50]}...")
            
            # Screenshot before posting
            page.screenshot(path=str(vault_path.parent / 'twitter_before.png'))
            print("  Screenshot saved: twitter_before.png")
            
            # Ask before posting
            print("\n  Ready to post? Press Enter to confirm...")
            input("  (Or press Ctrl+C to skip)")
            
            # Click post
            post_buttons = page.query_selector_all('[data-testid="tweetButton"]')
            if post_buttons:
                post_buttons[0].click()
                time.sleep(5)
                print("  [OK] Tweet posted to Twitter!")
                
                # Screenshot after
                page.screenshot(path=str(vault_path.parent / 'twitter_after.png'))
            else:
                print("  [WARN] Post button not found")
        else:
            print("  [WARN] Tweet input not found")
    else:
        print("  [WARN] Not logged in to Twitter")
    
    time.sleep(3)
    
    # ============ FACEBOOK ============
    print("\n" + "="*70)
    print("POSTING TO FACEBOOK")
    print("="*70)
    
    page.goto('https://www.facebook.com', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    
    # Check if logged in
    menu = page.query_selector('[aria-label="Menu"]')
    
    if menu:
        print("  [OK] Facebook logged in!")
        
        # Find post box
        post_box = page.query_selector('[aria-label="What\'s on your mind?"]')
        
        if post_box:
            post_box.click()
            time.sleep(2)
            
            # Type post
            fb_text = "AI Employee Gold Tier Test! This is an ACTUAL automated post from my Personal AI Employee. #Hackathon2026 #AI"
            
            page.keyboard.type(fb_text, delay=50)
            time.sleep(2)
            
            print(f"  Post typed: {fb_text[:50]}...")
            
            # Screenshot
            page.screenshot(path=str(vault_path.parent / 'facebook_before.png'))
            print("  Screenshot saved: facebook_before.png")
            
            # Ask before posting
            print("\n  Ready to post? Press Enter to confirm...")
            input("  (Or press Ctrl+C to skip)")
            
            # Click post
            post_buttons = page.query_selector_all('[aria-label="Post"]')
            if post_buttons:
                post_buttons[0].click()
                time.sleep(5)
                print("  [OK] Posted to Facebook!")
                
                page.screenshot(path=str(vault_path.parent / 'facebook_after.png'))
            else:
                print("  [WARN] Post button not found")
        else:
            print("  [WARN] Post box not found")
    else:
        print("  [WARN] Not logged in to Facebook")
    
    time.sleep(3)
    
    # ============ INSTAGRAM ============
    print("\n" + "="*70)
    print("POSTING TO INSTAGRAM")
    print("="*70)
    
    page.goto('https://www.instagram.com', wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)
    
    # Check if logged in
    profile = page.query_selector('[aria-label="See profile"]')
    
    if profile:
        print("  [OK] Instagram logged in!")
        
        # Find new post button
        new_post = page.query_selector('[aria-label="New post"]')
        
        if new_post:
            new_post.click()
            time.sleep(2)
            
            # Upload image
            if image_path.exists():
                print(f"  Uploading image: {image_path}")
                
                file_input = page.query_selector('input[type="file"]')
                if file_input:
                    file_input.set_input_files(str(image_path))
                    time.sleep(5)
                    print("  [OK] Image uploaded!")
                    
                    # Click Next
                    next_buttons = page.query_selector_all('button:has-text("Next")')
                    if next_buttons:
                        next_buttons[0].click()
                        time.sleep(2)
                        
                        # Next again
                        next_buttons = page.query_selector_all('button:has-text("Next")')
                        if next_buttons:
                            next_buttons[0].click()
                            time.sleep(2)
                            
                            # Add caption
                            caption = "AI Employee Gold Tier Test! #Hackathon2026 #AI #Automation"
                            
                            caption_input = page.query_selector('textarea[aria-label="Write a caption..."]')
                            if caption_input:
                                caption_input.fill(caption)
                                time.sleep(1)
                                print(f"  Caption added: {caption[:50]}...")
                            
                            # Screenshot
                            page.screenshot(path=str(vault_path.parent / 'instagram_before.png'))
                            print("  Screenshot saved: instagram_before.png")
                            
                            # Ask before posting
                            print("\n  Ready to post? Press Enter to confirm...")
                            input("  (Or press Ctrl+C to skip)")
                            
                            # Click Share
                            share_buttons = page.query_selector_all('button:has-text("Share")')
                            if share_buttons:
                                share_buttons[0].click()
                                time.sleep(5)
                                print("  [OK] Posted to Instagram!")
                                
                                page.screenshot(path=str(vault_path.parent / 'instagram_after.png'))
                            else:
                                print("  [WARN] Share button not found")
            else:
                print(f"  [WARN] Image not found: {image_path}")
        else:
            print("  [WARN] New post button not found")
    else:
        print("  [WARN] Not logged in to Instagram")
    
    browser.close()

print("\n" + "="*70)
print("ALL POSTS COMPLETE!")
print("="*70)
print("\nScreenshots saved:")
print("  - twitter_before.png")
print("  - twitter_after.png")
print("  - facebook_before.png")
print("  - facebook_after.png")
print("  - instagram_before.png")
print("  - instagram_after.png")
print("\nCheck your social media profiles to see the posts!")
print("="*70)
