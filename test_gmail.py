#!/usr/bin/env python3
"""Test Gmail API Connection"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path

# Load token
token_path = Path(__file__).parent / 'token.json'
creds = Credentials.from_authorized_user_file(token_path)

# Build service
service = build('gmail', 'v1', credentials=creds)

# Get profile
profile = service.users().getProfile(userId='me').execute()
print(f"Connected to: {profile['emailAddress']}")

# Get unread emails
print("\n--- Unread Emails ---")
results = service.users().messages().list(
    userId='me', q='is:unread', maxResults=10
).execute()
messages = results.get('messages', [])

if messages:
    print(f"Found {len(messages)} unread email(s):\n")
    for msg in messages:
        detail = service.users().messages().get(
            userId='me', id=msg['id']
        ).execute()
        headers = {h['name']: h['value'] for h in detail['payload']['headers']}
        print(f"From: {headers.get('From', 'Unknown')}")
        print(f"Subject: {headers.get('Subject', 'No Subject')}")
        print(f"Date: {headers.get('Date', 'Unknown')}")
        print("-" * 40)
else:
    print("No unread emails found")

# Get important emails
print("\n--- Important Emails ---")
results = service.users().messages().list(
    userId='me', q='is:important', maxResults=10
).execute()
messages = results.get('messages', [])

if messages:
    print(f"Found {len(messages)} important email(s):\n")
    for msg in messages:
        detail = service.users().messages().get(
            userId='me', id=msg['id']
        ).execute()
        headers = {h['name']: h['value'] for h in detail['payload']['headers']}
        print(f"From: {headers.get('From', 'Unknown')}")
        print(f"Subject: {headers.get('Subject', 'No Subject')}")
        print(f"Date: {headers.get('Date', 'Unknown')}")
        print("-" * 40)
else:
    print("No important emails found")

# Get unread AND important
print("\n--- Unread AND Important Emails ---")
results = service.users().messages().list(
    userId='me', q='is:unread is:important', maxResults=10
).execute()
messages = results.get('messages', [])

if messages:
    print(f"Found {len(messages)} unread+important email(s):")
    for msg in messages:
        print(f"  - {msg['id']}")
else:
    print("No unread AND important emails found")
    print("\nNOTE: Gmail's 'important' marker may not be set for new emails yet.")
    print("Try: python test_gmail_all.py")
