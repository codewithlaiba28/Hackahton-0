#!/usr/bin/env python3
"""
Gmail OAuth Token Setup Script - Simple Version

Run this script directly in your terminal (not through AI):
    python auth_setup.py

It will:
1. Open browser for Google login
2. Save token.json after authorization
3. Test the connection
"""

import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    script_dir = Path(__file__).parent.absolute()
    credentials_path = script_dir / 'credentials.json'
    token_path = script_dir / 'token.json'
    
    print("=" * 60)
    print("Gmail OAuth Token Setup")
    print("=" * 60)
    print()
    
    # Check credentials
    if not credentials_path.exists():
        print("ERROR: credentials.json not found!")
        sys.exit(1)
    
    print("Found credentials.json")
    
    # Check existing token
    creds = None
    if token_path.exists():
        print("Found existing token.json - deleting for fresh auth...")
        token_path.unlink()
    
    # Run OAuth flow
    print()
    print("Opening browser for authorization...")
    print()
    print("IMPORTANT: If you see 'This app isn't verified':")
    print("  -> Click 'Continue' or 'Go to AI Employee (unsafe)'")
    print()
    
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(port=0, open_browser=True,
                                   success_message="Success! Close this window.")
    
    # Save token
    with open(token_path, 'w') as token:
        token.write(creds.to_json())
    
    print()
    print("=" * 60)
    print("SUCCESS! Token saved to token.json")
    print("=" * 60)
    print()
    
    # Test connection
    print("Testing connection...")
    from googleapiclient.discovery import build
    service = build('gmail', 'v1', credentials=creds)
    profile = service.users().getProfile(userId='me').execute()
    print(f"Connected as: {profile['emailAddress']}")
    print()
    print("Now you can run: python gmail_watcher.py")
    print()

if __name__ == '__main__':
    main()
