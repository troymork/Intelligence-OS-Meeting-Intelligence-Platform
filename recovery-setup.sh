#!/bin/bash

# Intelligence OS Platform - Recovery Setup
# Run this if the automatic Codespace setup fails

echo "🔧 Intelligence OS Platform - Recovery Mode Setup"
echo "=================================================="

# Make scripts executable
echo "📝 Making scripts executable..."
chmod +x scripts/*.sh || echo "⚠️ Some scripts may not exist yet"
chmod +x *.sh || echo "⚠️ Some root scripts may not exist yet"

# Check if we have the basic files
echo "📁 Checking project structure..."
if [ -d "src/backend" ]; then
    echo "✅ Backend directory found"
else
    echo "❌ Backend directory missing"
fi

if [ -d "src/frontend" ]; then
    echo "✅ Frontend directory found"
else
    echo "❌ Frontend directory missing"
fi

if [ -f "docker-compose.fast.yml" ] || [ -f "docker-compose.yml" ]; then
    echo "✅ Docker Compose file found"
else
    echo "❌ Docker Compose file missing"
fi

# Create minimal environment file
echo "⚙️ Creating environment configuration..."
cat > .env << 'EOF'
# Intelligence OS Platform - Recovery Environment
ENVIRONMENT=codespace
NODE_ENV=development
DATABASE_URL=postgresql://intelligence_user:intelligence_pass@postgres:5432/intelligence_os
REDIS_URL=redis://redis:6379
FLASK_APP=app.py
FLASK_ENV=development
EOF

echo "✅ Environment file created"

# Create a simple start script
echo "🚀 Creating startup script..."
cat > start-simple.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Intelligence OS Platform (Simple Mode)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not available"
    exit 1
fi

# Use the available compose file
if [ -f "docker-compose.fast.yml" ]; then
    COMPOSE_FILE="docker-compose.fast.yml"
elif [ -f "docker-compose.yml" ]; then
    COMPOSE_FILE="docker-compose.yml"
else
    echo "❌ No Docker Compose file found"
    echo "Starting individual containers..."
    
    # Start basic containers
    docker run -d --name postgres -p 5432:5432 \
        -e POSTGRES_DB=intelligence_os \
        -e POSTGRES_USER=intelligence_user \
        -e POSTGRES_PASSWORD=intelligence_pass \
        postgres:15-alpine
    
    docker run -d --name redis -p 6379:6379 redis:7-alpine
    
    echo "✅ Basic services started"
    echo "🌐 You can now run the backend manually:"
    echo "   cd src/backend && python app.py"
    exit 0
fi

echo "🐳 Using $COMPOSE_FILE"
docker-compose -f "$COMPOSE_FILE" up -d

echo "⏳ Waiting for services..."
sleep 20

echo "📊 Service Status:"
docker-compose -f "$COMPOSE_FILE" ps

echo ""
echo "🌐 Access URLs:"
if [ -n "${CODESPACE_NAME:-}" ]; then
    echo "   Frontend: https://$CODESPACE_NAME-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    echo "   Backend:  https://$CODESPACE_NAME-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
else
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
fi
echo ""
echo "✅ Platform started!"
EOF

chmod +x start-simple.sh

echo ""
echo "🎯 Recovery Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Run: ./start-simple.sh"
echo "2. Or manually start services:"
echo "   - docker-compose up -d"
echo "   - cd src/backend && python app.py"
echo ""
echo "🔧 If Docker Compose fails:"
echo "   - Individual containers will start automatically"
echo "   - Run backend manually: cd src/backend && python app.py"
echo ""
echo "📞 Need help? Check CODESPACE-TROUBLESHOOTING.md"