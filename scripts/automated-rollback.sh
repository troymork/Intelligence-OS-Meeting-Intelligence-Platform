#!/bin/bash

# Automated Rollback Script
# This script performs automated rollbacks when deployments fail

set -euo pipefail

# Configuration
NAMESPACE=${1:-"intelligence-os-production"}
DEPLOYMENT_TYPE=${2:-"standard"}
ROLLBACK_REASON=${3:-"health_check_failure"}

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

# Function to send notification
send_notification() {
    local message=$1
    local webhook_url=${SLACK_WEBHOOK_URL:-""}
    
    if [[ -n "$webhook_url" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🔄 $message\"}" \
            "$webhook_url" || warn "Failed to send Slack notification"
    fi
    
    log "Notification: $message"
}

# Function to create rollback snapshot
create_rollback_snapshot() {
    local namespace=$1
    local timestamp=$(date +%Y%m%d-%H%M%S)
    
    log "Creating rollback snapshot for namespace $namespace"
    
    # Create snapshot directory
    local snapshot_dir="rollback-snapshots/$namespace-$timestamp"
    mkdir -p "$snapshot_dir"
    
    # Save current deployment configurations
    kubectl get deployments -n "$namespace" -o yaml > "$snapshot_dir/deployments.yaml"
    kubectl get services -n "$namespace" -o yaml > "$snapshot_dir/services.yaml"
    kubectl get ingress -n "$namespace" -o yaml > "$snapshot_dir/ingress.yaml"
    kubectl get configmaps -n "$namespace" -o yaml > "$snapshot_dir/configmaps.yaml"
    
    log "Rollback snapshot created at $snapshot_dir"
    echo "$snapshot_dir"
}

# Function to perform standard rollback
perform_standard_rollback() {
    local namespace=$1
    
    log "Performing standard rollback for namespace $namespace"
    
    local deployments=("frontend" "backend" "voice-processor")
    local rollback_failed=false
    
    for deployment in "${deployments[@]}"; do
        log "Rolling back deployment $deployment"
        
        if kubectl rollout undo deployment/"$deployment" -n "$namespace"; then
            log "Successfully initiated rollback for $deployment"
            
            # Wait for rollback to complete
            if kubectl rollout status deployment/"$deployment" -n "$namespace" --timeout=300s; then
                log "Rollback completed successfully for $deployment"
            else
                error "Rollback failed for $deployment"
                rollback_failed=true
            fi
        else
            error "Failed to initiate rollback for $deployment"
            rollback_failed=true
        fi
    done
    
    return $([[ "$rollback_failed" == true ]] && echo 1 || echo 0)
}

# Function to perform blue-green rollback
perform_blue_green_rollback() {
    local namespace=$1
    
    log "Performing blue-green rollback for namespace $namespace"
    
    # Get current active environment
    local current_env=$(kubectl get configmap deployment-config -n "$namespace" -o jsonpath='{.data.active_environment}' 2>/dev/null || echo "blue")
    
    # Determine previous environment
    local previous_env
    if [[ "$current_env" == "blue" ]]; then
        previous_env="green"
    else
        previous_env="blue"
    fi
    
    log "Current environment: $current_env, rolling back to: $previous_env"
    
    # Check if previous environment exists
    if ! kubectl get deployment "frontend-$previous_env" -n "$namespace" &>/dev/null; then
        error "Previous environment $previous_env not found. Cannot perform blue-green rollback."
        return 1
    fi
    
    # Update ingress to point back to previous environment
    log "Updating ingress to point to $previous_env environment"
    
    kubectl patch ingress frontend-ingress -n "$namespace" --type=json \
        -p="[{\"op\": \"replace\", \"path\": \"/spec/rules/0/http/paths/0/backend/service/name\", \"value\": \"frontend-$previous_env\"}]"
    
    kubectl patch ingress backend-ingress -n "$namespace" --type=json \
        -p="[{\"op\": \"replace\", \"path\": \"/spec/rules/0/http/paths/0/backend/service/name\", \"value\": \"backend-$previous_env\"}]"
    
    # Update active environment in config
    kubectl create configmap deployment-config --from-literal=active_environment="$previous_env" \
        -n "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    log "Blue-green rollback completed. Active environment is now: $previous_env"
    return 0
}

# Function to perform canary rollback
perform_canary_rollback() {
    local namespace=$1
    
    log "Performing canary rollback for namespace $namespace"
    
    # Remove canary deployments
    local canary_deployments=("frontend-canary" "backend-canary" "voice-processor-canary")
    
    for deployment in "${canary_deployments[@]}"; do
        if kubectl get deployment "$deployment" -n "$namespace" &>/dev/null; then
            log "Removing canary deployment $deployment"
            kubectl delete deployment "$deployment" -n "$namespace"
        fi
    done
    
    # Remove canary services
    local canary_services=("frontend-canary" "backend-canary" "voice-processor-canary")
    
    for service in "${canary_services[@]}"; do
        if kubectl get service "$service" -n "$namespace" &>/dev/null; then
            log "Removing canary service $service"
            kubectl delete service "$service" -n "$namespace"
        fi
    done
    
    # Remove canary ingress annotations
    kubectl annotate ingress frontend-ingress -n "$namespace" \
        nginx.ingress.kubernetes.io/canary- \
        nginx.ingress.kubernetes.io/canary-weight- \
        --overwrite || true
    
    # Remove canary ingress if it exists
    if kubectl get ingress frontend-ingress-canary -n "$namespace" &>/dev/null; then
        kubectl delete ingress frontend-ingress-canary -n "$namespace"
    fi
    
    log "Canary rollback completed. All canary resources removed."
    return 0
}

# Function to verify rollback health
verify_rollback_health() {
    local namespace=$1
    
    log "Verifying rollback health for namespace $namespace"
    
    # Wait for services to stabilize
    sleep 30
    
    # Run health check script
    if ./scripts/deployment-health-check.sh "$namespace"; then
        log "Rollback health verification passed"
        return 0
    else
        error "Rollback health verification failed"
        return 1
    fi
}

# Function to cleanup failed deployment artifacts
cleanup_failed_deployment() {
    local namespace=$1
    local deployment_type=$2
    
    log "Cleaning up failed deployment artifacts for namespace $namespace"
    
    case "$deployment_type" in
        "blue-green")
            # Clean up failed blue-green deployment
            local current_env=$(kubectl get configmap deployment-config -n "$namespace" -o jsonpath='{.data.active_environment}' 2>/dev/null || echo "blue")
            local failed_env
            if [[ "$current_env" == "blue" ]]; then
                failed_env="green"
            else
                failed_env="blue"
            fi
            
            # Remove failed environment deployments
            kubectl delete deployment "frontend-$failed_env" -n "$namespace" --ignore-not-found=true
            kubectl delete deployment "backend-$failed_env" -n "$namespace" --ignore-not-found=true
            kubectl delete deployment "voice-processor-$failed_env" -n "$namespace" --ignore-not-found=true
            
            # Remove failed environment services
            kubectl delete service "frontend-$failed_env" -n "$namespace" --ignore-not-found=true
            kubectl delete service "backend-$failed_env" -n "$namespace" --ignore-not-found=true
            kubectl delete service "voice-processor-$failed_env" -n "$namespace" --ignore-not-found=true
            ;;
        "canary")
            # Canary cleanup is handled in perform_canary_rollback
            log "Canary cleanup completed during rollback"
            ;;
        *)
            log "No specific cleanup required for standard deployment"
            ;;
    esac
}

