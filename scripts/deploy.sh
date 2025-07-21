#!/bin/bash

# Intelligence OS Platform Deployment Script
# Comprehensive deployment orchestration for all environments

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-"local"}
CLOUD_PROVIDER=${2:-"aws"}
REGION=${3:-"us-west-2"}

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                Intelligence OS Platform                      ║"
    echo "║                   Deployment Script                         ║"
    echo "║                                                              ║"
    echo "║  Environment: $ENVIRONMENT                                        ║"
    echo "║  Cloud Provider: $CLOUD_PROVIDER                                  ║"
    echo "║  Region: $REGION                                             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Prerequisites check
check_prerequisites() {
    log "Checking deployment prerequisites..."
    
    local missing_tools=()
    
    # Check required tools
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v kubectl >/dev/null 2>&1 || missing_tools+=("kubectl")
    command -v terraform >/dev/null 2>&1 || missing_tools+=("terraform")
    command -v helm >/dev/null 2>&1 || missing_tools+=("helm")
    command -v node >/dev/null 2>&1 || missing_tools+=("node")
    command -v python3 >/dev/null 2>&1 || missing_tools+=("python3")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        error "Missing required tools: ${missing_tools[*]}"
        echo "Please install the missing tools and try again."
        exit 1
    fi
    
    # Check Docker is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    log "All prerequisites satisfied ✓"
}

# Environment setup
setup_environment() {
    log "Setting up deployment environment..."
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p backups
    mkdir -p certificates
    
    # Set environment variables
    export ENVIRONMENT=$ENVIRONMENT
    export CLOUD_PROVIDER=$CLOUD_PROVIDER
    export REGION=$REGION
    export TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    # Copy environment-specific configuration
    if [ -f ".env.${ENVIRONMENT}" ]; then
        cp ".env.${ENVIRONMENT}" .env
        log "Environment configuration loaded for $ENVIRONMENT"
    else
        warn "No environment-specific configuration found, using defaults"
        cp .env.example .env
    fi
    
    log "Environment setup complete ✓"
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    # Build frontend image
    info "Building frontend image..."
    docker build -t intelligence-os/frontend:latest -f src/frontend/Dockerfile src/frontend/
    
    # Build backend image
    info "Building backend image..."
    docker build -t intelligence-os/backend:latest -f src/backend/Dockerfile src/backend/
    
    # Build voice processor image
    info "Building voice processor image..."
    docker build -t intelligence-os/voice-processor:latest -f src/voice-processor/Dockerfile src/voice-processor/
    
    log "Docker images built successfully ✓"
}

# Run tests
run_tests() {
    log "Running comprehensive test suite..."
    
    # Install test dependencies
    npm install
    
    # Run unit tests
    info "Running unit tests..."
    npm run test:unit
    
    # Run integration tests
    info "Running integration tests..."
    npm run test:integration
    
    # Run security tests
    info "Running security tests..."
    node tests/security/SecurityTestFramework.js
    
    # Run performance tests
    info "Running performance tests..."
    node tests/performance/PerformanceTestSuite.js
    
    log "All tests passed ✓"
}

# Local deployment
deploy_local() {
    log "Deploying to local environment..."
    
    # Start local services with Docker Compose
    info "Starting services with Docker Compose..."
    docker-compose up -d
    
    # Wait for services to be ready
    info "Waiting for services to be ready..."
    sleep 30
    
    # Run health checks
    info "Running health checks..."
    ./scripts/deployment-health-check.sh local
    
    # Run smoke tests
    info "Running smoke tests..."
    cd tests/smoke
    npm install
    npm test -- --url http://localhost:3000
    cd ../..
    
    log "Local deployment complete ✓"
    info "Frontend: http://localhost:3000"
    info "Backend API: http://localhost:8000"
    info "Voice Processor: http://localhost:5000"
}

