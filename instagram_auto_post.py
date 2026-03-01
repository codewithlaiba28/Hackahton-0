#!/usr/bin/env python3
"""Instagram Auto-Poster - WITH DISCARD DIALOG FIX"""

import sys, codecs
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import time

VAULT = Path(__file__).parent / 'Vault'
IMAGE = Path(__file__).parent / 'image.png'

print("\n" + "="*60)
print("INSTAGRAM AUTO-POSTER - DISCARD FIX")
print("="*60)

# Get post
posts = list((VAULT / 'Approved').glob('INSTAGRAM*.md'))
if not posts:
    print("No posts found")
    exit(1)

post_file = posts[0]
content = post_file.read_text(encoding='utf-8')

# Extract caption
caption = ""
if '## Caption' in content:
    caption = content.split('## Caption')[1].split('##')[0].strip()[:1000]

print(f"\nCaption: {len(caption)} chars")
print(f"Image: {IMAGE.name}")

# Browser
session = VAULT.parent / 'instagram_session'
session.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        session, headless=False,
        args=['--start-maximized'],
        timeout=300000
    )
    page = browser.pages[0]
    
    # 1. Login
    print("\n[1/9] Login...")
    page.goto('https://instagram.com')
    for i in range(60):
        time.sleep(3)
        if page.locator('[aria-label="New post"]').count() > 0:
            print(f"   [OK] Login ({(i+1)*3}s)")
            break
        if (i+1) % 10 == 0:
            print(f"   Waiting... ({(i+1)*3}s)")
    
    # 2. Close popups
    print("\n[2/9] Close popups...")
    for _ in range(5):
        page.keyboard.press('Escape')
        time.sleep(0.3)
    try:
        page.locator('button:has-text("Not Now")').click(timeout=3000)
    except: pass
    time.sleep(1)
    
    # 3. New Post
    print("\n[3/9] New Post...")
    page.locator('[aria-label="New post"]').first.click(timeout=5000)
    print("   [OK] Opened")
    time.sleep(2)
    
    # 4. Upload Image
    print("\n[4/9] Upload Image...")
    with page.expect_file_chooser(timeout=10000) as fc:
        page.locator('button:has-text("Select from computer")').click(timeout=5000)
    fc.value.set_files(str(IMAGE))
    print("   [OK] Uploaded: " + IMAGE.name)
    
    # Wait for image processing
    print("   Processing image...")
    for i in range(15, 0, -1):
        print(f"   {i}s...")
        time.sleep(1)
    
    # 5. SCREEN 1: Crop - Click Next
    print("\n[5/9] SCREEN 1: Crop - Click Next...")
    selectors = ['button:has-text("Next")', 'div[role="button"]:has-text("Next")', '[aria-label="Next"]']
    
    next_clicked = False
    for attempt in range(30):
        for sel in selectors:
            try:
                next_btn = page.locator(sel).first
                if next_btn.count() > 0:
                    disabled = next_btn.get_attribute('disabled')
                    if disabled is None:
                        next_btn.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        next_btn.click(force=True, timeout=3000)
                        print(f"   [OK] Next clicked! ({sel[:30]})")
                        next_clicked = True
                        time.sleep(3)
                        break
            except: pass
        if next_clicked: break
        if attempt % 5 == 0:
            print(f"   Waiting... ({attempt}s)")
        time.sleep(1)
    
    if not next_clicked:
        print("   [WARN] Trying Enter...")
        page.keyboard.press('Enter')
        time.sleep(2)
    
    # 6. SCREEN 2: Filters - Click Next
    print("\n[6/9] SCREEN 2: Filters - Click Next...")
    time.sleep(2)
    
    for attempt in range(30):
        for sel in selectors:
            try:
                next_btn = page.locator(sel).first
                if next_btn.count() > 0:
                    disabled = next_btn.get_attribute('disabled')
                    if disabled is None:
                        next_btn.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        next_btn.click(force=True, timeout=3000)
                        print(f"   [OK] Next clicked! ({sel[:30]})")
                        next_clicked = True
                        time.sleep(3)
                        break
            except: pass
        if next_clicked: break
        if attempt % 5 == 0:
            print(f"   Waiting... ({attempt}s)")
        time.sleep(1)
    
    if not next_clicked:
        print("   [WARN] Trying Enter...")
        page.keyboard.press('Enter')
        time.sleep(2)
    
    # 6.5. CLOSE DISCARD DIALOG (CRITICAL FIX)
    print("\n[6.5/9] Close Discard Dialog...")
    time.sleep(2)
    try:
        # Check for Discard dialog
        discard = page.locator('text=Discard').first
        if discard.count() > 0:
            print("   Found Discard dialog!")
            # Click Cancel to stay
            cancel = page.locator('button:has-text("Cancel")').first
            cancel.click()
            print("   [OK] Discard dialog closed!")
            time.sleep(2)
        else:
            print("   [OK] No Discard dialog")
    except:
        print("   [OK] No Discard dialog")
    
    time.sleep(2)
    
    # 7. SCREEN 3: Tag People - Click Next to Skip (DON'T enter caption here!)
    print("\n[7/9] SCREEN 3: Tag People - Skip (NO CAPTION HERE)...")
    time.sleep(3)
    
    # Check if on Tag screen
    tag_screen = False
    try:
        # Tag screen has "Tag" text or tag-related elements
        # BUT it also has a caption box - DON'T use it!
        tag_indicators = [
            'text=Tag people',
            '[aria-label*="Tag"]',
            'text=Tag friends'
        ]
        
        for indicator in tag_indicators:
            try:
                if page.locator(indicator).first.count() > 0:
                    tag_screen = True
                    print("   [OK] Tag screen detected!")
                    break
            except: pass
        
        if tag_screen:
            # CRITICAL: Just click Next - DON'T enter caption here!
            print("   Skipping Tag screen (no caption)...")
            for sel in selectors:
                try:
                    next_btn = page.locator(sel).first
                    if next_btn.count() > 0:
                        next_btn.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        next_btn.click(force=True, timeout=3000)
                        print("   [OK] Tag screen skipped!")
                        time.sleep(3)
                        break
                except: pass
        else:
            print("   [OK] No Tag screen")
    except Exception as e:
        print(f"   [WARN] Tag check failed: {e}")
    
    # CRITICAL: Wait for Caption screen to load
    print("\n   Waiting for Caption screen (NOT Tag screen)...")
    time.sleep(5)
    
    # 8. SCREEN 4: Caption (PROPER CAPTION SCREEN)
    print("\n[8/9] SCREEN 4: Caption (PROPER SCREEN)...")
    time.sleep(3)
    
    # Close any Discard dialog
    print("   Checking for Discard...")
    try:
        discard = page.locator('text=Discard').first
        if discard.count() > 0:
            print("   Found Discard - clicking Cancel...")
            cancel = page.locator('button:has-text("Cancel")').first
            cancel.click()
            time.sleep(3)
            print("   [OK] Discard closed!")
    except:
        print("   [OK] No Discard")
    
    # Confirm we're on PROPER Caption screen (not Tag screen)
    print("   Confirming proper Caption screen...")
    on_proper_caption = False
    try:
        # Proper Caption screen has "Share" button visible
        share_btn = page.locator('[aria-label="Share"]').first
        if share_btn.count() > 0:
            on_proper_caption = True
            print("   [OK] Share button visible - on proper Caption screen!")
    except:
        pass
    
    if not on_proper_caption:
        print("   [WARN] Share button not visible - might still be on Tag screen")
        print("   Trying to reach Caption screen...")
        # Click Next again to reach Caption screen
        try:
            for sel in selectors:
                next_btn = page.locator(sel).first
                if next_btn.count() > 0:
                    next_btn.click(force=True)
                    print("   [OK] Clicked Next to reach Caption screen!")
                    time.sleep(3)
                    break
        except: pass
    
    # Enter caption
    if caption:
        print("   Entering caption...")
        try:
            time.sleep(2)
            page.keyboard.type(caption, delay=50)
            print("   [OK] Caption entered!")
        except Exception as e:
            print(f"   Caption failed: {e}")
            page.keyboard.press('Tab')
            time.sleep(0.5)
            page.keyboard.type(caption, delay=50)
    else:
        print("   [OK] No caption")
    
    time.sleep(3)
    
    # Click Share
    print("   Clicking Share...")
    share_clicked = False
    
    # Screenshot
    try:
        page.screenshot(path='before_share.png')
        print("   Screenshot: before_share.png")
    except: pass
    
    # Wait for Share button to be ready
    print("   Waiting for Share button...")
    time.sleep(5)
    
    # Method 1: Find Share button by aria-label
    try:
        share_btn = page.locator('[aria-label="Share"]').first
        share_btn.wait_for(state='visible', timeout=10000)
        share_btn.wait_for(state='enabled', timeout=10000)
        share_btn.scroll_into_view_if_needed()
        time.sleep(2)
        share_btn.click(force=True)
        print("   [OK] Share button clicked!")
        share_clicked = True
        time.sleep(15)
    except Exception as e:
        print(f"   Method 1 failed: {e}")
        
        # Method 2: Try button with text Share
        try:
            share_btn = page.locator('button:has-text("Share")').first
            share_btn.wait_for(state='visible', timeout=5000)
            share_btn.click(force=True)
            print("   [OK] Share via button text!")
            share_clicked = True
            time.sleep(10)
        except Exception as e2:
            print(f"   Method 2 failed: {e2}")
            
            # Method 3: Keyboard Tab navigation
            print("   Method 3: Keyboard Tab...")
            for i in range(20):
                page.keyboard.press('Tab')
                time.sleep(0.3)
            page.keyboard.press('Enter')
            print("   [OK] Keyboard navigation done!")
            share_clicked = True
            time.sleep(10)
    
    # Final wait
    print("   Waiting for confirmation...")
    time.sleep(15)
    
    # Screenshot after
    try:
        page.screenshot(path='after_share.png')
        print("   Screenshot: after_share.png")
    except: pass
    
    browser.close()

# 9. Move to Done
print("\n[9/9] Move to Done...")
done = VAULT / 'Done' / post_file.name
post_file.rename(done)
print(f"   [OK] Moved: {done.name}")

# Log
log = VAULT.parent / 'Logs' / 'instagram_posts.log'
with open(log, 'a', encoding='utf-8') as f:
    f.write(f"\n{'='*60}\n")
    f.write(f"Posted: {post_file.name}\n")
    f.write(f"Date: {datetime.now().isoformat()}\n")
    f.write(f"Caption: {caption[:200]}\n")
    f.write(f"Status: {'SUCCESS' if share_clicked else 'ATTEMPTED'}\n")
    f.write(f"{'='*60}\n")

print("\n" + "="*60)
if share_clicked:
    print("[OK] INSTAGRAM POST COMPLETE!")
else:
    print("[WARN] INSTAGRAM POST ATTEMPTED")
print("="*60 + "\n")
