# Facebook Auto-Posting Setup Guide

## Overview
The Facebook auto-poster is now fixed with robust selectors and improved content entry.

## Files
- `facebook_poster.py` - Main auto-posting script (FIXED)
- `social_login_helper.py` - Login helper to save session
- `Vault/Approved/` - Place approved posts here
- `Vault/Done/` - Completed posts are moved here
- `Vault/Logs/` - Post logs

## Quick Start

### Step 1: Login to Facebook (First Time Only)

Run the login helper to save your Facebook session:

```bash
python social_login_helper.py
```

Select option `2` for Facebook. A browser will open:
1. Login to Facebook
2. Wait for your home feed to load
3. Session will be saved automatically
4. Browser will close

**Note:** You only need to do this once. The session is saved for future posts.

### Step 2: Create a Facebook Post

Create a markdown file in `Vault/Approved/` with this format:

```markdown
---
type: facebook_post
created: 2026-03-01
status: approved
platform: facebook
image: image.png  # Optional
---

# Facebook Post Title

## Post Content
Your Facebook post content goes here.

This can be multiple lines.

#Hashtags #Here
```

**Important:** The `type: facebook_post` in front matter is required!

### Step 3: Run the Auto-Poster

```bash
# Post all approved Facebook posts
python facebook_poster.py

# Post with a specific image
python facebook_poster.py --image path/to/image.jpg

# Post direct text (creates temporary post)
python facebook_poster.py --text "Your post text here"

# Run in headless mode (no browser UI)
python facebook_poster.py --headless
```

## How It Works

1. **Checks Approved/** - Finds all `.md` files with `type: facebook_post`
2. **Loads Session** - Uses saved Facebook session (no login needed)
3. **Opens Composer** - Automatically clicks "What's on your mind?"
4. **Enters Content** - Types your post content
5. **Uploads Image** - If image is specified
6. **Clicks Post** - Automatically posts
7. **Moves to Done/** - Moves completed post to Done/ folder

## Troubleshooting

### "Login not detected"
- Run `python social_login_helper.py` to login first
- Make sure you complete the full login process
- Wait for your home feed to load before script continues

### "Composer failed to open"
- Facebook may have updated their UI
- Check screenshots: `fb_debug.png`, `fb_composer_fail.png`
- Try manual posting with the demo script

### "Post button not found"
- The script will try Enter key as fallback
- Check `fb_before_post.png` to see what was detected
- Your post may have already been published

### Session Issues
If Facebook logs you out frequently:
1. Delete the session folder: `Vault/facebook_session/`
2. Re-run `python social_login_helper.py`
3. Make sure to check "Keep me logged in" on Facebook

## Debugging Screenshots

The script creates these screenshots for debugging:
- `fb_debug.png` - Initial state after login
- `fb_before_type.png` - Before entering content
- `fb_after_type.png` - After entering content
- `fb_before_post.png` - Before clicking Post
- `fb_after_post.png` - After clicking Post
- `fb_*.png` - Various error states

## Logs

Check `Vault/Logs/facebook_posts.log` for:
- Posted content
- Timestamps
- Image paths
- Success/failure status

## Example Post

See `Vault/Approved/FACEBOOK_TEST_POST.md` for an example.

## Command Line Options

```
python facebook_poster.py [OPTIONS]

Options:
  --headless      Run without browser UI
  --image PATH    Image file to upload
  --text TEXT     Direct text to post (creates temp post)
  --help          Show help message
```

## Known Limitations

1. **Facebook UI Changes** - Facebook frequently changes their UI class names
2. **Two-Factor Auth** - May need to re-authenticate occasionally
3. **Rate Limiting** - Don't post too frequently or Facebook may block
4. **Image Formats** - Use JPG or PNG for best compatibility

## Support

If posting fails:
1. Check the debugging screenshots
2. Check `Vault/Logs/facebook_posts.log`
3. Try running with `--headless` to see full browser
4. Re-run login helper if session expired
