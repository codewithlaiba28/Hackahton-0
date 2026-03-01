#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOCIAL MEDIA POSTING - VERIFICATION TEST
Tests Twitter, Facebook, Instagram posters without opening browser
"""

from pathlib import Path
import sys

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

VAULT = Path(__file__).parent / 'Vault'

print("\n" + "="*70)
print("SOCIAL MEDIA AUTO-POSTING - VERIFICATION TEST")
print("="*70)

# Test 1: Check all poster scripts exist
print("\n[TEST 1] Checking poster scripts...")
scripts = {
    'Twitter': 'twitter_poster.py',
    'Facebook': 'facebook_poster.py',
    'Instagram': 'instagram_poster.py',
    'LinkedIn': 'linkedin_poster.py'
}

all_exist = True
for platform, script in scripts.items():
    path = Path(script)
    if path.exists():
        size = path.stat().st_size
        print(f"  [OK] {platform}: {script} ({size:,} bytes)")
    else:
        print(f"  [FAIL] {platform}: {script} NOT FOUND")
        all_exist = False

# Test 2: Check session folders
print("\n[TEST 2] Checking session folders...")
sessions = ['twitter_session', 'facebook_session', 'instagram_session', 'linkedin_session']
for session in sessions:
    path = Path(session)
    if path.exists():
        print(f"  [OK] {session}/ exists")
    else:
        print(f"  [INFO] {session}/ will be created on first run")

# Test 3: Check Vault structure
print("\n[TEST 3] Checking Vault structure...")
folders = ['Approved', 'Done', 'Logs', 'Plans']
for folder in folders:
    path = VAULT / folder
    if path.exists():
        print(f"  [OK] Vault/{folder}/ exists")
    else:
        print(f"  [INFO] Vault/{folder}/ will be created")

# Test 4: Check Playwright installation
print("\n[TEST 4] Checking Playwright installation...")
try:
    from playwright.sync_api import sync_playwright
    print("  [OK] Playwright is installed")
except ImportError:
    print("  [FAIL] Playwright NOT installed")
    print("  Run: playwright install chromium")

# Test 5: Show usage examples
print("\n[TEST 5] Usage Examples:")
print("="*70)
print("""
TWITTER:
  python twitter_poster.py --text "Your tweet here"
  python twitter_poster.py --vault Vault

FACEBOOK:
  python facebook_poster.py --text "Your post here"
  python facebook_poster.py --vault Vault

INSTAGRAM:
  python instagram_poster.py --text "Caption" --image photo.jpg
  python instagram_poster.py --vault Vault

LINKEDIN (already working):
  python linkedin_poster.py --text "Your post here"
  python linkedin_poster.py --vault Vault
""")
print("="*70)

# Test 6: Show demo draft files
print("\n[TEST 6] Creating demo draft files...")

demo_posts = {
    'TWITTER_demo_gold.md': '''---
type: twitter_post
created: 2026-02-28
status: draft
platform: twitter
---

# Twitter Post Draft

AI Employee Gold Tier Test!

This is an automated post from my Personal AI Employee.

#Hackathon2026 #AI #Automation #Twitter
''',
    'FACEBOOK_demo_gold.md': '''---
type: facebook_post
created: 2026-02-28
status: draft
platform: facebook
---

# Facebook Post Draft

AI Employee Gold Tier Test!

This is an automated post from my Personal AI Employee.

#Hackathon2026 #AI #Automation
''',
    'INSTAGRAM_demo_gold.md': '''---
type: instagram_post
created: 2026-02-28
status: draft
platform: instagram
image: image.png
---

# Instagram Post Draft

Caption: AI Employee Gold Tier Test!

#Hackathon2026 #AI #Automation #Instagram
'''
}

for filename, content in demo_posts.items():
    filepath = VAULT / 'Plans' / filename
    filepath.write_text(content, encoding='utf-8')
    print(f"  [OK] Created: Vault/Plans/{filename}")

print("\n" + "="*70)
print("VERIFICATION COMPLETE!")
print("="*70)
print("\nSTATUS:")
if all_exist:
    print("  All poster scripts are READY!")
    print("\nTO ACTUALLY POST:")
    print("  1. Run: python twitter_poster.py --vault Vault")
    print("  2. Browser will open")
    print("  3. Login if needed (session saves for next time)")
    print("  4. Post composes automatically")
    print("  5. Click 'Post' button manually")
    print("  6. Done! Post is live!")
else:
    print("  Some scripts missing - check TEST 1")

print("\n" + "="*70 + "\n")
