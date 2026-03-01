#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOCIAL MEDIA LOGIN HELPER
Login to Twitter, Facebook, Instagram and save sessions
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

VAULT = Path(__file__).parent / 'Vault'

def login_twitter():
    """Login to Twitter and save session."""
    print("\n" + "="*70)
    print("TWITTER LOGIN HELPER")
    print("="*70)
    print("\nInstructions:")
    print("  1. Browser will open")
    print("  2. Login to Twitter")
    print("  3. Wait for home feed to load")
    print("  4. Script will auto-detect login")
    print("\nSession will be saved for auto-posting!")
    print("="*70)
    input("\nPress Enter to open Twitter...")

    session_path = VAULT.parent / 'twitter_session'
    session_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--start-maximized'],
            timeout=300000  # 5 minutes
        )
        page = browser.pages[0]

        print("\nOpening Twitter...")
        print("Setting timeout to 5 minutes...")
        
        try:
            page.goto('https://twitter.com', timeout=120000, wait_until='domcontentloaded')
        except:
            print("Initial load timeout, continuing anyway...")

        print("\n" + "="*60)
        print("WAITING FOR LOGIN...")
        print("="*60)
        print("LOGIN NOW in the browser window!")
        print("Script will wait indefinitely...")
        print("="*60 + "\n")

        # Wait indefinitely until logged in
        attempts = 0
        while True:
            time.sleep(3)
            attempts += 1

            try:
                if page.locator('[data-testid="SideNav_NewTweet_Button"]').count() > 0:
                    print("\n✅ LOGIN DETECTED! Twitter is ready!")
                    break
                if page.locator('[data-testid="SideNav_AccountSwitcher_Button"]').count() > 0:
                    print("\n✅ LOGIN DETECTED! Twitter is ready!")
                    break
            except:
                pass

            if attempts % 10 == 0:
                print(f"Still waiting... ({attempts * 3}s elapsed)")
                print("Keep browser open and complete login")

        print("\nSession saved!")
        print("Browser will close in 5 seconds...")
        time.sleep(5)
        browser.close()

    print("\n✅ TWITTER LOGIN COMPLETE!")
    print("Now run: python twitter_poster.py")

def login_facebook():
    """Login to Facebook and save session."""
    print("\n" + "="*70)
    print("FACEBOOK LOGIN HELPER")
    print("="*70)
    print("\nInstructions:")
    print("  1. Browser will open")
    print("  2. Login to Facebook")
    print("  3. Wait for home feed to load")
    print("  4. Script will auto-detect login")
    print("\nSession will be saved for auto-posting!")
    print("="*70)
    input("\nPress Enter to open Facebook...")

    session_path = VAULT.parent / 'facebook_session'
    session_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--start-maximized'],
            timeout=300000  # 5 minutes
        )
        page = browser.pages[0]

        print("\nOpening Facebook...")
        print("Setting timeout to 5 minutes...")
        
        try:
            page.goto('https://www.facebook.com', timeout=120000, wait_until='domcontentloaded')
        except:
            print("Initial load timeout, continuing anyway...")

        print("\n" + "="*60)
        print("WAITING FOR LOGIN...")
        print("="*60)
        print("LOGIN NOW in the browser window!")
        print("Script will wait indefinitely...")
        print("="*60 + "\n")

        # Wait indefinitely until logged in
        attempts = 0
        while True:
            time.sleep(3)
            attempts += 1

            try:
                if page.locator('[aria-label="Menu"]').count() > 0:
                    print("\n✅ LOGIN DETECTED! Facebook is ready!")
                    break
                if page.locator('[aria-label*="What"]').count() > 0:
                    print("\n✅ LOGIN DETECTED! Facebook is ready!")
                    break
            except:
                pass

            if attempts % 10 == 0:
                print(f"Still waiting... ({attempts * 3}s elapsed)")
                print("Keep browser open and complete login")

        print("\nSession saved!")
        print("Browser will close in 5 seconds...")
        time.sleep(5)
        browser.close()

    print("\n✅ FACEBOOK LOGIN COMPLETE!")
    print("Now run: python facebook_poster.py")

def login_instagram():
    """Login to Instagram and save session."""
    print("\n" + "="*70)
    print("INSTAGRAM LOGIN HELPER")
    print("="*70)
    print("\nInstructions:")
    print("  1. Browser will open")
    print("  2. Login to Instagram")
    print("  3. Wait for home feed to load")
    print("  4. Script will auto-detect login")
    print("\nSession will be saved for auto-posting!")
    print("="*70)
    input("\nPress Enter to open Instagram...")

    session_path = VAULT.parent / 'instagram_session'
    session_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            session_path,
            headless=False,
            args=['--start-maximized'],
            timeout=300000  # 5 minutes
        )
        page = browser.pages[0]

        print("\nOpening Instagram...")
        print("Setting timeout to 5 minutes...")
        
        # Go to Instagram with longer timeout
        try:
            page.goto('https://www.instagram.com', timeout=120000, wait_until='domcontentloaded')
        except:
            print("Initial load timeout, continuing anyway...")

        print("\n" + "="*60)
        print("WAITING FOR LOGIN...")
        print("="*60)
        print("LOGIN NOW in the browser window!")
        print("Script will wait indefinitely...")
        print("="*60 + "\n")

        # Wait indefinitely until logged in
        attempts = 0
        while True:
            time.sleep(3)
            attempts += 1

            try:
                # Check for logged in indicators
                if page.locator('[aria-label="New post"]').count() > 0:
                    print("\n✅ LOGIN DETECTED! Instagram is ready!")
                    break
                if page.locator('[href*="/accounts/"]').count() > 0:
                    print("\n✅ LOGIN DETECTED! Instagram is ready!")
                    break
                if page.locator('[aria-label="Activity Feed"]').count() > 0:
                    print("\n✅ LOGIN DETECTED! Instagram is ready!")
                    break
            except:
                pass

            if attempts % 10 == 0:
                print(f"Still waiting... ({attempts * 3}s elapsed)")
                print("Keep browser open and complete login")

        print("\nSession saved!")
        print("Browser will close in 5 seconds...")
        time.sleep(5)
        browser.close()

    print("\n✅ INSTAGRAM LOGIN COMPLETE!")
    print("Now run: python instagram_poster.py --image image.png")

if __name__ == '__main__':
    print("\n" + "="*70)
    print("SOCIAL MEDIA LOGIN HELPER")
    print("="*70)
    print("\nSelect platform to login:")
    print("  1. Twitter")
    print("  2. Facebook")
    print("  3. Instagram")
    print("  4. All three")
    print()
    
    choice = input("Your choice (1-4): ").strip()
    
    if choice == '1':
        login_twitter()
    elif choice == '2':
        login_facebook()
    elif choice == '3':
        login_instagram()
    elif choice == '4':
        login_twitter()
        time.sleep(2)
        login_facebook()
        time.sleep(2)
        login_instagram()
    else:
        print("Invalid choice!")
    
    print("\n" + "="*70)
    print("ALL LOGINS COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Run: python twitter_poster.py")
    print("  2. Run: python facebook_poster.py")
    print("  3. Run: python instagram_poster.py --image image.png")
    print("\nSessions are saved, no need to login again!")
    print("="*70 + "\n")
