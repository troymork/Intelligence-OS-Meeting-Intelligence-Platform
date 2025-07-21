#!/bin/bash

# Intelligence OS Platform - Simplified Local Deployment
# Quick local deployment using Docker Compose only

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"; }
info() { echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO: $1${NC}"; }

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                Intelligence OS Platform                      ║"
echo "║                 Local Deployment (Simple)                   ║"
echo "║                                                              ║"
echo "║  🚀 Quick local deployment with Docker Compose              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check Docker
log "Checking Docker..."
if ! command -v docker &> /dev/null; then
    error "Docker not found. Please install Docker and try again."
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    error "Docker is not running. Please start Docker and try again."
    exit 1
fi

log "Docker is available and running ✓"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose not found. Please install Docker Compose and try again."
    exit 1
fi

log "Docker Compose is available ✓"

# Setup environment
log "Setting up local environment..."
cp .env.local .env
log "Environment configuration loaded ✓"

# Build and start services
log "Building and starting Intelligence OS Platform..."
info "This may take a few minutes on first run..."

# Build images
log "Building Docker images..."
docker-compose build

# Start services
log "Starting services..."
docker-compose up -d

# Wait for services to be ready
log "Waiting for services to initialize..."
sleep 15

# Check service health
log "Checking service health..."

# Check frontend
if curl -s -f http://localhost:3000 >/dev/null 2>&1; then
    log "✓ Frontend is healthy (http://localhost:3000)"
else
    warn "⚠ Frontend may still be starting up"
fi

# Check backend
if curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
    log "✓ Backend API is healthy (http://localhost:8000)"
else
    warn "⚠ Backend API may still be starting up"
fi

# Check voice processor
if curl -s -f http://localhost:5000/health >/dev/null 2>&1; then
    log "✓ Voice Processor is healthy (http://localhost:5000)"
else
    warn "⚠ Voice Processor may still be starting up"
fi

# Show running containers
log "Current container status:"
docker-compose ps

echo ""
echo -e "${GREEN}🎉 Intelligence OS Platform deployed locally!${NC}"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend:        http://localhost:3000"
echo "   Backend API:     http://localhost:8000"
echo "   Voice Processor: http://localhost:5000"
echo "   API Docs:        http://localhost:8000/docs"
echo ""
echo "📊 Management Commands:"
echo "   View logs:       docker-compose logs -f"
echo "   Stop services:   docker-compose down"
echo "   Restart:         docker-compose restart"
echo "   Status:          ./scripts/deployment-status.sh local"
echo ""
echo "🔧 Next Steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Test the voice interface"
echo "   3. Upload a meeting transcript"
echo "   4. Explore the AI analysis features"
echo ""

# Optional: Open browser
if command -v open &> /dev/null; then
    info "Opening Intelligence OS Platform in your browser..."
    sleep 2
    open http://localhost:3000
fi