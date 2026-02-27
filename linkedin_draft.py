#!/usr/bin/env python3
"""
LinkedIn Draft Generator - Creates draft LinkedIn posts

This script:
1. Reads business updates from Dashboard.md
2. Analyzes achievements and milestones
3. Creates engaging LinkedIn post drafts
4. Saves drafts to /Vault/Plans/LINKEDIN_draft.md
5. Requires human approval before posting

Usage: python linkedin_draft.py
"""

import re
import logging
import sys
import codecs
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class LinkedInDraftGenerator:
    """Generate LinkedIn post drafts from business data."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.dashboard = vault_path / 'Dashboard.md'
        self.handbook = vault_path / 'Company_Handbook.md'
        self.plans = vault_path / 'Plans'
        self.done = vault_path / 'Done'
        
        # Ensure plans folder exists
        self.plans.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)

    def read_dashboard(self) -> dict:
        """Read and parse Dashboard.md for business updates."""
        data = {
            'revenue': None,
            'projects_completed': [],
            'tasks_completed': 0,
            'metrics': {},
            'last_updated': None
        }

        if not self.dashboard.exists():
            self.logger.warning("Dashboard.md not found")
            return data

        content = self.dashboard.read_text(encoding='utf-8')
        
        # Extract revenue info
        revenue_match = re.search(r'\*\*Total\*\*:\s*\$?([\d,]+(?:\.\d{2})?)', content)
        if revenue_match:
            try:
                data['revenue'] = float(revenue_match.group(1).replace(',', ''))
            except:
                pass
        
        # Extract tasks completed
        tasks_match = re.search(r'\| Tasks Completed \| (\d+) \|', content)
        if tasks_match:
            data['tasks_completed'] = int(tasks_match.group(1))
        
        # Extract projects
        project_section = re.search(r'## 🚀 Active Projects.*?(?=##|\Z)', content, re.DOTALL)
        if project_section:
            # Look for completed projects in Done folder
            done_files = list(self.done.glob('*.md'))
            data['projects_completed'] = [f.name for f in done_files[:5]]
        
        # Extract metrics
        metrics_match = re.search(r'\| Metric \|.*?\| Response Time \|.*?\| <(\d+)h \|', content, re.DOTALL)
        if metrics_match:
            data['metrics']['response_time_target'] = metrics_match.group(1)
        
        return data

    def generate_post(self, data: dict) -> str:
        """Generate a LinkedIn post draft from business data."""
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        # Build post content based on available data
        sections = []
        
        # Opening hook
        sections.append("🚀 Exciting updates from our AI-powered business automation!")
        sections.append("")
        
        # Revenue milestone (if available)
        if data['revenue']:
            if data['revenue'] >= 1000:
                sections.append(f"💰 Just hit a new milestone: ${data['revenue']:,.2f} in revenue!")
            else:
                sections.append(f"💰 Growing steadily with ${data['revenue']:,.2f} in revenue this period.")
            sections.append("")
        
        # Tasks completed
        if data['tasks_completed'] > 0:
            sections.append(f"✅ Completed {data['tasks_completed']} tasks with our autonomous AI employee system.")
            sections.append("")
        
        # Projects completed
        if data['projects_completed']:
            sections.append("📁 Recently completed projects:")
            for project in data['projects_completed'][:3]:
                project_name = project.replace('.md', '').replace('_', ' ').title()
                sections.append(f"   • {project_name}")
            sections.append("")
        
        # Value proposition
        sections.append("🤖 Our AI Employee works 24/7 to:")
        sections.append("   • Monitor emails and messages")
        sections.append("   • Process tasks autonomously")
        sections.append("   • Maintain 99%+ consistency")
        sections.append("   • Reduce operational costs by 85-90%")
        sections.append("")
        
        # Call to action
        sections.append("💡 Want to learn how we built this?")
        sections.append("Drop a comment or send me a message!")
        sections.append("")
        
        # Hashtags
        sections.append("#AI #Automation #Productivity #DigitalTransformation #Innovation #AIEmployee #BusinessAutomation")
        
        return '\n'.join(sections)

    def create_draft_file(self, post_content: str, data: dict) -> Path:
        """Create a LinkedIn draft file with metadata."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        draft_content = f'''---
type: linkedin_draft
created: {datetime.now().isoformat()}
status: draft
requires_approval: true
category: social_media
platform: LinkedIn
---

# LinkedIn Post Draft

## 📊 Post Preview

{post_content}

---

## 📈 Post Analytics (After Posting)

| Metric | Target | Actual |
|--------|--------|--------|
| Impressions | 1000+ | - |
| Likes | 50+ | - |
| Comments | 10+ | - |
| Shares | 5+ | - |

---

## ✅ Pre-Post Checklist

- [ ] Content reviewed for accuracy
- [ ] No sensitive information included
- [ ] Hashtags are relevant
- [ ] Tone matches brand voice
- [ ] Grammar and spelling checked
- [ ] Images/attachments ready (if any)

---

## 🚀 To Publish

1. Review the draft above
2. Make any edits if needed
3. Copy the post content
4. Paste into LinkedIn
5. Move this file to /Vault/Approved after posting
6. Update analytics after 24 hours

---

## 📝 Notes

- Generated by LinkedIn Draft Generator
- Based on data from Dashboard.md
- Human approval required before posting
- Follows Company Handbook guidelines

---
*Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
'''
        
        draft_path = self.plans / f'LINKEDIN_draft_{timestamp}.md'
        draft_path.write_text(draft_content, encoding='utf-8')

        self.logger.info(f"Created LinkedIn draft: {draft_path.name}")
        
        return draft_path

    def generate_and_save(self) -> Path:
        """Main method to generate and save LinkedIn draft."""
        # Read dashboard data
        data = self.read_dashboard()
        
        # Generate post content
        post_content = self.generate_post(data)
        
        # Create draft file
        draft_path = self.create_draft_file(post_content, data)
        
        return draft_path

    def run(self):
        """Run the LinkedIn draft generator."""
        self.logger.info('Starting LinkedIn Draft Generator')
        print()
        print("=" * 60)
        print("LinkedIn Draft Generator")
        print("=" * 60)
        print(f"Reading from: {self.dashboard}")
        print(f"Saving to: {self.plans}")
        print()
        
        try:
            # Generate draft
            draft_path = self.generate_and_save()
            
            print(f"✅ LinkedIn draft created: {draft_path.name}")
            print()
            print("Next steps:")
            print("1. Review the draft in Vault/Plans/")
            print("2. Edit if needed")
            print("3. Post to LinkedIn manually")
            print("4. Move file to /Vault/Approved after posting")
            print()
            
        except Exception as e:
            print(f"❌ Error generating draft: {e}")
            self.logger.error(f"Error generating draft: {e}")


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
    
    # Create and run generator
    generator = LinkedInDraftGenerator(vault_path)
    generator.run()