# Main rollback function
main() {
    log "Starting automated rollback for namespace: $NAMESPACE"
    log "Deployment type: $DEPLOYMENT_TYPE"
    log "Rollback reason: $ROLLBACK_REASON"
    
    # Send initial notification
    send_notification "Automated rollback initiated for $NAMESPACE ($DEPLOYMENT_TYPE deployment) - Reason: $ROLLBACK_REASON"
    
    # Create rollback snapshot
    local snapshot_dir=$(create_rollback_snapshot "$NAMESPACE")
    
    # Perform rollback based on deployment type
    local rollback_success=false
    
    case "$DEPLOYMENT_TYPE" in
        "standard")
            if perform_standard_rollback "$NAMESPACE"; then
                rollback_success=true
            fi
            ;;
        "blue-green")
            if perform_blue_green_rollback "$NAMESPACE"; then
                rollback_success=true
            fi
            ;;
        "canary")
            if perform_canary_rollback "$NAMESPACE"; then
                rollback_success=true
            fi
            ;;
        *)
            error "Unknown deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
    
    if [[ "$rollback_success" == true ]]; then
        log "Rollback completed successfully"
        
        # Verify rollback health
        if verify_rollback_health "$NAMESPACE"; then
            log "Rollback health verification passed"
            send_notification "✅ Automated rollback completed successfully for $NAMESPACE"
            
            # Cleanup failed deployment artifacts
            cleanup_failed_deployment "$NAMESPACE" "$DEPLOYMENT_TYPE"
            
            exit 0
        else
            error "Rollback health verification failed"
            send_notification "❌ Automated rollback completed but health verification failed for $NAMESPACE"
            exit 1
        fi
    else
        error "Rollback failed"
        send_notification "❌ Automated rollback failed for $NAMESPACE"
        exit 1
    fi
}

# Make script executable and run main function
chmod +x "$0"
main "$@"