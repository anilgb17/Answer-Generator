# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the Question Answer Generator system.

## Quick Start

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Container images pushed to a registry
- Ingress controller (nginx-ingress recommended)
- cert-manager (for SSL certificates)

### Automated Deployment

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

The script will:
1. Check prerequisites
2. Prompt for secrets (API keys, passwords)
3. Create namespace
4. Create secrets
5. Deploy all resources
6. Show deployment status

### Manual Deployment

1. **Update image references**
   
   Edit the following files and replace `your-registry` with your actual registry:
   - `backend-deployment.yaml`
   - `celery-deployment.yaml`
   - `frontend-deployment.yaml`

2. **Create namespace**
   ```bash
   kubectl apply -f namespace.yaml
   ```

3. **Create secrets**
   ```bash
   kubectl create secret generic app-secrets \
     --from-literal=OPENAI_API_KEY=your_key \
     --from-literal=ANTHROPIC_API_KEY=your_key \
     --from-literal=SECRET_KEY=your_secret \
     --from-literal=REDIS_PASSWORD=your_password \
     --from-literal=CELERY_BROKER_URL=redis://:your_password@redis-service:6379/0 \
     --from-literal=CELERY_RESULT_BACKEND=redis://:your_password@redis-service:6379/0 \
     -n question-answer-generator
   ```

4. **Deploy resources**
   ```bash
   kubectl apply -f configmap.yaml
   kubectl apply -f redis-deployment.yaml
   kubectl apply -f backend-deployment.yaml
   kubectl apply -f celery-deployment.yaml
   kubectl apply -f frontend-deployment.yaml
   kubectl apply -f hpa.yaml
   ```

5. **Deploy ingress (optional)**
   
   Update `ingress.yaml` with your domain, then:
   ```bash
   kubectl apply -f ingress.yaml
   ```

## Manifest Files

### Core Resources

- **namespace.yaml**: Creates the application namespace
- **configmap.yaml**: Application configuration
- **secrets.yaml**: Template for secrets (DO NOT use directly in production)

### Services

- **redis-deployment.yaml**: Redis cache and message broker
- **backend-deployment.yaml**: FastAPI backend service
- **celery-deployment.yaml**: Celery worker for async tasks
- **frontend-deployment.yaml**: React frontend with Nginx

### Networking

- **ingress.yaml**: Ingress configuration for external access

### Scaling

- **hpa.yaml**: Horizontal Pod Autoscalers for automatic scaling

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Ingress                              │
│                    (your-domain.com)                         │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   Frontend   │  │   Backend    │
│   Service    │  │   Service    │
│   (Port 80)  │  │  (Port 8000) │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   Frontend   │  │   Backend    │
│     Pods     │  │     Pods     │
│   (2-5 reps) │  │   (3-10 reps)│
└──────────────┘  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │    Redis     │
                  │   Service    │
                  └──────┬───────┘
                         │
                  ┌──────┴───────┐
                  │              │
                  ▼              ▼
           ┌──────────┐   ┌──────────────┐
           │  Redis   │   │    Celery    │
           │   Pod    │   │    Workers   │
           │          │   │  (2-8 reps)  │
           └──────────┘   └──────────────┘
```

## Resource Requirements

### Minimum Resources

| Component | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|-------------|----------------|-----------|--------------|
| Backend | 250m | 512Mi | 1000m | 2Gi |
| Celery Worker | 500m | 1Gi | 2000m | 4Gi |
| Frontend | 100m | 128Mi | 500m | 256Mi |
| Redis | 100m | 256Mi | 500m | 512Mi |

### Storage Requirements

| Volume | Size | Access Mode |
|--------|------|-------------|
| Redis Data | 5Gi | ReadWriteOnce |
| Backend Uploads | 10Gi | ReadWriteMany |
| Backend Outputs | 20Gi | ReadWriteMany |
| Backend Logs | 5Gi | ReadWriteMany |
| Backend Data | 10Gi | ReadWriteMany |

## Scaling

### Horizontal Pod Autoscaling

The system includes HPA configurations:

- **Backend**: 3-10 replicas (CPU: 70%, Memory: 80%)
- **Celery Workers**: 2-8 replicas (CPU: 75%, Memory: 85%)
- **Frontend**: 2-5 replicas (CPU: 70%)

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n question-answer-generator

# Scale Celery workers
kubectl scale deployment celery-worker --replicas=4 -n question-answer-generator

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n question-answer-generator
```

