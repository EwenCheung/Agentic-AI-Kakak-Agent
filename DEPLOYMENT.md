# GitHub Pages Deployment

This branch (`gh-pages`) is configured for automatic deployment to GitHub Pages.

## How it works

1. **Automatic Deployment**: When you push to the `gh-pages` branch, GitHub Actions will automatically:
   - Install Node.js dependencies
   - Build the React frontend application
   - Deploy it to GitHub Pages

2. **Live URL**: Once deployed, your application will be available at:
   ```
   https://EwenCheung.github.io/Agentic-AI-Kakak-Agent
   ```

3. **Workflow**: The deployment workflow is defined in `.github/workflows/deploy-gh-pages.yml`

## Manual Deployment

If you want to deploy manually:

```bash
# Switch to gh-pages branch
git checkout gh-pages

# Make your changes
# ...

# Commit and push
git add .
git commit -m "Update for deployment"
git push origin gh-pages
```

## Frontend Configuration

The frontend is configured with:
- **Homepage**: Set in `frontend/package.json` to match GitHub Pages URL
- **Build Output**: React build files are served from the `frontend/build` directory

## Backend Note

The backend is not deployed to GitHub Pages (which only serves static files). You'll need to deploy the backend separately to a service like:
- Heroku
- Railway
- Render
- AWS/Google Cloud/Azure

Make sure to update the frontend API endpoints to point to your deployed backend.
