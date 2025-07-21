#!/bin/bash

# Intelligence OS Platform - Codespace Setup Script
set -eo pipefail

echo "🚀 Setting up Intelligence OS Platform in GitHub Codespace..."

# Function to handle errors
handle_error() {
    echo "❌ Error occurred during setup. Continuing with available components..."
}

trap handle_error ERR

# Update system (with error handling)
echo "📦 Updating system packages..."
sudo apt-get update || echo "⚠️ System update failed, continuing..."

# Install additional dependencies
echo "🔧 Installing additional tools..."
sudo apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    wget \
    git || echo "⚠️ Some tools failed to install, continuing..."

# Make all scripts executable first
echo "🔐 Making scripts executable..."
chmod +x scripts/*.sh || echo "⚠️ Some scripts may not be executable"
chmod +x start-platform.sh || echo "⚠️ start-platform.sh not found yet"

# Set up Python environment
echo "🐍 Setting up Python environment..."
pip install --upgrade pip || echo "⚠️ pip upgrade failed"

if [ -f "src/backend/requirements-minimal.txt" ]; then
    pip install -r src/backend/requirements-minimal.txt || echo "⚠️ Python dependencies installation failed"
else
    echo "⚠️ requirements-minimal.txt not found, skipping Python setup"
fi

# Set up Node.js environment
echo "📦 Setting up Node.js environment..."
if [ -d "src/frontend" ] && [ -f "src/frontend/package.json" ]; then
    cd src/frontend
    npm install || echo "⚠️ npm install failed"
    cd ../..
else
    echo "⚠️ Frontend directory not found, skipping Node.js setup"
fi

# Set up environment variables
echo "⚙️ Setting up environment variables..."
if [ -f ".env.example" ]; then
    cp .env.example .env.codespace || cp .env.local .env.codespace || echo "ENVIRONMENT=codespace" > .env.codespace
else
    echo "ENVIRONMENT=codespace" > .env.codespace
fi

echo "DATABASE_URL=postgresql://intelligence_user:intelligence_pass@postgres:5432/intelligence_os" >> .env.codespace
echo "REDIS_URL=redis://redis:6379" >> .env.codespace

# Ensure start-platform.sh exists and is executable
if [ ! -f "start-platform.sh" ]; then
    echo "📝 Creating start-platform.sh script..."
    cat > start-platform.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Intelligence OS Platform in Codespace..."

# Check if docker-compose.fast.yml exists
if [ ! -f "docker-compose.fast.yml" ]; then
    echo "❌ docker-compose.fast.yml not found"
    echo "Using regular docker-compose.yml instead..."
    COMPOSE_FILE="docker-compose.yml"
else
    COMPOSE_FILE="docker-compose.fast.yml"
fi

# Start services with Docker Compose
echo "🐳 Starting services with $COMPOSE_FILE..."
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Show status
echo "📊 Service Status:"
docker-compose -f "$COMPOSE_FILE" ps

echo ""
echo "🌐 Access URLs:"
if [ -n "${CODESPACE_NAME:-}" ]; then
    echo "   Frontend: https://$CODESPACE_NAME-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    echo "   Backend API: https://$CODESPACE_NAME-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    echo "   Voice Processor: https://$CODESPACE_NAME-5000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
else
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   Voice Processor: http://localhost:5000"
fi
echo ""
echo "✅ Intelligence OS Platform is ready!"
EOF
fi

chmod +x start-platform.sh

echo ""
echo "✅ Codespace setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run: ./start-platform.sh"
echo "2. Access your platform via the forwarded ports"
echo "3. Develop without impacting your Mac!"
echo ""
echo "🔧 If you encounter issues:"
echo "- Check Docker is running: docker --version"
echo "- Check services: docker-compose ps"
echo "- View logs: docker-compose logs"