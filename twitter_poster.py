#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter (X) Auto-Poster - GOLD TIER - FULLY AUTONOMOUS
Personal AI Employee Hackathon 0

Posts to Twitter/X using Playwright browser automation.
Pattern: Same as LinkedIn (proven working)

Usage:
    python twitter_poster.py                      # Auto-post all approved
    python twitter_poster.py --edit               # Edit before posting
    python twitter_poster.py --image path.jpg     # Add image
    python twitter_poster.py --headless           # Headless mode
"""

import sys
import codecs
import logging
import argparse
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TwitterPoster:
    """Post to Twitter/X via browser automation - LinkedIn pattern."""

    def __init__(self, vault_path: Path, session_path: Path = None):
        self.vault_path = vault_path
        self.approved_folder = vault_path / 'Approved'
        self.done_folder = vault_path / 'Done'
        self.logs_folder = vault_path / 'Logs'
        self.session_path = session_path or (vault_path.parent / 'twitter_session')

        # Ensure folders exist
        for folder in [self.approved_folder, self.done_folder, self.logs_folder, self.session_path]:
            folder.mkdir(parents=True, exist_ok=True)

        logger.info("Twitter Poster initialized")

    def check_approved_posts(self) -> list:
        """Check for approved Twitter post files."""
        approved_files = []

        for f in self.approved_folder.glob('*.md'):
            content = f.read_text(encoding='utf-8')
            if 'type: twitter' in content.lower():
                approved_files.append(f)

        return approved_files

    def parse_post_file(self, filepath: Path) -> dict:
        """Parse Twitter post file and extract content."""
        content = filepath.read_text(encoding='utf-8')

        post_data = {'content': '', 'hashtags': '', 'image': None, 'filepath': filepath}

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
                        if key == 'image':
                            post_data['image'] = value

        # Extract content from various sections
        for section in ['## Tweet Content', '## Twitter Post', '## Content']:
            if section in content:
                preview_start = content.find(section)
                preview_end = content.find('---', preview_start)
                if preview_end == -1:
                    preview_end = len(content)
                post_content = content[preview_start:preview_end]
                lines = [line for line in post_content.split('\n') 
                        if not line.startswith('#') and not line.startswith('---')]
                post_data['content'] = '\n'.join(lines).strip()
                break

        if not post_data['content'] and len(parts) >= 3:
            post_data['content'] = parts[2].strip()

        return post_data

    def post_to_twitter(self, post_data: dict, image_path: Path = None, headless: bool = False) -> bool:
        """Post content to Twitter/X - LinkedIn pattern."""
        try:
            print(f"  Opening Twitter...")
            if image_path:
                print(f"  Image to upload: {image_path.name}")

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--start-maximized'
                    ],
                    timeout=300000  # 5 minutes for login
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Navigate to Twitter
                print(f"  Navigating to Twitter...")
                print(f"  Waiting for login (up to 3 minutes)...")
                page.goto('https://twitter.com', timeout=120000)

                # Wait for login - INFINITE WAIT LIKE LINKEDIN
                logged_in = False
                wait_attempts = 0
                max_wait_attempts = 60  # 3 minutes

                while not logged_in and wait_attempts < max_wait_attempts:
                    time.sleep(3)
                    wait_attempts += 1

                    try:
                        # Check for Tweet button (logged in indicator)
                        tweet_btn = page.locator('[data-testid="SideNav_NewTweet_Button"]')
                        if tweet_btn.count() > 0:
                            print(f"  Login detected! ({wait_attempts * 3}s)")
                            logged_in = True
                            break
                    except:
                        pass

                    # Show progress every 10 attempts
                    if wait_attempts % 10 == 0:
                        print(f"  Waiting for login... ({wait_attempts * 3}s elapsed)")

                if not logged_in:
                    print(f"  Login timeout!")
                    browser.close()
                    return False

                # Wait for page to stabilize
                page.wait_for_timeout(3000)

                # DISMISS OVERLAYS (Escape key like LinkedIn)
                print(f"  Dismissing overlays...")
                for i in range(3):
                    page.keyboard.press('Escape')
                    page.wait_for_timeout(500)

                # Click on body to dismiss any popups
                try:
                    page.locator('body').first.click(timeout=2000)
                    page.wait_for_timeout(1000)
                except:
                    pass

                # METHOD 1: Go to compose URL (most reliable)
                print(f"  Opening tweet composer...")
                composer_opened = False

                try:
                    print(f"  Method 1: Direct URL...")
                    page.goto('https://twitter.com/compose/tweet', timeout=10000)
                    page.wait_for_timeout(5000)

                    composer = page.locator('[data-testid="tweetTextarea_0"]')
                    if composer.count() > 0:
                        print(f"  Composer opened via URL!")
                        composer_opened = True
                except Exception as e:
                    print(f"  Method 1 failed: {e}")

                # METHOD 2: Keyboard shortcut 't'
                if not composer_opened:
                    try:
                        print(f"  Method 2: Keyboard shortcut 't'...")
                        page.keyboard.press('t')
                        page.wait_for_timeout(5000)

                        composer = page.locator('[data-testid="tweetTextarea_0"]')
                        if composer.count() > 0:
                            print(f"  Composer opened via keyboard!")
                            composer_opened = True
                    except Exception as e:
                        print(f"  Method 2 failed: {e}")

                # METHOD 3: Click Tweet button
                if not composer_opened:
                    try:
                        print(f"  Method 3: Click Tweet button...")
                        tweet_btn = page.locator('[data-testid="SideNav_NewTweet_Button"]').first
                        tweet_btn.click(timeout=5000, force=True)
                        page.wait_for_timeout(5000)

                        composer = page.locator('[data-testid="tweetTextarea_0"]')
                        if composer.count() > 0:
                            print(f"  Composer opened via button!")
                            composer_opened = True
                    except Exception as e:
                        print(f"  Method 3 failed: {e}")

                if not composer_opened:
                    print(f"  Could not open composer")
                    browser.close()
                    return False

                # Wait for composer
                page.wait_for_timeout(2000)

                # Enter content
                print(f"  Entering content...")
                try:
                    editor = page.locator('[data-testid="tweetTextarea_0"]').first
                    editor.wait_for(state='visible', timeout=10000)
                    editor.click()
                    page.wait_for_timeout(500)

                    # Clear existing
                    page.keyboard.press('Control+A')
                    page.wait_for_timeout(200)
                    page.keyboard.press('Delete')
                    page.wait_for_timeout(500)

                    # Type content in chunks
                    content = post_data['content']
                    if len(content) > 280:
                        content = content[:280]
                        print(f"  Truncated to 280 chars")

                    chunk_size = 50
                    for i in range(0, len(content), chunk_size):
                        chunk = content[i:i+chunk_size]
                        page.keyboard.type(chunk, delay=30)
                        page.wait_for_timeout(100)

                    print(f"  Content entered!")

                except Exception as e:
                    print(f"  Error entering content: {e}")
                    browser.close()
                    return False

                # Upload image if provided
                if image_path:
                    print(f"  Uploading image...")
                    try:
                        media_btn = page.locator('[data-testid="toolBarImages"]').first
                        media_btn.click(timeout=5000)

                        with page.expect_file_chooser(timeout=10000) as fc_info:
                            pass
                        file_chooser = fc_info.value
                        file_chooser.set_files(str(image_path.resolve()))
                        print(f"  Image uploaded!")

                        page.wait_for_timeout(3000)
                    except Exception as e:
                        print(f"  Image upload failed: {e}")

                # Click Post button
                print(f"  Posting tweet...")
                page.wait_for_timeout(3000)

                try:
                    post_btn = page.locator('[data-testid="tweetButton"]').first
                    post_btn.wait_for(state='visible', timeout=10000)
                    post_btn.click(timeout=10000)
                    print(f"  Tweet posted!")

                    page.wait_for_timeout(5000)
                    browser.close()
                    return True

                except Exception as e:
                    print(f"  Error clicking Post: {e}")
                    browser.close()
                    return False

        except Exception as e:
            print(f"  Error: {e}")
            logger.error(f"Error posting to Twitter: {e}")
            return False

    def log_post(self, filename: str, content: str, image: str = None):
        """Log the posted content."""
        log_file = self.logs_folder / 'twitter_posts.log'

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Posted: {filename}\n")
            f.write(f"Date: {datetime.now().isoformat()}\n")
            if image:
                f.write(f"Image: {image}\n")
            f.write(f"Content:\n{content}\n")
            f.write(f"{'='*60}\n")

    def process_approved_post(self, filepath: Path, headless: bool = False,
                               edit_mode: bool = False, image_arg: str = None):
        """Process a single approved Twitter post."""
        print(f"\nProcessing: {filepath.name}")

        try:
            post_data = self.parse_post_file(filepath)

            if not post_data['content']:
                print(f"  No content found")
                return False

            print(f"  Content length: {len(post_data['content'])} chars")

            # Get image
            image_path = None
            if image_arg:
                image_path = Path(image_arg)
                if not image_path.exists():
                    print(f"  Image not found: {image_path}")
                    image_path = None
            elif post_data.get('image'):
                img_path = self.vault_path / post_data['image']
                if img_path.exists():
                    image_path = img_path

            # Post
            success = self.post_to_twitter(post_data, image_path, headless)

            if success:
                dest = self.done_folder / filepath.name
                filepath.rename(dest)
                print(f"  Moved to Done: {dest.name}")
                self.log_post(filepath.name, post_data['content'],
                              str(image_path) if image_path else None)
                return True
            else:
                print(f"  Failed to post")
                return False

        except Exception as e:
            print(f"  Error: {e}")
            logger.error(f"Error processing {filepath.name}: {e}")
            return False

    def run(self, headless: bool = False, edit_mode: bool = False, image_arg: str = None):
        """Run the Twitter poster."""
        print()
        print("=" * 60)
        print("Twitter Auto-Poster")
        print("=" * 60)
        print(f"Monitoring: {self.approved_folder}")
        print(f"Session: {self.session_path}")
        print(f"Mode: {'Headless' if headless else 'Interactive'}")
        print()

        try:
            approved_files = self.check_approved_posts()

            if approved_files:
                print(f"Found {len(approved_files)} approved Twitter post(s)")

                for filepath in approved_files:
                    self.process_approved_post(
                        filepath,
                        headless=headless,
                        edit_mode=edit_mode,
                        image_arg=image_arg
                    )
            else:
                print("No approved Twitter posts found")

        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error in Twitter poster: {e}")


if __name__ == '__main__':
    vault_path = Path(__file__).parent / 'Vault'

    if not vault_path.exists():
        print(f"ERROR: Vault folder not found: {vault_path}")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Twitter Auto-Poster')
    parser.add_argument('--headless', action='store_true', help='Headless mode')
    parser.add_argument('--edit', action='store_true', help='Edit before posting')
    parser.add_argument('--image', type=str, default=None, help='Image path')
    args = parser.parse_args()

    try:
        poster = TwitterPoster(vault_path)
        poster.run(
            headless=args.headless,
            edit_mode=args.edit,
            image_arg=args.image
        )
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
