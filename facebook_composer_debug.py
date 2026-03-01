#!/usr/bin/env python3
"""
Facebook Composer Debug - Find the correct selector for composer
"""

from playwright.sync_api import sync_playwright
from pathlib import Path

session_path = Path(__file__).parent / 'facebook_session'
session_path.mkdir(parents=True, exist_ok=True)

print("="*60)
print("FACEBOOK COMPOSER DEBUG")
print("="*60)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        session_path,
        headless=False,
        args=['--start-maximized'],
        timeout=120000
    )
    
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    print("\nNavigating to Facebook...")
    page.goto('https://www.facebook.com', timeout=120000, wait_until='domcontentloaded')
    
    print("\nWaiting for login (check browser and complete login if needed)...")
    for i in range(60, 0, -1):
        if page.locator('[aria-label="Menu"]').count() > 0:
            print("Login detected!")
            break
        print(f"  Waiting... {i}s remaining")
        page.wait_for_timeout(1000)
    
    page.wait_for_timeout(5000)
    
    print("\n=== DEBUG: Finding composer elements ===\n")
    
    # Test different selectors
    selectors = [
        '[aria-label*="What"]',
        'input[placeholder*="mind"]',
        'div:has-text("What\'s on your mind")',
        'div[role="button"]:has-text("What")',
        '[data-testid="status-cta-wrapper"]',
        'div[class*="ShareButton"]',
    ]
    
    for sel in selectors:
        try:
            count = page.locator(sel).count()
            print(f"  {sel}: {count} elements")
            
            if count > 0:
                # Try to get text content
                try:
                    text = page.locator(sel).first.inner_text(timeout=2000)
                    print(f"    -> Text: {text[:50]}...")
                except:
                    pass
                    
                # Try to get aria-label
                try:
                    label = page.locator(sel).first.get_attribute('aria-label', timeout=2000)
                    if label:
                        print(f"    -> aria-label: {label[:50]}...")
                except:
                    pass
                    
                # Try to get placeholder
                try:
                    placeholder = page.locator(sel).first.get_attribute('placeholder', timeout=2000)
                    if placeholder:
                        print(f"    -> placeholder: {placeholder[:50]}...")
                except:
                    pass
                    
                # Try to get bounding box
                try:
                    box = page.locator(sel).first.bounding_box(timeout=2000)
                    if box:
                        print(f"    -> Box: x={box['x']}, y={box['y']}, w={box['width']}, h={box['height']}")
                except:
                    pass
                    
        except Exception as e:
            print(f"  {sel}: ERROR - {e}")
    
    print("\n=== Testing Click ===\n")
    
    # Try clicking the first matching element
    try:
        composer = page.locator('[aria-label*="What"]').first
        if composer.count() > 0:
            print("Clicking on [aria-label*='What']...")
            composer.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            composer.click(force=True)
            print("Clicked!")
            
            page.wait_for_timeout(5000)
            page.screenshot(path='fb_debug_after_click.png')
            print("Screenshot saved: fb_debug_after_click.png")
            
            # Check if dialog appeared
            if page.locator('div[role="dialog"]').count() > 0:
                print("Dialog detected after click!")
            else:
                print("No dialog detected")
    except Exception as e:
        print(f"Click failed: {e}")
    
    print("\nKeeping browser open for 30 seconds...")
    page.wait_for_timeout(30000)
    
    browser.close()

print("\nDone!")