## Monitoring

### Check Status

```bash
# All resources
kubectl get all -n question-answer-generator

# Pods
kubectl get pods -n question-answer-generator

# Services
kubectl get svc -n question-answer-generator

# HPA status
kubectl get hpa -n question-answer-generator

# Ingress
kubectl get ingress -n question-answer-generator
```

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -n question-answer-generator

# Celery worker logs
kubectl logs -f deployment/celery-worker -n question-answer-generator

# Frontend logs
kubectl logs -f deployment/frontend -n question-answer-generator

# Redis logs
kubectl logs -f deployment/redis -n question-answer-generator
```

### Describe Resources

```bash
# Describe pod
kubectl describe pod <pod-name> -n question-answer-generator

# Describe deployment
kubectl describe deployment backend -n question-answer-generator

# Describe service
kubectl describe svc backend-service -n question-answer-generator
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n question-answer-generator

# Describe pod for events
kubectl describe pod <pod-name> -n question-answer-generator

# Check logs
kubectl logs <pod-name> -n question-answer-generator
```

### Image Pull Errors

- Verify image exists in registry
- Check image pull secrets if using private registry
- Verify image tag is correct

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n question-answer-generator

# Check service
kubectl describe svc backend-service -n question-answer-generator

# Port forward for testing
kubectl port-forward svc/backend-service 8000:8000 -n question-answer-generator
```

### Persistent Volume Issues

```bash
# Check PVCs
kubectl get pvc -n question-answer-generator

# Describe PVC
kubectl describe pvc backend-uploads-pvc -n question-answer-generator
```

## Updates and Rollbacks

### Update Deployment

```bash
# Update image
kubectl set image deployment/backend \
  backend=your-registry/question-answer-backend:v2.0 \
  -n question-answer-generator

# Check rollout status
kubectl rollout status deployment/backend -n question-answer-generator
```

### Rollback Deployment

```bash
# View rollout history
kubectl rollout history deployment/backend -n question-answer-generator

# Rollback to previous version
kubectl rollout undo deployment/backend -n question-answer-generator

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n question-answer-generator
```

## Cleanup

### Delete All Resources

```bash
# Delete namespace (removes all resources)
kubectl delete namespace question-answer-generator
```

### Delete Specific Resources

```bash
# Delete deployment
kubectl delete deployment backend -n question-answer-generator

# Delete service
kubectl delete svc backend-service -n question-answer-generator

# Delete PVC (WARNING: This deletes data)
kubectl delete pvc backend-uploads-pvc -n question-answer-generator
```

## Security Best Practices

1. **Secrets Management**
   - Never commit secrets to version control
   - Use external secret management (Vault, AWS Secrets Manager)
   - Rotate secrets regularly

2. **Network Policies**
   - Implement network policies to restrict pod communication
   - Use separate namespaces for different environments

3. **RBAC**
   - Use Role-Based Access Control
   - Follow principle of least privilege
   - Create service accounts for applications

4. **Image Security**
   - Use official base images
   - Scan images for vulnerabilities
   - Use specific image tags, not `latest`

5. **Pod Security**
   - Run containers as non-root user
   - Use read-only root filesystem where possible
   - Drop unnecessary capabilities

## Production Checklist

Before deploying to production:

- [ ] Images pushed to production registry
- [ ] Secrets created securely
- [ ] Domain configured in ingress
- [ ] SSL certificates configured
- [ ] Resource limits set appropriately
- [ ] HPA configured and tested
- [ ] Persistent volumes configured
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting set up
- [ ] Log aggregation configured
- [ ] Network policies applied
- [ ] RBAC configured
- [ ] Security scanning completed
- [ ] Load testing performed
- [ ] Disaster recovery plan documented

## Additional Resources

- [Main Deployment Guide](../DEPLOYMENT.md)
- [Quick Start Guide](../QUICKSTART.md)
- [Design Document](../.kiro/specs/question-answer-generator/design.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
