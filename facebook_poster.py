#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Auto-Poster - GOLD TIER - FULLY AUTONOMOUS
Fixed version with robust selectors and better content entry
"""

import sys, codecs, logging, argparse, time, re
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FacebookPoster:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.approved = vault_path / 'Approved'
        self.done = vault_path / 'Done'
        self.logs = vault_path / 'Logs'
        self.session = vault_path.parent / 'facebook_session'
        for f in [self.approved, self.done, self.logs, self.session]:
            f.mkdir(parents=True, exist_ok=True)

    def check_approved(self):
        """Find approved Facebook posts."""
        files = []
        for f in self.approved.glob('*.md'):
            content = f.read_text(encoding='utf-8').lower()
            if 'type: facebook' in content or 'platform: facebook' in content:
                files.append(f)
        return files

    def parse_post(self, filepath: Path):
        """Parse post content from markdown file."""
        content = filepath.read_text(encoding='utf-8')
        data = {'content': '', 'image': None}
        
        # Parse front matter
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 2:
                for line in parts[1].split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        if k.strip() == 'image':
                            data['image'] = v.strip()
        
        # Find post content - look for various section headers
        for sec in ['## Post Content', '## Facebook Post', '## Content']:
            if sec in content:
                start = content.find(sec)
                end = content.find('---', start)
                if end == -1:
                    end = len(content)
                lines = [l for l in content[start:end].split('\n') 
                        if not l.startswith('#') and not l.startswith('---')]
                data['content'] = '\n'.join(lines).strip()
                break
        
        # Fallback: use content after front matter
        if not data['content'] and len(parts) >= 3:
            data['content'] = parts[2].strip()
        
        return data

    def wait_for_login(self, page, timeout_seconds=180):
        """Wait for Facebook login with multiple detection methods."""
        print("  Waiting for login (up to 3 min)...")
        logged_in = False
        start_time = time.time()
        attempts = 0
        
        while not logged_in and (time.time() - start_time) < timeout_seconds:
            time.sleep(3)
            attempts += 1
            
            # Multiple login detection methods
            try:
                # Method 1: Menu button (desktop)
                if page.locator('[aria-label="Menu"]').count() > 0:
                    print(f"  Login detected via Menu! ({attempts*3}s)")
                    logged_in = True
                    break
                    
                # Method 2: "What's on your mind?" composer
                if page.locator('[aria-label*="What\'s on your mind"]').count() > 0:
                    print(f"  Login detected via composer! ({attempts*3}s)")
                    logged_in = True
                    break
                    
                # Method 3: "What is on your mind" (alternative text)
                if page.locator('[aria-label*="What is on your mind"]').count() > 0:
                    print(f"  Login detected via composer alt! ({attempts*3}s)")
                    logged_in = True
                    break
                    
                # Method 4: Check for profile picture
                if page.locator('img[alt*="profile"], img[alt*="Profile"]').count() > 0:
                    print(f"  Login detected via profile! ({attempts*3}s)")
                    logged_in = True
                    break
                    
            except Exception as e:
                pass
                
            if attempts % 10 == 0:
                elapsed = int(time.time() - start_time)
                print(f"  Still waiting... ({elapsed}s)")
                # Take screenshot for debugging
                try:
                    page.screenshot(path='fb_login_wait.png')
                except:
                    pass
        
        return logged_in

    def open_composer(self, page):
        """Open the Facebook post composer by clicking the 'What's on your mind?' box."""
        print("  Opening composer...")
        page.wait_for_timeout(3000)
        
        # Take screenshot before trying
        page.screenshot(path='fb_before_composer.png')
        print("  Screenshot saved: fb_before_composer.png")
        
        # Debug: Print what elements we can find
        try:
            count_aria = page.locator('[aria-label*="What"]').count()
            count_input = page.locator('input[placeholder*="mind"]').count()
            count_div = page.locator('div[role="button"]:has-text("What")').count()
            print(f"  Debug: Found {count_aria} aria-label, {count_input} input, {count_div} div[role=button] elements")
        except:
            pass
        
        # Method 1: Click on div[role="button"]:has-text("What") - MOST RELIABLE
        # This specifically targets the composer box that says "What's on your mind, [Name]?"
        try:
            composer = page.locator('div[role="button"]:has-text("What")').first
            
            if composer.count() > 0:
                # Get bounding box for precise click
                box = composer.bounding_box(timeout=5000)
                if box:
                    composer.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    
                    # Click in the middle of the composer box
                    x = box['x'] + box['width'] / 2
                    y = box['y'] + box['height'] / 2
                    
                    print(f"  Clicking composer at ({x}, {y}) - Box: {box['width']}x{box['height']}")
                    
                    # Use mouse click at precise location
                    page.mouse.click(x, y)
                    print("  Composer clicked via div[role=button]")
                    
                    # Wait for modal to appear
                    page.wait_for_timeout(8000)
                    page.screenshot(path='fb_after_composer.png')
                    
                    return True
        except Exception as e:
            print(f"  Method 1 failed: {e}")
            pass
        
        # Method 2: Fallback - click any element with "What's on your mind" text
        try:
            composer = page.locator(':has-text("What\'s on your mind")').first
            
            if composer.count() > 0:
                box = composer.bounding_box(timeout=3000)
                if box:
                    x = box['x'] + 100  # Click towards the left side where input is
                    y = box['y'] + box['height'] / 2
                    page.mouse.click(x, y)
                    print(f"  Composer clicked at ({x}, {y}) via text")
                    
                    page.wait_for_timeout(8000)
                    page.screenshot(path='fb_after_composer.png')
                    return True
        except:
            pass
        
        # Method 3: Try aria-label
        try:
            composer = page.locator('[aria-label*="What"]').first
            if composer.count() > 0:
                composer.wait_for(state='visible', timeout=5000)
                composer.click(timeout=5000, force=True)
                print("  Composer clicked via aria-label")
                page.wait_for_timeout(8000)
                page.screenshot(path='fb_after_composer.png')
                return True
        except:
            pass
        
        # Method 4: Click at fixed coordinates based on debug output
        try:
            print("  Trying fixed coordinate click (401, 104)...")
            # Based on debug: x=401.5, y=84, height=40 -> center is y=104
            page.mouse.click(550, 104)
            page.wait_for_timeout(5000)
            page.screenshot(path='fb_after_composer.png')
            return True
        except:
            pass
        
        print("  All composer methods failed")
        page.screenshot(path='fb_composer_fail.png')
        return False

    def find_editor(self, page):
        """Find the post editor element in the composer modal."""
        editor_selectors = [
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
            'textarea[aria-label*="What"]',
            'textarea[aria-label*="Write"]',
            'div[data-testid="composer"] div[contenteditable]',
            '[aria-label*="What\'s on your mind"]',
            '[aria-label*="Write something"]',
            'p[data-visualcompletion="ignore-dynamic"]',
            'div[class*="editable"]',
            'div[class*="composer"] div[contenteditable]',
            'div[role="dialog"] div[contenteditable]',
            '[data-key="composer_text"]',
        ]
        
        for sel in editor_selectors:
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.wait_for(state='visible', timeout=3000)
                    print(f"  Found editor with: {sel}")
                    return el
            except:
                pass
        
        return None

    def enter_content(self, page, content: str) -> bool:
        """Enter content into the composer."""
        print("  Entering content...")
        
        try:
            # Take screenshot before typing
            page.screenshot(path='fb_before_type.png')
            
            # Find editor
            editor = self.find_editor(page)
            
            if editor is None:
                print("  No editor found, trying keyboard fallback...")
                # Try tabbing to find input
                for _ in range(10):
                    page.keyboard.press('Tab')
                    time.sleep(0.3)
            else:
                # Click and focus
                editor.click()
                page.wait_for_timeout(500)
                
                # Clear existing content
                try:
                    page.keyboard.press('Control+A')
                    page.wait_for_timeout(200)
                    page.keyboard.press('Delete')
                    page.wait_for_timeout(300)
                except:
                    pass
            
            # Type content in chunks to avoid issues
            content = content[:2000] if len(content) > 2000 else content
            
            # Type in chunks for reliability
            chunk_size = 100
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                page.keyboard.type(chunk, delay=30)
                page.wait_for_timeout(100)
                
            print(f"  Content entered! ({len(content)} chars)")
            
            # Wait for content to render
            page.wait_for_timeout(3000)
            
            # Screenshot after typing
            page.screenshot(path='fb_after_type.png')
            print("  Screenshots saved: fb_before_type.png, fb_after_type.png")
            
            return True
            
        except Exception as e:
            print(f"  Content entry failed: {e}")
            page.screenshot(path='fb_content_error.png')
            return False

    def upload_image(self, page, image_path: Path) -> bool:
        """Upload image to post."""
        print("  Uploading image...")
        page.screenshot(path='fb_before_photo.png')

        try:
            # Wait for composer to be stable
            page.wait_for_timeout(3000)
            
            # Look for photo/video button with multiple selectors
            photo_selectors = [
                '[aria-label*="Photo"]',
                '[aria-label*="photo"]',
                '[aria-label*="Photo/video"]',
                '[aria-label*="Add a photo"]',
                '[aria-label*="Add media"]',
                '[data-testid*="media"]',
                'div[role="button"][aria-label*="Photo"]',
                'div[role="button"][aria-label*="photo"]',
                'svg[aria-label*="photo"] + div',
                'i[class*="photo"]',
                '[data-key="media"]',
                'button:has-text("Photo")',
                'button:has-text("photo")',
            ]

            photo_btn = None
            for sel in photo_selectors:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        el.wait_for(state='visible', timeout=5000)
                        photo_btn = el
                        print(f"  Found photo button with: {sel}")
                        break
                except:
                    pass
            
            if photo_btn is None:
                print("  Photo button not found, trying alternative method...")
                # Try clicking any button that looks like a photo icon
                try:
                    # Facebook often has a green camera/photo icon
                    photo_btn = page.locator('[data-testid*="photo"]').first
                    if photo_btn.count() > 0:
                        photo_btn.wait_for(state='visible', timeout=3000)
                        print("  Found photo button via data-testid")
                except:
                    pass
            
            if photo_btn is not None:
                photo_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                photo_btn.click(timeout=5000)
                print("  Photo button clicked")
            else:
                print("  Could not find photo button, trying keyboard shortcut...")
                # Try Alt+O which sometimes opens file dialog
                page.keyboard.press('Alt+O')
                page.wait_for_timeout(2000)

            # Wait for file chooser with longer timeout
            print("  Waiting for file chooser...")
            with page.expect_file_chooser(timeout=20000) as fc_info:
                pass

            file_chooser = fc_info.value
            file_chooser.set_files(str(image_path.resolve()))
            print(f"  Image selected: {image_path.name}")

            # Wait for upload preview to load
            page.wait_for_timeout(10000)
            page.screenshot(path='fb_after_photo.png')
            print("  Image upload complete!")

            return True

        except Exception as e:
            print(f"  Image upload failed: {e}")
            page.screenshot(path='fb_photo_error.png')
            return False

    def click_post_button(self, page) -> bool:
        """Click the Post button."""
        print("  Clicking Post button...")
        page.wait_for_timeout(5000)
        
        # Screenshot before posting
        page.screenshot(path='fb_before_post.png')
        
        post_selectors = [
            '[aria-label="Post"]',
            'button:has-text("Post")',
            'div[role="button"]:has-text("Post")',
            '[data-testid*="post"]',
            'div[class*="post_button"]',
            'button[class*="post"]',
            '[class*="x1n2onr6"]:has-text("Post")',
        ]
        
        for sel in post_selectors:
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.wait_for(state='visible', timeout=5000)
                    el.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    el.click(timeout=5000)
                    print(f"  Posted with selector: {sel}")
                    page.wait_for_timeout(8000)
                    page.screenshot(path='fb_after_post.png')
                    return True
            except Exception as e:
                pass
        
        # Fallback: Try Enter key
        print("  Post button not found, trying Enter key...")
        page.keyboard.press('Enter')
        page.wait_for_timeout(5000)
        page.screenshot(path='fb_after_enter.png')
        return True

    def post(self, data: dict, image_path: Path = None, headless: bool = False) -> bool:
        """Main posting function."""
        try:
            print("  Opening Facebook...")
            if image_path:
                print(f"  Image: {image_path.name}")

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session,
                    headless=headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--start-maximized',
                        '--disable-dev-shm-usage',
                    ],
                    timeout=300000
                )
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Set viewport
                page.set_viewport_size({"width": 1920, "height": 1080})

                print("  Navigating to Facebook...")
                try:
                    page.goto('https://facebook.com', timeout=120000, wait_until='domcontentloaded')
                except Exception as e:
                    print(f"  Initial load issue: {e}")
                
                # Wait for login
                logged_in = self.wait_for_login(page)
                
                if not logged_in:
                    print("  Login not detected, closing...")
                    page.screenshot(path='fb_login_fail.png')
                    browser.close()
                    return False
                
                page.wait_for_timeout(3000)

                # Dismiss overlays
                print("  Dismissing overlays...")
                for _ in range(3):
                    page.keyboard.press('Escape')
                    time.sleep(0.5)
                try:
                    page.locator('body').first.click(timeout=2000)
                    time.sleep(1)
                except:
                    pass

                # Go to main Facebook page (not /home - that's a different UI)
                print("  Going to Facebook main page...")
                try:
                    page.goto('https://www.facebook.com', wait_until='domcontentloaded', timeout=30000)
                    page.wait_for_timeout(8000)
                except:
                    pass

                # Take screenshot for debugging
                page.screenshot(path='fb_debug.png')
                print("  Screenshot saved: fb_debug.png")

                # Open composer
                if not self.open_composer(page):
                    print("  Failed to open composer")
                    page.screenshot(path='fb_composer_fail.png')
                    browser.close()
                    return False
                
                page.wait_for_timeout(3000)

                # Enter content
                if not self.enter_content(page, data['content']):
                    print("  Failed to enter content")
                    browser.close()
                    return False

                # Upload image if provided
                if image_path:
                    if not self.upload_image(page, image_path):
                        print("  Image upload failed, continuing without image")

                # Click post button
                if not self.click_post_button(page):
                    print("  Failed to click post button")
                    browser.close()
                    return False
                
                # Wait for post to complete
                page.wait_for_timeout(5000)
                page.screenshot(path='fb_post_complete.png')
                
                browser.close()
                return True
                
        except Exception as e:
            print(f"  Error: {e}")
            try:
                page.screenshot(path='fb_fatal_error.png')
            except:
                pass
            return False

    def log_post(self, name, content, image=None):
        """Log the post to a file."""
        with open(self.logs / 'facebook_posts.log', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Posted: {name}\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            if image:
                f.write(f"Image: {image}\n")
            f.write(f"Content:\n{content}\n")
            f.write(f"{'='*60}\n")

    def process(self, filepath: Path, headless=False, image_arg=None):
        """Process a single post file."""
        print(f"\nProcessing: {filepath.name}")
        data = self.parse_post(filepath)
        
        if not data['content']:
            print("  No content found")
            return False
            
        print(f"  Content: {len(data['content'])} chars")
        
        # Determine image path
        img = Path(image_arg) if image_arg else None
        if not img and data.get('image'):
            p = self.vault_path / data['image']
            if p.exists():
                img = p
        
        # Post
        ok = self.post(data, img, headless)
        
        if ok:
            # Move to Done
            (self.done / filepath.name).write_bytes(filepath.read_bytes())
            filepath.unlink()
            self.log_post(filepath.name, data['content'], str(img) if img else None)
            print(f"  ✓ Moved to Done")
            return True
            
        print("  ✗ Failed")
        return False

    def run(self, headless=False, image_arg=None):
        """Main run method."""
        print("\n" + "="*60)
        print("Facebook Auto-Poster")
        print("="*60)
        print(f"Approved: {self.approved}")
        print(f"Session: {self.session}")
        print()
        
        files = self.check_approved()
        
        if files:
            print(f"Found {len(files)} Facebook post(s)")
            for f in files:
                self.process(f, headless, image_arg)
        else:
            print("No approved Facebook posts found")
            print("\nTo create a Facebook post:")
            print("  1. Create a .md file in Approved/")
            print("  2. Add 'type: facebook_post' in front matter")
            print("  3. Add content under '## Post Content'")

if __name__ == '__main__':
    vault = Path(__file__).parent / 'Vault'
    if not vault.exists():
        print("No Vault directory found")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description='Facebook Auto-Poster')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--image', type=str, default=None, help='Image to upload')
    parser.add_argument('--text', type=str, default=None, help='Direct text to post')
    args = parser.parse_args()
    
    try:
        poster = FacebookPoster(vault)
        
        # If --text is provided, create a temporary post
        if args.text:
            print(f"Posting direct text: {args.text[:50]}...")
            temp_file = vault / 'Approved' / f'facebook_temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
            temp_file.write_text(f'''---
type: facebook_post
created: {datetime.now().strftime("%Y-%m-%d")}
status: approved
platform: facebook
---

# Facebook Post

## Post Content
{args.text}
''', encoding='utf-8')
            poster.process(temp_file, args.headless, args.image)
        else:
            poster.run(headless=args.headless, image_arg=args.image)
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
