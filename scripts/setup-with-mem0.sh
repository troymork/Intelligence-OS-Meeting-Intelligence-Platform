#!/bin/bash

# Oracle 9.1 Protocol Development Kit Setup Script with Mem0 and AI Infrastructure
# This script sets up the complete development environment including mem0 and AI infrastructure

set -e

echo "🚀 Oracle 9.1 Protocol Development Kit Setup with Mem0"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if running on supported OS
check_os() {
    print_header "Checking operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Linux detected"
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "macOS detected"
        OS="macos"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_status "Docker found: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_status "Docker Compose found: $(docker-compose --version)"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    print_status "Python found: $(python3 --version)"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    fi
    print_status "Node.js found: $(node --version)"
}

# Setup environment variables
setup_environment() {
    print_header "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            print_status "Created .env file from .env.example"
            print_warning "Please edit .env file with your actual API keys"
        else
            print_error ".env.example file not found"
            exit 1
        fi
    else
        print_status ".env file already exists"
    fi
    
    # Generate secure passwords if not set
    if command -v openssl &> /dev/null; then
        POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        NEO4J_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        sed -i.bak "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" .env
        sed -i.bak "s/NEO4J_PASSWORD=.*/NEO4J_PASSWORD=$NEO4J_PASSWORD/" .env
        print_status "Generated secure passwords"
    fi
}

# Setup Python virtual environment with mem0
setup_python_env() {
    print_header "Setting up Python environment with mem0..."
    
    cd src/backend
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Created Python virtual environment"
    fi
    
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    print_status "Upgraded pip"
    
    # Install requirements including mem0
    pip install -r requirements.txt
    print_status "Installed Python dependencies including mem0ai"
    
    # Verify mem0 installation
    python -c "import mem0; print('Mem0 version:', mem0.__version__)" 2>/dev/null || print_warning "Mem0 installation verification failed"
    
    cd ../..
}

# Setup Node.js environment
setup_node_env() {
    print_header "Setting up Node.js environment..."
    
    cd src/frontend
    
    # Install dependencies
    npm install
    print_status "Installed Node.js dependencies"
    
    cd ../..
}

# Setup AI infrastructure
setup_infrastructure() {
    print_header "Setting up AI infrastructure..."
    
    # Create necessary directories
    mkdir -p logs uploads mem0_data qdrant_config redis_config
    mkdir -p elasticsearch_config kibana_config monitoring/grafana
    mkdir -p nginx/ssl scripts/backups
    
    print_status "Created infrastructure directories"
    
    # Pull required Docker images
    print_status "Pulling Docker images..."
    docker pull mem0/mem0-api-server:latest
    docker pull pgvector/pgvector:pg16
    docker pull neo4j:5.15
    docker pull qdrant/qdrant:latest
    docker pull redis:7-alpine
    docker pull rabbitmq:3-management
    docker pull docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    docker pull prom/prometheus:latest
    docker pull grafana/grafana:latest
    
    print_status "Docker images pulled successfully"
}

# Setup mem0 configuration
setup_mem0() {
    print_header "Setting up mem0 configuration..."
    
    mkdir -p mem0_config
    
    cat > mem0_config/config.yaml << EOF
# Mem0 Configuration for Oracle 9.1 Protocol

llm:
  provider: openai
  config:
    model: gpt-4o-mini
    temperature: 0.1
    max_tokens: 1000

embedder:
  provider: openai
  config:
    model: text-embedding-3-small

vector_store:
  provider: qdrant
  config:
    host: qdrant
    port: 6333
    collection_name: oracle_memory

graph_store:
  provider: neo4j
  config:
    url: bolt://neo4j:7687
    username: neo4j
    password: \${NEO4J_PASSWORD}

version: "1.0"
EOF
    print_status "Created mem0 configuration"
}