# Cloud infrastructure deployment
deploy_infrastructure() {
    log "Deploying cloud infrastructure with Terraform..."
    
    cd infrastructure/terraform
    
    # Initialize Terraform
    info "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    info "Planning infrastructure deployment..."
    terraform plan \
        -var="environment=$ENVIRONMENT" \
        -var="cloud_provider=$CLOUD_PROVIDER" \
        -var="region=$REGION" \
        -out=tfplan
    
    # Apply infrastructure
    info "Applying infrastructure changes..."
    terraform apply tfplan
    
    # Save outputs
    terraform output -json > ../terraform-outputs.json
    
    cd ../..
    
    log "Infrastructure deployment complete ✓"
}

# Kubernetes deployment
deploy_kubernetes() {
    log "Deploying to Kubernetes..."
    
    # Configure kubectl
    info "Configuring kubectl..."
    if [ "$CLOUD_PROVIDER" = "aws" ]; then
        aws eks update-kubeconfig --name "intelligence-os-$ENVIRONMENT" --region "$REGION"
    fi
    
    # Deploy to staging first
    if [ "$ENVIRONMENT" = "production" ]; then
        info "Deploying to staging for validation..."
        kubectl apply -f k8s/staging/
        
        # Wait for staging deployment
        kubectl rollout status deployment/frontend -n intelligence-os-staging
        kubectl rollout status deployment/backend -n intelligence-os-staging
        kubectl rollout status deployment/voice-processor -n intelligence-os-staging
        
        # Run staging tests
        info "Running staging validation tests..."
        ./scripts/deployment-health-check.sh intelligence-os-staging
    fi
    
    # Deploy to target environment
    info "Deploying to $ENVIRONMENT environment..."
    if [ "$ENVIRONMENT" = "production" ]; then
        kubectl apply -f k8s/production/
        
        # Wait for production deployment
        kubectl rollout status deployment/frontend -n intelligence-os-production
        kubectl rollout status deployment/backend -n intelligence-os-production
        kubectl rollout status deployment/voice-processor -n intelligence-os-production
    else
        kubectl apply -f k8s/staging/
        
        # Wait for staging deployment
        kubectl rollout status deployment/frontend -n intelligence-os-staging
        kubectl rollout status deployment/backend -n intelligence-os-staging
        kubectl rollout status deployment/voice-processor -n intelligence-os-staging
    fi
    
    log "Kubernetes deployment complete ✓"
}

# Deploy monitoring
deploy_monitoring() {
    log "Deploying monitoring and observability stack..."
    
    # Deploy monitoring with Terraform
    cd infrastructure/terraform
    terraform apply -target=module.monitoring
    cd ../..
    
    # Wait for monitoring services
    info "Waiting for monitoring services to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n monitoring --timeout=300s
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s
    
    log "Monitoring deployment complete ✓"
}

# Post-deployment validation
validate_deployment() {
    log "Validating deployment..."
    
    # Health checks
    info "Running health checks..."
    if [ "$ENVIRONMENT" = "local" ]; then
        ./scripts/deployment-health-check.sh local
    else
        ./scripts/deployment-health-check.sh "intelligence-os-$ENVIRONMENT"
    fi
    
    # Smoke tests
    info "Running smoke tests..."
    cd tests/smoke
    npm install
    
    if [ "$ENVIRONMENT" = "local" ]; then
        npm test -- --url http://localhost:3000
    elif [ "$ENVIRONMENT" = "staging" ]; then
        npm test -- --url https://staging.intelligence-os.example.com
    else
        npm test -- --url https://intelligence-os.example.com
    fi
    
    cd ../..
    
    # Security validation
    info "Running security validation..."
    node tests/security/SecurityTestFramework.js
    
    # Performance validation
    info "Running performance validation..."
    node tests/performance/PerformanceTestSuite.js
    
    log "Deployment validation complete ✓"
}

# Backup current deployment
backup_deployment() {
    log "Creating deployment backup..."
    
    local backup_dir="backups/deployment_${TIMESTAMP}"
    mkdir -p "$backup_dir"
    
    # Backup Kubernetes configurations
    if [ "$ENVIRONMENT" != "local" ]; then
        kubectl get all -n "intelligence-os-$ENVIRONMENT" -o yaml > "$backup_dir/kubernetes_resources.yaml"
        kubectl get configmaps -n "intelligence-os-$ENVIRONMENT" -o yaml > "$backup_dir/configmaps.yaml"
        kubectl get secrets -n "intelligence-os-$ENVIRONMENT" -o yaml > "$backup_dir/secrets.yaml"
    fi
    
    # Backup Terraform state
    if [ -f "infrastructure/terraform/terraform.tfstate" ]; then
        cp infrastructure/terraform/terraform.tfstate "$backup_dir/"
    fi
    
    # Backup database (if applicable)
    if [ "$ENVIRONMENT" != "local" ]; then
        info "Creating database backup..."
        # Database backup commands would go here
    fi
    
    log "Backup created at $backup_dir ✓"
}

