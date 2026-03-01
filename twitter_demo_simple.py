#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TWITTER AUTO-POST DEMO - SIMPLE
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

VAULT = Path(__file__).parent / 'Vault'
SESSION = VAULT.parent / 'twitter_session'
SESSION.mkdir(parents=True, exist_ok=True)

print("\n" + "="*70)
print("TWITTER AUTO-POST DEMO")
print("="*70)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        SESSION,
        headless=False,
        args=['--start-maximized']
    )
    page = browser.pages[0]
    
    print("\n[1/4] Opening Twitter...")
    page.goto('https://twitter.com', wait_until='domcontentloaded', timeout=30000)
    time.sleep(3)
    
    print("\n[2/4] Checking login status...")
    time.sleep(2)
    
    # Check if logged in
    try:
        if page.locator('[data-testid="SideNav_NewTweet_Button"]').count() > 0:
            print("Already logged in!")
        else:
            print("NOT logged in - Please login now (60 seconds)...")
            for i in range(60, 0, -1):
                print(f"Time left: {i}s", end='\r')
                time.sleep(1)
                if page.locator('[data-testid="SideNav_NewTweet_Button"]').count() > 0:
                    print("\nLogin detected!")
                    break
    except:
        pass
    
    print("\n[3/4] Composing tweet...")
    page.goto('https://twitter.com/home')
    time.sleep(2)
    
    try:
        textbox = page.locator('[data-testid="DraftTweet"]').first
        textbox.click()
        time.sleep(1)
        
        text = "AI Employee Gold Tier Test! Automated post from my Personal AI Employee. #Hackathon2026 #AI"
        textbox.fill(text)
        time.sleep(2)
        
        print(f"Tweet composed: {text}")
        
        print("\n[4/4] CLICK 'Post' BUTTON NOW!")
        print("="*70)
        print("Waiting 30 seconds for you to click Post...")
        print("="*70)
        
        for i in range(30, 0, -1):
            print(f"Time left: {i}s", end='\r')
            time.sleep(1)
        
    except Exception as e:
        print(f"Error: {e}")
    
    browser.close()

print("\nDONE!")
print("="*70 + "\n")
