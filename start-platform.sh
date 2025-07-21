#!/bin/bash

# Intelligence OS Platform - Codespace Quick Start
set -euo pipefail

echo "🚀 Starting Intelligence OS Platform in GitHub Codespace..."

# Set environment variables for Codespace
if [ -n "${CODESPACE_NAME:-}" ]; then
    export FRONTEND_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    export API_URL="https://${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    export VOICE_PROCESSOR_URL="https://${CODESPACE_NAME}-5000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    
    # Update environment file
    sed -i "s|FRONTEND_URL=.*|FRONTEND_URL=${FRONTEND_URL}|g" .env.codespace
    sed -i "s|API_URL=.*|API_URL=${API_URL}|g" .env.codespace
    sed -i "s|VOICE_PROCESSOR_URL=.*|VOICE_PROCESSOR_URL=${VOICE_PROCESSOR_URL}|g" .env.codespace
fi

# Copy environment file
cp .env.codespace .env

# Start services with Docker Compose
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.fast.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose -f docker-compose.fast.yml exec -T postgres pg_isready -U intelligence_user > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "⚠️  PostgreSQL is starting up..."
fi

# Check Redis
if docker-compose -f docker-compose.fast.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "⚠️  Redis is starting up..."
fi

# Check Backend
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "⚠️  Backend API is starting up..."
fi

# Show service status
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.fast.yml ps

echo ""
echo "🌐 Access URLs:"
if [ -n "${CODESPACE_NAME:-}" ]; then
    echo "   🎨 Frontend:        ${FRONTEND_URL}"
    echo "   🔧 Backend API:     ${API_URL}"
    echo "   🎤 Voice Processor: ${VOICE_PROCESSOR_URL}"
    echo "   📊 Health Check:    ${API_URL}/health"
    echo "   📚 API Docs:        ${API_URL}/docs"
else
    echo "   🎨 Frontend:        http://localhost:3000"
    echo "   🔧 Backend API:     http://localhost:8000"
    echo "   🎤 Voice Processor: http://localhost:5000"
    echo "   📊 Health Check:    http://localhost:8000/health"
fi

echo ""
echo "🎯 Quick Commands:"
echo "   View logs:          docker-compose -f docker-compose.fast.yml logs -f"
echo "   Stop services:      docker-compose -f docker-compose.fast.yml down"
echo "   Restart services:   docker-compose -f docker-compose.fast.yml restart"
echo ""
echo "✅ Intelligence OS Platform is ready in the cloud!"
echo "💡 Your Mac is now free from resource-intensive development work!"