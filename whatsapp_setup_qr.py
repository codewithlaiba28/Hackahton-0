#!/usr/bin/env python3
"""
WhatsApp QR Code Setup - One-time authentication

This script:
1. Opens WhatsApp Web in a visible browser
2. Waits for you to scan the QR code
3. Saves the session for future use
4. Exits once authenticated

Usage: python whatsapp_setup_qr.py
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
import time

def main():
    session_path = Path(__file__).parent / 'whatsapp_session'
    
    print("=" * 60)
    print("WhatsApp QR Code Setup")
    print("=" * 60)
    print()
    print("This will open WhatsApp Web for QR code scanning.")
    print()
    print("Steps:")
    print("1. Browser will open automatically")
    print("2. WhatsApp Web QR code will appear")
    print("3. Open WhatsApp on your phone")
    print("4. Go to: Settings → Linked Devices → Link a Device")
    print("5. Scan the QR code in the browser")
    print()
    print("Waiting 120 seconds for you to scan the QR code...")
    print()
    
    with sync_playwright() as p:
        # Launch browser (visible mode)
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        page = browser.pages[0]
        
        print("Opening WhatsApp Web...")
        page.goto('https://web.whatsapp.com', wait_until='networkidle')
        
        print()
        print("QR Code should be visible now.")
        print("Please scan it with your phone.")
        print()
        
        # Wait for chat list (success) or timeout
        max_wait = 120  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Check if chat list is loaded (authenticated)
            chat_list = page.query_selector('[data-testid="chat-list"]')
            if chat_list:
                print()
                print("✅ SUCCESS! WhatsApp Web is authenticated!")
                print()
                print("Session saved to: whatsapp_session/")
                print()
                print("You can now run: python whatsapp_watcher.py")
                print()
                time.sleep(3)  # Let user see success
                break
            
            # Check if QR code is still showing
            qr_code = page.query_selector('[data-icon="qr-phone"]')
            if not qr_code:
                # Might be loading or already authenticated
                time.sleep(1)
            else:
                time.sleep(2)
        else:
            print()
            print("⏱️  Timeout: 120 seconds elapsed")
            print()
            print("If QR code expired, just run this script again:")
            print("  python whatsapp_setup_qr.py")
            print()
        
        browser.close()
    
    print("=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: python whatsapp_watcher.py")
    print("2. Watcher will monitor WhatsApp every 30 seconds")
    print()

if __name__ == '__main__':
    main()
