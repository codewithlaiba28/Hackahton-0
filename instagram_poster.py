#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instagram Auto-Poster - GOLD TIER - FULLY AUTONOMOUS
Pattern: Same as LinkedIn (proven working)
"""

import sys, codecs, logging, argparse, time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstagramPoster:
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.approved = vault_path / 'Approved'
        self.done = vault_path / 'Done'
        self.logs = vault_path / 'Logs'
        self.session = vault_path.parent / 'instagram_session'
        for f in [self.approved, self.done, self.logs, self.session]:
            f.mkdir(parents=True, exist_ok=True)

    def check_approved(self):
        files = []
        for f in self.approved.glob('*.md'):
            if 'type: instagram' in f.read_text(encoding='utf-8').lower():
                files.append(f)
        return files

    def parse_post(self, filepath: Path):
        content = filepath.read_text(encoding='utf-8')
        data = {'content': '', 'image': None}
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 2:
                for line in parts[1].split('\n'):
                    if ':' in line:
                        k, v = line.split(':', 1)
                        if k.strip() == 'image':
                            data['image'] = v.strip()
        for sec in ['## Caption', '## Instagram Post', '## Content']:
            if sec in content:
                start = content.find(sec)
                end = content.find('---', start)
                if end == -1: end = len(content)
                lines = [l for l in content[start:end].split('\n') if not l.startswith('#') and not l.startswith('---')]
                data['content'] = '\n'.join(lines).strip()
                break
        if not data['content'] and len(parts) >= 3:
            data['content'] = parts[2].strip()
        return data

    def post(self, data: dict, image_path: Path, headless: bool = False) -> bool:
        try:
            print("  Opening Instagram...")
            if not image_path:
                print("  ERROR: Image required for Instagram!"); return False
            print(f"  Image: {image_path.name}")

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    self.session, headless=headless,
                    args=['--disable-blink-features=AutomationControlled', '--no-sandbox', '--start-maximized'],
                    timeout=300000)
                page = browser.pages[0] if browser.pages else browser.new_page()

                print("  Navigating to Instagram...")
                print("  Waiting for login (up to 3 min)...")
                page.goto('https://instagram.com', timeout=120000)

                # Infinite login wait
                logged, attempts = False, 0
                while not logged and attempts < 60:
                    time.sleep(3); attempts += 1
                    try:
                        if page.locator('[aria-label="New post"]').count() > 0 or page.locator('[href*="/accounts/"]').count() > 0:
                            print(f"  Login detected! ({attempts*3}s)"); logged = True; break
                    except: pass
                    if attempts % 10 == 0: print(f"  Waiting... ({attempts*3}s)")

                if not logged: browser.close(); return False
                page.wait_for_timeout(3000)

                # Dismiss overlays
                print("  Dismissing overlays...")
                for _ in range(3): page.keyboard.press('Escape'); time.sleep(0.5)
                try: page.locator('body').first.click(timeout=2000); time.sleep(1)
                except: pass

                # Open new post
                print("  Opening new post...")
                try:
                    page.locator('[aria-label="New post"]').first.click(timeout=5000)
                    page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"  New post failed: {e}"); browser.close(); return False

                # Upload image
                print("  Uploading image...")
                try:
                    with page.expect_file_chooser(timeout=10000) as fc:
                        try: page.locator('button:has-text("Select from computer")').first.click()
                        except: pass
                    file_chooser = fc.value
                    file_chooser.set_files(str(image_path.resolve()))
                    print("  Image uploaded!"); time.sleep(5)
                except Exception as e:
                    print(f"  Upload failed: {e}"); browser.close(); return False

                # Click Next
                print("  Clicking Next...")
                try:
                    for _ in range(3):
                        try:
                            page.locator('button:has-text("Next")').first.click(timeout=5000)
                            print("  Next clicked"); time.sleep(3); break
                        except: time.sleep(1)
                except: print("  Next failed, continuing")

                # Enter caption
                if data['content']:
                    print("  Entering caption...")
                    try:
                        page.locator('textarea[aria-label*="caption"]').first.click()
                        time.sleep(0.5)
                        page.keyboard.press('Control+A'); time.sleep(0.2)
                        page.keyboard.press('Delete'); time.sleep(0.5)
                        caption = data['content'][:1000] if len(data['content']) > 1000 else data['content']
                        page.keyboard.type(caption, delay=30)
                        print("  Caption entered!")
                    except: print("  Caption failed")

                # Click Share
                print("  Clicking Share...")
                page.wait_for_timeout(3000)
                try:
                    page.locator('button:has-text("Share")').first.wait_for(state='visible', timeout=10000)
                    page.locator('button:has-text("Share")').first.click(timeout=10000)
                    print("  Shared!"); time.sleep(5)
                    browser.close(); return True
                except Exception as e:
                    print(f"  Share failed: {e}"); browser.close(); return False
        except Exception as e:
            print(f"  Error: {e}"); return False

    def log_post(self, name, content, image=None):
        with open(self.logs / 'instagram_posts.log', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\nPosted: {name}\nDate: {datetime.now().isoformat()}\n")
            if image: f.write(f"Image: {image}\n")
            f.write(f"Content:\n{content}\n{'='*60}\n")

    def process(self, filepath: Path, headless=False, image_arg=None):
        print(f"\nProcessing: {filepath.name}")
        data = self.parse_post(filepath)
        if not data['content']: print("  No content"); return False
        print(f"  Content: {len(data['content'])} chars")
        img = Path(image_arg) if image_arg else None
        if not img and data.get('image'):
            p = self.vault_path / data['image']
            if p.exists(): img = p
        if not img:
            print("  No image specified"); return False
        ok = self.post(data, img, headless)
        if ok:
            (self.done / filepath.name).write_bytes(filepath.read_bytes())
            filepath.unlink()
            self.log_post(filepath.name, data['content'], str(img) if img else None)
            print(f"  Moved to Done"); return True
        print("  Failed"); return False

    def run(self, headless=False, image_arg=None):
        print("\n" + "="*60 + "\nInstagram Auto-Poster\n" + "="*60)
        print(f"Approved: {self.approved}\nSession: {self.session}\n")
        files = self.check_approved()
        if files:
            print(f"Found {len(files)} post(s)")
            for f in files: self.process(f, headless, image_arg)
        else: print("No approved posts")

if __name__ == '__main__':
    vault = Path(__file__).parent / 'Vault'
    if not vault.exists(): print("No Vault"); sys.exit(1)
    parser = argparse.ArgumentParser()
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--image', type=str, required=True, help='Image path (REQUIRED)')
    args = parser.parse_args()
    try: InstagramPoster(vault).run(headless=args.headless, image_arg=args.image)
    except Exception as e: print(f"ERROR: {e}"); sys.exit(1)
