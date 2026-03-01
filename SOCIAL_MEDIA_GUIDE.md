# 🚀 SOCIAL MEDIA AUTO-POSTING - QUICK GUIDE

## ✅ SETUP COMPLETE

All three social media auto-posting scripts are ready:
- **Twitter Poster**: `twitter_poster.py` (18KB)
- **Facebook Poster**: `facebook_poster.py` (18KB)
- **Instagram Poster**: `instagram_poster.py` (20KB)

---

## 📝 WORKFLOW

### Step 1: Create Draft
Drafts are already created in `Vault/Plans/`:
- `TWITTER_GOLD_TIER_TEST.md`
- `FACEBOOK_GOLD_TIER_TEST.md`
- `INSTAGRAM_GOLD_TIER_TEST.md`

### Step 2: Move to Approved
Files already copied to `Vault/Approved/`

### Step 3: Login (One-time only)
```bash
python social_login_helper.py
```
- Select platform (1=Twitter, 2=Facebook, 3=Instagram, 4=All)
- Browser opens
- Login to the platform
- Wait for feed to load
- Session saved automatically!

### Step 4: Auto-Post
```bash
# Twitter
python twitter_poster.py

# Facebook
python facebook_poster.py

# Instagram (requires image)
python instagram_poster.py --image image.png
```

**What happens:**
1. Browser opens (saved session)
2. Navigates to platform
3. Enters content automatically
4. Uploads image (if specified)
5. **You click "Post" button manually** (Human-in-the-Loop)
6. File moved to `Vault/Done/`
7. Logged in `Logs/` folder

---

## 🎯 COMMANDS

### Login (First time only)
```bash
python social_login_helper.py
```

### Auto-Post Commands
```bash
# Twitter - No image
python twitter_poster.py

# Twitter - With image
python twitter_poster.py --image image.png

# Facebook - No image
python facebook_poster.py

# Facebook - With image
python facebook_poster.py --image photo.jpg

# Instagram - Image required
python instagram_poster.py --image image.png
```

---

## 📁 FOLDER STRUCTURE

```
Vault/
├── Plans/                    # Draft posts
│   ├── TWITTER_GOLD_TIER_TEST.md
│   ├── FACEBOOK_GOLD_TIER_TEST.md
│   └── INSTAGRAM_GOLD_TIER_TEST.md
├── Approved/                 # Ready to auto-post
│   ├── TWITTER_GOLD_TIER_TEST.md ✅
│   ├── FACEBOOK_GOLD_TIER_TEST.md ✅
│   └── INSTAGRAM_GOLD_TIER_TEST.md ✅
├── Done/                     # Successfully posted
└── Logs/                     # Post logs
    ├── twitter_posts.log
    ├── facebook_posts.log
    └── instagram_posts.log
```

---

## 🔑 FEATURES

| Feature | Twitter | Facebook | Instagram |
|---------|---------|----------|-----------|
| Auto-login | ✅ | ✅ | ✅ |
| Session save | ✅ | ✅ | ✅ |
| Auto-compose | ✅ | ✅ | ✅ |
| Image upload | ✅ | ✅ | ✅ |
| Edit before post | ✅ | ✅ | ✅ |
| Human approval | ✅ | ✅ | ✅ |
| Auto-post click | ❌ HITL | ❌ HITL | ❌ HITL |

**HITL = Human-in-the-Loop** (You click "Post" button for safety)

---

## ⚡ QUICK START

```bash
# 1. Login (one-time)
python social_login_helper.py

# 2. Post to Twitter
python twitter_poster.py

# 3. Post to Facebook
python facebook_poster.py

# 4. Post to Instagram
python instagram_poster.py --image image.png
```

---

## 🎉 DEMO CONTENT

All three posts contain:
- Gold Tier test message
- Hashtags: #Hackathon2026 #AI #Automation
- Platform-specific formatting

---

## 📊 STATUS CHECK

```bash
python run_social_agents.py
```

This shows:
- Approved posts ready to post
- Script status
- Session status
- Usage instructions

---

**Ready to auto-post! 🚀**
