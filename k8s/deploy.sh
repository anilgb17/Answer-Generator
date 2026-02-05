#!/bin/bash

# Kubernetes Deployment Script for Question Answer Generator
# This script helps deploy the application to a Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="question-answer-generator"
REGISTRY="${REGISTRY:-your-registry}"
VERSION="${VERSION:-latest}"

echo -e "${GREEN}Question Answer Generator - Kubernetes Deployment${NC}"
echo "=================================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${GREEN}✓ kubectl is installed and connected${NC}"
echo ""

# Function to prompt for secrets
prompt_for_secrets() {
    echo -e "${YELLOW}Please provide the following secrets:${NC}"
    echo ""
    
    read -sp "OpenAI API Key: " OPENAI_API_KEY
    echo ""
    
    read -sp "Anthropic API Key (optional, press Enter to skip): " ANTHROPIC_API_KEY
    echo ""
    
    read -sp "Secret Key (or press Enter to generate): " SECRET_KEY
    echo ""
    if [ -z "$SECRET_KEY" ]; then
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        echo -e "${GREEN}Generated secret key${NC}"
    fi
    
    read -sp "Redis Password (or press Enter to generate): " REDIS_PASSWORD
    echo ""
    if [ -z "$REDIS_PASSWORD" ]; then
        REDIS_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        echo -e "${GREEN}Generated Redis password${NC}"
    fi
    
    CELERY_BROKER_URL="redis://:${REDIS_PASSWORD}@redis-service:6379/0"
    CELERY_RESULT_BACKEND="redis://:${REDIS_PASSWORD}@redis-service:6379/0"
}

# Function to create namespace
create_namespace() {
    echo "Creating namespace..."
    kubectl apply -f namespace.yaml
    echo -e "${GREEN}✓ Namespace created${NC}"
    echo ""
}

# Function to create secrets
create_secrets() {
    echo "Creating secrets..."
    
    # Check if secrets already exist
    if kubectl get secret app-secrets -n $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}Secrets already exist. Do you want to update them? (y/n)${NC}"
        read -r response
        if [[ "$response" != "y" ]]; then
            echo "Skipping secrets creation"
            return
        fi
        kubectl delete secret app-secrets -n $NAMESPACE
    fi
    
    kubectl create secret generic app-secrets \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --from-literal=ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
        --from-literal=SECRET_KEY="$SECRET_KEY" \
        --from-literal=REDIS_PASSWORD="$REDIS_PASSWORD" \
        --from-literal=CELERY_BROKER_URL="$CELERY_BROKER_URL" \
        --from-literal=CELERY_RESULT_BACKEND="$CELERY_RESULT_BACKEND" \
        -n $NAMESPACE
    
    echo -e "${GREEN}✓ Secrets created${NC}"
    echo ""
}

# Function to deploy resources
deploy_resources() {
    echo "Deploying resources..."
    
    kubectl apply -f configmap.yaml
    echo -e "${GREEN}✓ ConfigMap deployed${NC}"
    
    kubectl apply -f redis-deployment.yaml
    echo -e "${GREEN}✓ Redis deployed${NC}"
    
    echo "Waiting for Redis to be ready..."
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=120s
    
    kubectl apply -f backend-deployment.yaml
    echo -e "${GREEN}✓ Backend deployed${NC}"
    
    kubectl apply -f celery-deployment.yaml
    echo -e "${GREEN}✓ Celery worker deployed${NC}"
    
    kubectl apply -f frontend-deployment.yaml
    echo -e "${GREEN}✓ Frontend deployed${NC}"
    
    kubectl apply -f hpa.yaml
    echo -e "${GREEN}✓ Horizontal Pod Autoscalers deployed${NC}"
    
    echo ""
}

# Function to deploy ingress
deploy_ingress() {
    echo -e "${YELLOW}Do you want to deploy the Ingress? (y/n)${NC}"
    read -r response
    if [[ "$response" == "y" ]]; then
        echo "Please update k8s/ingress.yaml with your domain name first"
        echo -e "${YELLOW}Have you updated the domain in ingress.yaml? (y/n)${NC}"
        read -r response
        if [[ "$response" == "y" ]]; then
            kubectl apply -f ingress.yaml
            echo -e "${GREEN}✓ Ingress deployed${NC}"
        else
            echo "Skipping Ingress deployment"
        fi
    fi
    echo ""
}

# Function to check deployment status
check_status() {
    echo "Checking deployment status..."
    echo ""
    
    echo "Pods:"
    kubectl get pods -n $NAMESPACE
    echo ""
    
    echo "Services:"
    kubectl get svc -n $NAMESPACE
    echo ""
    
    echo "Ingress:"
    kubectl get ingress -n $NAMESPACE 2>/dev/null || echo "No ingress configured"
    echo ""
    
    echo "HPA:"
    kubectl get hpa -n $NAMESPACE
    echo ""
}

# Function to show access information
show_access_info() {
    echo -e "${GREEN}Deployment complete!${NC}"
    echo ""
    echo "Access information:"
    echo "==================="
    
    # Get LoadBalancer IP
    EXTERNAL_IP=$(kubectl get svc frontend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ -z "$EXTERNAL_IP" ]; then
        EXTERNAL_IP=$(kubectl get svc frontend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
    fi
    
    if [ -n "$EXTERNAL_IP" ]; then
        echo "Frontend: http://$EXTERNAL_IP"
        echo "Backend API: http://$EXTERNAL_IP/api"
    else
        echo "LoadBalancer IP not yet assigned. Run 'kubectl get svc -n $NAMESPACE' to check"
    fi
    
    echo ""
    echo "Useful commands:"
    echo "  View logs: kubectl logs -f deployment/backend -n $NAMESPACE"
    echo "  Check status: kubectl get all -n $NAMESPACE"
    echo "  Scale backend: kubectl scale deployment backend --replicas=5 -n $NAMESPACE"
    echo ""
}

# Main deployment flow
main() {
    echo "Starting deployment..."
    echo ""
    
    # Check if this is a fresh deployment
    if kubectl get namespace $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}Namespace already exists. This will update the existing deployment.${NC}"
        echo -e "${YELLOW}Continue? (y/n)${NC}"
        read -r response
        if [[ "$response" != "y" ]]; then
            echo "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Prompt for secrets
    prompt_for_secrets
    
    # Create namespace
    create_namespace
    
    # Create secrets
    create_secrets
    
    # Deploy resources
    deploy_resources
    
    # Deploy ingress (optional)
    deploy_ingress
    
    # Check status
    check_status
    
    # Show access information
    show_access_info
}

# Run main function
main
