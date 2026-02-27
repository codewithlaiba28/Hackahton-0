#!/usr/bin/env python3
"""
Email Reply Sender - Sends email replies via Gmail API

This script:
1. Reads approved email replies from Vault/Approved/
2. Sends emails via Gmail API
3. Moves processed files to Vault/Done/

Usage: python email_reply.py
"""

import base64
import sys
import codecs
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailReplySender:
    """Send email replies via Gmail API."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.approved_folder = vault_path / 'Approved'
        self.done_folder = vault_path / 'Done'
        self.pending_folder = vault_path / 'Pending_Approval'
        
        # Ensure folders exist
        self.approved_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)
        
        # Load credentials
        token_path = Path(__file__).parent / 'token.json'
        if not token_path.exists():
            raise Exception("token.json not found. Run auth_setup.py first.")
        
        self.creds = Credentials.from_authorized_user_file(token_path, [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly'
        ])
        self.service = build('gmail', 'v1', credentials=self.creds)
        
        logger.info("Email Reply Sender initialized")

    def check_approved_replies(self) -> list:
        """Check for approved email reply files."""
        approved_files = []
        
        for f in self.approved_folder.glob('*.md'):
            content = f.read_text()
            
            # Check if it's an email reply approval
            if 'type: email_reply' in content or 'type:email_reply' in content:
                approved_files.append(f)
        
        return approved_files

    def parse_reply_file(self, filepath: Path) -> dict:
        """Parse email reply file and extract details."""
        content = filepath.read_text()
        
        reply_data = {
            'to': '',
            'subject': '',
            'body': '',
            'in_reply_to': '',
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
                        
                        if key == 'to':
                            reply_data['to'] = value
                        elif key == 'subject':
                            reply_data['subject'] = value
                        elif key == 'in_reply_to':
                            reply_data['in_reply_to'] = value
        
        # Extract body (after ## Reply Content or similar)
        if '## Reply' in content:
            body_start = content.find('## Reply')
            body_content = content[body_start:]
            # Remove markdown headers
            lines = []
            for line in body_content.split('\n'):
                if not line.startswith('#') and not line.startswith('---'):
                    lines.append(line)
            reply_data['body'] = '\n'.join(lines).strip()
        else:
            # Use entire content after frontmatter as body
            if '---' in content:
                parts = content.split('---')
                if len(parts) >= 3:
                    reply_data['body'] = parts[2].strip()
        
        return reply_data

    def create_message(self, to: str, subject: str, body: str, in_reply_to: str = None) -> dict:
        """Create Gmail API message."""
        message = EmailMessage()
        message['to'] = to
        message['subject'] = subject
        message.set_content(body)
        
        # Add In-Reply-To header for threading
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to
        
        # Encode message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        return {'raw': encoded_message}

    def send_reply(self, reply_data: dict) -> bool:
        """Send email reply via Gmail API."""
        try:
            print(f"  Sending email to: {reply_data['to']}")
            print(f"  Subject: {reply_data['subject']}")
            
            message = self.create_message(
                to=reply_data['to'],
                subject=reply_data['subject'],
                body=reply_data['body'],
                in_reply_to=reply_data.get('in_reply_to')
            )
            
            # Send via Gmail API
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            print(f"  ✅ Email sent! Message ID: {sent_message['id']}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error sending email: {e}")
            logger.error(f"Error sending email: {e}")
            return False

    def process_approved_reply(self, filepath: Path):
        """Process a single approved email reply."""
        print(f"\nProcessing: {filepath.name}")
        
        try:
            # Parse reply file
            reply_data = self.parse_reply_file(filepath)
            
            if not reply_data['to']:
                print(f"  ⚠️ No recipient found in {filepath.name}")
                return False
            
            # Send email
            success = self.send_reply(reply_data)
            
            if success:
                # Move to Done folder
                dest = self.done_folder / filepath.name
                filepath.rename(dest)
                print(f"  ✅ Moved to Done: {dest.name}")
                return True
            else:
                print(f"  ⚠️ Failed to send, keeping in Approved")
                return False
                
        except Exception as e:
            print(f"  ❌ Error processing {filepath.name}: {e}")
            logger.error(f"Error processing {filepath.name}: {e}")
            return False

    def run(self):
        """Run the email reply processor."""
        print()
        print("=" * 60)
        print("Email Reply Sender - Checking for approved replies...")
        print("=" * 60)
        print(f"Monitoring: {self.approved_folder}")
        print()
        
        try:
            # Check for approved replies
            approved_files = self.check_approved_replies()
            
            if approved_files:
                print(f"Found {len(approved_files)} approved email reply(s)")
                
                for filepath in approved_files:
                    self.process_approved_reply(filepath)
            else:
                print("No approved email replies found")
                print()
                print("To send an email reply:")
                print("1. Create reply draft in Pending_Approval/")
                print("2. Move file to Approved/ when ready to send")
                print("3. This script will automatically send it")
                
        except Exception as e:
            print(f"Error: {e}")
            logger.error(f"Error in email reply sender: {e}")


def create_email_reply_draft(
    vault_path: Path,
    to: str,
    subject: str,
    body: str,
    in_reply_to: str = None,
    original_email: str = None
) -> Path:
    """Create an email reply draft file for approval."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    draft_content = f'''---
type: email_reply
to: {to}
subject: {subject}
in_reply_to: {in_reply_to or 'N/A'}
created: {datetime.now().isoformat()}
status: pending_approval
---

# Email Reply Draft

## Recipient
**To:** {to}

## Subject
{subject}

## Reply Content

{body}

---

## Original Email Reference
{original_email or 'N/A'}

---

## To Send This Email

1. Review the reply above
2. Make any edits if needed
3. Move this file to `/Vault/Approved/` folder
4. The email will be sent automatically

## To Cancel

1. Move this file to `/Vault/Rejected/` folder
2. Add a note explaining why

---
*Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
'''
    
    # Save to Pending_Approval
    pending_folder = vault_path / 'Pending_Approval'
    pending_folder.mkdir(parents=True, exist_ok=True)
    
    filepath = pending_folder / f'EMAIL_REPLY_{timestamp}.md'
    filepath.write_text(draft_content, encoding='utf-8')
    
    logger.info(f"Created email reply draft: {filepath.name}")
    
    return filepath


if __name__ == '__main__':
    vault_path = Path(__file__).parent / 'Vault'
    
    if not vault_path.exists():
        print(f"ERROR: Vault folder not found: {vault_path}")
        import sys
        sys.exit(1)
    
    try:
        sender = EmailReplySender(vault_path)
        sender.run()
    except Exception as e:
        print(f"ERROR: {e}")
        import sys
        sys.exit(1)
