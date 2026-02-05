#!/bin/bash

# Build and Push Script for Question Answer Generator
# This script builds Docker images and pushes them to a registry

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="${REGISTRY:-your-registry}"
VERSION="${VERSION:-latest}"
BACKEND_IMAGE="${REGISTRY}/question-answer-backend"
FRONTEND_IMAGE="${REGISTRY}/question-answer-frontend"

echo -e "${BLUE}Question Answer Generator - Build and Push${NC}"
echo "=============================================="
echo ""
echo "Registry: $REGISTRY"
echo "Version: $VERSION"
echo ""

# Function to build backend
build_backend() {
    echo -e "${YELLOW}Building backend image...${NC}"
    docker build \
        -f backend/Dockerfile.prod \
        -t ${BACKEND_IMAGE}:${VERSION} \
        -t ${BACKEND_IMAGE}:latest \
        ./backend
    echo -e "${GREEN}✓ Backend image built${NC}"
    echo ""
}

# Function to build frontend
build_frontend() {
    echo -e "${YELLOW}Building frontend image...${NC}"
    docker build \
        -f frontend/Dockerfile.prod \
        -t ${FRONTEND_IMAGE}:${VERSION} \
        -t ${FRONTEND_IMAGE}:latest \
        ./frontend
    echo -e "${GREEN}✓ Frontend image built${NC}"
    echo ""
}

# Function to push images
push_images() {
    echo -e "${YELLOW}Pushing images to registry...${NC}"
    
    docker push ${BACKEND_IMAGE}:${VERSION}
    docker push ${BACKEND_IMAGE}:latest
    echo -e "${GREEN}✓ Backend image pushed${NC}"
    
    docker push ${FRONTEND_IMAGE}:${VERSION}
    docker push ${FRONTEND_IMAGE}:latest
    echo -e "${GREEN}✓ Frontend image pushed${NC}"
    
    echo ""
}

# Function to scan images for vulnerabilities
scan_images() {
    echo -e "${YELLOW}Scanning images for vulnerabilities...${NC}"
    
    if command -v trivy &> /dev/null; then
        echo "Scanning backend image..."
        trivy image ${BACKEND_IMAGE}:${VERSION}
        
        echo "Scanning frontend image..."
        trivy image ${FRONTEND_IMAGE}:${VERSION}
        
        echo -e "${GREEN}✓ Image scanning complete${NC}"
    else
        echo -e "${YELLOW}Trivy not installed. Skipping vulnerability scan.${NC}"
        echo "Install Trivy: https://github.com/aquasecurity/trivy"
    fi
    echo ""
}

# Function to show image info
show_info() {
    echo -e "${GREEN}Build complete!${NC}"
    echo ""
    echo "Images built:"
    echo "  Backend:  ${BACKEND_IMAGE}:${VERSION}"
    echo "  Frontend: ${FRONTEND_IMAGE}:${VERSION}"
    echo ""
    echo "Image sizes:"
    docker images | grep question-answer
    echo ""
}

# Parse command line arguments
BUILD_ONLY=false
PUSH_ONLY=false
SCAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --push-only)
            PUSH_ONLY=true
            shift
            ;;
        --scan)
            SCAN=true
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --build-only       Only build images, don't push"
            echo "  --push-only        Only push images, don't build"
            echo "  --scan             Scan images for vulnerabilities"
            echo "  --registry REGISTRY  Set registry (default: your-registry)"
            echo "  --version VERSION    Set version tag (default: latest)"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Build and push with defaults"
            echo "  $0 --build-only                       # Only build images"
            echo "  $0 --registry myregistry --version v1.0  # Custom registry and version"
            echo "  $0 --scan                             # Build and scan for vulnerabilities"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Main execution
if [ "$PUSH_ONLY" = true ]; then
    push_images
elif [ "$BUILD_ONLY" = true ]; then
    build_backend
    build_frontend
    if [ "$SCAN" = true ]; then
        scan_images
    fi
    show_info
else
    build_backend
    build_frontend
    if [ "$SCAN" = true ]; then
        scan_images
    fi
    push_images
    show_info
fi

echo -e "${GREEN}Done!${NC}"
