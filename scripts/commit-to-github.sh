#!/bin/bash

# Intelligence OS Platform - Commit All Files to GitHub
set -euo pipefail

echo "🚀 Preparing Intelligence OS Platform for GitHub Codespaces..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run 'git init' first."
    exit 1
fi

# Add all files
echo "📁 Adding all files to git..."
git add .

# Check git status
echo "📊 Git status:"
git status --short

# Create comprehensive commit
echo "💾 Creating commit..."
git commit -m "🚀 Add GitHub Codespaces support for Intelligence OS Platform

✨ Features Added:
- Complete GitHub Codespaces configuration
- Cloud-optimized Docker setup for resource efficiency
- Simplified deployment scripts for quick startup
- Comprehensive documentation and setup guides
- Lightweight backend with minimal dependencies
- Fast Docker builds optimized for cloud deployment

🛠 Technical Improvements:
- .devcontainer/devcontainer.json with full VS Code setup
- docker-compose.fast.yml for efficient cloud deployment
- Minimal requirements.txt to avoid timeout issues
- Automated setup scripts for seamless onboarding
- Port forwarding configuration for all services
- Environment-specific configurations

📚 Documentation:
- README-CODESPACE.md with detailed setup instructions
- Comprehensive main README.md with architecture overview
- Quick start scripts and troubleshooting guides

🎯 Benefits:
- Zero local resource usage - everything runs in GitHub's cloud
- 2-4 CPU cores + 8GB RAM in Codespace (more than most local setups)
- Automatic HTTPS URLs for secure access
- Pre-configured development environment
- Persistent cloud storage
- Access from any device with a browser

This setup completely frees up local Mac resources while providing
a powerful, cloud-based development environment for the Intelligence OS Platform!"

echo "✅ Commit created successfully!"

# Check if we have a remote
if git remote get-url origin > /dev/null 2>&1; then
    echo "🌐 Pushing to GitHub..."
    git push origin main || git push origin master
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🎉 Ready for Codespaces!"
    echo "👉 Go to your GitHub repository and click 'Code' > 'Codespaces' > 'Create codespace on main'"
else
    echo "⚠️  No remote repository configured."
    echo "Please add your GitHub repository as origin:"
    echo "git remote add origin https://github.com/your-username/intelligence-os-platform.git"
    echo "Then run: git push -u origin main"
fi

echo ""
echo "🌟 Next Steps:"
echo "1. Go to your GitHub repository"
echo "2. Click the green 'Code' button"
echo "3. Select 'Codespaces' tab"
echo "4. Click 'Create codespace on main'"
echo "5. Wait for setup to complete"
echo "6. Run: ./start-platform.sh"
echo ""
echo "🎯 Your Mac will be completely free while you develop in the cloud!"