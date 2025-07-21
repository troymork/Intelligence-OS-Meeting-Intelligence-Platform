#!/bin/bash

# Intelligence OS Platform - Deployment Status Monitor
# Quick status check for all deployment environments

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"; }
info() { echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO: $1${NC}"; }

# Check local deployment
check_local() {
    echo "🏠 Local Environment Status:"
    
    # Check Docker containers
    if docker-compose ps | grep -q "Up"; then
        log "✓ Docker containers are running"
        docker-compose ps
    else
        warn "⚠ Docker containers not running"
    fi
    
    # Check local endpoints
    echo ""
    echo "🌐 Endpoint Health Checks:"
    
    # Frontend
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
        log "✓ Frontend (http://localhost:3000) - Healthy"
    else
        error "✗ Frontend (http://localhost:3000) - Not responding"
    fi
    
    # Backend
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
        log "✓ Backend API (http://localhost:8000) - Healthy"
    else
        error "✗ Backend API (http://localhost:8000) - Not responding"
    fi
    
    # Voice Processor
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health | grep -q "200"; then
        log "✓ Voice Processor (http://localhost:5000) - Healthy"
    else
        error "✗ Voice Processor (http://localhost:5000) - Not responding"
    fi
}

# Check Kubernetes deployment
check_kubernetes() {
    local env=$1
    echo "☸️  Kubernetes Environment Status ($env):"
    
    if ! command -v kubectl &> /dev/null; then
        error "kubectl not found"
        return 1
    fi
    
    local namespace="intelligence-os-$env"
    
    # Check if namespace exists
    if ! kubectl get namespace "$namespace" &> /dev/null; then
        warn "Namespace $namespace not found"
        return 1
    fi
    
    # Check deployments
    echo ""
    echo "📦 Deployment Status:"
    kubectl get deployments -n "$namespace" -o wide
    
    echo ""
    echo "🏃 Pod Status:"
    kubectl get pods -n "$namespace" -o wide
    
    echo ""
    echo "🌐 Service Status:"
    kubectl get services -n "$namespace" -o wide
    
    echo ""
    echo "🔗 Ingress Status:"
    kubectl get ingress -n "$namespace" -o wide
    
    # Check pod health
    echo ""
    echo "💊 Health Check Summary:"
    local pods=$(kubectl get pods -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    
    for pod in $pods; do
        local status=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.phase}')
        local ready=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.containerStatuses[0].ready}')
        
        if [[ "$status" == "Running" && "$ready" == "true" ]]; then
            log "✓ $pod - Running and Ready"
        else
            error "✗ $pod - Status: $status, Ready: $ready"
        fi
    done
}

# Check monitoring
check_monitoring() {
    echo "📊 Monitoring Status:"
    
    if kubectl get namespace monitoring &> /dev/null; then
        echo ""
        echo "🔍 Monitoring Services:"
        kubectl get pods -n monitoring -o wide
        
        # Check Prometheus
        if kubectl get pod -n monitoring -l app.kubernetes.io/name=prometheus | grep -q "Running"; then
            log "✓ Prometheus - Running"
        else
            warn "⚠ Prometheus - Not running"
        fi
        
        # Check Grafana
        if kubectl get pod -n monitoring -l app.kubernetes.io/name=grafana | grep -q "Running"; then
            log "✓ Grafana - Running"
        else
            warn "⚠ Grafana - Not running"
        fi
        
        # Check Elasticsearch
        if kubectl get pod -n monitoring -l app=elasticsearch-master | grep -q "Running"; then
            log "✓ Elasticsearch - Running"
        else
            warn "⚠ Elasticsearch - Not running"
        fi
    else
        warn "Monitoring namespace not found"
    fi
}

# Main function
main() {
    echo "🚀 Intelligence OS Platform - Deployment Status"
    echo "=============================================="
    echo ""
    
    case "${1:-all}" in
        "local")
            check_local
            ;;
        "staging")
            check_kubernetes "staging"
            ;;
        "production")
            check_kubernetes "production"
            ;;
        "monitoring")
            check_monitoring
            ;;
        "all")
            check_local
            echo ""
            echo "=============================================="
            echo ""
            check_kubernetes "staging" 2>/dev/null || warn "Staging environment not available"
            echo ""
            echo "=============================================="
            echo ""
            check_kubernetes "production" 2>/dev/null || warn "Production environment not available"
            echo ""
            echo "=============================================="
            echo ""
            check_monitoring 2>/dev/null || warn "Monitoring not available"
            ;;
        *)
            echo "Usage: $0 [local|staging|production|monitoring|all]"
            exit 1
            ;;
    esac
    
    echo ""
    echo "✅ Status check complete!"
}

main "$@"