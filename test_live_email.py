#!/usr/bin/env python3
"""
Live Gmail Test - Send yourself an email and watch it appear!

1. Run this script
2. Wait for instructions
3. Send email to: antigravityuser18@gmail.com
4. Watch the magic!
"""

import time
from pathlib import Path

vault_path = Path(__file__).parent / 'Vault' / 'Needs_Action'

print("=" * 60)
print("Gmail Watcher Live Test")
print("=" * 60)
print()
print("Step 1: Open Gmail in another window/tab")
print("Step 2: Send an email to: antigravityuser18@gmail.com")
print("        Subject: Test Email")
print()
print("Waiting for new email...")
print("(Watcher should detect it within 120 seconds)")
print()

# Count existing email files
existing = list(vault_path.glob('EMAIL_*.md'))
print(f"Current email files: {len(existing)}")
print()
print("Now send the email and watch this folder:")
print(f"  {vault_path}")
print()
print("Press Ctrl+C when done")
