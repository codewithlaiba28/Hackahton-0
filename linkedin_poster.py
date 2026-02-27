#!/usr/bin/env python3
"""
LinkedIn Auto-Poster - Posts to LinkedIn via browser automation

This script:
1. Reads approved LinkedIn posts from Vault/Approved/
2. Allows text editing before posting
3. Supports image uploads
4. Logs into LinkedIn via browser automation
5. Posts the content automatically
6. Moves processed files to Vault/Done/

Usage: 
    python linkedin_poster.py                    # Interactive mode
    python linkedin_poster.py --headless         # Headless mode
    python linkedin_poster.py --edit             # Edit before post
    python linkedin_poster.py --image path.jpg   # Add image
"""

import sys
import codecs
import logging
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
                # Check if it's been approved (moved to Approved folder)
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
                # Remove markdown headers
                lines = []
                for line in post_content.split('\n'):
                    if not line.startswith('#') and not line.startswith('---'):
                        lines.append(line)
                post_data['content'] = '\n'.join(lines).strip()
        else:
            # Use entire content after frontmatter
            if '---' in content:
                parts = content.split('---')
                if len(parts) >= 3:
                    post_data['content'] = parts[2].strip()

        return post_data

    def post_to_linkedin(self, post_data: dict, image_path: Path = None, headless: bool = False) -> bool:
        """Post content to LinkedIn via browser automation with optional image."""
        try:
            print(f"  Opening LinkedIn...")

            with sync_playwright() as p:
                # Launch browser with persistent context (keep session)
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ],
                    timeout=120000  # 2 minutes for first load
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Go to LinkedIn
                print(f"  Navigating to LinkedIn...")
                print(f"  ⏳ If not logged in, please login now (waiting up to 2 minutes)...")
                page.goto('https://www.linkedin.com/feed/', timeout=120000)

                # Wait for page to load - give user time to login
                print(f"  ⏳ Waiting for LinkedIn feed to load...")
                try:
                    # Wait for feed to be visible
                    page.wait_for_selector('[aria-label="Start a post"]', timeout=60000)
                    print(f"  ✅ Feed loaded successfully")
                except PlaywrightTimeout:
                    print(f"  ⏳ Still waiting... Keep LinkedIn tab open and login if needed")
                    # Wait additional time
                    page.wait_for_timeout(60000)  # Wait 1 more minute
                    print(f"  Continuing...")

                # Click on "Start a post"
                print(f"  Clicking 'Start a post'...")
                try:
                    # Try multiple selectors for "Start a post" button
                    post_button = None
                    
                    # Method 1: aria-label
                    try:
                        post_button = page.locator('[aria-label="Start a post"]').first
                        post_button.click(timeout=5000)
                        print(f"  Post button clicked (method 1)")
                    except:
                        # Method 2: div with specific class
                        post_button = page.locator('.share-box-feed-entry__trigger').first
                        post_button.click(timeout=5000)
                        print(f"  Post button clicked (method 2)")
                    
                    # Wait for post dialog with better selector
                    print(f"  Waiting for post dialog...")
                    try:
                        # Wait for dialog to be visible
                        dialog = page.locator('div[role="dialog"]').first
                        dialog.wait_for(state='visible', timeout=10000)
                        print(f"  ✅ Post dialog opened")
                    except:
                        # Alternative: wait for textbox to appear
                        editor = page.locator('div[role="textbox"][contenteditable="true"]').first
                        editor.wait_for(state='visible', timeout=10000)
                        print(f"  ✅ Post editor ready")

                except Exception as e:
                    print(f"  ⚠️ Could not open post dialog: {e}")
                    browser.close()
                    return False

                # Find the text editor and type content
                print(f"  Entering post content...")
                try:
                    # LinkedIn uses a contenteditable div
                    editor = page.locator('div[role="textbox"][contenteditable="true"]').first
                    editor.wait_for(state='visible', timeout=10000)
                    print(f"  ✅ Editor found")

                    # Click editor to focus
                    editor.click()
                    page.wait_for_timeout(500)
                    print(f"  ✅ Editor focused")

                    # Clear any existing content (Ctrl+A, Delete)
                    print(f"  Clearing existing content...")
                    page.keyboard.press('Control+A')
                    page.wait_for_timeout(200)
                    page.keyboard.press('Delete')
                    page.wait_for_timeout(500)
                    print(f"  ✅ Editor cleared")

                    # Type the post content with better timing
                    print(f"  Typing content ({len(post_data['content'])} chars)...")
                    
                    # Type in chunks to avoid detection
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

                # Wait for content to render
                page.wait_for_timeout(3000)

                # Click Post button - try multiple methods
                print(f"  Clicking 'Post' button...")
                post_clicked = False
                
                # Method 1: Direct "Post" button
                try:
                    post_submit = page.locator('button:has-text("Post")').first
                    post_submit.click(timeout=10000)
                    print(f"  ✅ Post button clicked (method 1)")
                    post_clicked = True
                except:
                    pass
                
                # Method 2: Alternative selector
                if not post_clicked:
                    try:
                        post_submit = page.locator('.share-actions__primary-action').first
                        post_submit.click(timeout=10000)
                        print(f"  ✅ Post button clicked (method 2)")
                        post_clicked = True
                    except:
                        pass
                
                # Method 3: Any button with Post text
                if not post_clicked:
                    try:
                        post_submit = page.locator('button').filter(has_text='Post').first
                        post_submit.click(timeout=10000)
                        print(f"  ✅ Post button clicked (method 3)")
                        post_clicked = True
                    except:
                        pass
                
                if post_clicked:
                    # Wait for post to complete
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

    def process_approved_post(self, filepath: Path, headless: bool = False):
        """Process a single approved LinkedIn post - FULLY AUTONOMOUS."""
        print(f"\nProcessing: {filepath.name}")

        try:
            # Parse post file
            post_data = self.parse_post_file(filepath)

            if not post_data['content']:
                print(f"  ⚠️ No content found in {filepath.name}")
                return False

            print(f"  Post content length: {len(post_data['content'])} characters")

            # Post to LinkedIn (NO IMAGE - FULLY AUTONOMOUS)
            success = self.post_to_linkedin(post_data, None, headless)

            if success:
                # Move to Done folder
                dest = self.done_folder / filepath.name
                filepath.rename(dest)
                print(f"  ✅ Moved to Done: {dest.name}")

                # Log the post
                self.log_post(filepath.name, post_data['content'])
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

    def run(self, headless: bool = False):
        """Run the LinkedIn poster - FULLY AUTONOMOUS."""
        print()
        print("=" * 60)
        print("LinkedIn Auto-Poster - FULLY AUTONOMOUS")
        print("=" * 60)
        print(f"Monitoring: {self.approved_folder}")
        print(f"Session: {self.session_path}")
        print()
        print("ℹ️  Text-only posts (images not supported)")
        print()

        try:
            # Check for approved posts
            approved_files = self.check_approved_posts()

            if approved_files:
                print(f"Found {len(approved_files)} approved LinkedIn post(s)")

                for filepath in approved_files:
                    self.process_approved_post(filepath, headless)
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
        import sys
        sys.exit(1)

    # Parse command line arguments
    headless = '--headless' in sys.argv

    try:
        poster = LinkedInPoster(vault_path)
        poster.run(headless)
    except Exception as e:
        print(f"ERROR: {e}")
        import sys
        sys.exit(1)