# Setup development tools
setup_dev_tools() {
    print_header "Setting up development tools..."
    
    # Create comprehensive development script
    cat > scripts/dev-with-mem0.sh << EOF
#!/bin/bash
# Development server startup script with mem0 and AI infrastructure

echo "🚀 Starting Oracle Nexus development environment with Mem0..."

# Load environment variables
if [ -f .env ]; then
    export \$(cat .env | grep -v '^#' | xargs)
fi

# Start infrastructure services
echo "📦 Starting infrastructure services..."
docker-compose up -d postgres neo4j qdrant redis rabbitmq elasticsearch mem0-server

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 45

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Start backend with mem0 integration
echo "🔧 Starting backend with mem0 integration..."
cd src/backend
source venv/bin/activate
export FLASK_ENV=development
export FLASK_DEBUG=true
python src/main.py &
BACKEND_PID=\$!
cd ../..

# Start frontend
echo "🎨 Starting frontend..."
cd src/frontend
npm start &
FRONTEND_PID=\$!
cd ../..

echo "✅ Development environment started!"
echo ""
echo "🌐 Access URLs:"
echo "- Oracle Nexus Frontend: http://localhost:3000"
echo "- Oracle Nexus Backend: http://localhost:5000"
echo "- Mem0 API Server: http://localhost:8888"
echo "- Neo4j Browser: http://localhost:7474"
echo "- Qdrant Dashboard: http://localhost:6333/dashboard"
echo "- Kibana: http://localhost:5601"
echo "- Grafana: http://localhost:3001"
echo "- RabbitMQ Management: http://localhost:15672"
echo ""
echo "🔑 Default Credentials:"
echo "- Neo4j: neo4j / \${NEO4J_PASSWORD}"
echo "- RabbitMQ: guest / guest"
echo "- Grafana: admin / \${GRAFANA_PASSWORD}"
echo ""
echo "📚 API Documentation:"
echo "- Health Check: http://localhost:5000/api/oracle/health"
echo "- Mem0 Health: http://localhost:8888/health"
echo ""

# Wait for user input to stop
read -p "Press Enter to stop development environment..."

# Stop processes
echo "🛑 Stopping development environment..."
kill \$BACKEND_PID \$FRONTEND_PID 2>/dev/null || true
docker-compose down

echo "✅ Development environment stopped"
EOF
    chmod +x scripts/dev-with-mem0.sh
    print_status "Created development startup script with mem0"
    
    # Create testing script
    cat > scripts/test-mem0.sh << EOF
#!/bin/bash
# Test mem0 integration

echo "🧪 Testing mem0 integration..."

# Load environment variables
if [ -f .env ]; then
    export \$(cat .env | grep -v '^#' | xargs)
fi

# Start minimal infrastructure for testing
docker-compose up -d postgres neo4j qdrant redis mem0-server

# Wait for services
sleep 30

# Run Python tests
cd src/backend
source venv/bin/activate
python -c "
import sys
sys.path.append('src')
from routes.oracle_ai_with_mem0 import memory_manager, analysis_engine

print('Testing mem0 components...')
print('Memory manager initialized:', memory_manager.memory is not None)
print('Analysis engine initialized:', analysis_engine.memory is not None)
print('OpenAI client available:', memory_manager.openai_client is not None)
print('Redis client available:', memory_manager.redis_client is not None)

# Test basic functionality
if memory_manager.memory:
    print('✅ Mem0 integration successful')
else:
    print('❌ Mem0 integration failed')
"

cd ../..

# Stop test infrastructure
docker-compose down

echo "🧪 Mem0 integration test completed"
EOF
    chmod +x scripts/test-mem0.sh
    print_status "Created mem0 testing script"
}

# Setup monitoring
setup_monitoring() {
    print_header "Setting up monitoring and observability..."
    
    # Create Prometheus configuration
    mkdir -p monitoring
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'oracle-nexus'
    static_configs:
      - targets: ['oracle-backend:5000']
  
  - job_name: 'mem0'
    static_configs:
      - targets: ['mem0-server:8888']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
  
  - job_name: 'neo4j'
    static_configs:
      - targets: ['neo4j:7474']
  
  - job_name: 'qdrant'
    static_configs:
      - targets: ['qdrant:6333']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
    print_status "Created Prometheus configuration"
    
    # Create Grafana datasource
    mkdir -p monitoring/grafana/datasources
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    print_status "Created Grafana configuration"
}

# Validate setup
validate_setup() {
    print_header "Validating setup..."
    
    # Check if all required files exist
    required_files=(
        ".env"
        "docker-compose.yml"
        "src/backend/requirements.txt"
        "src/backend/src/routes/oracle_ai_with_mem0.py"
        "scripts/dev-with-mem0.sh"
        "scripts/test-mem0.sh"
        "mem0_config/config.yaml"
        "monitoring/prometheus.yml"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_status "✅ $file exists"
        else
            print_error "❌ $file missing"
        fi
    done
    
    # Check Docker
    if docker info >/dev/null 2>&1; then
        print_status "✅ Docker is running"
    else
        print_warning "⚠️ Docker is not running"
    fi
}

# Main setup function
main() {
    print_header "Starting Oracle 9.1 Protocol Development Kit Setup with Mem0"
    
    check_os
    check_prerequisites
    setup_environment
    setup_python_env
    setup_node_env
    setup_infrastructure
    setup_mem0
    setup_dev_tools
    setup_monitoring
    validate_setup
    
    print_header "Setup completed successfully! 🎉"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Edit .env file with your OpenAI API key and other configuration"
    echo "2. Run './scripts/dev-with-mem0.sh' to start the development environment"
    echo "3. Run './scripts/test-mem0.sh' to test mem0 integration"
    echo "4. Visit http://localhost:3000 to access the Oracle Nexus platform"
    echo ""
    echo "🔧 Key services with mem0 integration:"
    echo "- Oracle Nexus Frontend: http://localhost:3000"
    echo "- Oracle Nexus Backend: http://localhost:5000"
    echo "- Mem0 API Server: http://localhost:8888"
    echo "- Neo4j Browser: http://localhost:7474"
    echo "- Qdrant Dashboard: http://localhost:6333/dashboard"
    echo "- Kibana Dashboard: http://localhost:5601"
    echo "- Grafana Monitoring: http://localhost:3001"
    echo ""
    echo "📖 Documentation:"
    echo "- Mem0 Integration: ./docs/infrastructure/mem0-integration.md"
    echo "- AI Infrastructure: ./docs/infrastructure/ai-infrastructure-stack.md"
    echo "- API Reference: ./docs/api/api-reference.md"
    echo ""
    echo "🆘 Support: https://github.com/troymork/Intelligence-OS-Meeting-Intelligence-Platform"
    echo ""
    echo "⚠️ Important: Make sure to set your OPENAI_API_KEY in the .env file!"
}

# Run main function
main "$@"

