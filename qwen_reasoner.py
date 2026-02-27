#!/usr/bin/env python3
"""
Qwen Reasoner - AI Reasoning Loop for Personal AI Employee

This script:
1. Watches /Vault/Needs_Action folder for new files
2. Reads file contents and analyzes the task
3. Creates Plan.md files with step-by-step actions
4. Determines if human approval is needed
5. Creates reply drafts for emails/WhatsApp
6. Moves processed files to appropriate folders

Usage: python qwen_reasoner.py
"""

import time
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class QwenReasoner:
    """AI Reasoning engine for task processing."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.needs_action = vault_path / 'Needs_Action'
        self.plans = vault_path / 'Plans'
        self.done = vault_path / 'Done'
        self.pending_approval = vault_path / 'Pending_Approval'
        self.dashboard = vault_path / 'Dashboard.md'
        self.handbook = vault_path / 'Company_Handbook.md'

        # Ensure folders exist
        self.plans.mkdir(parents=True, exist_ok=True)
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved = vault_path / 'Approved'
        self.approved.mkdir(parents=True, exist_ok=True)

        # Track processed files
        self.processed_files = set()

        # Load existing processed files
        self._load_processed_files()

        self.logger = logging.getLogger(self.__class__.__name__)

    def _load_processed_files(self):
        """Load already processed files from Done folder."""
        for f in self.done.glob('*.md'):
            self.processed_files.add(f.name)
        for f in self.needs_action.glob('*.md'):
            self.processed_files.add(f.name)

    def check_for_new_tasks(self) -> List[Path]:
        """Check for new task files in Needs_Action folder."""
        new_tasks = []
        
        for f in self.needs_action.glob('*.md'):
            if f.name not in self.processed_files:
                # Skip if file is too new (still being written)
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    age = (datetime.now() - mtime).total_seconds()
                    if age > 2:  # File is at least 2 seconds old
                        new_tasks.append(f)
                except:
                    pass
        
        return new_tasks

    def read_task_file(self, filepath: Path) -> Dict:
        """Read and parse a task file."""
        content = filepath.read_text()
        
        # Extract frontmatter
        task_data = {
            'filepath': filepath,
            'content': content,
            'type': 'unknown',
            'from': 'unknown',
            'subject': 'unknown',
            'priority': 'medium',
            'status': 'pending'
        }
        
        # Parse YAML frontmatter
        frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    task_data[key.strip()] = value.strip()
        
        # Extract body content
        body_match = re.search(r'---\n.*?\n---\n(.*)', content, re.DOTALL)
        if body_match:
            task_data['body'] = body_match.group(1)
        
        return task_data

    def analyze_task(self, task_data: Dict) -> Dict:
        """Analyze task and determine required actions."""
        analysis = {
            'requires_approval': False,
            'approval_reason': None,
            'actions': [],
            'category': 'general',
            'urgency': 'normal'
        }
        
        content = task_data.get('content', '').lower()
        task_type = task_data.get('type', 'unknown')
        
        # Load handbook rules
        approval_threshold = 500.0  # Default from handbook
        
        # Check for payment/financial tasks
        if any(word in content for word in ['payment', 'invoice', 'pay', 'money', '$']):
            analysis['category'] = 'financial'
            
            # Extract amount if present
            amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', content)
            if amount_match:
                try:
                    amount = float(amount_match.group(1).replace(',', ''))
                    if amount > approval_threshold:
                        analysis['requires_approval'] = True
                        analysis['approval_reason'] = f'Payment over ${approval_threshold}'
                except:
                    pass
        
        # Check for email tasks
        if task_type == 'email':
            analysis['category'] = 'communication'
            analysis['actions'].append('reply_to_sender')
        
        # Check for WhatsApp tasks
        if task_type == 'whatsapp':
            analysis['category'] = 'communication'
            analysis['actions'].append('reply_to_sender')
        
        # Check for urgent keywords
        if any(word in content for word in ['urgent', 'asap', 'emergency', 'critical']):
            analysis['urgency'] = 'high'
        
        # Check for file drop tasks
        if task_type == 'file_drop':
            analysis['category'] = 'file_processing'
            analysis['actions'].append('review_file')
        
        return analysis

    def create_plan(self, task_data: Dict, analysis: Dict) -> Path:
        """Create a Plan.md file for the task."""
        task_name = task_data['filepath'].stem
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Determine actions based on analysis
        actions = analysis.get('actions', [])
        if not actions:
            actions = ['review_task', 'take_appropriate_action']
        
        # Build action checkboxes
        action_items = '\n'.join([f'- [ ] {action.replace("_", " ").title()}' for action in actions])
        
        # Add category-specific actions
        if analysis['category'] == 'financial':
            action_items += '\n- [ ] Verify payment details'
            action_items += '\n- [ ] Record in accounting system'
        
        if analysis['category'] == 'communication':
            action_items += '\n- [ ] Draft response'
            action_items += '\n- [ ] Review before sending'
        
        # Determine if approval is needed
        approval_status = "Required" if analysis['requires_approval'] else "Not Required"
        
        plan_content = f'''---
type: action_plan
task_source: {task_data['filepath'].name}
created: {timestamp}
category: {analysis['category']}
urgency: {analysis['urgency']}
approval_required: {approval_status}
status: pending
---

# Action Plan: {task_name}

## Task Summary
- **Type:** {task_data.get('type', 'Unknown')}
- **From:** {task_data.get('from', 'Unknown')}
- **Subject:** {task_data.get('subject', 'Unknown')}
- **Priority:** {task_data.get('priority', 'Medium')}
- **Category:** {analysis['category'].title()}
- **Urgency:** {analysis['urgency'].title()}

## Objective
Process and complete the task identified in {task_data['filepath'].name}

## Required Actions
{action_items}

## Approval Status
- **Human Approval:** {approval_status}
'''
        
        if analysis['requires_approval']:
            plan_content += f'''
- **Reason:** {analysis['approval_reason']}
- **Next Step:** Wait for approval before proceeding
'''
        else:
            plan_content += '''
- **Status:** Can proceed with actions
'''
        
        plan_content += f'''
## Notes
- Plan created by Qwen Reasoner
- Review Company Handbook for guidelines
- Move task to /Done when complete

---
*Generated: {timestamp}*
'''
        
        # Save plan file
        plan_path = self.plans / f'PLAN_{task_name}.md'
        plan_path.write_text(plan_content)
        
        self.logger.info(f"Created plan: {plan_path.name}")
        
        return plan_path

    def create_approval_request(self, task_data: Dict, analysis: Dict) -> Optional[Path]:
        """Create an approval request file for sensitive actions."""
        if not analysis['requires_approval']:
            return None

        task_name = task_data['filepath'].stem
        timestamp = datetime.now().isoformat()
        expires = datetime.now().replace(hour=23, minute=59).isoformat()

        # Extract details
        amount = "Unknown"
        recipient = task_data.get('from', 'Unknown')
        reason = task_data.get('subject', 'Unknown')

        amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', task_data.get('content', ''))
        if amount_match:
            amount = f"${amount_match.group(1)}"

        approval_content = f'''---
type: approval_request
action: payment
amount: {amount}
recipient: {recipient}
reason: {reason}
created: {timestamp}
expires: {expires}
status: pending
source_task: {task_data['filepath'].name}
---

# Approval Required

## Payment Details
- **Amount:** {amount}
- **To:** {recipient}
- **Reference:** {reason}
- **Source:** {task_data['filepath'].name}

## Why Approval is Required
{analysis['approval_reason']}

## Company Handbook Rules
- Payments over $500 require explicit approval
- Verify recipient details before approving
- Check invoice/reference number

## To Approve
1. Review the details above
2. Move this file to `/Vault/Approved` folder
3. The system will process the action

## To Reject
1. Move this file to `/Vault/Rejected` folder
2. Add a note explaining the rejection

---
*Created: {timestamp}*
*Expires: {expires}*
'''

        approval_path = self.pending_approval / f'APPROVAL_{task_name}_{datetime.now().strftime("%Y%m%d")}.md'
        approval_path.write_text(approval_content)

        self.logger.info(f"Created approval request: {approval_path.name}")

        return approval_path

    def create_reply_draft(self, task_data: Dict) -> Optional[Path]:
        """Create a reply draft for email/WhatsApp messages."""
        task_type = task_data.get('type', '')
        
        # Only create reply drafts for communication tasks
        if task_type not in ['email', 'whatsapp']:
            return None
        
        # Extract reply details
        to_address = task_data.get('from', 'Unknown')
        subject = task_data.get('subject', 'Re: Your Message')
        content = task_data.get('content', '')
        original_file = task_data['filepath'].name
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if task_type == 'email':
            # Create email reply draft
            draft_content = f'''---
type: email_reply
to: {to_address}
subject: Re: {subject}
in_reply_to: {task_data['filepath'].stem}
created: {datetime.now().isoformat()}
status: pending_approval
---

# Email Reply Draft

## Recipient
**To:** {to_address}

## Subject
Re: {subject}

## Reply Content

Dear Sender,

Thank you for your email. We have received your message and will respond shortly.

[Edit this draft with your response]

Best regards,
AI Employee

---

## Original Email Reference
{original_file}

---

## To Send This Email

1. Review and edit the reply above
2. Move this file to `/Vault/Approved/` folder
3. The email will be sent automatically by email_reply.py

## To Cancel

1. Move this file to `/Vault/Rejected/` folder

---
*Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
'''
            
            filepath = self.pending_approval / f'EMAIL_REPLY_{timestamp}.md'
            filepath.write_text(draft_content, encoding='utf-8')
            self.logger.info(f"Created email reply draft: {filepath.name}")
            return filepath
            
        elif task_type == 'whatsapp':
            # Create WhatsApp reply draft
            draft_content = f'''---
type: whatsapp_reply
to: {to_address}
original_message: {original_file}
created: {datetime.now().isoformat()}
status: pending_approval
---

# WhatsApp Reply Draft

## Recipient
**To:** {to_address}

## Reply Message

[Edit this draft with your WhatsApp response]

---

## Original Message Reference
{original_file}

---

## To Send This Message

1. Review and edit the reply above
2. Move this file to `/Vault/Approved/` folder
3. The message will be sent automatically by whatsapp_reply.py

## To Cancel

1. Move this file to `/Vault/Rejected/` folder

---
*Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
'''
            
            filepath = self.pending_approval / f'WHATSAPP_REPLY_{timestamp}.md'
            filepath.write_text(draft_content, encoding='utf-8')
            self.logger.info(f"Created WhatsApp reply draft: {filepath.name}")
            return filepath
        
        return None

    def process_task(self, filepath: Path):
        """Process a single task file."""
        self.logger.info(f"Processing task: {filepath.name}")

        try:
            # Read task
            task_data = self.read_task_file(filepath)

            # Analyze task
            analysis = self.analyze_task(task_data)

            # Create plan
            plan_path = self.create_plan(task_data, analysis)

            # Create approval request if needed
            if analysis['requires_approval']:
                approval_path = self.create_approval_request(task_data, analysis)
                print(f"  [!] Approval required: {approval_path.name}")
            else:
                print(f"  [OK] Plan created: {plan_path.name}")

            # Create reply draft for communication tasks
            reply_draft = self.create_reply_draft(task_data)
            if reply_draft:
                print(f"  [REPLY] Reply draft created: {reply_draft.name}")
                print(f"          Move to Approved/ to send the reply")

            # Mark as processed
            self.processed_files.add(filepath.name)

            # Update dashboard (increment pending count)
            self.update_dashboard()

        except Exception as e:
            self.logger.error(f"Error processing task {filepath.name}: {e}")

    def update_dashboard(self):
        """Update the dashboard with current task counts."""
        try:
            if not self.dashboard.exists():
                return
            
            # Count pending tasks
            pending_count = len([f for f in self.needs_action.glob('*.md') if f.name not in self.processed_files])
            plans_count = len(list(self.plans.glob('*.md')))
            approval_count = len(list(self.pending_approval.glob('*.md')))
            
            content = self.dashboard.read_text()
            
            # Update pending messages section
            if '## 📬 Pending Messages' in content:
                # Find the section and update
                pass  # Simple count update
            
            # Add quick stats
            stats_section = f'''
## 🔄 AI Processing Status
| Metric | Count |
|--------|-------|
| Pending Tasks | {pending_count} |
| Active Plans | {plans_count} |
| Awaiting Approval | {approval_count} |

*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
'''
            
            # Append stats if not present
            if '## 🔄 AI Processing Status' not in content:
                content += '\n' + stats_section
                self.dashboard.write_text(content)
            
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")

    def check_approvals(self):
        """Check for approved files - DO NOT auto-move reply files."""
        approved_folder = self.vault_path / 'Approved'

        if not approved_folder.exists():
            return

        for f in approved_folder.glob('*.md'):
            content = f.read_text()
            
            # DO NOT auto-move email/whatsapp reply files
            # These need to be processed by their respective reply scripts
            if 'type: email_reply' in content or 'type:email_reply' in content:
                self.logger.info(f"Email reply waiting in Approved/: {f.name}")
                continue
            if 'type: whatsapp_reply' in content or 'type:whatsapp_reply' in content:
                self.logger.info(f"WhatsApp reply waiting in Approved/: {f.name}")
                continue
            
            # Only move non-reply approved files
            self.logger.info(f"Processing approved file: {f.name}")
            dest = self.done / f.name
            try:
                f.rename(dest)
                self.logger.info(f"Moved approved file to Done: {f.name}")
            except Exception as e:
                self.logger.error(f"Error moving approved file: {e}")

    def run(self):
        """Run the reasoner loop."""
        self.logger.info('Starting Qwen Reasoner')
        print()
        print("=" * 60)
        print("Qwen Reasoner - AI Reasoning Loop")
        print("=" * 60)
        print(f"Vault: {self.vault_path}")
        print(f"Monitoring: {self.needs_action}")
        print(f"Plans folder: {self.plans}")
        print(f"Approval folder: {self.pending_approval}")
        print()
        print("Waiting for new tasks...")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        while True:
            try:
                # Check for new tasks
                new_tasks = self.check_for_new_tasks()
                
                if new_tasks:
                    print(f"\n[{self._get_timestamp()}] Found {len(new_tasks)} new task(s)")
                    for task in new_tasks:
                        self.process_task(task)
                else:
                    print(f"[{self._get_timestamp()}] No new tasks")
                
                # Check for approved files
                self.check_approvals()
                
            except Exception as e:
                self.logger.error(f"Error in reasoner loop: {e}")
            
            time.sleep(10)  # Check every 10 seconds
    
    def _get_timestamp(self):
        return datetime.now().strftime('%H:%M:%S')


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get vault path
    vault_path = Path(__file__).parent / 'Vault'
    
    if not vault_path.exists():
        print(f"ERROR: Vault folder not found: {vault_path}")
        import sys
        sys.exit(1)
    
    # Create and run reasoner
    reasoner = QwenReasoner(vault_path)
    reasoner.run()
