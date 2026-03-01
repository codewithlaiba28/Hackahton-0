#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CREATE ODOO DATABASE
Create 'odoo' database for integration
"""

import requests
import json

print("\n" + "="*70)
print("CREATE ODOO DATABASE")
print("="*70)

url = 'http://localhost:8069/jsonrpc'
headers = {'Content-Type': 'application/json'}

# Create database
print("\nCreating 'odoo' database...")
print("This may take 2-3 minutes...")

payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "db",
        "method": "create_database",
        "args": ["admin", "odoo", True, "UTF-8", "admin"]
    },
    "id": 1
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=180)
    result = response.json()
    
    if 'result' in result:
        print(f"\n[OK] Database 'odoo' created successfully!")
        print(f"    URL: http://localhost:8069")
        print(f"    Database: odoo")
        print(f"    Username: admin")
        print(f"    Password: admin")
    else:
        print(f"\n[WARN] Response: {result}")
        print("Database might already exist or there was an error")
except Exception as e:
    print(f"\n[WARN] Error: {e}")
    print("Database might already exist")

print("\n" + "="*70)
print("Testing connection...")
print("="*70)

# Test authentication
payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "authenticate",
        "args": ["odoo", "admin", "admin", {}]
    },
    "id": 2
}

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    result = response.json()
    
    if 'result' in result and result['result']:
        uid = result['result']
        print(f"\n[OK] Authentication successful! UID: {uid}")
        print("\nOdoo is ready for integration!")
    else:
        print(f"\n[WARN] Authentication failed: {result}")
        print("Please login to Odoo manually at http://localhost:8069")
except Exception as e:
    print(f"\n[WARN] Test failed: {e}")

print("\n" + "="*70 + "\n")
