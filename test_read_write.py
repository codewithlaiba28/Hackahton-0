#!/usr/bin/env python3
"""Read/Write Test Script for Bronze Tier Audit"""
from pathlib import Path
import datetime

vault = Path('C:/Code-journy/Quator-4/Hackahton-0/Vault')

# Test 1: Create test file in Needs_Action
test_file = vault / 'Needs_Action' / 'AUDIT_TEST_001.md'
content = f'''---
type: audit_test
created: {datetime.datetime.now().isoformat()}
status: pending
---
# Audit Test File
Created during Bronze Tier audit.
'''
test_file.write_text(content)
print(f'CREATE: {test_file} - OK')

# Test 2: Read the file back
read_content = test_file.read_text()
print(f'READ: {len(read_content)} bytes - OK')

# Test 3: Move to Done
done_file = vault / 'Done' / 'AUDIT_TEST_001.md'
test_file.rename(done_file)
print(f'MOVE: {test_file} -> {done_file} - OK')

# Test 4: Create Logs folder and log action
logs_dir = Path('C:/Code-journy/Quator-4/Hackahton-0/Logs')
logs_dir.mkdir(exist_ok=True)
log_file = logs_dir / 'audit_log.md'
log_entry = f'''---
type: audit_log
timestamp: {datetime.datetime.now().isoformat()}
---
# Audit Log Entry
- Created: AUDIT_TEST_001.md in Needs_Action
- Read: {len(read_content)} bytes
- Moved to: Done/AUDIT_TEST_001.md
'''
log_file.write_text(log_entry)
print(f'LOG: {log_file} - OK')

print('\nAll read/write tests PASSED')
