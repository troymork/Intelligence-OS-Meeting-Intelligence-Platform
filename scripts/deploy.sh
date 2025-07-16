#!/bin/bash

# Oracle Nexus Production Deployment Script
# Supports multiple deployment targets: Docker, Kubernetes, Cloud platforms

set -e

echo "🚀 Oracle Nexus Production Deployment"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Default deployment target
DEPLOYMENT_TARGET="docker"
ENVIRONMENT="production"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--target)
            DEPLOYMENT_TARGET="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -t, --target TARGET     Deployment target (docker, k8s, aws, azure, gcp)"
            echo "  -e, --environment ENV   Environment (production, staging, development)"
            echo "  -h, --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --target docker --environment production"
            echo "  $0 --target k8s --environment staging"
            echo "  $0 --target aws --environment production"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate deployment target
validate_target() {
    case $DEPLOYMENT_TARGET in
        docker|k8s|kubernetes|aws|azure|gcp)
            print_success "Deployment target: $DEPLOYMENT_TARGET"
            ;;
        *)
            print_error "Invalid deployment target: $DEPLOYMENT_TARGET"
            print_error "Supported targets: docker, k8s, aws, azure, gcp"
            exit 1
            ;;
    esac
}

# Build application
build_application() {
    print_status "Building Oracle Nexus application..."
    
    # Run build script
    ./scripts/build.sh
    
    print_success "Application build completed"
}

# Docker deployment
deploy_docker() {
    print_status "Deploying with Docker..."
    
    # Create Dockerfile if it doesn't exist
    if [ ! -f "Dockerfile" ]; then
        cat > Dockerfile << 'EOF'
# Multi-stage build for Oracle Nexus
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY src/frontend/package*.json ./
RUN npm ci --only=production

COPY src/frontend/ ./
RUN npm run build

FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY src/backend/ ./
COPY --from=frontend-builder /app/frontend/dist ./src/static

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd --create-home --shell /bin/bash oracle
RUN chown -R oracle:oracle /app
USER oracle

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/oracle/health || exit 1

# Start application
CMD ["python", "src/main.py"]
EOF
        print_success "Dockerfile created"
    fi
    
    # Create docker-compose.yml
    if [ ! -f "docker-compose.yml" ]; then
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  oracle-nexus:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://oracle:oracle@postgres:5432/oracle_nexus
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/oracle/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=oracle_nexus
      - POSTGRES_USER=oracle
      - POSTGRES_PASSWORD=oracle
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - oracle-nexus
    restart: unless-stopped

volumes:
  postgres_data:
EOF
        print_success "docker-compose.yml created"
    fi
    
    # Build and start containers
    docker-compose build
    docker-compose up -d
    
    print_success "Docker deployment completed"
    print_status "Application available at: http://localhost"
}

# Kubernetes deployment
deploy_kubernetes() {
    print_status "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl create namespace oracle-nexus --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Kubernetes manifests directory
    mkdir -p k8s
    
    # Create deployment manifest
    cat > k8s/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: oracle-nexus
  namespace: oracle-nexus
  labels:
    app: oracle-nexus
spec:
  replicas: 3
  selector:
    matchLabels:
      app: oracle-nexus
  template:
    metadata:
      labels:
        app: oracle-nexus
    spec:
      containers:
      - name: oracle-nexus
        image: oracle-nexus:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: oracle-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: oracle-secrets
              key: openai-api-key
        livenessProbe:
          httpGet:
            path: /api/oracle/health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/oracle/health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
EOF
    
    # Create service manifest
    cat > k8s/service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: oracle-nexus-service
  namespace: oracle-nexus
spec:
  selector:
    app: oracle-nexus
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
EOF
    
    # Create ingress manifest
    cat > k8s/ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: oracle-nexus-ingress
  namespace: oracle-nexus
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - oracle-nexus.yourdomain.com
    secretName: oracle-nexus-tls
  rules:
  - host: oracle-nexus.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: oracle-nexus-service
            port:
              number: 80
EOF
    
    # Apply manifests
    kubectl apply -f k8s/
    
    print_success "Kubernetes deployment completed"
    print_status "Check deployment status: kubectl get pods -n oracle-nexus"
}

# AWS deployment
deploy_aws() {
    print_status "Deploying to AWS..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed"
        exit 1
    fi
    
    # Create ECS task definition
    cat > aws-task-definition.json << 'EOF'
{
  "family": "oracle-nexus",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "oracle-nexus",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/oracle-nexus:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:oracle-nexus/database-url"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:oracle-nexus/openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/oracle-nexus",
          "awslogs-region": "REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF
    
    print_success "AWS deployment configuration created"
    print_warning "Please update aws-task-definition.json with your AWS account details"
    print_status "Deploy with: aws ecs register-task-definition --cli-input-json file://aws-task-definition.json"
}

# Main deployment function
main() {
    print_status "Starting deployment process..."
    print_status "Target: $DEPLOYMENT_TARGET"
    print_status "Environment: $ENVIRONMENT"
    echo ""
    
    validate_target
    build_application
    
    case $DEPLOYMENT_TARGET in
        docker)
            deploy_docker
            ;;
        k8s|kubernetes)
            deploy_kubernetes
            ;;
        aws)
            deploy_aws
            ;;
        azure)
            print_warning "Azure deployment not yet implemented"
            exit 1
            ;;
        gcp)
            print_warning "GCP deployment not yet implemented"
            exit 1
            ;;
    esac
    
    echo ""
    print_success "🎉 Deployment completed successfully!"
    echo ""
}

# Run main function
main "$@"

