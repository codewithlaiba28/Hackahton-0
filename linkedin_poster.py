#!/usr/bin/env python3
"""
LinkedIn Auto-Poster - Posts to LinkedIn via browser automation

This script:
1. Reads approved LinkedIn posts from Vault/Approved/
2. Allows text editing before posting (--edit option)
3. Supports image uploads (--image option)
4. Logs into LinkedIn via browser automation
5. Uploads image and clicks Next button automatically
6. Posts the content automatically
7. Moves processed files to Vault/Done/

FIXES APPLIED (v2.0):
- Added Next button click after image upload
- Improved Post button selectors (4 methods)
- Better wait times for UI stabilization
- Image upload with file chooser

Usage:
    python linkedin_poster.py                      # Auto-post approved drafts
    python linkedin_poster.py --edit               # Edit before posting
    python linkedin_poster.py --image path.jpg     # Add image to post
    python linkedin_poster.py --edit --image x.jpg # Both options
    python linkedin_poster.py --headless           # Headless mode
"""

import sys
import codecs
import logging
import argparse  # FIX 1: Proper argument parsing
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkedInPoster:
    """Post content to LinkedIn via browser automation."""

    def __init__(self, vault_path: Path, session_path: Path = None):
        self.vault_path = vault_path
        self.approved_folder = vault_path / 'Approved'
        self.done_folder = vault_path / 'Done'
        self.pending_folder = vault_path / 'Pending_Approval'
        self.session_path = session_path or (vault_path.parent / 'linkedin_session')

        # Ensure folders exist
        self.approved_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)

        logger.info("LinkedIn Poster initialized")

    def edit_post_content(self, content: str) -> str:
        """Allow user to edit post content before posting."""
        print("\n" + "=" * 60)
        print("EDIT POST CONTENT")
        print("=" * 60)
        print("\nCurrent content:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        print("\nOptions:")
        print("  1. Keep as is (press Enter)")
        print("  2. Edit content (type 'edit')")
        print("  3. Cancel post (type 'cancel')")
        print()
        
        choice = input("Your choice: ").strip().lower()
        
        if choice == 'cancel':
            return None
        elif choice == 'edit':
            print("\nEnter new content (type 'DONE' on a new line to finish):")
            print("-" * 60)
            lines = []
            while True:
                line = input()
                if line.strip() == 'DONE':
                    break
                lines.append(line)
            return '\n'.join(lines)
        else:
            return content

    def select_image(self, image_arg: str = None) -> Path:
        """Select image file for upload."""
        if image_arg:
            image_path = Path(image_arg)
            if image_path.exists():
                print(f"  Using image: {image_path}")
                return image_path
            else:
                print(f"  ⚠️ Image not found: {image_path}")
        
        # Interactive image selection
        print("\n" + "=" * 60)
        print("SELECT IMAGE FOR POST")
        print("=" * 60)
        print("\nOptions:")
        print("  1. No image (press Enter)")
        print("  2. Specify image path (type path)")
        print("  3. Browse images in Vault/Images/")
        print()
        
        choice = input("Your choice: ").strip()
        
        if not choice:
            return None
        elif choice == '3':
            images_folder = self.vault_path / 'Images'
            if images_folder.exists():
                images = list(images_folder.glob('*.png')) + list(images_folder.glob('*.jpg')) + list(images_folder.glob('*.jpeg'))
                if images:
                    print("\nAvailable images:")
                    for i, img in enumerate(images, 1):
                        print(f"  {i}. {img.name}")
                    print()
                    img_choice = input("Select image number: ").strip()
                    try:
                        idx = int(img_choice) - 1
                        if 0 <= idx < len(images):
                            return images[idx]
                    except:
                        pass
                else:
                    print("  No images found in Vault/Images/")
            else:
                print("  Images folder not found")
        else:
            image_path = Path(choice)
            if image_path.exists():
                return image_path
            else:
                print(f"  ⚠️ Image not found: {image_path}")
        
        return None

    def check_approved_posts(self) -> list:
        """Check for approved LinkedIn post files."""
        approved_files = []

        for f in self.approved_folder.glob('*.md'):
            content = f.read_text(encoding='utf-8')

            # Check if it's a LinkedIn draft/post
            if 'type: linkedin_draft' in content or 'type:linkedin_draft' in content:
                approved_files.append(f)

        return approved_files

    def parse_post_file(self, filepath: Path) -> dict:
        """Parse LinkedIn post file and extract content."""
        content = filepath.read_text(encoding='utf-8')

        post_data = {
            'content': '',
            'hashtags': '',
            'created': None,
            'filepath': filepath
        }

        # Extract frontmatter
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 2:
                frontmatter = parts[1]
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()

                        if key == 'created':
                            post_data['created'] = value

        # Extract post content from "Post Preview" section
        if '## 📊 Post Preview' in content:
            preview_start = content.find('## 📊 Post Preview')
            preview_end = content.find('---', preview_start)
            if preview_end == -1:
                preview_end = content.find('## 📈', preview_start)
            
            if preview_end != -1:
                post_content = content[preview_start:preview_end]
                lines = []
                for line in post_content.split('\n'):
                    if not line.startswith('#') and not line.startswith('---'):
                        lines.append(line)
                post_data['content'] = '\n'.join(lines).strip()
        else:
            if '---' in content:
                parts = content.split('---')
                if len(parts) >= 3:
                    post_data['content'] = parts[2].strip()

        return post_data

    # =========================================================
    # FIX 2: Image upload logic added inside post_to_linkedin()
    # =========================================================
    def post_to_linkedin(self, post_data: dict, image_path: Path = None, headless: bool = False) -> bool:
        """Post content to LinkedIn via browser automation with optional image."""
        try:
            print(f"  Opening LinkedIn...")
            if image_path:
                print(f"  🖼️  Image to upload: {image_path.name}")

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ],
                    timeout=120000
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                print(f"  Navigating to LinkedIn...")
                print(f"  ⏳ If not logged in, please login now (waiting up to 2 minutes)...")
                page.goto('https://www.linkedin.com/feed/', timeout=120000)

                print(f"  ⏳ Waiting for LinkedIn feed to load...")
                try:
                    page.wait_for_selector('[aria-label="Start a post"]', timeout=60000)
                    print(f"  ✅ Feed loaded successfully")
                except PlaywrightTimeout:
                    print(f"  ⏳ Still waiting... Keep LinkedIn tab open and login if needed")
                    page.wait_for_timeout(60000)
                    print(f"  Continuing...")

                # Click on "Start a post"
                print(f"  Clicking 'Start a post'...")
                try:
                    post_button = None
                    try:
                        post_button = page.locator('[aria-label="Start a post"]').first
                        post_button.click(timeout=5000)
                        print(f"  Post button clicked (method 1)")
                    except:
                        post_button = page.locator('.share-box-feed-entry__trigger').first
                        post_button.click(timeout=5000)
                        print(f"  Post button clicked (method 2)")
                    
                    print(f"  Waiting for post dialog...")
                    try:
                        dialog = page.locator('div[role="dialog"]').first
                        dialog.wait_for(state='visible', timeout=10000)
                        print(f"  ✅ Post dialog opened")
                    except:
                        editor = page.locator('div[role="textbox"][contenteditable="true"]').first
                        editor.wait_for(state='visible', timeout=10000)
                        print(f"  ✅ Post editor ready")

                except Exception as e:
                    print(f"  ⚠️ Could not open post dialog: {e}")
                    browser.close()
                    return False

                # Enter post content
                print(f"  Entering post content...")
                try:
                    editor = page.locator('div[role="textbox"][contenteditable="true"]').first
                    editor.wait_for(state='visible', timeout=10000)
                    editor.click()
                    page.wait_for_timeout(500)

                    print(f"  Clearing existing content...")
                    page.keyboard.press('Control+A')
                    page.wait_for_timeout(200)
                    page.keyboard.press('Delete')
                    page.wait_for_timeout(500)

                    print(f"  Typing content ({len(post_data['content'])} chars)...")
                    content = post_data['content']
                    chunk_size = 100
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        page.keyboard.type(chunk, delay=50)
                        page.wait_for_timeout(100)
                    
                    print(f"  ✅ Content entered successfully!")

                except Exception as e:
                    print(f"  ⚠️ Error entering content: {e}")
                    browser.close()
                    return False

                page.wait_for_timeout(1000)

                # -----------------------------------------------
                # FIX 2 (core): Actually upload the image
                # -----------------------------------------------
                if image_path:
                    print(f"  🖼️  Uploading image: {image_path.name}...")
                    try:
                        media_btn = None
                        for label in ['Add media', 'Add a photo', 'Photo']:
                            try:
                                media_btn = page.locator(f'[aria-label="{label}"]').first
                                media_btn.wait_for(state='visible', timeout=4000)
                                break
                            except:
                                continue

                        if media_btn is None:
                            media_btn = page.locator('button.share-creation-state__media-btn').first

                        with page.expect_file_chooser(timeout=10000) as fc_info:
                            media_btn.click()
                        file_chooser = fc_info.value
                        file_chooser.set_files(str(image_path.resolve()))
                        print(f"  ✅ Image file selected via file chooser")

                        # Wait for image preview to load
                        page.wait_for_timeout(3000)
                        print(f"  ✅ Image uploaded and preview loaded")

                        # -----------------------------------------------
                        # CRITICAL FIX: Click "Next" button after image upload
                        # -----------------------------------------------
                        print(f"  ➡️  Clicking 'Next' button after image upload...")
                        next_clicked = False
                        
                        for selector in [
                            'button:has-text("Next")',
                            'button:has-text("next")',
                            'button:has-text("Next step")',
                            '.artdeco-button--primary'
                        ]:
                            try:
                                next_btn = page.locator(selector).first
                                next_btn.wait_for(state='visible', timeout=5000)
                                next_btn.click(timeout=5000)
                                print(f"  ✅ Next button clicked ({selector})")
                                next_clicked = True
                                break
                            except:
                                continue
                        
                        if not next_clicked:
                            print(f"  ⚠️  Next button not found, continuing...")
                        
                        # Wait for final post screen to load
                        page.wait_for_timeout(5000)

                    except Exception as e:
                        print(f"  ⚠️  Image upload failed: {e}")
                        print(f"  ⚠️  Continuing without image...")

                page.wait_for_timeout(2000)

                # Click Post button
                print(f"  Clicking 'Post' button...")
                post_clicked = False

                # Wait for UI to stabilize
                page.wait_for_timeout(3000)

                # Method 1: Direct "Post" button
                try:
                    post_submit = page.locator('button:has-text("Post")').first
                    post_submit.wait_for(state='visible', timeout=5000)
                    post_submit.click(timeout=10000)
                    print(f"  ✅ Post button clicked (method 1: has-text)")
                    post_clicked = True
                except:
                    pass

                # Method 2: Alternative selector
                if not post_clicked:
                    try:
                        post_submit = page.locator('.share-actions__primary-action').first
                        post_submit.wait_for(state='visible', timeout=5000)
                        post_submit.click(timeout=10000)
                        print(f"  ✅ Post button clicked (method 2: share-actions)")
                        post_clicked = True
                    except:
                        pass

                # Method 3: Any button with Post text
                if not post_clicked:
                    try:
                        post_submit = page.locator('button').filter(has_text='Post').first
                        post_submit.wait_for(state='visible', timeout=5000)
                        post_submit.click(timeout=10000)
                        print(f"  ✅ Post button clicked (method 3: filter)")
                        post_clicked = True
                    except:
                        pass

                # Method 4: Primary artdeco button
                if not post_clicked:
                    try:
                        post_submit = page.locator('.artdeco-button--primary').last
                        post_submit.wait_for(state='visible', timeout=5000)
                        post_submit.click(timeout=10000)
                        print(f"  ✅ Post button clicked (method 4: artdeco)")
                        post_clicked = True
                    except:
                        pass

                if post_clicked:
                    page.wait_for_timeout(5000)
                    print(f"  ✅ Post submitted successfully!")
                    browser.close()
                    return True
                else:
                    print(f"  ❌ Could not click Post button")
                    browser.close()
                    return False

        except Exception as e:
            print(f"  ❌ Error posting to LinkedIn: {e}")
            logger.error(f"Error posting to LinkedIn: {e}")
            return False

    # =========================================================
    # FIX 3: process_approved_post now accepts & passes image
    # =========================================================
    def process_approved_post(self, filepath: Path, headless: bool = False,
                               edit_mode: bool = False, image_arg: str = None):
        """Process a single approved LinkedIn post."""
        print(f"\nProcessing: {filepath.name}")

        try:
            post_data = self.parse_post_file(filepath)

            if not post_data['content']:
                print(f"  ⚠️ No content found in {filepath.name}")
                return False

            print(f"  Post content length: {len(post_data['content'])} characters")

            # FIX 3a: Optionally edit content before posting
            if edit_mode:
                edited = self.edit_post_content(post_data['content'])
                if edited is None:
                    print(f"  ℹ️ Post cancelled by user")
                    return False
                post_data['content'] = edited

            # FIX 3b: Resolve image
            image_path = None
            if image_arg:
                image_path = self.select_image(image_arg)
            elif not headless:
                image_path = self.select_image()

            # FIX 3c: Pass image_path (was always None before)
            success = self.post_to_linkedin(post_data, image_path, headless)

            if success:
                dest = self.done_folder / filepath.name
                filepath.rename(dest)
                print(f"  ✅ Moved to Done: {dest.name}")
                self.log_post(filepath.name, post_data['content'],
                              str(image_path) if image_path else None)
                return True
            else:
                print(f"  ⚠️ Failed to post, keeping in Approved")
                return False

        except Exception as e:
            print(f"  ❌ Error processing {filepath.name}: {e}")
            logger.error(f"Error processing {filepath.name}: {e}")
            return False

    def log_post(self, filename: str, content: str, image: str = None):
        """Log the posted content."""
        log_file = self.vault_path.parent / 'Logs' / 'linkedin_posts.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Posted: {filename}\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            if image:
                f.write(f"Image: {image}\n")
            f.write(f"Content:\n{content}\n")
            f.write(f"{'='*60}\n")

    # =========================================================
    # FIX 4: run() passes edit_mode and image_arg properly
    # =========================================================
    def run(self, headless: bool = False, edit_mode: bool = False, image_arg: str = None):
        """Run the LinkedIn poster."""
        print()
        print("=" * 60)
        print("LinkedIn Auto-Poster")
        print("=" * 60)
        print(f"Monitoring: {self.approved_folder}")
        print(f"Session: {self.session_path}")
        print(f"Mode: {'Headless' if headless else 'Interactive'}")
        if image_arg:
            print(f"Image: {image_arg}")
        print()

        try:
            approved_files = self.check_approved_posts()

            if approved_files:
                print(f"Found {len(approved_files)} approved LinkedIn post(s)")

                for filepath in approved_files:
                    self.process_approved_post(
                        filepath,
                        headless=headless,
                        edit_mode=edit_mode,
                        image_arg=image_arg
                    )
            else:
                print("No approved LinkedIn posts found")
                print()
                print("To auto-post to LinkedIn:")
                print("1. Generate draft: python linkedin_draft.py")
                print("2. Review draft in Vault/Plans/")
                print("3. Move file to Approved/ when ready")
                print("4. This script will auto-post!")

        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error in LinkedIn poster: {e}")


if __name__ == '__main__':
    vault_path = Path(__file__).parent / 'Vault'

    if not vault_path.exists():
        print(f"ERROR: Vault folder not found: {vault_path}")
        sys.exit(1)

    # FIX 1: Proper argument parsing with argparse
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Poster')
    parser.add_argument('--headless', action='store_true',
                        help='Run browser in headless mode')
    parser.add_argument('--edit', action='store_true',
                        help='Edit post content before posting')
    parser.add_argument('--image', type=str, default=None,
                        help='Path to image file to attach to the post')
    args = parser.parse_args()

    try:
        poster = LinkedInPoster(vault_path)
        poster.run(
            headless=args.headless,
            edit_mode=args.edit,
            image_arg=args.image
        )
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)