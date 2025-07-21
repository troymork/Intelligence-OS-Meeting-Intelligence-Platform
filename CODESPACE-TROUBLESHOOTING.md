# 🔧 Codespace Troubleshooting Guide

## Common Configuration Errors and Solutions

### ❌ "Configuration Error" During Build

**Possible Causes:**
1. Invalid JSON syntax in devcontainer.json
2. Missing or incorrect feature specifications
3. Network issues during setup

**Solutions:**

#### Option 1: Use Simple Configuration
If the main devcontainer fails, rename the files:
```bash
mv .devcontainer/devcontainer.json .devcontainer/devcontainer-full.json
mv .devcontainer/devcontainer-simple.json .devcontainer/devcontainer.json
```

#### Option 2: Manual Setup
If automatic setup fails, run these commands in your Codespace terminal:
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup manually
./scripts/setup-codespace.sh

# Start the platform
./start-platform.sh
```

#### Option 3: Minimal Docker Setup
If Docker Compose fails, try individual containers:
```bash
# Start database only
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine

# Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run backend directly
cd src/backend
python app.py
```

### 🐳 Docker Issues

**Error: "Docker daemon not running"**
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker if needed
sudo systemctl start docker
```

**Error: "Permission denied"**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart terminal or run
newgrp docker
```

### 📦 Package Installation Issues

**Python packages fail to install:**
```bash
# Use minimal requirements
pip install flask flask-cors psycopg2-binary redis python-dotenv

# Or install individually
pip install --no-cache-dir flask
pip install --no-cache-dir psycopg2-binary
```

**Node.js packages fail:**
```bash
# Clear npm cache
npm cache clean --force

# Install with legacy peer deps
npm install --legacy-peer-deps

# Or use yarn
npm install -g yarn
yarn install
```

### 🌐 Port Forwarding Issues

**Ports not accessible:**
1. Check the "Ports" tab in VS Code
2. Make sure ports are set to "Public"
3. Try different port numbers if conflicts occur

**URLs not working:**
```bash
# Check if services are running
docker-compose ps

# Check specific service logs
docker-compose logs backend
docker-compose logs frontend
```

### 🔧 Service Startup Issues

**Services won't start:**
```bash
# Check Docker Compose file exists
ls -la docker-compose*.yml

# Try with verbose output
docker-compose -f docker-compose.fast.yml up -d --verbose

# Check individual service status
docker ps -a
```

**Database connection errors:**
```bash
# Check if PostgreSQL is running
docker exec -it postgres pg_isready

# Connect to database manually
docker exec -it postgres psql -U intelligence_user -d intelligence_os
```

### 🚀 Quick Recovery Commands

**Complete Reset:**
```bash
# Stop all containers
docker-compose down

# Remove all containers and volumes
docker system prune -a --volumes

# Restart setup
./scripts/setup-codespace.sh
./start-platform.sh
```

**Minimal Working Setup:**
```bash
# Just start the essential services
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run backend directly
cd src/backend && python app.py &

# Serve frontend statically
cd src/frontend && python -m http.server 3000
```

### 📞 Getting Help

If you're still having issues:

1. **Check the Codespace logs** in the terminal
2. **Look at the "Problems" tab** in VS Code
3. **Try the simple configuration** (devcontainer-simple.json)
4. **Use manual setup commands** instead of automatic setup
5. **Create a new Codespace** if the current one is corrupted

### 🎯 Alternative: Local Development

If Codespaces continues to have issues, you can still develop locally:
```bash
# Clone the repository
git clone https://github.com/troymork/Intelligence-OS-Meeting-Intelligence-Platform.git

# Use the simple local deployment
./scripts/deploy-local-simple.sh
```

Remember: The goal is to get you developing quickly. Don't spend too much time troubleshooting - sometimes starting fresh is faster!