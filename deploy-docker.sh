#!/bin/bash
# LegalEdge Docker Build and Deployment Script

set -e

ENVIRONMENT=${1:-production}
REGISTRY=${2:-ghcr.io}  # Default to GitHub Container Registry
IMAGE_TAG=${3:-latest}

echo "🐳 LegalEdge Docker Build and Deployment"
echo "Environment: $ENVIRONMENT"
echo "Registry: $REGISTRY"
echo "Tag: $IMAGE_TAG"
echo ""

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
DOCKER_BACKEND="Dockerfile.backend"
DOCKER_APP="Dockerfile"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."

    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is required but not installed${NC}"
        exit 1
    fi

    # Check if logged into registry
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker daemon not running${NC}"
        exit 1
    fi

    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        echo -e "${RED}❌ Backend directory not found${NC}"
        exit 1
    fi

    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        echo -e "${RED}❌ Frontend directory not found${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Function to build backend image
build_backend() {
    echo ""
    echo -e "${BLUE}🔧 Building backend image...${NC}"

    cd "$BACKEND_DIR"

    # Install backend dependencies
    echo "📦 Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi

    cd ..

    # Build backend image
    echo "🏗️  Building Docker image: $REGISTRY/legaledge-backend:$IMAGE_TAG"
    docker build -f "$DOCKER_BACKEND" -t "$REGISTRY/legaledge-backend:$IMAGE_TAG" .

    echo -e "${GREEN}✅ Backend image built successfully${NC}"
}

# Function to build frontend and application image
build_frontend() {
    echo ""
    echo -e "${BLUE}🎨 Building frontend...${NC}"

    cd "$FRONTEND_DIR"

    # Install frontend dependencies
    echo "📦 Installing Node.js dependencies..."
    if [ -f "package.json" ]; then
        npm install
        npm run build
    fi

    cd ..

    echo -e "${GREEN}✅ Frontend built successfully${NC}"
}

# Function to build application image
build_application() {
    echo ""
    echo -e "${BLUE}🚀 Building application image...${NC}"

    # Build main application image (includes both backend and frontend)
    echo "🏗️  Building Docker image: $REGISTRY/legaledge-app:$IMAGE_TAG"
    docker build -f "$DOCKER_APP" -t "$REGISTRY/legaledge-app:$IMAGE_TAG" .

    echo -e "${GREEN}✅ Application image built successfully${NC}"
}

# Function to login to registry
login_to_registry() {
    echo ""
    echo -e "${YELLOW}🔐 Registry Authentication${NC}"

    if [ "$REGISTRY" = "ghcr.io" ]; then
        echo "GitHub Container Registry detected."
        echo "Make sure you're logged in with: echo \$GITHUB_TOKEN | docker login ghcr.io -u \$GITHUB_USERNAME --password-stdin"
        if ! docker login ghcr.io >/dev/null 2>&1; then
            echo -e "${RED}❌ Please login to GitHub Container Registry first${NC}"
            exit 1
        fi
    elif [[ "$REGISTRY" == *"amazonaws.com"* ]]; then
        echo "Amazon ECR detected."
        echo "Make sure you're logged in with: aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin \$REGISTRY"
        if ! docker login "$REGISTRY" >/dev/null 2>&1; then
            echo -e "${RED}❌ Please login to Amazon ECR first${NC}"
            exit 1
        fi
    else
        echo "Custom registry detected."
        if ! docker login "$REGISTRY" >/dev/null 2>&1; then
            echo -e "${RED}❌ Please login to $REGISTRY first${NC}"
            exit 1
        fi
    fi

    echo -e "${GREEN}✅ Registry authentication successful${NC}"
}

# Function to push images
push_images() {
    echo ""
    echo -e "${BLUE}📤 Pushing images to registry...${NC}"

    # Push backend image
    echo "Pushing backend image..."
    docker push "$REGISTRY/legaledge-backend:$IMAGE_TAG"

    # Push application image
    echo "Pushing application image..."
    docker push "$REGISTRY/legaledge-app:$IMAGE_TAG"

    echo -e "${GREEN}✅ Images pushed successfully${NC}"
}

# Function to tag images for deployment
tag_for_deployment() {
    local deploy_tag="$ENVIRONMENT-$(date +%Y%m%d%H%M%S)"

    echo ""
    echo -e "${BLUE}🏷️  Tagging images for deployment...${NC}"
    echo "Deployment tag: $deploy_tag"

    # Tag images with deployment-specific tags
    docker tag "$REGISTRY/legaledge-backend:$IMAGE_TAG" "$REGISTRY/legaledge-backend:$deploy_tag"
    docker tag "$REGISTRY/legaledge-app:$IMAGE_TAG" "$REGISTRY/legaledge-app:$deploy_tag"

    # Push deployment tags
    docker push "$REGISTRY/legaledge-backend:$deploy_tag"
    docker push "$REGISTRY/legaledge-app:$deploy_tag"

    echo -e "${GREEN}✅ Deployment tags created and pushed${NC}"
    echo "Images tagged as: $deploy_tag"
}

# Function to cleanup old images (optional)
cleanup_images() {
    echo ""
    read -p "🧹 Clean up old Docker images? (yes/no): " cleanup
    if [ "$cleanup" = "yes" ]; then
        echo "Cleaning up dangling images..."
        docker image prune -f
        echo -e "${GREEN}✅ Cleanup completed${NC}"
    fi
}

# Function to update ECS service
update_ecs_service() {
    echo ""
    echo -e "${BLUE}🔄 Updating ECS service...${NC}"

    # Update the app_image variable in terraform.tfvars
    sed -i.bak "s|app_image = \".*\"|app_image = \"$REGISTRY/legaledge-app:$IMAGE_TAG\"|g" ../terraform.tfvars

    echo "Updated terraform.tfvars with new image: $REGISTRY/legaledge-app:$IMAGE_TAG"

    # Deploy to ECS
    echo "Deploying to ECS..."
    aws ecs update-service --cluster "legaledge-$ENVIRONMENT-cluster" \
        --service "legaledge-$ENVIRONMENT-app" --force-new-deployment

    echo "⏳ Waiting for deployment to complete..."
    aws ecs wait services-stable --cluster "legaledge-$ENVIRONMENT-cluster" \
        --service "legaledge-$ENVIRONMENT-app"

    echo -e "${GREEN}✅ ECS deployment completed${NC}"
}

# Main execution
echo "🔍 Step 1: Prerequisites check..."
check_prerequisites

echo ""
echo "🐳 Step 2: Docker authentication..."
login_to_registry

echo ""
echo "🔧 Step 3: Building images..."
build_frontend
build_backend
build_application

echo ""
echo "📤 Step 4: Pushing images..."
push_images

echo ""
echo "🏷️  Step 5: Creating deployment tags..."
tag_for_deployment

echo ""
echo "🔄 Step 6: Updating ECS service..."
update_ecs_service

echo ""
echo "🧹 Step 7: Cleanup..."
cleanup_images

echo ""
echo -e "${GREEN}🎉 Docker build and deployment completed!${NC}"
echo ""
echo "📋 Deployment Summary:"
echo "- Backend image: $REGISTRY/legaledge-backend:$IMAGE_TAG"
echo "- Application image: $REGISTRY/legaledge-app:$IMAGE_TAG"
echo "- Environment: $ENVIRONMENT"
echo "- Registry: $REGISTRY"
echo ""
echo "🔍 Next steps:"
echo "1. Verify deployment with health checks"
echo "2. Test application functionality"
echo "3. Monitor costs and performance"
echo "4. Set up backup verification"
