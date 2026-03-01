#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Audit Logger - GOLD TIER
Personal AI Employee Hackathon 0

Logs all actions taken by the AI Employee for compliance, debugging, and transparency.
Stores logs in Vault/Logs/YYYY-MM-DD.json format with 90-day retention.

Usage:
    from audit_logger import AuditLogger
    
    logger = AuditLogger(vault_path)
    logger.log_action(
        action_type="email_send",
        actor="qwen_reasoner",
        target="client@example.com",
        parameters={"subject": "Invoice #123"},
        approval_status="approved",
        approved_by="human",
        result="success"
    )
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')


class AuditLogger:
    """Comprehensive audit logger for AI Employee actions."""
    
    def __init__(self, vault_path: str, retention_days: int = 90):
        """
        Initialize audit logger.
        
        Args:
            vault_path: Path to Obsidian vault
            retention_days: Number of days to retain logs (default: 90)
        """
        self.vault_path = Path(vault_path)
        self.logs_folder = self.vault_path / 'Logs'
        self.retention_days = retention_days
        
        # Create logs folder if not exists
        self.logs_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Clean old logs on initialization
        self._cleanup_old_logs()
    
    def _setup_logging(self):
        """Setup Python logging to file and console."""
        log_file = self.vault_path.parent / 'Logs' / 'system.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('AuditLogger')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
    
    def _get_today_log_file(self) -> Path:
        """Get path to today's log file."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.logs_folder / f'{today}.json'
    
    def _load_today_log(self) -> list:
        """Load today's log entries."""
        log_file = self._get_today_log_file()
        if log_file.exists():
            try:
                content = log_file.read_text(encoding='utf-8')
                return json.loads(content)
            except (json.JSONDecodeError, Exception) as e:
                self.logger.warning(f"Could not parse log file: {e}")
                return []
        return []
    
    def _save_today_log(self, entries: list):
        """Save log entries to today's log file."""
        log_file = self._get_today_log_file()
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False, default=str)
    
    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        approval_status: Optional[str] = None,
        approved_by: Optional[str] = None,
        result: str = "unknown",
        error: Optional[str] = None,
        retry_count: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Log an action to the audit log.
        
        Args:
            action_type: Type of action (email_send, whatsapp_reply, social_post, etc.)
            actor: Who/what performed the action (qwen_reasoner, gmail_watcher, etc.)
            target: Target of the action (email address, contact name, etc.)
            parameters: Action parameters (subject, message, etc.)
            approval_status: pending, approved, rejected, auto
            approved_by: human, system, auto
            result: success, failure, partial
            error: Error message if failed
            retry_count: Number of retry attempts
            metadata: Additional metadata
            
        Returns:
            Path to the log file
        """
        # Create log entry
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters or {},
            "approval_status": approval_status,
            "approved_by": approved_by,
            "result": result,
            "error": error,
            "retry_count": retry_count,
            "metadata": metadata or {}
        }
        
        # Load today's logs
        entries = self._load_today_log()
        
        # Add new entry
        entries.append(entry)
        
        # Save back
        self._save_today_log(entries)
        
        # Log to Python logger
        status_icon = "✅" if result == "success" else "❌" if result == "failure" else "⚠️"
        self.logger.info(
            f"{status_icon} {action_type} by {actor} -> {target} [{result}]"
        )
        
        return self._get_today_log_file()
    
    def get_logs_for_date(
        self,
        date: str,
        action_type: Optional[str] = None,
        actor: Optional[str] = None,
        result: Optional[str] = None
    ) -> list:
        """
        Get logs for a specific date with optional filters.
        
        Args:
            date: Date in YYYY-MM-DD format
            action_type: Filter by action type
            actor: Filter by actor
            result: Filter by result
            
        Returns:
            List of matching log entries
        """
        log_file = self.logs_folder / f'{date}.json'
        if not log_file.exists():
            return []
        
        try:
            content = log_file.read_text(encoding='utf-8')
            entries = json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.error(f"Could not parse log file: {e}")
            return []
        
        # Apply filters
        filtered = entries
        if action_type:
            filtered = [e for e in filtered if e.get('action_type') == action_type]
        if actor:
            filtered = [e for e in filtered if e.get('actor') == actor]
        if result:
            filtered = [e for e in filtered if e.get('result') == result]
        
        return filtered
    
    def get_recent_logs(
        self,
        days: int = 7,
        action_type: Optional[str] = None
    ) -> list:
        """
        Get logs from the last N days.
        
        Args:
            days: Number of days to look back
            action_type: Filter by action type
            
        Returns:
            List of matching log entries
        """
        all_entries = []
        today = datetime.now()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            entries = self.get_logs_for_date(date, action_type=action_type)
            all_entries.extend(entries)
        
        # Sort by timestamp
        all_entries.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return all_entries
    
    def get_statistics(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get action statistics for the last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with statistics
        """
        logs = self.get_recent_logs(days)
        
        stats = {
            "period_days": days,
            "total_actions": len(logs),
            "by_result": {},
            "by_action_type": {},
            "by_actor": {},
            "errors": 0,
            "success_rate": 0.0
        }
        
        for entry in logs:
            # Count by result
            result = entry.get('result', 'unknown')
            stats['by_result'][result] = stats['by_result'].get(result, 0) + 1
            
            # Count by action type
            action_type = entry.get('action_type', 'unknown')
            stats['by_action_type'][action_type] = stats['by_action_type'].get(action_type, 0) + 1
            
            # Count by actor
            actor = entry.get('actor', 'unknown')
            stats['by_actor'][actor] = stats['by_actor'].get(actor, 0) + 1
            
            # Count errors
            if entry.get('error'):
                stats['errors'] += 1
        
        # Calculate success rate
        if stats['total_actions'] > 0:
            success_count = stats['by_result'].get('success', 0)
            stats['success_rate'] = (success_count / stats['total_actions']) * 100
        
        return stats
    
    def _cleanup_old_logs(self):
        """Delete logs older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        try:
            for log_file in self.logs_folder.glob('*.json'):
                # Extract date from filename (YYYY-MM-DD.json)
                try:
                    date_str = log_file.stem
                    file_date = datetime.strptime(date_str, '%Y-%m-%d')
                    
                    if file_date < cutoff:
                        log_file.unlink()
                        self.logger.info(f"Deleted old log: {log_file.name}")
                except ValueError:
                    # Not a date-formatted file, skip
                    pass
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
    
    def export_logs(
        self,
        start_date: str,
        end_date: str,
        output_path: str
    ) -> Path:
        """
        Export logs to a file for external analysis.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_path: Path to output file
            
        Returns:
            Path to exported file
        """
        all_entries = []
        
        # Collect all logs in date range
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            entries = self.get_logs_for_date(date_str)
            all_entries.extend(entries)
            current += timedelta(days=1)
        
        # Write to output file
        output = Path(output_path)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(all_entries, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Exported {len(all_entries)} logs to {output_path}")
        return output


# Convenience functions for quick logging
_default_logger: Optional[AuditLogger] = None

def get_audit_logger(vault_path: str) -> AuditLogger:
    """Get or create the default audit logger."""
    global _default_logger
    if _default_logger is None:
        _default_logger = AuditLogger(vault_path)
    return _default_logger

def log_action(
    vault_path: str,
    action_type: str,
    actor: str,
    target: str,
    **kwargs
) -> Path:
    """Quick log an action."""
    logger = get_audit_logger(vault_path)
    return logger.log_action(
        action_type=action_type,
        actor=actor,
        target=target,
        **kwargs
    )


if __name__ == '__main__':
    # Test the audit logger
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audit_logger.py <vault_path>")
        print("Example: python audit_logger.py C:\\Code-journy\\Quator-4\\Hackahton-0\\Vault")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    logger = AuditLogger(vault_path)
    
    # Test logging
    print("\n" + "="*60)
    print("AUDIT LOGGER TEST")
    print("="*60)
    
    # Log a test action
    log_file = logger.log_action(
        action_type="test_action",
        actor="audit_logger_test",
        target="test_target",
        parameters={"test": "data"},
        approval_status="auto",
        approved_by="system",
        result="success"
    )
    
    print(f"\n[OK] Log entry created: {log_file}")
    
    # Get statistics
    stats = logger.get_statistics(days=1)
    print(f"\n[STATS] Today's Statistics:")
    print(f"   Total Actions: {stats['total_actions']}")
    print(f"   Success Rate: {stats['success_rate']:.1f}%")
    
    print("\n" + "="*60)
    print("AUDIT LOGGER READY")
    print("="*60 + "\n")
