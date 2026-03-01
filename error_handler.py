#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Handler & Recovery System - GOLD TIER
Personal AI Employee Hackathon 0

Handles errors gracefully with automatic recovery, exponential backoff,
and human escalation when needed.

Usage:
    from error_handler import ErrorHandler, ErrorCategory
    
    handler = ErrorHandler(vault_path)
    
    @handler.with_retry(max_attempts=3, category=ErrorCategory.TRANSIENT)
    def send_email(to, subject, body):
        # Your code here
        pass
"""

import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Callable, Any, Dict, List
from enum import Enum
from functools import wraps
import json
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')


class ErrorCategory(Enum):
    """Categories of errors with different handling strategies."""
    TRANSIENT = "transient"  # Network timeout, rate limit - retry
    AUTHENTICATION = "authentication"  # Expired token - alert human
    LOGIC = "logic"  # AI misinterpretation - human review
    DATA = "data"  # Corrupted file - quarantine
    SYSTEM = "system"  # Crash, disk full - restart


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    LOW = "low"  # Can auto-recover
    MEDIUM = "medium"  # Needs attention
    HIGH = "high"  # Needs immediate human intervention
    CRITICAL = "critical"  # System-wide failure


class ErrorHandler:
    """Centralized error handling and recovery system."""
    
    def __init__(self, vault_path: str):
        """
        Initialize error handler.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.errors_folder = self.vault_path / 'Errors'
        self.quarantine_folder = self.vault_path / 'Quarantine'
        
        # Create folders
        self.errors_folder.mkdir(parents=True, exist_ok=True)
        self.quarantine_folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Error tracking
        self.error_counts: Dict[str, int] = {}
        self.last_error_time: Dict[str, datetime] = {}
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1.0  # seconds
        self.max_delay = 60.0  # seconds
        
        # Load error history
        self._load_error_history()
    
    def _setup_logging(self):
        """Setup Python logging."""
        log_file = self.vault_path.parent / 'Logs' / 'errors.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('ErrorHandler')
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
    
    def _load_error_history(self):
        """Load error history from file."""
        history_file = self.errors_folder / 'history.json'
        if history_file.exists():
            try:
                content = history_file.read_text(encoding='utf-8')
                data = json.loads(content)
                self.error_counts = data.get('counts', {})
            except Exception as e:
                self.logger.warning(f"Could not load error history: {e}")
    
    def _save_error_history(self):
        """Save error history to file."""
        history_file = self.errors_folder / 'history.json'
        data = {
            'counts': self.error_counts,
            'last_updated': datetime.now().isoformat()
        }
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def classify_error(self, error: Exception) -> ErrorCategory:
        """
        Classify an error into a category.
        
        Args:
            error: The exception to classify
            
        Returns:
            ErrorCategory
        """
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Transient errors (retry)
        transient_keywords = ['timeout', 'temporary', 'rate limit', 'connection',
                             'network', 'unavailable', 'busy']
        if any(kw in error_str for kw in transient_keywords):
            return ErrorCategory.TRANSIENT
        
        # Authentication errors (alert human)
        auth_keywords = ['unauthorized', 'forbidden', 'authentication', 'token',
                        'expired', 'permission', '403', '401']
        if any(kw in error_str for kw in auth_keywords) or 'auth' in error_type:
            return ErrorCategory.LOGIC
        
        # Data errors (quarantine)
        data_keywords = ['corrupt', 'invalid', 'parse', 'format', 'missing field',
                        'validation', 'checksum']
        if any(kw in error_str for kw in data_keywords):
            return ErrorCategory.DATA
        
        # System errors (restart)
        system_keywords = ['disk', 'memory', 'permission denied', 'file system',
                          'out of space']
        if any(kw in error_str for kw in system_keywords):
            return ErrorCategory.SYSTEM
        
        # Default to logic error
        return ErrorCategory.LOGIC
    
    def get_severity(self, category: ErrorCategory, retry_count: int) -> ErrorSeverity:
        """
        Determine error severity.
        
        Args:
            category: Error category
            retry_count: Number of retries attempted
            
        Returns:
            ErrorSeverity
        """
        if category == ErrorCategory.LOGIC:
            return ErrorSeverity.HIGH
        elif category == ErrorCategory.SYSTEM:
            return ErrorSeverity.CRITICAL
        elif category == ErrorCategory.DATA:
            return ErrorSeverity.MEDIUM
        elif category == ErrorCategory.LOGIC:
            return ErrorSeverity.MEDIUM
        elif category == ErrorCategory.TRANSIENT:
            if retry_count >= self.max_retries:
                return ErrorSeverity.HIGH
            return ErrorSeverity.LOW
        
        return ErrorSeverity.MEDIUM
    
    def calculate_backoff(self, retry_count: int) -> float:
        """
        Calculate exponential backoff delay.
        
        Args:
            retry_count: Current retry attempt number
            
        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (2 ** retry_count)
        return min(delay, self.max_delay)
    
    def log_error(
        self,
        error: Exception,
        category: ErrorCategory,
        actor: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Path:
        """
        Log an error to the errors folder.
        
        Args:
            error: The exception
            category: Error category
            actor: Who encountered the error
            action: What action was being performed
            context: Additional context
            retry_count: Number of retries
            
        Returns:
            Path to error log file
        """
        timestamp = datetime.now()
        error_id = timestamp.strftime('%Y%m%d_%H%M%S_%f')
        
        error_data = {
            'id': error_id,
            'timestamp': timestamp.isoformat(),
            'category': category.value,
            'severity': self.get_severity(category, retry_count).value,
            'actor': actor,
            'action': action,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'retry_count': retry_count,
            'context': context or {},
            'resolved': False,
            'resolution': None
        }
        
        # Write error file
        error_file = self.errors_folder / f'ERROR_{error_id}.md'
        
        content = f'''---
id: {error_id}
timestamp: {error_data['timestamp']}
category: {category.value}
severity: {error_data['severity']}
actor: {actor}
action: {action}
error_type: {type(error).__name__}
retry_count: {retry_count}
status: unresolved
---

# Error Report

## Summary
**Action:** {action}  
**Actor:** {actor}  
**Category:** {category.value}  
**Severity:** {error_data['severity']}

## Error Details
```
{type(error).__name__}: {str(error)}
```

## Context
```json
{json.dumps(context or {}, indent=2, default=str)}
```

## Retry History
Retry Count: {retry_count}

## Resolution
[ ] Auto-resolved
[ ] Manually resolved
[ ] Escalated to human

## Notes
Add resolution notes here...
'''
        
        error_file.write_text(content, encoding='utf-8')
        
        # Update error counts
        key = f"{actor}:{action}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        self.last_error_time[key] = timestamp
        self._save_error_history()
        
        # Log to Python logger
        self.logger.error(
            f"[{category.value}] {action} by {actor}: {error}"
        )
        
        return error_file
    
    def quarantine_file(self, file_path: Path, reason: str) -> Path:
        """
        Move a corrupted/problematic file to quarantine.
        
        Args:
            file_path: Path to file
            reason: Reason for quarantine
            
        Returns:
            New path in quarantine
        """
        if not file_path.exists():
            return file_path
        
        # Create quarantine path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        quarantine_name = f'{timestamp}_{file_path.name}'
        quarantine_path = self.quarantine_folder / quarantine_name
        
        # Move file
        file_path.rename(quarantine_path)
        
        # Create metadata file
        meta_path = self.quarantine_folder / f'{quarantine_name}.meta'
        meta_content = f'''---
original_path: {file_path}
quarantine_path: {quarantine_path}
timestamp: {datetime.now().isoformat()}
reason: {reason}
status: pending_review
---

# Quarantined File

## Original Path
{file_path}

## Reason for Quarantine
{reason}

## Review Instructions
1. Review the file content
2. Determine if it can be safely restored
3. If safe, move back to original location
4. If not safe, delete permanently
'''
        meta_path.write_text(meta_content, encoding='utf-8')
        
        self.logger.warning(f"Quarantined file: {file_path} -> {quarantine_path}")
        
        return quarantine_path
    
    def should_retry(self, error: Exception, retry_count: int) -> bool:
        """
        Determine if an action should be retried.
        
        Args:
            error: The exception
            retry_count: Current retry count
            
        Returns:
            True if should retry
        """
        category = self.classify_error(error)
        
        # Never retry authentication errors
        if category == ErrorCategory.LOGIC:
            return False
        
        # Never retry system errors
        if category == ErrorCategory.SYSTEM:
            return False
        
        # Retry transient errors up to max
        if category == ErrorCategory.TRANSIENT:
            return retry_count < self.max_retries
        
        # Don't retry logic or data errors
        return False
    
    def with_retry(
        self,
        max_attempts: int = 3,
        category: Optional[ErrorCategory] = None,
        actor: str = "unknown",
        action: str = "unknown"
    ) -> Callable:
        """
        Decorator for automatic retry with exponential backoff.
        
        Args:
            max_attempts: Maximum retry attempts
            category: Force error category
            actor: Actor name for logging
            action: Action name for logging
            
        Returns:
            Decorated function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_error = None
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    
                    except Exception as e:
                        last_error = e
                        error_category = category or self.classify_error(e)
                        
                        # Log the error
                        self.log_error(
                            error=e,
                            category=error_category,
                            actor=actor or func.__name__,
                            action=action or func.__name__,
                            context={'args': str(args)[:100], 'kwargs': str(kwargs)[:100]},
                            retry_count=attempt
                        )
                        
                        # Check if should retry
                        if not self.should_retry(e, attempt):
                            self.logger.error(
                                f"Not retrying {func.__name__}: {error_category.value}"
                            )
                            raise
                        
                        # Calculate delay
                        delay = self.calculate_backoff(attempt)
                        self.logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        # Wait before retry
                        time.sleep(delay)
                
                # All attempts failed
                self.logger.error(
                    f"All {max_attempts} attempts failed for {func.__name__}"
                )
                raise last_error
            
            return wrapper
        return decorator
    
    def get_error_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get summary of errors in the last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Error summary dictionary
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        summary = {
            'period_days': days,
            'total_errors': 0,
            'by_category': {},
            'by_severity': {},
            'by_actor': {},
            'unresolved': 0,
            'top_errors': []
        }
        
        # Read all error files
        for error_file in self.errors_folder.glob('ERROR_*.md'):
            try:
                content = error_file.read_text(encoding='utf-8')
                
                # Parse frontmatter
                if '---' not in content:
                    continue
                
                frontmatter = content.split('---')[1]
                data = {}
                for line in frontmatter.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        data[key.strip()] = value.strip()
                
                # Check date
                if 'timestamp' in data:
                    error_date = datetime.fromisoformat(data['timestamp'])
                    if error_date < cutoff:
                        continue
                
                summary['total_errors'] += 1
                
                # Count by category
                category = data.get('category', 'unknown')
                summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
                
                # Count by severity
                severity = data.get('severity', 'unknown')
                summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
                
                # Count by actor
                actor = data.get('actor', 'unknown')
                summary['by_actor'][actor] = summary['by_actor'].get(actor, 0) + 1
                
                # Count unresolved
                if data.get('status') == 'unresolved':
                    summary['unresolved'] += 1
                
            except Exception as e:
                self.logger.debug(f"Could not parse error file: {error_file}")
        
        # Get top errors
        summary['top_errors'] = sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return summary
    
    def escalate_to_human(
        self,
        error: Exception,
        action: str,
        details: Optional[str] = None
    ) -> Path:
        """
        Create an escalation file for human review.
        
        Args:
            error: The exception
            action: Action that failed
            details: Additional details
            
        Returns:
            Path to escalation file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        escalation_file = self.vault_path / 'Needs_Action' / f'ESCALATION_{timestamp}.md'
        
        content = f'''---
type: escalation
created: {datetime.now().isoformat()}
priority: high
status: pending
---

# Human Intervention Required

## Summary
An automated action failed and requires human review.

## Failed Action
{action}

## Error Details
```
{type(error).__name__}: {str(error)}
```

## Additional Details
{details or 'No additional details provided.'}

## Required Actions
- [ ] Review the error
- [ ] Determine root cause
- [ ] Take corrective action
- [ ] Update this file with resolution

## Related Files
Check /Vault/Errors/ and /Vault/Logs/ for more information.
'''
        
        escalation_file.write_text(content, encoding='utf-8')
        
        self.logger.critical(
            f"Escalated to human: {action} - {error}"
        )
        
        return escalation_file


# Convenience functions
_default_handler: Optional[ErrorHandler] = None

def get_error_handler(vault_path: str) -> ErrorHandler:
    """Get or create the default error handler."""
    global _default_handler
    if _default_handler is None:
        _default_handler = ErrorHandler(vault_path)
    return _default_handler


if __name__ == '__main__':
    # Test the error handler
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python error_handler.py <vault_path>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    handler = ErrorHandler(vault_path)
    
    print("\n" + "="*60)
    print("ERROR HANDLER TEST")
    print("="*60)
    
    # Test error classification
    test_errors = [
        (TimeoutError("Connection timeout"), ErrorCategory.TRANSIENT),
        (PermissionError("Access denied"), ErrorCategory.LOGIC),
        (ValueError("Invalid format"), ErrorCategory.DATA),
        (OSError("Disk full"), ErrorCategory.SYSTEM),
        (Exception("Unknown error"), ErrorCategory.LOGIC),
    ]
    
    print("\nError Classification Tests:")
    for error, expected in test_errors:
        result = handler.classify_error(error)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"  {status} {type(error).__name__}: {result.value}")
    
    # Test backoff calculation
    print("\nBackoff Calculation:")
    for i in range(5):
        delay = handler.calculate_backoff(i)
        print(f"  Retry {i}: {delay:.1f}s")
    
    # Get error summary
    summary = handler.get_error_summary(days=7)
    print(f"\nError Summary (Last 7 days):")
    print(f"  Total Errors: {summary['total_errors']}")
    print(f"  Unresolved: {summary['unresolved']}")
    
    print("\n" + "="*60)
    print("ERROR HANDLER READY")
    print("="*60 + "\n")
