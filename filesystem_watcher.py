# filesystem_watcher.py
"""
File System Watcher - Monitors a drop folder for new files
and creates action files in Vault/Needs_Action folder.

Uses watchdog library for efficient file system monitoring.

Usage: python filesystem_watcher.py

Files dropped in /Vault/Inbox will be automatically processed.
"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import shutil
import logging
import time

class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        super().__init__()
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logger = logging.getLogger(self.__class__.__name__)

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Only process files in inbox folder
        if self.inbox not in source.parents and source.parent != self.inbox:
            return
        
        # Skip hidden files and temp files
        if source.name.startswith('.') or source.suffix in ['.tmp', '.part']:
            return
        
        self.logger.info(f"New file detected: {source.name}")
        self.process_file(source)

    def on_moved(self, event):
        """Handle file move events (some editors save this way)."""
        if event.is_directory:
            return
        
        dest = Path(event.dest_path)
        
        # Only process files in inbox folder
        if self.inbox not in dest.parents and dest.parent != self.inbox:
            return
        
        # Skip hidden files
        if dest.name.startswith('.'):
            return
        
        self.logger.info(f"File moved to inbox: {dest.name}")
        self.process_file(dest)

    def process_file(self, source: Path):
        """Process a dropped file and create action file."""
        try:
            # Copy file to Needs_Action
            dest = self.needs_action / f'FILE_{source.name}'
            shutil.copy2(source, dest)
            
            # Create metadata file
            meta_path = dest.with_suffix('.md')
            self.create_metadata(source, dest, meta_path)
            
            self.logger.info(f"Processed file: {source.name} -> {meta_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error processing file {source.name}: {e}")

    def create_metadata(self, source: Path, dest: Path, meta_path: Path):
        """Create markdown metadata file for the dropped file."""
        from datetime import datetime
        
        try:
            size = source.stat().st_size
        except:
            size = 0
        
        content = f'''---
type: file_drop
original_name: {source.name}
dropped_file: {dest.name}
size: {size} bytes
received: {datetime.now().isoformat()}
priority: medium
status: pending
---

# File Drop for Processing

## Original File
- **Name:** {source.name}
- **Size:** {size} bytes
- **Location:** {dest}

## Suggested Actions
- [ ] Review file contents
- [ ] Process or take action
- [ ] Move to /Done when complete
- [ ] Archive original file

## Notes
File was automatically detected in Inbox folder.
'''
        
        meta_path.write_text(content)


class FileSystemWatcher:
    """Main file system watcher class."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure folders exist
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        # Setup observer
        self.event_handler = DropFolderHandler(str(vault_path))
        self.observer = Observer()

    def start(self):
        """Start the file system watcher."""
        self.observer.schedule(
            self.event_handler,
            str(self.inbox),
            recursive=False
        )
        self.observer.start()
        
        self.logger.info(f"Watching folder: {self.inbox}")
        print()
        print("File System Watcher is running...")
        print(f"Monitoring: {self.inbox}")
        print(f"Output: {self.needs_action}")
        print()
        print("Drop files in the Inbox folder to process them.")
        print("Press Ctrl+C to stop")
        print("-" * 40)

    def run(self):
        """Run the watcher loop."""
        self.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the watcher."""
        self.observer.stop()
        self.observer.join()
        self.logger.info("File System Watcher stopped")


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
    
    # Create and run watcher
    watcher = FileSystemWatcher(str(vault_path))
    watcher.run()
