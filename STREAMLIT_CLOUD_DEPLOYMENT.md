# Streamlit Cloud Deployment Guide

This guide will help you deploy the GLASS Data Standardizer to Streamlit Cloud.

## Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Repository Access**: Make sure your repository is accessible (public or private with Streamlit Cloud access)

## Step 1: Prepare Your Repository

### 1.1 Ensure Required Files Exist

Your repository should have:
- ✅ `app.py` (main application file)
- ✅ `requirements.txt` (dependencies)
- ✅ `.streamlit/config.toml` (Streamlit configuration)
- ✅ `utils/` directory (all utility modules)
- ✅ `config/` directory (configuration files)

### 1.2 Check File Paths

All file paths should be relative (not absolute). The app has been updated to:
- Use relative paths for images
- Handle missing files gracefully
- Work in cloud environments

### 1.3 Commit and Push to GitHub

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Sign In to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Authorize Streamlit Cloud to access your repositories

### 2.2 Create New App

1. Click **"New app"**
2. Select your repository: `data-standardizer_Glass`
3. Select branch: `main` (or your default branch)
4. Main file path: `app.py`
5. App URL: Choose a unique name (e.g., `glass-data-standardizer`)

### 2.3 Configure Secrets (Optional)

If you need environment variables or secrets:

1. Go to **"Settings"** → **"Secrets"**
2. Add your secrets in TOML format:

```toml
ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "INFO"
SECRET_KEY = "your-secret-key-here"
MAX_FILE_SIZE_MB = "100"
```

Or use the template in `.streamlit/secrets.toml.example`

### 2.4 Deploy

Click **"Deploy"** and wait for the app to build and deploy.

## Step 3: Verify Deployment

### 3.1 Check Build Logs

- Review the build logs for any errors
- Ensure all dependencies install correctly
- Check for any import errors

### 3.2 Test the Application

1. Open your deployed app URL
2. Test file upload functionality
3. Verify all workflows work correctly
4. Check that images/logo display properly

## Step 4: Post-Deployment

### 4.1 Monitor Performance

- Check app performance in Streamlit Cloud dashboard
- Monitor resource usage
- Review error logs if any

### 4.2 Update Configuration

You can update configuration by:
- Editing `.streamlit/config.toml` in your repository
- Updating secrets in Streamlit Cloud settings
- Pushing changes to trigger automatic redeployment

## Troubleshooting

### Common Issues

#### 1. **Import Errors**
- Ensure all modules in `utils/` are committed
- Check that `__init__.py` files exist in package directories
- Verify all dependencies are in `requirements.txt`

#### 2. **File Not Found Errors**
- Check that file paths are relative (not absolute)
- Ensure required directories exist (logs, data, etc.)
- The app handles missing files gracefully with fallbacks

#### 3. **Memory Issues**
- Streamlit Cloud has memory limits
- Large file processing may need optimization
- Consider chunking large datasets

#### 4. **Build Failures**
- Check `requirements.txt` for compatibility
- Ensure Python version is compatible (3.8+)
- Review build logs for specific errors

#### 5. **Logo/Image Not Displaying**
- Ensure image files are in the repository
- Check file paths are relative
- The app has fallback text if images aren't found

### Getting Help

- Check Streamlit Cloud documentation: [docs.streamlit.io/streamlit-cloud](https://docs.streamlit.io/streamlit-cloud)
- Review build logs in Streamlit Cloud dashboard
- Check application logs for runtime errors

## Configuration Files

### `.streamlit/config.toml`
Contains Streamlit-specific configuration (theme, server settings, etc.)

### `requirements.txt`
All Python dependencies needed for the application

### `.streamlit/secrets.toml` (optional)
Environment variables and secrets (not committed to repo)

## Best Practices

1. **Keep Dependencies Updated**: Regularly update `requirements.txt`
2. **Monitor Resource Usage**: Watch memory and CPU usage
3. **Test Before Deploying**: Test locally before pushing changes
4. **Use Secrets for Sensitive Data**: Never commit secrets to repository
5. **Version Control**: Tag releases for easy rollback

## Deployment Checklist

- [ ] All files committed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] `.streamlit/config.toml` exists
- [ ] File paths are relative (not absolute)
- [ ] Repository is accessible to Streamlit Cloud
- [ ] Secrets configured (if needed)
- [ ] App builds successfully
- [ ] All features tested and working
- [ ] Performance is acceptable

## Support

For issues specific to:
- **Streamlit Cloud**: Check [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-cloud)
- **Application**: Review application logs and error messages
- **Deployment**: Follow troubleshooting steps above

---

**Your app will be available at**: `https://your-app-name.streamlit.app`

