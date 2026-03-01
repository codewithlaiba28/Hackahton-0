#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ralph Wiggum Persistence Loop - GOLD TIER
Personal AI Employee Hackathon 0

Keeps the AI working autonomously until multi-step tasks are complete.
Uses file-movement based completion detection (Gold tier pattern).

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

Usage:
    from ralph_wiggum import RalphWiggumLoop
    
    ralph = RalphWiggumLoop(vault_path, max_iterations=10)
    
    # Start a task
    ralph.start_task(
        task_id="process_emails",
        prompt="Process all emails in Needs_Action folder",
        completion_criteria="All files moved to Done"
    )
    
    # Run the loop
    ralph.run()
"""

import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
import json
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')


class TaskStatus:
    """Task status constants."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"


class RalphWiggumLoop:
    """
    Ralph Wiggum Persistence Loop for autonomous task completion.
    
    File-Movement Based Completion Detection:
    1. Orchestrator creates state file: Vault/In_Progress/TASK_<id>.md
    2. Qwen processes task, creates plans, executes actions
    3. After each action, moves file closer to Done/
    4. Completion detected when file reaches Vault/Done/
    5. If task incomplete after max iterations, alert human
    """
    
    def __init__(
        self,
        vault_path: str,
        max_iterations: int = 10,
        iteration_delay: float = 5.0,
        actor: str = "ralph_wiggum"
    ):
        """
        Initialize Ralph Wiggum Loop.
        
        Args:
            vault_path: Path to Obsidian vault
            max_iterations: Maximum iterations before giving up (default: 10)
            iteration_delay: Delay between iterations in seconds (default: 5.0)
            actor: Actor name for audit logging
        """
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.iteration_delay = iteration_delay
        self.actor = actor
        
        # Folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        
        # Create folders
        for folder in [self.inbox, self.needs_action, self.in_progress,
                       self.pending_approval, self.approved, self.rejected, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Task tracking
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.iteration_counts: Dict[str, int] = {}
        
        # Load task history
        self._load_task_history()
    
    def _setup_logging(self):
        """Setup Python logging."""
        log_file = self.vault_path.parent / 'Logs' / 'ralph.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger('RalphWiggum')
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
        console_format = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
    
    def _load_task_history(self):
        """Load task history from file."""
        history_file = self.in_progress / 'history.json'
        if history_file.exists():
            try:
                content = history_file.read_text(encoding='utf-8')
                data = json.loads(content)
                self.iteration_counts = data.get('iterations', {})
            except Exception as e:
                self.logger.warning(f"Could not load task history: {e}")
    
    def _save_task_history(self):
        """Save task history to file."""
        history_file = self.in_progress / 'history.json'
        data = {
            'iterations': self.iteration_counts,
            'last_updated': datetime.now().isoformat()
        }
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def start_task(
        self,
        task_id: str,
        prompt: str,
        completion_criteria: str,
        source_folder: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Start a new task in the Ralph Wiggum loop.
        
        Args:
            task_id: Unique task identifier
            prompt: Task prompt/description
            completion_criteria: Description of what "done" looks like
            source_folder: Folder to move task from (default: Needs_Action)
            metadata: Additional metadata
            
        Returns:
            Path to state file
        """
        timestamp = datetime.now()
        
        # Create state file
        state_file = self.in_progress / f'TASK_{task_id}.md'
        
        content = f'''---
task_id: {task_id}
created: {timestamp.isoformat()}
status: {TaskStatus.IN_PROGRESS}
iteration: 0
max_iterations: {self.max_iterations}
prompt: |
  {prompt}
completion_criteria: {completion_criteria}
actor: {self.actor}
---

# Task: {task_id}

## Prompt
{prompt}

## Completion Criteria
{completion_criteria}

## Progress
- Iteration: 0 / {self.max_iterations}
- Status: In Progress

## Actions Taken
(Will be logged here)

## Notes
'''
        
        state_file.write_text(content, encoding='utf-8')
        
        # Move from source folder if specified
        if source_folder:
            source_file = source_folder / f'TASK_{task_id}.md'
            if source_file.exists():
                source_file.rename(state_file)
        
        # Track task
        self.active_tasks[task_id] = {
            'state_file': state_file,
            'prompt': prompt,
            'completion_criteria': completion_criteria,
            'status': TaskStatus.IN_PROGRESS,
            'iteration': 0,
            'created': timestamp
        }
        
        self.iteration_counts[task_id] = 0
        self._save_task_history()
        
        self.logger.info(f"[START] Task {task_id}: {prompt[:50]}...")
        
        return state_file
    
    def update_task_iteration(
        self,
        task_id: str,
        action_taken: str,
        result: str,
        next_action: Optional[str] = None
    ):
        """
        Update task state after an iteration.
        
        Args:
            task_id: Task identifier
            action_taken: What action was just taken
            result: Result of the action
            next_action: What action will be taken next
        """
        if task_id not in self.active_tasks:
            self.logger.warning(f"Task {task_id} not found")
            return
        
        task = self.active_tasks[task_id]
        task['iteration'] += 1
        self.iteration_counts[task_id] = task['iteration']
        self._save_task_history()
        
        # Update state file
        state_file = task['state_file']
        
        if state_file.exists():
            content = state_file.read_text(encoding='utf-8')
            
            # Add action log
            timestamp = datetime.now().isoformat()
            action_log = f"\n- [{timestamp}] {action_taken}: {result}"
            
            # Find Actions Taken section and append
            if '## Actions Taken' in content:
                content = content.replace('## Actions Taken', f'## Actions Taken{action_log}')
            else:
                content += f'\n\n## Actions Taken{action_log}'
            
            # Update iteration count
            content = content.replace(
                f"- Iteration: {task['iteration'] - 1} /",
                f"- Iteration: {task['iteration']} /"
            )
            
            # Add next action if provided
            if next_action:
                content += f'\n\n## Next Action\n{next_action}'
            
            state_file.write_text(content, encoding='utf-8')
        
        self.logger.info(
            f"[ITER {task['iteration']}] {task_id}: {action_taken} -> {result}"
        )
    
    def check_completion(self, task_id: str) -> bool:
        """
        Check if a task is complete.
        
        Gold Tier: File-movement based detection
        Task is complete when state file reaches Done/ folder.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if complete
        """
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        state_file = task['state_file']
        
        # Check if file moved to Done
        done_file = self.done / state_file.name
        if done_file.exists():
            task['status'] = TaskStatus.COMPLETED
            self.logger.info(f"[COMPLETE] Task {task_id} moved to Done/")
            return True
        
        # Check if file moved to Rejected
        rejected_file = self.rejected / state_file.name
        if rejected_file.exists():
            task['status'] = TaskStatus.FAILED
            self.logger.info(f"[REJECTED] Task {task_id} moved to Rejected/")
            return True
        
        # Check if waiting for approval
        pending_file = self.pending_approval / state_file.name
        if pending_file.exists():
            task['status'] = TaskStatus.WAITING_APPROVAL
            self.logger.info(f"[WAITING] Task {task_id} in Pending_Approval/")
            return False
        
        # Check if in Approved (ready for final action)
        approved_file = self.approved / state_file.name
        if approved_file.exists():
            self.logger.info(f"[APPROVED] Task {task_id} ready for execution")
            return False
        
        # Still in progress
        return state_file.exists() and task['iteration'] > 0
    
    def should_continue(self, task_id: str) -> bool:
        """
        Check if task should continue iterating.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if should continue
        """
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        
        # Check if already complete
        if self.check_completion(task_id):
            return False
        
        # Check iteration limit
        if task['iteration'] >= self.max_iterations:
            task['status'] = TaskStatus.MAX_ITERATIONS
            self.logger.warning(
                f"[MAX ITER] Task {task_id} reached {self.max_iterations} iterations"
            )
            return False
        
        return True
    
    def escalate_to_human(self, task_id: str, reason: str) -> Path:
        """
        Escalate task to human when stuck.
        
        Args:
            task_id: Task identifier
            reason: Reason for escalation
            
        Returns:
            Path to escalation file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        escalation_file = self.needs_action / f'ESCALATION_RALPH_{timestamp}.md'
        
        task = self.active_tasks.get(task_id, {})
        
        content = f'''---
type: escalation
created: {datetime.now().isoformat()}
priority: high
status: pending
task_id: {task_id}
reason: {reason}
iterations: {task.get('iteration', 0)}
---

# Ralph Wiggum Loop - Human Intervention Required

## Summary
The autonomous task completion loop is stuck and needs human help.

## Task Details
- **Task ID:** {task_id}
- **Prompt:** {task.get('prompt', 'Unknown')}
- **Iterations:** {task.get('iteration', 0)} / {self.max_iterations}
- **Reason:** {reason}

## Current State
Check /Vault/In_Progress/ for the task state file.

## Required Actions
- [ ] Review the task state
- [ ] Determine why task is stuck
- [ ] Take corrective action manually
- [ ] Move task to Done when complete

## Common Issues
1. Missing credentials or permissions
2. External API unavailable
3. Task criteria unclear
4. File movement blocked
'''
        
        escalation_file.write_text(content, encoding='utf-8')
        
        self.logger.critical(f"[ESCALATE] Task {task_id}: {reason}")
        
        return escalation_file
    
    def complete_task(self, task_id: str, summary: Optional[str] = None):
        """
        Mark a task as complete and move to Done.
        
        Args:
            task_id: Task identifier
            summary: Optional completion summary
        """
        if task_id not in self.active_tasks:
            return
        
        task = self.active_tasks[task_id]
        state_file = task['state_file']
        
        # Update state file with completion
        if state_file.exists():
            content = state_file.read_text(encoding='utf-8')
            
            # Update status
            content = content.replace(
                'status: in_progress',
                'status: completed'
            )
            
            # Add summary
            if summary:
                content += f'\n\n## Completion Summary\n{summary}'
            
            # Move to Done
            done_file = self.done / state_file.name
            done_file.write_text(content, encoding='utf-8')
            state_file.unlink()
        
        task['status'] = TaskStatus.COMPLETED
        del self.active_tasks[task_id]
        
        self.logger.info(f"[DONE] Task {task_id} completed successfully")
    
    def run_task(
        self,
        task_id: str,
        processor: Callable[[str, int], tuple],
        prompt: str,
        completion_criteria: str
    ) -> bool:
        """
        Run a complete task through the Ralph Wiggum loop.
        
        Args:
            task_id: Task identifier
            processor: Function that processes the task
                       Signature: (prompt, iteration) -> (action_taken, continue_bool)
            prompt: Task prompt
            completion_criteria: What "done" looks like
            
        Returns:
            True if completed successfully
        """
        # Start the task
        self.start_task(task_id, prompt, completion_criteria)
        
        # Run iterations
        while self.should_continue(task_id):
            task = self.active_tasks[task_id]
            iteration = task['iteration']
            
            # Call processor
            try:
                action_taken, should_continue = processor(prompt, iteration)
                
                # Update state
                self.update_task_iteration(
                    task_id,
                    action_taken=action_taken,
                    result="success" if should_continue else "completed",
                    next_action=None if not should_continue else "Continue processing"
                )
                
                # Check if processor says done
                if not should_continue:
                    break
                
                # Delay before next iteration
                time.sleep(self.iteration_delay)
                
            except Exception as e:
                self.logger.error(f"Iteration {iteration} failed: {e}")
                self.update_task_iteration(
                    task_id,
                    action_taken="Error",
                    result=str(e),
                    next_action="Retry or escalate"
                )
        
        # Check final status
        if self.check_completion(task_id):
            self.complete_task(task_id, summary="Task completed via Ralph Wiggum loop")
            return True
        else:
            # Escalate to human
            task = self.active_tasks.get(task_id, {})
            reason = f"Task did not complete after {task.get('iteration', 0)} iterations"
            self.escalate_to_human(task_id, reason)
            return False
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get list of active tasks."""
        return list(self.active_tasks.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Ralph Wiggum loop statistics."""
        return {
            'active_tasks': len(self.active_tasks),
            'total_iterations': sum(t['iteration'] for t in self.active_tasks.values()),
            'max_iterations_configured': self.max_iterations,
            'iteration_delay': self.iteration_delay
        }


# Convenience functions
_default_ralph: Optional[RalphWiggumLoop] = None

def get_ralph(vault_path: str) -> RalphWiggumLoop:
    """Get or create the default Ralph Wiggum loop."""
    global _default_ralph
    if _default_ralph is None:
        _default_ralph = RalphWiggumLoop(vault_path)
    return _default_ralph


if __name__ == '__main__':
    # Test the Ralph Wiggum loop
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ralph_wiggum.py <vault_path>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    ralph = RalphWiggumLoop(vault_path, max_iterations=5, iteration_delay=1.0)
    
    print("\n" + "="*60)
    print("RALPH WIGGUM LOOP TEST")
    print("="*60)
    
    # Test: Create a simple task
    def test_processor(prompt: str, iteration: int) -> tuple:
        """Simulated processor that completes in 3 iterations."""
        if iteration < 3:
            return (f"Processing step {iteration + 1}", True)
        return ("Task completed", False)
    
    # Run the task
    result = ralph.run_task(
        task_id="test_task_001",
        processor=test_processor,
        prompt="Test task for Ralph Wiggum loop",
        completion_criteria="3 processing steps completed"
    )
    
    print(f"\n[OK] Task completed: {result}")
    
    # Get statistics
    stats = ralph.get_statistics()
    print(f"\nStatistics:")
    print(f"  Active Tasks: {stats['active_tasks']}")
    print(f"  Total Iterations: {stats['total_iterations']}")
    
    print("\n" + "="*60)
    print("RALPH WIGGUM LOOP READY")
    print("="*60 + "\n")