# Rollback deployment
rollback_deployment() {
    warn "Initiating deployment rollback..."
    
    if [ "$ENVIRONMENT" = "local" ]; then
        docker-compose down
        docker-compose up -d
    else
        ./scripts/automated-rollback.sh "intelligence-os-$ENVIRONMENT" standard deployment_failure
    fi
    
    log "Rollback completed ✓"
}

# Cleanup resources
cleanup() {
    log "Cleaning up temporary resources..."
    
    # Remove temporary files
    rm -f tfplan
    rm -f terraform-outputs.json
    
    # Clean up Docker images (optional)
    if [ "$1" = "full" ]; then
        docker system prune -f
    fi
    
    log "Cleanup complete ✓"
}

# Main deployment function
main() {
    print_banner
    
    # Trap errors and cleanup
    trap 'error "Deployment failed! Check logs for details."; cleanup; exit 1' ERR
    
    case "$ENVIRONMENT" in
        "local")
            log "Starting local deployment..."
            check_prerequisites
            setup_environment
            build_images
            run_tests
            deploy_local
            validate_deployment
            ;;
        "staging"|"production")
            log "Starting cloud deployment to $ENVIRONMENT..."
            check_prerequisites
            setup_environment
            build_images
            run_tests
            backup_deployment
            deploy_infrastructure
            deploy_kubernetes
            deploy_monitoring
            validate_deployment
            ;;
        *)
            error "Invalid environment: $ENVIRONMENT"
            echo "Valid environments: local, staging, production"
            exit 1
            ;;
    esac
    
    cleanup
    
    log "🎉 Deployment to $ENVIRONMENT completed successfully!"
    
    # Display access information
    echo ""
    echo "🌐 Access Information:"
    if [ "$ENVIRONMENT" = "local" ]; then
        echo "   Frontend: http://localhost:3000"
        echo "   Backend API: http://localhost:8000"
        echo "   Voice Processor: http://localhost:5000"
        echo "   Monitoring: http://localhost:3001"
    elif [ "$ENVIRONMENT" = "staging" ]; then
        echo "   Frontend: https://staging.intelligence-os.example.com"
        echo "   Backend API: https://api.staging.intelligence-os.example.com"
        echo "   Monitoring: https://monitoring.intelligence-os.example.com"
    else
        echo "   Frontend: https://intelligence-os.example.com"
        echo "   Backend API: https://api.intelligence-os.example.com"
        echo "   Monitoring: https://monitoring.intelligence-os.example.com"
    fi
    
    echo ""
    echo "📊 Next Steps:"
    echo "   1. Monitor deployment health"
    echo "   2. Run user acceptance tests"
    echo "   3. Configure monitoring alerts"
    echo "   4. Set up backup schedules"
    echo ""
}

# Handle script arguments
case "${1:-help}" in
    "local"|"staging"|"production")
        main "$@"
        ;;
    "rollback")
        rollback_deployment
        ;;
    "cleanup")
        cleanup "${2:-}"
        ;;
    "help"|*)
        echo "Usage: $0 [local|staging|production|rollback|cleanup] [cloud_provider] [region]"
        echo ""
        echo "Examples:"
        echo "  $0 local                    # Deploy locally with Docker Compose"
        echo "  $0 staging aws us-west-2    # Deploy to AWS staging environment"
        echo "  $0 production aws us-west-2 # Deploy to AWS production environment"
        echo "  $0 rollback                 # Rollback current deployment"
        echo "  $0 cleanup full             # Full cleanup including Docker images"
        echo ""
        exit 0
        ;;
esac