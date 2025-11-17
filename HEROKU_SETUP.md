# Heroku Setup Instructions

## Critical: Configure Buildpacks

The apt buildpack **must** run before the Python buildpack to install Tesseract.

### Option 1: Using Heroku CLI (Recommended)

**First, set up the Heroku remote (if not already done):**

```bash
# If you know your app name (replace tesocr with your actual app name)
heroku git:remote -a tesocr

# OR if you don't know the app name, list your apps:
heroku apps
```

**Then configure buildpacks:**

```bash
# Clear existing buildpacks (use --app flag if remote not set)
heroku buildpacks:clear --app tesocr

# Add apt buildpack FIRST (this installs Tesseract)
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt --app tesocr

# Add Python buildpack SECOND
heroku buildpacks:add heroku/python --app tesocr

# Verify buildpacks are set correctly
heroku buildpacks --app tesocr
```

**Or if you've set up the git remote, you can omit --app:**

```bash
heroku buildpacks:clear
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add heroku/python
heroku buildpacks
```

You should see:
```
1. https://github.com/heroku/heroku-buildpack-apt
2. heroku/python
```

### Option 2: Using Heroku Dashboard

1. Go to your app's Settings page
2. Scroll to "Buildpacks" section
3. Click "Add buildpack"
4. Add in this order:
   - First: `https://github.com/heroku/heroku-buildpack-apt`
   - Second: `heroku/python`

## Verify Installation

After deploying, check the build logs:

```bash
heroku logs --tail
```

Look for messages like:
- "Installing apt packages"
- "Reading Aptfile"
- "Installing tesseract-ocr"

## Test Tesseract

Visit the debug endpoint:
```
https://your-app.herokuapp.com/debug/tesseract
```

Or check health:
```
https://your-app.herokuapp.com/health
```

## Troubleshooting

If Tesseract is still not found:

1. **Check build logs** - Make sure apt buildpack ran:
   ```bash
   heroku logs --tail | grep -i "apt\|tesseract"
   ```

2. **Verify Aptfile exists** - Should contain:
   ```
   tesseract-ocr
   tesseract-ocr-eng
   ```

3. **Check buildpack order**:
   ```bash
   heroku buildpacks
   ```
   Apt must be first!

4. **Redeploy** after fixing buildpacks:
   ```bash
   git commit --allow-empty -m "Trigger rebuild"
   git push heroku master
   ```

