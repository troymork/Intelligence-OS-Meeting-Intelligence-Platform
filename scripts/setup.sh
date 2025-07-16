#!/bin/bash

# Oracle 9.1 Protocol Development Kit Setup Script
# This script sets up the complete development environment for the Oracle Nexus platform

set -e  # Exit on any error

echo "🚀 Oracle 9.1 Protocol Development Kit Setup"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_status "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Linux detected"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "macOS detected"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_success "Windows detected"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        
        # Check if Python version is 3.11+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            print_success "Python version is compatible (3.11+)"
        else
            print_error "Python 3.11+ is required. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.11+"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
        
        # Check if Node version is 18+
        if node -e "process.exit(process.version.slice(1).split('.')[0] >= 18 ? 0 : 1)"; then
            print_success "Node.js version is compatible (18+)"
        else
            print_error "Node.js 18+ is required. Current version: $NODE_VERSION"
            exit 1
        fi
    else
        print_error "Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is not installed. Please install npm"
        exit 1
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version)
        print_success "$GIT_VERSION found"
    else
        print_warning "Git is not installed. Some features may not work properly"
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        print_success "$DOCKER_VERSION found"
    else
        print_warning "Docker is not installed. Docker deployment will not be available"
    fi
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd src/backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "pip upgraded"
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    cd ../..
}

# Setup Node.js environment
setup_node_env() {
    print_status "Setting up Node.js environment..."
    
    cd src/frontend
    
    # Install dependencies
    if [ -f "package.json" ]; then
        npm install
        print_success "Node.js dependencies installed"
    else
        print_error "package.json not found"
        exit 1
    fi
    
    cd ../..
}

# Setup environment variables
setup_env_vars() {
    print_status "Setting up environment variables..."
    
    # Backend environment
    if [ ! -f "src/backend/.env" ]; then
        cat > src/backend/.env << EOF
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///oracle_nexus.db

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Oracle 9.1 Protocol Configuration
ORACLE_PROTOCOL_VERSION=9.1
ORACLE_ANALYSIS_TIMEOUT=30
ORACLE_MAX_PARTICIPANTS=50
EOF
        print_success "Backend environment file created"
        print_warning "Please update .env file with your actual API keys"
    else
        print_warning "Backend .env file already exists"
    fi
    
    # Frontend environment
    if [ ! -f "src/frontend/.env" ]; then
        cat > src/frontend/.env << EOF
# API Configuration
VITE_API_URL=http://localhost:5000/api
VITE_API_TIMEOUT=30000

# Application Configuration
VITE_APP_NAME=Oracle Nexus
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=development

# Oracle Protocol Configuration
VITE_ORACLE_PROTOCOL_VERSION=9.1
VITE_ENABLE_VOICE_PROCESSING=true
VITE_ENABLE_REAL_TIME_ANALYSIS=true

# Feature Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_WEBHOOKS=false
VITE_ENABLE_MOCK_DATA=true
EOF
        print_success "Frontend environment file created"
    else
        print_warning "Frontend .env file already exists"
    fi
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    cd src/backend
    source venv/bin/activate
    
    # Initialize database
    python -c "
from src.models.user import db
from src.main import app

with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"
    
    print_success "Database setup completed"
    cd ../..
}

# Create development scripts
create_dev_scripts() {
    print_status "Creating development scripts..."
    
    # Development start script
    cat > scripts/dev.sh << 'EOF'
#!/bin/bash

# Start Oracle Nexus development environment

echo "🚀 Starting Oracle Nexus Development Environment"
echo "================================================"

# Start backend
echo "Starting backend server..."
cd src/backend
source venv/bin/activate
python src/main.py &
BACKEND_PID=$!
cd ../..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend development server..."
cd src/frontend
npm run dev &
FRONTEND_PID=$!
cd ../..

echo "✅ Development environment started!"
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

    chmod +x scripts/dev.sh
    print_success "Development script created"
    
    # Build script
    cat > scripts/build.sh << 'EOF'
#!/bin/bash

# Build Oracle Nexus for production

echo "🏗️  Building Oracle Nexus for Production"
echo "========================================"

# Build frontend
echo "Building frontend..."
cd src/frontend
npm run build
cd ../..

# Copy frontend build to backend static directory
echo "Copying frontend build to backend..."
mkdir -p src/backend/src/static
cp -r src/frontend/dist/* src/backend/src/static/

echo "✅ Build completed successfully!"
echo "   Production files are ready in src/backend/src/static/"
EOF

    chmod +x scripts/build.sh
    print_success "Build script created"
    
    # Test script
    cat > scripts/test.sh << 'EOF'
#!/bin/bash

# Run Oracle Nexus test suite

echo "🧪 Running Oracle Nexus Test Suite"
echo "=================================="

# Backend tests
echo "Running backend tests..."
cd src/backend
source venv/bin/activate
python -m pytest tests/ -v
BACKEND_EXIT_CODE=$?
cd ../..

# Frontend tests
echo "Running frontend tests..."
cd src/frontend
npm test
FRONTEND_EXIT_CODE=$?
cd ../..

if [ $BACKEND_EXIT_CODE -eq 0 ] && [ $FRONTEND_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed!"
    exit 1
fi
EOF

    chmod +x scripts/test.sh
    print_success "Test script created"
}

# Main setup function
main() {
    echo ""
    print_status "Starting Oracle 9.1 Protocol Development Kit setup..."
    echo ""
    
    check_os
    check_prerequisites
    setup_python_env
    setup_node_env
    setup_env_vars
    setup_database
    create_dev_scripts
    
    echo ""
    print_success "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Update API keys in src/backend/.env"
    echo "2. Run './scripts/dev.sh' to start development environment"
    echo "3. Visit http://localhost:5173 to access the Oracle Nexus platform"
    echo ""
    echo "For more information, see docs/README.md"
    echo ""
}

# Run main function
main "$@"

