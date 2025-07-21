#!/bin/bash

# Deployment Health Check Script
# This script performs comprehensive health checks on deployed services

set -euo pipefail

# Configuration
NAMESPACE=${1:-"intelligence-os-production"}
TIMEOUT=${2:-300}
HEALTH_CHECK_INTERVAL=${3:-10}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Function to check deployment status
check_deployment_status() {
    local deployment=$1
    local namespace=$2
    
    log "Checking deployment status for $deployment in namespace $namespace"
    
    # Check if deployment exists
    if ! kubectl get deployment "$deployment" -n "$namespace" &>/dev/null; then
        error "Deployment $deployment not found in namespace $namespace"
        return 1
    fi
    
    # Check deployment rollout status
    if ! kubectl rollout status deployment/"$deployment" -n "$namespace" --timeout="${TIMEOUT}s"; then
        error "Deployment $deployment rollout failed or timed out"
        return 1
    fi
    
    # Check if all replicas are ready
    local desired_replicas=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.spec.replicas}')
    local ready_replicas=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.readyReplicas}')
    
    if [[ "$ready_replicas" != "$desired_replicas" ]]; then
        error "Deployment $deployment: $ready_replicas/$desired_replicas replicas ready"
        return 1
    fi
    
    log "Deployment $deployment is healthy: $ready_replicas/$desired_replicas replicas ready"
    return 0
}

# Function to check service endpoints
check_service_endpoints() {
    local service=$1
    local namespace=$2
    
    log "Checking service endpoints for $service in namespace $namespace"
    
    # Check if service exists
    if ! kubectl get service "$service" -n "$namespace" &>/dev/null; then
        error "Service $service not found in namespace $namespace"
        return 1
    fi
    
    # Check if service has endpoints
    local endpoints=$(kubectl get endpoints "$service" -n "$namespace" -o jsonpath='{.subsets[*].addresses[*].ip}' | wc -w)
    
    if [[ "$endpoints" -eq 0 ]]; then
        error "Service $service has no endpoints"
        return 1
    fi
    
    log "Service $service has $endpoints endpoint(s)"
    return 0
}

# Function to perform HTTP health checks
check_http_health() {
    local url=$1
    local expected_status=${2:-200}
    local max_attempts=${3:-5}
    
    log "Performing HTTP health check on $url"
    
    for ((i=1; i<=max_attempts; i++)); do
        if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
            log "HTTP health check passed for $url (attempt $i/$max_attempts)"
            return 0
        else
            warn "HTTP health check failed for $url (attempt $i/$max_attempts)"
            if [[ $i -lt $max_attempts ]]; then
                sleep $HEALTH_CHECK_INTERVAL
            fi
        fi
    done
    
    error "HTTP health check failed for $url after $max_attempts attempts"
    return 1
}

# Function to check pod health
check_pod_health() {
    local namespace=$1
    
    log "Checking pod health in namespace $namespace"
    
    # Get all pods in the namespace
    local pods=$(kubectl get pods -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    
    for pod in $pods; do
        # Check pod status
        local pod_status=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.phase}')
        
        if [[ "$pod_status" != "Running" ]]; then
            error "Pod $pod is in $pod_status state"
            return 1
        fi
        
        # Check container readiness
        local ready_containers=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.containerStatuses[?(@.ready==true)].name}' | wc -w)
        local total_containers=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.containerStatuses[*].name}' | wc -w)
        
        if [[ "$ready_containers" -ne "$total_containers" ]]; then
            error "Pod $pod: $ready_containers/$total_containers containers ready"
            return 1
        fi
        
        log "Pod $pod is healthy: $ready_containers/$total_containers containers ready"
    done
    
    return 0
}

# Function to check resource usage
check_resource_usage() {
    local namespace=$1
    
    log "Checking resource usage in namespace $namespace"
    
    # Check CPU and memory usage
    kubectl top pods -n "$namespace" --no-headers | while read -r line; do
        local pod_name=$(echo "$line" | awk '{print $1}')
        local cpu_usage=$(echo "$line" | awk '{print $2}')
        local memory_usage=$(echo "$line" | awk '{print $3}')
        
        log "Pod $pod_name - CPU: $cpu_usage, Memory: $memory_usage"
    done
    
    return 0
}

# Function to check ingress health
check_ingress_health() {
    local namespace=$1
    
    log "Checking ingress health in namespace $namespace"
    
    # Get all ingresses in the namespace
    local ingresses=$(kubectl get ingress -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    
    for ingress in $ingresses; do
        # Check if ingress has load balancer IP
        local lb_ip=$(kubectl get ingress "$ingress" -n "$namespace" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
        local lb_hostname=$(kubectl get ingress "$ingress" -n "$namespace" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        
        if [[ -z "$lb_ip" && -z "$lb_hostname" ]]; then
            warn "Ingress $ingress has no load balancer IP or hostname"
        else
            log "Ingress $ingress has load balancer: ${lb_ip:-$lb_hostname}"
        fi
    done
    
    return 0
}

# Main health check function
main() {
    log "Starting comprehensive health check for namespace: $namespace"
    
    local health_check_failed=false
    
    # Check deployments
    local deployments=("frontend" "backend" "voice-processor")
    for deployment in "${deployments[@]}"; do
        if ! check_deployment_status "$deployment" "$NAMESPACE"; then
            health_check_failed=true
        fi
    done
    
    # Check services
    local services=("frontend-service" "backend-service" "voice-processor-service")
    for service in "${services[@]}"; do
        if ! check_service_endpoints "$service" "$NAMESPACE"; then
            health_check_failed=true
        fi
    done
    
    # Check pod health
    if ! check_pod_health "$NAMESPACE"; then
        health_check_failed=true
    fi
    
    # Check ingress health
    if ! check_ingress_health "$NAMESPACE"; then
        health_check_failed=true
    fi
    
    # Check resource usage (informational)
    check_resource_usage "$NAMESPACE" || true
    
    # Perform HTTP health checks if ingress is available
    if [[ "$NAMESPACE" == "intelligence-os-production" ]]; then
        check_http_health "https://intelligence-os.example.com/health" 200 3 || health_check_failed=true
        check_http_health "https://api.intelligence-os.example.com/health" 200 3 || health_check_failed=true
    elif [[ "$NAMESPACE" == "intelligence-os-staging" ]]; then
        check_http_health "https://staging.intelligence-os.example.com/health" 200 3 || health_check_failed=true
        check_http_health "https://api.staging.intelligence-os.example.com/health" 200 3 || health_check_failed=true
    fi
    
    if [[ "$health_check_failed" == true ]]; then
        error "Health check failed for namespace $NAMESPACE"
        exit 1
    else
        log "All health checks passed for namespace $NAMESPACE"
        exit 0
    fi
}

# Run main function
main "$@"