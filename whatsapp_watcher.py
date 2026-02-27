# whatsapp_watcher.py
"""
WhatsApp Watcher - Monitors WhatsApp Web for unread messages
containing keywords and creates action files in Vault/Needs_Action folder.

Uses Playwright for browser automation.

Usage: python whatsapp_watcher.py

Note: Be aware of WhatsApp's terms of service when using automation.
"""

from playwright.sync_api import sync_playwright
from base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import logging
import time

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None):
        super().__init__(vault_path, check_interval=30)
        
        # Default session path
        if session_path is None:
            self.session_path = Path(__file__).parent / 'whatsapp_session'
        else:
            self.session_path = Path(session_path)
        
        # Keywords to watch for
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help']
        
        # Track processed chats to avoid duplicates
        self.processed_chats = set()
        
        # Browser instance (kept open across cycles)
        self.playwright = None
        self.browser = None
        self.page = None
        self.initialized = False

    def _init_browser(self):
        """Initialize browser once and keep it open."""
        if self.initialized:
            return True
            
        try:
            print()
            print("  Initializing WhatsApp Web...")
            
            # Start Playwright
            self.playwright = sync_playwright().start()
            
            # Launch browser with persistent session
            self.browser = self.playwright.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--window-size=1280,720'
                ]
            )
            
            self.page = self.browser.pages[0]
            
            # Navigate to WhatsApp Web
            print("  Loading WhatsApp Web...")
            self.page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=30000)
            
            # Wait a bit for page to fully load
            time.sleep(5)
            
            # Check what we have - use working selector #pane-side
            print("  Checking WhatsApp status...")
            
            # Give user time to scan QR if needed
            max_wait = 120
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # Check if pane-side exists (chat list container)
                pane = self.page.query_selector('#pane-side')
                if pane:
                    print("  [OK] WhatsApp Web is connected and ready!")
                    self.initialized = True
                    return True
                
                # Check for QR code
                qr_code = self.page.query_selector('[data-icon="qr-phone"]')
                if qr_code:
                    elapsed = int(time.time() - start_time)
                    if elapsed % 10 == 0 or elapsed < 5:
                        print(f"  [QR] QR Code visible - Please scan it! ({elapsed}s/{max_wait}s)")
                else:
                    # Page might be loading
                    elapsed = int(time.time() - start_time)
                    if elapsed % 10 == 0:
                        print(f"  [...] Loading WhatsApp... ({elapsed}s/{max_wait}s)")
                
                time.sleep(2)
            
            # Timeout
            print(f"  [!!] Timeout after {max_wait} seconds")
            print("  Please run the script again to retry QR scan.")
            self._cleanup()
            return False
            
        except Exception as e:
            print(f"  [!!] Error initializing: {e}")
            self._cleanup()
            return False

    def _cleanup(self):
        """Cleanup browser resources."""
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            self.page = None
            self.initialized = False
        except:
            pass

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for unread messages with keywords."""
        messages = []
        
        # Initialize browser if needed
        if not self._init_browser():
            return []
        
        try:
            # Check if still authenticated using #pane-side
            pane = self.page.query_selector('#pane-side')
            if not pane:
                print("  [!!] Not authenticated, reinitializing...")
                self._cleanup()
                return []
            
            # Find unread messages using working selectors
            print("  Checking for unread messages...")
            
            # Look for chat items in pane-side
            chat_items = self.page.query_selector_all('#pane-side div[role="listitem"], #pane-side div[aria-label]')
            
            for chat in chat_items:
                try:
                    text = chat.inner_text().lower()
                    
                    # Skip empty or very short texts
                    if len(text) < 5:
                        continue
                    
                    # Check if message contains keywords
                    if any(kw in text for kw in self.keywords):
                        # Extract chat name
                        chat_name = "Unknown"
                        try:
                            name_elem = chat.query_selector('[dir="auto"]')
                            if name_elem:
                                chat_name = name_elem.inner_text()[:30]
                        except:
                            pass
                        
                        # Skip if already processed
                        chat_id = f"{chat_name}:{text[:50]}"
                        if chat_id not in self.processed_chats:
                            messages.append({
                                'text': text[:200],
                                'chat_name': chat_name,
                                'chat_id': chat_id
                            })
                            self.processed_chats.add(chat_id)
                            print(f"  [MSG] New message from {chat_name}")
                            
                except Exception as e:
                    self.logger.debug(f"Error processing chat: {e}")
                
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            self._cleanup()
        
        return messages

    def create_action_file(self, message) -> Path:
        """Create markdown action file for the WhatsApp message."""
        content = f'''---
type: whatsapp
from: {message['chat_name']}
received: {datetime.now().isoformat()}
priority: high
status: pending
keywords: {', '.join(self.keywords)}
---

## WhatsApp Message

**From:** {message['chat_name']}

**Content:**
{message.get('text', 'No content extracted')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Flag for follow-up
- [ ] Archive after processing

## Notes
Message matched keywords: {', '.join(self.keywords)}
'''
        
        # Create filename from chat name and timestamp
        # Replace invalid filename characters: / \ : * ? " < > |
        safe_name = message['chat_name']
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '+', ' ']:
            safe_name = safe_name.replace(char, '_')
        safe_name = safe_name[:30]  # Limit length
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.needs_action / f'WHATSAPP_{safe_name}_{timestamp}.md'
        
        # Write with UTF-8 encoding to handle special characters
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created WhatsApp action file: {filepath.name}")
        
        return filepath

    def run(self):
        """Run the WhatsApp watcher loop."""
        self.logger.info('Starting WhatsAppWatcher')
        print()
        print("=" * 60)
        print("WhatsApp Watcher is running...")
        print(f"Checking every {self.check_interval} seconds")
        print(f"Vault: {self.vault_path}")
        print(f"Output: {self.needs_action}")
        print(f"Keywords: {', '.join(self.keywords)}")
        print()
        print("Browser will stay open for fast operation.")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while True:
                items = self.check_for_updates()
                if items:
                    print(f"[{self._get_timestamp()}] Found {len(items)} WhatsApp message(s)")
                    for item in items:
                        self.create_action_file(item)
                else:
                    print(f"[{self._get_timestamp()}] No new WhatsApp messages")
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n\nStopping WhatsApp Watcher...")
        finally:
            self._cleanup()
            print("WhatsApp Watcher stopped.")
    
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
    
    # Create and run watcher
    watcher = WhatsAppWatcher(str(vault_path))
    watcher.run()
