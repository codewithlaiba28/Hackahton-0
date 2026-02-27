# gmail_watcher.py
"""
Gmail Watcher - Monitors Gmail for unread, important messages
and creates action files in Vault/Needs_Action folder.

Usage: python gmail_watcher.py
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime
from pathlib import Path
import sys
import time

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str = None):
        # Default paths
        if credentials_path is None:
            credentials_path = Path(__file__).parent / 'credentials.json'
        
        super().__init__(vault_path, check_interval=120)
        
        # Load credentials
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(__file__).parent / 'token.json'
        
        # Load token
        if not self.token_path.exists():
            print("ERROR: token.json not found!")
            print("Run 'python auth_setup.py' first to authorize.")
            sys.exit(1)
        
        self.creds = Credentials.from_authorized_user_file(self.token_path)
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.processed_ids = set()
        
        # Load already processed IDs from existing files
        self._load_processed_ids()

    def _load_processed_ids(self):
        """Load already processed email IDs from Needs_Action folder."""
        # Only load from existing EMAIL_*.md files
        for f in self.needs_action.glob('EMAIL_*.md'):
            try:
                email_id = f.stem.replace('EMAIL_', '')
                self.processed_ids.add(email_id)
            except:
                pass
        
        # Also mark existing unread emails as processed (avoid flooding on first run)
        try:
            results = self.service.users().messages().list(
                userId='me', q='is:unread', maxResults=100
            ).execute()
            messages = results.get('messages', [])
            for msg in messages:
                self.processed_ids.add(msg['id'])
            if messages:
                self.logger.info(f"Marked {len(messages)} existing unread emails as processed")
        except Exception as e:
            self.logger.error(f"Error loading existing emails: {e}")

    def check_for_updates(self) -> list:
        """Check for new unread emails."""
        try:
            # Check ALL unread emails (not just important)
            results = self.service.users().messages().list(
                userId='me', q='is:unread'
            ).execute()
            messages = results.get('messages', [])
            return [m for m in messages if m['id'] not in self.processed_ids]
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []

    def create_action_file(self, message) -> Path:
        """Create markdown action file for the email."""
        try:
            msg = self.service.users().messages().get(
                userId='me', id=message['id']
            ).execute()

            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}

            content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content
{msg.get('snippet', '')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
'''
            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
            filepath.write_text(content)
            self.processed_ids.add(message['id'])
            
            self.logger.info(f"Created action file: {filepath.name}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None

    def run(self):
        """Run the watcher loop."""
        self.logger.info('Starting GmailWatcher')
        print()
        print("Gmail Watcher is running...")
        print(f"Checking every {self.check_interval} seconds")
        print(f"Vault: {self.vault_path}")
        print(f"Output: {self.needs_action}")
        print()
        print("Press Ctrl+C to stop")
        print("-" * 40)
        
        while True:
            try:
                items = self.check_for_updates()
                if items:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(items)} new email(s)")
                    for item in items:
                        self.create_action_file(item)
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No new emails")
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)


if __name__ == '__main__':
    # Setup logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get vault path
    vault_path = Path(__file__).parent / 'Vault'
    
    if not vault_path.exists():
        print(f"ERROR: Vault folder not found: {vault_path}")
        sys.exit(1)
    
    # Create and run watcher
    watcher = GmailWatcher(str(vault_path))
    watcher.run()
