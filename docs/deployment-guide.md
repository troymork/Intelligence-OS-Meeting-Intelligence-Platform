# Continuous Deployment System Guide

## Overview

The Intelligence OS Platform uses a comprehensive continuous deployment system with automated rollbacks, multiple deployment strategies, and real-time monitoring.

## Architecture

### Components

1. **CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
   - Automated testing and building
   - Multi-environment deployment
   - Security scanning
   - Automated rollbacks

2. **Kubernetes Configurations** (`k8s/`)
   - Staging environment (`k8s/staging/`)
   - Production environment (`k8s/production/`)
   - Blue-green and canary deployment support

3. **Monitoring & Health Checks**
   - Deployment health monitoring (`scripts/deployment-health-check.sh`)
   - Real-time monitoring dashboard (`scripts/deployment-monitor.py`)
   - Smoke tests (`tests/smoke/`)

4. **Automated Rollback System** (`scripts/automated-rollback.sh`)
   - Failure detection
   - Automatic rollback execution
   - Health verification

## Deployment Strategies

### 1. Standard Deployment
- Rolling updates with zero downtime
- Gradual replacement of old pods
- Automatic rollback on failure

### 2. Blue-Green Deployment
- Two identical production environments
- Instant traffic switching
- Quick rollback capability
- Zero downtime deployments

### 3. Canary Deployment
- Gradual traffic shifting (20% → 40% → 60% → 80% → 100%)
- Risk mitigation through limited exposure
- Automated monitoring and rollback

## Environment Configuration

### Staging Environment
- **URL**: `https://staging.intelligence-os.example.com`
- **API**: `https://api.staging.intelligence-os.example.com`
- **Namespace**: `intelligence-os-staging`
- **Replicas**: 2 per service
- **Auto-deploy**: On push to `develop` branch

### Production Environment
- **URL**: `https://intelligence-os.example.com`
- **API**: `https://api.intelligence-os.example.com`
- **Namespace**: `intelligence-os-production`
- **Replicas**: 3 per service
- **Auto-deploy**: On push to `main` branch

## Deployment Process

### Automatic Deployment

1. **Code Push** → Triggers CI/CD pipeline
2. **Build & Test** → Runs all test suites
3. **Security Scan** → Vulnerability assessment
4. **Docker Build** → Creates container images
5. **Deploy to Staging** → Automatic staging deployment
6. **Smoke Tests** → Validates basic functionality
7. **Deploy to Production** → Production deployment (if main branch)
8. **Health Monitoring** → Continuous health checks
9. **Rollback** → Automatic rollback on failure

### Manual Deployment

```bash
# Deploy to staging
gh workflow run ci-cd.yml -f environment=staging -f deploy_type=standard

# Deploy to production with canary strategy
gh workflow run ci-cd.yml -f environment=production -f deploy_type=canary

# Deploy to production with blue-green strategy
gh workflow run ci-cd.yml -f environment=production -f deploy_type=blue-green
```

## Health Monitoring

### Automated Health Checks

The system performs comprehensive health checks:

```bash
# Run health check for production
./scripts/deployment-health-check.sh intelligence-os-production

# Run health check for staging
./scripts/deployment-health-check.sh intelligence-os-staging
```

### Real-time Monitoring

```bash
# Start continuous monitoring
python3 scripts/deployment-monitor.py --namespace intelligence-os-production

# One-time status check
python3 scripts/deployment-monitor.py --namespace intelligence-os-production --once

# Save metrics to file
python3 scripts/deployment-monitor.py --namespace intelligence-os-production --output metrics.json
```

### Smoke Tests

```bash
# Run smoke tests for production
cd tests/smoke
npm test -- --url https://intelligence-os.example.com

# Run smoke tests for staging
npm run test:staging
```

## Rollback Procedures

### Automatic Rollback

The system automatically triggers rollbacks when:
- Health checks fail after deployment
- Smoke tests fail
- Error rates exceed thresholds
- Response times degrade significantly

### Manual Rollback

