#!/bin/bash

# Intelligence OS Platform - Codespace Setup Script
set -euo pipefail

echo "🚀 Setting up Intelligence OS Platform in GitHub Codespace..."

# Update system
sudo apt-get update

# Install additional dependencies
sudo apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    wget

# Set up Python environment
pip install --upgrade pip
pip install -r src/backend/requirements-minimal.txt

# Set up Node.js environment
cd src/frontend
npm install
cd ../..

# Make all scripts executable
chmod +x scripts/*.sh

# Set up environment variables
cp .env.example .env.codespace
echo "ENVIRONMENT=codespace" >> .env.codespace
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/intelligence_os" >> .env.codespace
echo "REDIS_URL=redis://localhost:6379" >> .env.codespace

# Create quick start script
cat > start-platform.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Intelligence OS Platform in Codespace..."

# Start services with Docker Compose
docker-compose -f docker-compose.fast.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Show status
echo "📊 Service Status:"
docker-compose -f docker-compose.fast.yml ps

echo ""
echo "🌐 Access URLs:"
echo "   Frontend: https://$CODESPACE_NAME-3000.app.github.dev"
echo "   Backend API: https://$CODESPACE_NAME-8000.app.github.dev"
echo "   Voice Processor: https://$CODESPACE_NAME-5000.app.github.dev"
echo ""
echo "✅ Intelligence OS Platform is ready!"
EOF

chmod +x start-platform.sh

echo "✅ Codespace setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run: ./start-platform.sh"
echo "2. Access your platform via the forwarded ports"
echo "3. Develop without impacting your Mac!"