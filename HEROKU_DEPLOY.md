# Heroku Deployment Guide

This guide will help you deploy the OCR Validation System to Heroku.

## Prerequisites

1. Heroku account (sign up at https://www.heroku.com)
2. Heroku CLI installed (download from https://devcenter.heroku.com/articles/heroku-cli)
3. Git installed
4. Docker installed (optional, for local testing)

## Deployment Steps

### Method 1: Using Heroku CLI (Recommended)

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**
   ```bash
   heroku create your-app-name
   ```
   (Replace `your-app-name` with your desired app name, or leave it blank for a random name)

3. **Set up Heroku to use Docker**
   ```bash
   heroku stack:set container
   ```

4. **Set environment variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
   heroku config:set TESSERACT_CMD=/usr/bin/tesseract
   ```

5. **Deploy to Heroku**
   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   ```
   (Use `master` instead of `main` if your default branch is `master`)

6. **Open your app**
   ```bash
   heroku open
   ```

### Method 2: Using Heroku Dashboard

1. Go to https://dashboard.heroku.com
2. Click "New" → "Create new app"
3. Enter app name and select region
4. Go to "Settings" → "Stack" → Change to "Container"
5. Go to "Settings" → "Config Vars" and add:
   - `FLASK_ENV`: `production`
   - `TESSDATA_PREFIX`: `/usr/share/tesseract-ocr/4.00/tessdata/`
   - `TESSERACT_CMD`: `/usr/bin/tesseract`
6. Connect your GitHub repository
7. Enable automatic deploys or manually deploy

## Post-Deployment

### Check Logs
```bash
heroku logs --tail
```

### Check Health
Visit: `https://your-app-name.herokuapp.com/health`

### Scale Your App (if needed)
```bash
heroku ps:scale web=1
```

## Troubleshooting

### Tesseract Not Found
- Ensure the Dockerfile is being used (check `heroku.yml` exists)
- Verify Tesseract is installed in the Docker image
- Check logs: `heroku logs --tail`

### Port Issues
- Heroku automatically sets the `PORT` environment variable
- The app should use `os.environ.get('PORT', 10000)`

### Build Failures
- Check build logs: `heroku logs --tail`
- Ensure all dependencies are in `requirements.txt`
- Verify Dockerfile syntax

### Memory Issues
- Heroku free tier has 512MB RAM limit
- Consider upgrading to a paid dyno if processing large images
- Optimize image processing in `app.py`

## Environment Variables

The following environment variables are set automatically or can be configured:

- `PORT`: Set automatically by Heroku
- `FLASK_ENV`: Set to `production`
- `TESSDATA_PREFIX`: Path to Tesseract data files
- `TESSERACT_CMD`: Path to Tesseract executable
- `PYTHON_VERSION`: Python version (3.9.13)

## File Structure for Heroku

Required files:
- `heroku.yml` - Tells Heroku to use Docker
- `Dockerfile` - Container configuration
- `Procfile` - Process configuration (fallback)
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version
- `app.json` - App metadata (optional)

## Notes

- Heroku uses ephemeral filesystem - uploaded files are temporary
- Consider using cloud storage (S3, etc.) for persistent file storage
- Free tier dynos sleep after 30 minutes of inactivity
- Upgrade to paid tier for 24/7 availability

