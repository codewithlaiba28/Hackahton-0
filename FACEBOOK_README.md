# Facebook Auto-Posting - Complete Setup

## Status: ✅ FIXED

The Facebook auto-poster has been completely rewritten with:
- **Robust selectors** - Multiple fallback selectors for all elements
- **Better login detection** - Multiple methods to detect logged-in state
- **Improved content entry** - Chunked typing for reliability
- **Better error handling** - Comprehensive screenshots for debugging
- **Session persistence** - Login once, post multiple times

---

## Quick Start (3 Steps)

### Step 1: Login to Facebook (First Time Only)

```bash
python social_login_helper.py
```

**What happens:**
- Browser opens Facebook
- You login manually
- Session is saved to `Vault/facebook_session/`
- Browser closes automatically

**You only need to do this once!** The session persists across runs.

---

### Step 2: Create a Post

Create a file in `Vault/Approved/` like `my_post.md`:

```markdown
---
type: facebook_post
created: 2026-03-01
status: approved
platform: facebook
---

# My Facebook Post

## Post Content
🎯 Exciting news from our company!

This is an automated post from our AI Employee system.

#Hackathon2026 #AI #Automation
```

**Required fields:**
- `type: facebook_post` (in front matter)
- `## Post Content` section with your text

**Optional:**
- `image: image.png` (in front matter) - path to image

---

### Step 3: Post to Facebook

```bash
# Post all approved posts
python facebook_poster.py

# Post with specific image
python facebook_poster.py --image path/to/image.jpg

# Post direct text (testing)
python facebook_poster.py --text "Your post text here"
```

---

## Files Overview

| File | Purpose |
|------|---------|
| `facebook_poster.py` | Main auto-posting script (FIXED) |
| `social_login_helper.py` | Login helper to save session |
| `facebook_quick_test.py` | Quick test script |
| `FACEBOOK_SETUP.md` | Detailed setup guide |
| `Vault/Approved/` | Place approved posts here |
| `Vault/Done/` | Completed posts moved here |
| `Vault/Logs/facebook_posts.log` | Post history log |

---

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  1. Check Vault/Approved/ for facebook_post files      │
│  2. Load saved Facebook session                         │
│  3. Navigate to Facebook (auto-login)                   │
│  4. Open composer ("What's on your mind?")              │
│  5. Enter post content                                  │
│  6. Upload image (if provided)                          │
│  7. Click Post button                                   │
│  8. Move post to Vault/Done/                            │
│  9. Log to Vault/Logs/facebook_posts.log                │
└─────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### "Login not detected"
```bash
# Solution: Re-run login helper
python social_login_helper.py
```

### "No approved Facebook posts found"
- Make sure your `.md` file has `type: facebook_post` in front matter
- File must be in `Vault/Approved/` directory

### "Composer failed to open"
- Check screenshots: `fb_debug.png`, `fb_composer_fail.png`
- Facebook may have updated their UI
- Try running without `--headless` to see what's happening

### "Post button not found"
- Script tries Enter key as fallback
- Check `fb_before_post.png` to see state
- Post may have already been published

### Session expires frequently
- Delete `Vault/facebook_session/` folder
- Re-run `python social_login_helper.py`
- Check "Keep me logged in" on Facebook login

---

## Debugging

The script creates these screenshots:
- `fb_debug.png` - Initial page state
- `fb_before_type.png` - Before entering content
- `fb_after_type.png` - After entering content  
- `fb_before_post.png` - Before clicking Post
- `fb_after_post.png` - After clicking Post
- `fb_*.png` - Various error states

**Check logs:**
```bash
type Vault\Logs\facebook_posts.log
```

---

## Command Line Options

```
python facebook_poster.py [OPTIONS]

--headless      Run without browser UI (for automated servers)
--image PATH    Image file to upload
--text TEXT     Direct text to post (creates temp post)
--help          Show help
```

---

## Example Usage

### Post text only:
```bash
python facebook_poster.py --text "Hello Facebook! This is a test."
```

### Post with image:
```bash
python facebook_poster.py --image "C:\path\to\image.jpg"
```

### Post all approved:
```bash
python facebook_poster.py
```

---

## Testing

Run the quick test:
```bash
python facebook_quick_test.py
```

This will:
1. Open Facebook
2. Use your saved session
3. Post a test message
4. Show success/failure

---

## Known Issues

1. **Facebook UI Changes** - Facebook frequently updates their interface
   - Solution: Script has multiple fallback selectors
   
2. **Two-Factor Authentication** - May require re-login occasionally
   - Solution: Re-run `python social_login_helper.py`

3. **Rate Limiting** - Don't post too frequently
   - Facebook may temporarily block automated posting

4. **Image Formats** - Use JPG or PNG
   - Other formats may not upload correctly

---

## Verification Checklist

- [ ] Ran `python social_login_helper.py`
- [ ] Session folder exists: `Vault/facebook_session/`
- [ ] Post file has `type: facebook_post` in front matter
- [ ] Post file is in `Vault/Approved/`
- [ ] Content is under `## Post Content` section

---

## Next Steps After Setup

1. **Test posting:**
   ```bash
   python facebook_quick_test.py
   ```

2. **Create your first real post:**
   - Create `.md` file in `Vault/Approved/`
   - Run `python facebook_poster.py`

3. **Automate (optional):**
   - Add to cron/scheduler for automated posting
   - See `cron_setup.md` for scheduling

---

## Support

If you're still having issues:

1. Check all `fb_*.png` screenshots
2. Review `Vault/Logs/facebook_posts.log`
3. Try running without `--headless` to see browser
4. Re-run login helper: `python social_login_helper.py`

---

**Status:** ✅ Ready to use!
