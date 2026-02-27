# Quick Setup Guide

## Step 1: Install Packages (Already Done)
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 2: Run Authorization
```bash
python auth_setup.py
```

This will:
- Open your browser
- Ask you to sign in to Google
- Save `token.json` after authorization

## Step 3: Run Gmail Watcher
```bash
python gmail_watcher.py
```

This will:
- Check Gmail every 120 seconds
- Create files in `Vault/Needs_Action/` for new emails

---

## Files Created

| File | Purpose |
|------|---------|
| `credentials.json` | OAuth credentials (you downloaded from Google) |
| `token.json` | Access token (auto-created by auth_setup.py) |

## Important

- **Never commit** `credentials.json` or `token.json` to Git
- These files contain sensitive authentication information

---

## Troubleshooting

### "token.json not found"
Run: `python auth_setup.py`

### "credentials.json not found"
Download from Google Cloud Console and save in project root.

### Browser doesn't open
Run `auth_setup.py` directly in terminal (not through AI assistant).