```bash
# Standard rollback
./scripts/automated-rollback.sh intelligence-os-production standard manual_rollback

# Blue-green rollback
./scripts/automated-rollback.sh intelligence-os-production blue-green manual_rollback

# Canary rollback
./scripts/automated-rollback.sh intelligence-os-production canary manual_rollback
```

### Kubernetes Native Rollback

```bash
# Rollback specific deployment
kubectl rollout undo deployment/frontend -n intelligence-os-production

# Rollback to specific revision
kubectl rollout undo deployment/frontend --to-revision=2 -n intelligence-os-production

# Check rollout status
kubectl rollout status deployment/frontend -n intelligence-os-production
```

## Security Features

### Container Security
- Non-root user execution
- Minimal base images
- Security scanning in CI/CD
- Regular dependency updates

### Network Security
- TLS/SSL encryption
- Security headers (HSTS, CSP, etc.)
- CORS configuration
- Rate limiting

### Access Control
- Kubernetes RBAC
- Namespace isolation
- Secret management
- Environment-specific configurations

## Monitoring & Alerting

### Metrics Collected
- Deployment status and health
- Pod resource usage
- Response times and error rates
- Service availability
- Infrastructure metrics

### Alerting Channels
- Slack notifications
- Email alerts (configurable)
- PagerDuty integration (optional)
- Custom webhook support

### Dashboards
- Real-time deployment status
- Historical metrics
- Performance trends
- Error tracking

## Troubleshooting

### Common Issues

1. **Deployment Stuck**
   ```bash
   kubectl get pods -n intelligence-os-production
   kubectl describe pod <pod-name> -n intelligence-os-production
   kubectl logs <pod-name> -n intelligence-os-production
   ```

2. **Health Check Failures**
   ```bash
   # Check service endpoints
   kubectl get endpoints -n intelligence-os-production
   
   # Test health endpoints directly
   curl -f https://intelligence-os.example.com/health
   ```

3. **Rollback Issues**
   ```bash
   # Check deployment history
   kubectl rollout history deployment/frontend -n intelligence-os-production
   
   # Force rollback
   kubectl rollout undo deployment/frontend -n intelligence-os-production
   ```

### Debug Commands

```bash
# Get all resources in namespace
kubectl get all -n intelligence-os-production

# Check events
kubectl get events -n intelligence-os-production --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n intelligence-os-production

# Check ingress status
kubectl describe ingress -n intelligence-os-production
```

## Configuration

### Required Secrets

Set these secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `AWS_REGION` - AWS region
- `EKS_CLUSTER_NAME` - EKS cluster name
- `STAGING_URL` - Staging environment URL
- `PRODUCTION_URL` - Production environment URL
- `SLACK_WEBHOOK_URL` - Slack webhook for notifications
- `SNYK_TOKEN` - Snyk token for security scanning

### Environment Variables

Configure these in your Kubernetes ConfigMaps:

- `NODE_ENV` - Environment (staging/production)
- `LOG_LEVEL` - Logging level
- `DATABASE_URL` - Database connection string
- `REDIS_HOST` - Redis host
- `API_URL` - API base URL

## Best Practices

### Deployment
1. Always test in staging first
2. Use feature flags for risky changes
3. Monitor metrics during and after deployment
4. Keep rollback procedures tested and ready
5. Document all configuration changes

### Monitoring
1. Set up comprehensive alerting
2. Monitor business metrics, not just technical ones
3. Use distributed tracing for complex issues
4. Keep historical data for trend analysis
5. Regular health check validation

### Security
1. Regular security scans
2. Keep dependencies updated
3. Use least privilege access
4. Encrypt sensitive data
5. Regular security audits

## Support

For deployment issues:
1. Check the monitoring dashboard
2. Review recent deployment logs
3. Run health checks manually
4. Check Slack notifications
5. Contact the DevOps team

For emergency rollbacks:
1. Use automated rollback scripts
2. Verify rollback success
3. Investigate root cause
4. Document incident
5. Update procedures if needed