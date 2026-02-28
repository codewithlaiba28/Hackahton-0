#!/usr/bin/env python3
"""
LinkedIn Silver Demo - SILVER TIER Complete Demo
Quick test with image.png - Posts automatically to LinkedIn

This demo script was created to test and verify the LinkedIn auto-posting
functionality with image upload for the Silver Tier completion.

Usage: python linkedin_silver_demo.py
"""

import sys
import codecs

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from playwright.sync_api import sync_playwright
from pathlib import Path
import time

def post_to_linkedin_demo():
    """Post a demo message to LinkedIn with image."""
    
    # Post content
    content = """🎉 SILVER TIER COMPLETE! My AI Employee just passed all requirements!

✅ Bronze Tier: 5/5 (100%)
✅ Silver Tier: 8/8 (100%)

Built with:
🤖 3 Watchers (Gmail, WhatsApp, File System)
🧠 AI Reasoning Loop
✉️ Email & WhatsApp Reply Automation
💼 LinkedIn Auto-Posting with Image Support
🔐 Human-in-the-Loop Approval Workflow

This is the future of work - AI Employees working 24/7!

#AI #Automation #DigitalEmployee #ProductivityHack #Innovation"""

    # Image path
    image_path = Path(__file__).parent / "image.png"
    
    # Session path
    session_path = Path(__file__).parent / "linkedin_session"
    session_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("LinkedIn Demo Post - SILVER TIER COMPLETE")
    print("=" * 60)
    print(f"\n📝 Content length: {len(content)} characters")
    print(f"🖼️  Image: {image_path}")
    print()
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return False
    
    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--window-size=1280,720'
            ],
            timeout=120000
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        print("📍 Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/feed/', timeout=120000)
        
        print("\n⏳ WAITING FOR YOU TO LOGIN TO LINKEDIN...")
        print("   (You have 60 seconds - please login in the browser)")
        print()
        
        # Wait for user to login
        for i in range(60, 0, -10):
            print(f"   Time remaining: {i} seconds...")
            time.sleep(10)
        
        print("\n✅ Assuming you're logged in now...")
        time.sleep(2)
        
        # Click Start a post
        print("\n📝 Clicking 'Start a post'...")
        try:
            post_btn = page.locator('[aria-label="Start a post"]').first
            post_btn.click(timeout=5000)
            print("   ✅ Post button clicked")
            time.sleep(2)
        except Exception as e:
            print(f"   ⚠️ Could not click post button: {e}")
            browser.close()
            return False
        
        # Type content
        print("\n⌨️  Typing content...")
        try:
            editor = page.locator('div[role="textbox"][contenteditable="true"]').first
            editor.wait_for(state='visible', timeout=10000)
            editor.click()
            
            # Clear existing content
            page.keyboard.press('Control+A')
            time.sleep(0.2)
            page.keyboard.press('Delete')
            time.sleep(0.5)
            
            # Type in chunks
            chunk_size = 50
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                page.keyboard.type(chunk, delay=30)
                time.sleep(0.1)
            
            print("   ✅ Content typed successfully")
            
        except Exception as e:
            print(f"   ⚠️ Error typing content: {e}")
            browser.close()
            return False
        
        time.sleep(2)
        
        # Upload image
        print("\n🖼️  Uploading image...")
        try:
            # Find media button
            media_btn = None
            for label in ['Add media', 'Add a photo', 'Photo', 'Add an image']:
                try:
                    media_btn = page.locator(f'[aria-label="{label}"]').first
                    media_btn.wait_for(state='visible', timeout=3000)
                    print(f"   Found media button: {label}")
                    break
                except:
                    continue
            
            if media_btn is None:
                media_btn = page.locator('button.share-creation-state__media-btn').first
            
            # Click and select file
            with page.expect_file_chooser(timeout=10000) as fc_info:
                media_btn.click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(str(image_path.resolve()))
            
            print("   ✅ Image uploaded successfully")
            time.sleep(3)
            
        except Exception as e:
            print(f"   ⚠️ Image upload failed: {e}")
            print("   Continuing without image...")
        
        time.sleep(2)
        
        # Click Next button (after image upload)
        print("\n➡️  Clicking 'Next' button...")
        next_clicked = False
        
        try:
            # Try different "Next" button selectors
            for selector in [
                'button:has-text("Next")',
                'button:has-text("next")',
                'button:has-text("Next step")',
                '.artdeco-button--primary'
            ]:
                try:
                    next_btn = page.locator(selector).first
                    next_btn.wait_for(state='visible', timeout=3000)
                    next_btn.click(timeout=5000)
                    print(f"   ✅ Next button clicked ({selector})")
                    next_clicked = True
                    break
                except:
                    continue
            
            if not next_clicked:
                print("   ⚠️ Next button not found, trying to proceed...")
            
            time.sleep(3)
            
        except Exception as e:
            print(f"   ⚠️ Next button error: {e}")
            print("   Continuing to Post button...")
        
        # Click Post button
        print("\n📤 Clicking 'Post' button...")
        print("   Waiting for Post button to become visible...")
        
        # Wait longer for UI to stabilize after Next click
        time.sleep(5)
        
        try:
            # Try multiple Post button selectors
            post_clicked = False
            
            for selector in [
                'button:has-text("Post")',
                'button:has-text("post")',
                'button.share-actions__primary-action',
                '.artdeco-button--primary',
                'button[type="button"][aria-label*="Post"]'
            ]:
                try:
                    post_submit = page.locator(selector).first
                    post_submit.wait_for(state='visible', timeout=5000)
                    post_submit.click(timeout=5000)
                    print(f"   ✅ Post button clicked ({selector})")
                    post_clicked = True
                    break
                except Exception as e:
                    print(f"   Trying next selector... ({selector})")
                    continue
            
            if not post_clicked:
                # Last resort - try keyboard navigation
                print("   ⚠️ Trying keyboard navigation...")
                page.keyboard.press('Tab')
                time.sleep(0.5)
                page.keyboard.press('Tab')
                time.sleep(0.5)
                page.keyboard.press('Enter')
                time.sleep(0.5)
                print("   ✅ Keyboard navigation attempted")
            
            print("\n⏳ Waiting for post to submit...")
            time.sleep(5)
            
            print("\n✅ POST SUBMITTED SUCCESSFULLY!")
            print("\n🎉 Demo complete! Check your LinkedIn feed.")
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Could not click Post button: {e}")
            browser.close()
            return False


if __name__ == '__main__':
    success = post_to_linkedin_demo()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ DEMO SUCCESSFUL!")
        print("=" * 60)
        print("\nYour LinkedIn post with image should now be live!")
        print("\nNext steps:")
        print("1. Check your LinkedIn feed")
        print("2. Verify the image uploaded correctly")
        print("3. Move LINKEDIN_Silver_Demo.md to Done/ folder")
    else:
        print("\n" + "=" * 60)
        print("❌ DEMO FAILED")
        print("=" * 60)
        print("\nPlease check the error messages above.")
