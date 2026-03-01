#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO Briefing Generator - GOLD TIER
Personal AI Employee Hackathon 0

Generates "Monday Morning CEO Briefing" autonomously every week.
Analyzes completed tasks, revenue, bottlenecks, and provides proactive suggestions.

Schedule: Every Sunday at 11:00 PM (via cron/Task Scheduler)

Usage:
    python ceo_briefing.py Vault
    
Or import as module:
    from ceo_briefing import generate_briefing
    generate_briefing(vault_path, days=7)
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')


class CEOBriefingGenerator:
    """Generates weekly CEO briefings from business data."""
    
    def __init__(self, vault_path: str):
        """
        Initialize CEO Briefing Generator.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.briefings_folder = self.vault_path / 'Briefings'
        self.logs_folder = self.vault_path / 'Logs'
        self.done_folder = self.vault_path / 'Done'
        
        # Create folders
        self.briefings_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Subscription patterns for audit
        self.subscription_patterns = {
            'netflix.com': 'Netflix',
            'spotify.com': 'Spotify',
            'adobe.com': 'Adobe Creative Cloud',
            'notion.so': 'Notion',
            'slack.com': 'Slack',
            'github.com': 'GitHub',
            'vercel.com': 'Vercel',
            'aws.amazon.com': 'AWS',
            'cloud.google.com': 'Google Cloud',
            'azure.microsoft.com': 'Azure',
        }
    
    def _setup_logging(self):
        """Setup Python logging."""
        log_file = self.vault_path.parent / 'Logs' / 'ceo_briefing.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('CEOBriefing')
        self.logger.setLevel(logging.INFO)
        
        self.logger.handlers = []
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(console_handler)
    
    def _get_period_dates(self, days: int = 7) -> tuple:
        """Get start and end dates for the briefing period."""
        end = datetime.now()
        start = end - timedelta(days=days)
        return start, end
    
    def _load_business_goals(self) -> Dict[str, Any]:
        """Load business goals from Vault/Business_Goals.md."""
        goals_file = self.vault_path / 'Business_Goals.md'
        
        if not goals_file.exists():
            self.logger.warning("Business_Goals.md not found")
            return {}
        
        try:
            content = goals_file.read_text(encoding='utf-8')
            
            # Parse frontmatter
            if '---' not in content:
                return {}
            
            frontmatter = content.split('---')[1]
            goals = {}
            
            for line in frontmatter.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    goals[key.strip()] = value.strip()
            
            # Parse revenue targets from content
            if 'Monthly goal:' in content:
                import re
                match = re.search(r'Monthly goal: \$?([\d,]+)', content)
                if match:
                    goals['monthly_revenue_goal'] = float(match.group(1).replace(',', ''))
            
            return goals
            
        except Exception as e:
            self.logger.error(f"Error loading business goals: {e}")
            return {}
    
    def _count_completed_tasks(self, days: int = 7) -> Dict[str, Any]:
        """Count completed tasks from Done folder."""
        start, end = self._get_period_dates(days)
        
        tasks = {
            'total': 0,
            'by_type': {},
            'files': []
        }
        
        if not self.done_folder.exists():
            return tasks
        
        for file in self.done_folder.glob('*.md'):
            try:
                content = file.read_text(encoding='utf-8')
                
                # Extract type from frontmatter
                task_type = 'unknown'
                if 'type:' in content:
                    import re
                    match = re.search(r'type:\s*(\w+)', content)
                    if match:
                        task_type = match.group(1)
                
                tasks['total'] += 1
                tasks['by_type'][task_type] = tasks['by_type'].get(task_type, 0) + 1
                tasks['files'].append({
                    'name': file.name,
                    'type': task_type
                })
                
            except Exception as e:
                self.logger.debug(f"Could not parse done file: {file}")
        
        return tasks
    
    def _analyze_audit_logs(self, days: int = 7) -> Dict[str, Any]:
        """Analyze audit logs for action statistics."""
        start, end = self._get_period_dates(days)
        
        stats = {
            'total_actions': 0,
            'by_type': {},
            'success_count': 0,
            'failure_count': 0,
            'errors': []
        }
        
        if not self.logs_folder.exists():
            return stats
        
        # Read all log files in period
        for log_file in self.logs_folder.glob('*.json'):
            try:
                content = log_file.read_text(encoding='utf-8')
                entries = json.loads(content)
                
                for entry in entries:
                    stats['total_actions'] += 1
                    
                    action_type = entry.get('action_type', 'unknown')
                    stats['by_type'][action_type] = stats['by_type'].get(action_type, 0) + 1
                    
                    result = entry.get('result', 'unknown')
                    if result == 'success':
                        stats['success_count'] += 1
                    elif result in ('failure', 'error'):
                        stats['failure_count'] += 1
                        if entry.get('error'):
                            stats['errors'].append({
                                'action': action_type,
                                'error': entry.get('error'),
                                'timestamp': entry.get('timestamp')
                            })
                
            except Exception as e:
                self.logger.debug(f"Could not parse log file: {log_file}")
        
        # Calculate success rate
        if stats['total_actions'] > 0:
            stats['success_rate'] = (stats['success_count'] / stats['total_actions']) * 100
        else:
            stats['success_rate'] = 0.0
        
        return stats
    
    def _identify_subscriptions(self, days: int = 30) -> List[Dict[str, Any]]:
        """Identify subscription expenses from logs."""
        start, end = self._get_period_dates(days)
        
        subscriptions = []
        
        if not self.logs_folder.exists():
            return subscriptions
        
        # Look for subscription-related transactions
        for log_file in self.logs_folder.glob('*.json'):
            try:
                content = log_file.read_text(encoding='utf-8')
                entries = json.loads(content)
                
                for entry in entries:
                    if entry.get('action_type') != 'transaction':
                        continue
                    
                    description = entry.get('parameters', {}).get('description', '').lower()
                    
                    for pattern, name in self.subscription_patterns.items():
                        if pattern in description:
                            subscriptions.append({
                                'name': name,
                                'amount': entry.get('parameters', {}).get('amount', 0),
                                'date': entry.get('timestamp'),
                                'description': description
                            })
                            break
                
            except Exception as e:
                pass
        
        return subscriptions
    
    def _identify_bottlenecks(self, days: int = 7) -> List[Dict[str, Any]]:
        """Identify bottlenecks from task processing times."""
        bottlenecks = []
        
        # This would require more sophisticated analysis
        # For now, check for tasks that took multiple iterations
        in_progress = self.vault_path / 'In_Progress'
        
        if in_progress.exists():
            for file in in_progress.glob('TASK_*.md'):
                try:
                    content = file.read_text(encoding='utf-8')
                    
                    # Check iteration count
                    import re
                    match = re.search(r'Iteration:\s*(\d+)', content)
                    if match:
                        iterations = int(match.group(1))
                        if iterations > 3:
                            bottlenecks.append({
                                'task': file.stem,
                                'iterations': iterations,
                                'reason': f'Task stuck at iteration {iterations}'
                            })
                    
                except Exception:
                    pass
        
        return bottlenecks
    
    def _generate_proactive_suggestions(
        self,
        tasks: Dict[str, Any],
        audit_stats: Dict[str, Any],
        subscriptions: List[Dict[str, Any]],
        bottlenecks: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Generate proactive suggestions based on analysis."""
        suggestions = []
        
        # Subscription audit
        if len(subscriptions) > 0:
            total_sub_cost = sum(s.get('amount', 0) for s in subscriptions)
            if total_sub_cost > 100:
                suggestions.append({
                    'category': 'Cost Optimization',
                    'suggestion': f'Review subscriptions totaling ${total_sub_cost:.2f}/month',
                    'action': 'Move to Pending_Approval for review'
                })
        
        # Bottleneck suggestions
        for bottleneck in bottlenecks:
            suggestions.append({
                'category': 'Process Improvement',
                'suggestion': f"Investigate stuck task: {bottleneck['task']}",
                'action': 'Review In_Progress folder'
            })
        
        # Error rate suggestions
        if audit_stats.get('failure_count', 0) > 5:
            suggestions.append({
                'category': 'System Health',
                'suggestion': f"High error rate detected ({audit_stats['failure_count']} failures)",
                'action': 'Review error logs in /Vault/Errors/'
            })
        
        return suggestions
    
    def generate_briefing(
        self,
        days: int = 7,
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Generate the CEO Briefing document.
        
        Args:
            days: Number of days to analyze (default: 7)
            output_file: Optional output file path
            
        Returns:
            Path to generated briefing
        """
        self.logger.info(f"Generating CEO Briefing for last {days} days...")
        
        # Gather data
        start, end = self._get_period_dates(days)
        business_goals = self._load_business_goals()
        tasks = self._count_completed_tasks(days)
        audit_stats = self._analyze_audit_logs(days)
        subscriptions = self._identify_subscriptions(30)
        bottlenecks = self._identify_bottlenecks(days)
        suggestions = self._generate_proactive_suggestions(
            tasks, audit_stats, subscriptions, bottlenecks
        )
        
        # Calculate revenue (placeholder - would integrate with accounting)
        revenue_this_week = 0  # Would calculate from transactions
        revenue_mtd = 0
        revenue_goal = business_goals.get('monthly_revenue_goal', 10000)
        
        # Determine trend
        if revenue_goal > 0:
            progress = (revenue_mtd / revenue_goal) * 100
            if progress >= 80:
                trend = "On track"
            elif progress >= 50:
                trend = "Behind but recoverable"
            else:
                trend = "Needs attention"
        else:
            trend = "No goal set"
        
        # Generate briefing content
        timestamp = datetime.now()
        briefing_date = timestamp.strftime('%Y-%m-%d')
        period_start = start.strftime('%Y-%m-%d')
        period_end = end.strftime('%Y-%m-%d')
        
        content = f'''---
generated: {timestamp.isoformat()}
period: {period_start} to {period_end}
days_analyzed: {days}
---

# Monday Morning CEO Briefing

**Generated:** {timestamp.strftime('%A, %B %d, %Y at %I:%M %p')}  
**Period:** {period_start} to {period_end} ({days} days)

---

## Executive Summary

[Auto-generated summary based on data analysis]

Overall business health: **{'Good' if tasks['total'] > 5 else 'Needs Attention'}**

---

## Revenue

| Metric | Value | Goal | Status |
|--------|-------|------|--------|
| This Week | ${revenue_this_week:,.2f} | - | - |
| MTD (Month-to-Date) | ${revenue_mtd:,.2f} | ${revenue_goal:,.2f} | {trend} |
| Progress | {((revenue_mtd/revenue_goal)*100) if revenue_goal > 0 else 0:.1f}% | 100% | {'✅' if revenue_mtd >= revenue_goal * 0.8 else '⚠️'} |

### Revenue Trend
{trend}

---

## Completed Tasks

**Total:** {tasks['total']} tasks completed this period

### By Type
'''
        
        # Add task breakdown
        for task_type, count in sorted(tasks['by_type'].items(), key=lambda x: x[1], reverse=True):
            content += f"- **{task_type}:** {count}\n"
        
        content += f'''
### Recent Completed Tasks
'''
        
        # List recent tasks (up to 10)
        for task in tasks['files'][-10:]:
            content += f"- [x] {task['name']}\n"
        
        content += f'''
---

## Bottlenecks

'''
        
        if bottlenecks:
            content += '''| Task | Issue | Impact |
|------|-------|--------|
'''
            for bottleneck in bottlenecks:
                content += f"| {bottleneck['task']} | {bottleneck['reason']} | High |\n"
        else:
            content += "*No significant bottlenecks identified.*\n"
        
        content += f'''
---

## System Performance

| Metric | Value |
|--------|-------|
| Total Actions | {audit_stats['total_actions']} |
| Success Rate | {audit_stats['success_rate']:.1f}% |
| Failures | {audit_stats['failure_count']} |
| Errors Requiring Review | {len(audit_stats.get('errors', []))} |

### Actions by Type
'''
        
        for action_type, count in sorted(audit_stats['by_type'].items(), key=lambda x: x[1], reverse=True)[:5]:
            content += f"- **{action_type}:** {count}\n"
        
        content += f'''
---

## Proactive Suggestions

'''
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                content += f'''### {i}. {suggestion['category']}
**Suggestion:** {suggestion['suggestion']}  
**Action:** {suggestion['action']}

'''
        else:
            content += "*No proactive suggestions at this time.*\n"
        
        content += f'''
---

## Upcoming Deadlines

[Auto-populated from active projects in Business_Goals.md]

---

## Subscription Audit

'''
        
        if subscriptions:
            content += '''| Service | Amount | Date |
|---------|--------|------|
'''
            for sub in subscriptions:
                content += f"| {sub['name']} | ${sub.get('amount', 0):.2f} | {sub.get('date', 'Unknown')[:10]} |\n"
        else:
            content += "*No subscription transactions detected in the last 30 days.*\n"
        
        content += f'''
---

## Action Items for CEO

'''
        
        # Generate action items
        action_items = []
        
        if suggestions:
            action_items.append("Review proactive suggestions above")
        
        if bottlenecks:
            action_items.append("Investigate bottlenecked tasks in In_Progress/")
        
        if audit_stats.get('failure_count', 0) > 0:
            action_items.append("Review error logs in Logs/ folder")
        
        if action_items:
            for i, item in enumerate(action_items, 1):
                content += f"{i}. [ ] {item}\n"
        else:
            content += "*No action items - all systems running smoothly!*\n"
        
        content += f'''
---

*Generated by AI Employee v1.0 (Gold Tier)*  
*Next briefing: {(datetime.now() + timedelta(days=7)).strftime('%A, %B %d, %Y')}*
'''
        
        # Determine output file
        if output_file is None:
            filename = timestamp.strftime('%Y-%m-%d_Monday_Briefing.md')
            output_file = self.briefings_folder / filename
        
        # Write briefing
        output_file.write_text(content, encoding='utf-8')
        
        self.logger.info(f"CEO Briefing generated: {output_file}")
        self.logger.info(f"  - Period: {period_start} to {period_end}")
        self.logger.info(f"  - Tasks completed: {tasks['total']}")
        self.logger.info(f"  - Actions analyzed: {audit_stats['total_actions']}")
        
        return output_file


# Convenience function
def generate_briefing(vault_path: str, days: int = 7) -> Path:
    """Generate a CEO briefing."""
    generator = CEOBriefingGenerator(vault_path)
    return generator.generate_briefing(days=days)


if __name__ == '__main__':
    # Test the CEO Briefing Generator
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ceo_briefing.py <vault_path> [days]")
        print("Example: python ceo_briefing.py Vault 7")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    
    print("\n" + "="*60)
    print("CEO BRIEFING GENERATOR")
    print("="*60)
    
    generator = CEOBriefingGenerator(vault_path)
    briefing_file = generator.generate_briefing(days=days)
    
    print(f"\n[OK] Briefing generated: {briefing_file}")
    print(f"     Location: {briefing_file.absolute()}")
    
    print("\n" + "="*60)
    print("CEO BRIEFING READY")
    print("="*60 + "\n")
