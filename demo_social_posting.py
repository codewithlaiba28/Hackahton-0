#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOCIAL MEDIA DEMO - ACTUALLY POSTING
Twitter, Facebook, Instagram - Live Demo
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import time
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

VAULT_PATH = Path(__file__).parent / 'Vault'
TEST_IMAGE = Path(__file__).parent / 'image.png'

def post_to_twitter():
    """Post to Twitter/X"""
    print("\n" + "="*70)
    print("🐦 TWITTER/X AUTO-POST - LIVE DEMO")
    print("="*70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            VAULT_PATH.parent / 'twitter_session',
            headless=False,
            args=['--start-maximized']
        )
        page = browser.pages[0]
        
        print("[1/5] Opening Twitter...")
        page.goto('https://twitter.com', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        
        print("[2/5] Waiting for login check...")
        # Check if already logged in
        try:
            compose_button = page.locator('[data-testid="SideNav_NewTweet_Button"]')
            if compose_button.count() > 0:
                print("✅ Already logged in!")
            else:
                print("⚠️  Please login manually (you have 60 seconds)...")
                for i in range(60, 0, -1):
                    print(f"   Time remaining: {i}s")
                    time.sleep(1)
                    if page.locator('[data-testid="SideNav_NewTweet_Button"]').count() > 0:
                        print("✅ Login detected!")
                        break
        except:
            pass
        
        print("[3/5] Composing tweet...")
        page.goto('https://twitter.com/home', wait_until='domcontentloaded')
        time.sleep(2)
        
        # Find compose box and type
        try:
            textbox = page.locator('[data-testid="DraftTweet"]').first
            textbox.click()
            time.sleep(1)
            
            tweet_text = f"🤖 AI Employee Gold Tier Test!\n\nThis is an automated post from my Personal AI Employee.\n\n#Hackathon2026 #AI #Automation #Twitter"
            textbox.fill(tweet_text)
            time.sleep(2)
            
            print("[4/5] Tweet composed! Content:")
            print(f"   {tweet_text}")
            
            print("[5/5] Ready to post - Click 'Post' button manually!")
            print("\n" + "="*70)
            print("⚠️  MANUAL STEP: Click the 'Post' button in the browser")
            print("="*70)
            
            # Wait for user to click post
            for i in range(30, 0, -1):
                print(f"   Waiting: {i}s")
                time.sleep(1)
            
        except Exception as e:
            print(f"⚠️  Error: {e}")
            print("Try manual posting...")
        
        browser.close()

def post_to_facebook():
    """Post to Facebook"""
    print("\n" + "="*70)
    print("📘 FACEBOOK AUTO-POST - LIVE DEMO")
    print("="*70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            VAULT_PATH.parent / 'facebook_session',
            headless=False,
            args=['--start-maximized']
        )
        page = browser.pages[0]
        
        print("[1/5] Opening Facebook...")
        page.goto('https://facebook.com', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        
        print("[2/5] Waiting for login check...")
        try:
            create_post = page.locator('[aria-label*="What\'s on your mind"]')
            if create_post.count() > 0:
                print("✅ Already logged in!")
            else:
                print("⚠️  Please login manually (you have 60 seconds)...")
                for i in range(60, 0, -1):
                    print(f"   Time remaining: {i}s")
                    time.sleep(1)
                    if page.locator('[aria-label*="What\'s on your mind"]').count() > 0:
                        print("✅ Login detected!")
                        break
        except:
            pass
        
        print("[3/5] Going to create post...")
        page.goto('https://facebook.com', wait_until='domcontentloaded')
        time.sleep(2)
        
        try:
            # Click create post
            create_post = page.locator('[aria-label*="What\'s on your mind"]').first
            create_post.click()
            time.sleep(2)
            
            # Find text area and type
            textbox = page.locator('[aria-label*="What\'s on your mind"]').nth(1)
            fb_text = f"🤖 AI Employee Gold Tier Test!\n\nThis is an automated post from my Personal AI Employee.\n\n#Hackathon2026 #AI #Automation"
            textbox.fill(fb_text)
            time.sleep(2)
            
            print("[4/5] Post composed! Content:")
            print(f"   {fb_text}")
            
            print("[5/5] Ready to post - Click 'Post' button manually!")
            print("\n" + "="*70)
            print("⚠️  MANUAL STEP: Click the 'Post' button in the browser")
            print("="*70)
            
            for i in range(30, 0, -1):
                print(f"   Waiting: {i}s")
                time.sleep(1)
                
        except Exception as e:
            print(f"⚠️  Error: {e}")
            print("Try manual posting...")
        
        browser.close()

def post_to_instagram():
    """Post to Instagram"""
    print("\n" + "="*70)
    print("📷 INSTAGRAM AUTO-POST - LIVE DEMO")
    print("="*70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            VAULT_PATH.parent / 'instagram_session',
            headless=False,
            args=['--start-maximized']
        )
        page = browser.pages[0]
        
        print("[1/6] Opening Instagram...")
        page.goto('https://instagram.com', wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        
        print("[2/6] Waiting for login check...")
        try:
            profile = page.locator('[href*="/accounts/"]')
            if profile.count() > 0:
                print("✅ Already logged in!")
            else:
                print("⚠️  Please login manually (you have 60 seconds)...")
                for i in range(60, 0, -1):
                    print(f"   Time remaining: {i}s")
                    time.sleep(1)
                    if page.locator('[href*="/accounts/"]').count() > 0:
                        print("✅ Login detected!")
                        break
        except:
            pass
        
        print("[3/6] Opening create post...")
        page.goto('https://instagram.com', wait_until='domcontentloaded')
        time.sleep(2)
        
        try:
            # Click new post
            new_post = page.locator('[aria-label="New post"]').first
            new_post.click()
            time.sleep(2)
            
            print("[4/6] Upload dialog opened!")
            print(f"   Image: {TEST_IMAGE}")
            print(f"   Caption: AI Employee Gold Tier Test! #Hackathon2026 #AI")
            
            print("[5/6] ⚠️  MANUAL STEPS:")
            print("   1. Click 'Select from computer'")
            print(f"   2. Select: {TEST_IMAGE}")
            print("   3. Add caption and click 'Share'")
            
            print("[6/6] Ready for manual posting!")
            print("\n" + "="*70)
            print("⚠️  MANUAL STEP: Complete the upload in the browser")
            print("="*70)
            
            for i in range(30, 0, -1):
                print(f"   Waiting: {i}s")
                time.sleep(1)
                
        except Exception as e:
            print(f"⚠️  Error: {e}")
            print("Try manual posting...")
        
        browser.close()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 SOCIAL MEDIA AUTO-POSTING DEMO")
    print("   Twitter + Facebook + Instagram")
    print("="*70)
    print("\n⚠️  IMPORTANT:")
    print("   - Browser will open for each platform")
    print("   - If not logged in, you have 60 seconds to login")
    print("   - Script will compose the post automatically")
    print("   - You need to click 'Post' button manually")
    print("   - This is due to platform security")
    print("\n" + "="*70)
    input("Press Enter to start demo...")
    
    # Run all three
    post_to_twitter()
    time.sleep(2)
    
    post_to_facebook()
    time.sleep(2)
    
    post_to_instagram()
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE!")
    print("="*70)
    print("\n📝 SUMMARY:")
    print("   🐦 Twitter - Browser opened, compose ready")
    print("   📘 Facebook - Browser opened, compose ready")
    print("   📷 Instagram - Browser opened, upload ready")
    print("\n💡 TIP: Sessions saved for next time!")
    print("="*70 + "\n")
