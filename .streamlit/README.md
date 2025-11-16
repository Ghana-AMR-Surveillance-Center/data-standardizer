# Streamlit Configuration Directory

This directory contains Streamlit-specific configuration files.

## Files

- **config.toml**: Streamlit app configuration (theme, server settings, etc.)
- **secrets.toml.example**: Template for secrets (copy to `secrets.toml` and fill in values)

## Important Notes

⚠️ **Never commit `secrets.toml` to version control!**

The `secrets.toml` file contains sensitive information like API keys and passwords. It's already in `.gitignore` to prevent accidental commits.

## For Streamlit Cloud

When deploying to Streamlit Cloud:
1. Use the "Secrets" section in Streamlit Cloud settings
2. Or create `.streamlit/secrets.toml` in your repository (for public repos, use Streamlit Cloud secrets instead)

## Local Development

For local development, you can create `.streamlit/secrets.toml` from the example file:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Then edit secrets.toml with your values
```

