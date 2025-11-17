# Complete Heroku Setup Guide - CLI Method

This guide will walk you through setting up your OCR app on Heroku using the command line interface.

## Prerequisites

1. **Heroku CLI installed** - Download from https://devcenter.heroku.com/articles/heroku-cli
2. **Git installed** - Usually comes with Heroku CLI
3. **Heroku account** - Sign up at https://signup.heroku.com

## Step 1: Login to Heroku

```bash
heroku login
```

This will open a browser window for you to login. After logging in, return to the terminal.

## Step 2: Navigate to Your Project

```bash
cd C:\Users\User1\Desktop\ocr\tes_ocr
```

## Step 3: Check if App Already Exists

```bash
# List all your Heroku apps
heroku apps

# If you see your app name (e.g., tesocr-b4a15d123f60), note it down
# If no apps exist, you'll create one in the next step
```

## Step 4: Create Heroku App (if needed)

**If you don't have an app yet:**

```bash
# Create a new app (Heroku will generate a name)
heroku create

# OR create with a specific name
heroku create your-app-name
```

**If you already have an app, set up the git remote:**

```bash
# Replace tesocr with your actual app name
heroku git:remote -a tesocr

# Example:
# heroku git:remote -a tesocr-b4a15d123f60
```

## Step 5: Configure Buildpacks (CRITICAL!)

The buildpack order is **essential**. The apt buildpack must run FIRST to install Tesseract.

```bash
# Replace tesocr with your actual app name
# Or omit --app if you've set up the git remote

# Clear any existing buildpacks
heroku buildpacks:clear --app tesocr

# Add apt buildpack FIRST (installs Tesseract)
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt --app tesocr

# Add Python buildpack SECOND
heroku buildpacks:add heroku/python --app tesocr

# Verify the buildpack order
heroku buildpacks --app tesocr
```

**Expected output:**
```
=== tesocr Buildpacks
1. https://github.com/heroku/heroku-buildpack-apt
2. heroku/python
```

**If you've set up the git remote, you can omit --app:**
```bash
heroku buildpacks:clear
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add heroku/python
heroku buildpacks
```

## Step 6: Verify Required Files

Make sure these files exist in your project:

```bash
# Check Aptfile exists and has correct content
type Aptfile

# Should show:
# tesseract-ocr
# tesseract-ocr-eng

# Check other required files
dir requirements.txt
dir Procfile
dir app.py
dir wsgi.py
```

## Step 7: Set Environment Variables (Optional but Recommended)

```bash
# Set environment variables for Tesseract
heroku config:set TESSERACT_CMD=/usr/bin/tesseract --app tesocr
heroku config:set TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata --app tesocr
heroku config:set FLASK_ENV=production --app tesocr

# Verify environment variables
heroku config --app tesocr
```

## Step 8: Commit and Deploy

```bash
# Make sure all files are committed
git status

# Add all files
git add .

# Commit changes
git commit -m "Configure Heroku deployment with Tesseract"

# Deploy to Heroku
git push heroku master

# OR if your default branch is 'main':
git push heroku main
```

## Step 9: Monitor the Build

Watch the build logs to ensure Tesseract is being installed:

```bash
# Watch build logs in real-time
heroku logs --tail --app tesocr
```

**Look for these messages:**
- `-----> Apt app detected`
- `Reading Aptfile...`
- `Installing apt packages...`
- `Installing tesseract-ocr`
- `Installing tesseract-ocr-eng`

## Step 10: Verify Deployment

### Check App Status

```bash
# Check if app is running
heroku ps --app tesocr

# Should show:
# === web (Free): gunicorn ... (1)
# web.1: up 2025/11/17 ...
```

### Test Health Endpoint

```bash
# Open the health endpoint
heroku open --app tesocr
# Then navigate to /health in your browser

# OR use curl (if installed)
curl https://tesocr.herokuapp.com/health
```

### Test Debug Endpoint

Visit in browser:
```
https://tesocr.herokuapp.com/debug/tesseract
```

This will show detailed Tesseract diagnostics.

## Step 11: Test the Application

```bash
# Open your app
heroku open --app tesocr
```

Try uploading an image and verifying text extraction works.

## Troubleshooting

### Issue: Buildpacks not in correct order

```bash
# Check current buildpacks
heroku buildpacks --app tesocr

# If wrong order, clear and re-add:
heroku buildpacks:clear --app tesocr
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt --app tesocr
heroku buildpacks:add heroku/python --app tesocr
```

### Issue: Tesseract not found after deployment

```bash
# Check build logs for apt buildpack
heroku logs --tail --app tesocr | findstr /i "apt tesseract"

# Check runtime logs
heroku logs --tail --app tesocr

# Visit debug endpoint
# https://tesocr.herokuapp.com/debug/tesseract
```

### Issue: App crashes on startup

```bash
# Check logs for errors
heroku logs --tail --app tesocr

# Check if all dependencies are in requirements.txt
type requirements.txt

# Restart the app
heroku restart --app tesocr
```

### Issue: Build fails

```bash
# Check build logs
heroku logs --tail --app tesocr

# Common issues:
# - Missing requirements.txt
# - Missing Procfile
# - Python version mismatch
# - Buildpack order wrong
```

## Quick Reference Commands

```bash
# View app info
heroku info --app tesocr

# View logs
heroku logs --tail --app tesocr

# Restart app
heroku restart --app tesocr

# Scale dynos (if needed)
heroku ps:scale web=1 --app tesocr

# Open app in browser
heroku open --app tesocr

# Run one-off commands
heroku run bash --app tesocr

# View config vars
heroku config --app tesocr

# Set config var
heroku config:set KEY=value --app tesocr
```

## Complete Example Workflow

Here's a complete example assuming your app name is `tesocr-b4a15d123f60`:

```bash
# 1. Login
heroku login

# 2. Navigate to project
cd C:\Users\User1\Desktop\ocr\tes_ocr

# 3. Set up remote
heroku git:remote -a tesocr-b4a15d123f60

# 4. Configure buildpacks
heroku buildpacks:clear
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add heroku/python
heroku buildpacks

# 5. Set environment variables
heroku config:set TESSERACT_CMD=/usr/bin/tesseract
heroku config:set TESSDATA_PREFIX=/usr/share/tesseract-ocr/tessdata
heroku config:set FLASK_ENV=production

# 6. Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku master

# 7. Monitor
heroku logs --tail

# 8. Test
heroku open
# Navigate to /health or /debug/tesseract
```

## Next Steps

After successful deployment:

1. **Test OCR functionality** - Upload an image and verify text extraction
2. **Monitor performance** - Check logs regularly
3. **Set up monitoring** - Consider Heroku add-ons for monitoring
4. **Scale if needed** - Upgrade dyno if you need more resources

## Support

If you encounter issues:

1. Check the logs: `heroku logs --tail --app tesocr`
2. Visit debug endpoint: `https://tesocr.herokuapp.com/debug/tesseract`
3. Verify buildpacks: `heroku buildpacks --app tesocr`
4. Check Heroku status: https://status.heroku.com

