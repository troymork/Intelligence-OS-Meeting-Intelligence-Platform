# Intelligence OS Platform - GitHub Codespace Setup

## 🚀 Quick Start in Codespace

This setup moves all the resource-intensive development work to GitHub's cloud infrastructure, keeping your Mac free and fast!

### Step 1: Create a Codespace

1. Go to your GitHub repository
2. Click the green "Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on main"

### Step 2: Wait for Setup

The Codespace will automatically:
- Install all dependencies
- Set up the development environment
- Configure Docker and services
- Make all scripts executable

### Step 3: Start the Platform

Once the Codespace is ready, run:

```bash
./start-platform.sh
```

This will:
- Start all services (PostgreSQL, Redis, Backend, Frontend, Voice Processor)
- Set up port forwarding
- Display access URLs

### Step 4: Access Your Platform

The Codespace will provide URLs like:
- **Frontend**: `https://your-codespace-3000.app.github.dev`
- **Backend API**: `https://your-codespace-8000.app.github.dev`
- **Voice Processor**: `https://your-codespace-5000.app.github.dev`

## 🛠 Development Commands

### Start/Stop Services
```bash
# Start all services
./start-platform.sh

# Stop all services
docker-compose -f docker-compose.fast.yml down

# Restart services
docker-compose -f docker-compose.fast.yml restart
```

### View Logs
```bash
# View all logs
docker-compose -f docker-compose.fast.yml logs -f

# View specific service logs
docker-compose -f docker-compose.fast.yml logs -f backend
docker-compose -f docker-compose.fast.yml logs -f frontend
```

### Development Workflow
```bash
# Backend development
cd src/backend
python app.py

# Frontend development
cd src/frontend
npm run dev

# Run tests
npm test
python -m pytest src/backend/tests/
```

## 🔧 Configuration

### Environment Variables
Edit `.env.codespace` to configure:
- AI API keys (OpenAI, Anthropic)
- External integrations (Notion, Zapier, Dart)
- Feature flags

### Adding AI API Keys
```bash
# Edit the environment file
code .env.codespace

# Add your keys:
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

## 📊 Monitoring

Access monitoring dashboards:
- **Health Check**: `https://your-codespace-8000.app.github.dev/health`
- **API Documentation**: `https://your-codespace-8000.app.github.dev/docs`
- **Metrics**: `https://your-codespace-9090.app.github.dev`

## 🎯 Benefits of Codespace Development

✅ **Zero Local Resource Usage**: Everything runs in the cloud
✅ **Consistent Environment**: Same setup for all developers
✅ **Pre-configured**: All dependencies and tools ready
✅ **Accessible Anywhere**: Work from any device with a browser
✅ **Automatic Backups**: Your work is saved in the cloud
✅ **Easy Sharing**: Share your Codespace with team members

## 🔄 Syncing Changes

Your Codespace automatically syncs with your GitHub repository:
- Changes are saved automatically
- Commit and push as usual
- Pull requests work normally

## 💡 Tips

1. **Keep Codespace Active**: Use it regularly to avoid automatic shutdown
2. **Use Extensions**: VS Code extensions are pre-installed and configured
3. **Port Forwarding**: All necessary ports are automatically forwarded
4. **Resource Limits**: Codespaces have generous resource limits for development

## 🆘 Troubleshooting

### Services Won't Start
```bash
# Check Docker status
docker ps

# Restart Docker daemon
sudo systemctl restart docker

# Rebuild containers
docker-compose -f docker-compose.fast.yml build --no-cache
```

### Port Forwarding Issues
- Check the "Ports" tab in VS Code
- Ensure ports are set to "Public" if needed
- Restart the Codespace if ports aren't forwarding

### Performance Issues
- Codespaces provide 2-4 CPU cores and 8GB RAM
- Much more powerful than typical local development
- No impact on your Mac's performance!

## 🎉 You're Ready!

Your Intelligence OS Platform is now running entirely in the cloud, leaving your Mac free for other tasks. Develop, test, and deploy without any local resource constraints!