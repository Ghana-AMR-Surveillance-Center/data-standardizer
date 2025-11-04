#!/bin/bash

# GLASS Data Standardizer - Production Deployment Script

set -e

# Configuration
APP_NAME="glass-data-standardizer"
VERSION="2.0.0"
DOCKER_IMAGE="glass-data-standardizer:latest"
CONTAINER_NAME="glass-data-standardizer-prod"
PORT="8501"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Check if required directories exist
check_directories() {
    log_info "Checking required directories..."
    
    mkdir -p data logs config ssl
    
    # Set proper permissions
    chmod 755 data logs config
    chmod 700 ssl 2>/dev/null || true
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    docker build -t $DOCKER_IMAGE .
    
    if [ $? -eq 0 ]; then
        log_info "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

# Stop existing container
stop_container() {
    log_info "Stopping existing container..."
    
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        docker stop $CONTAINER_NAME
        log_info "Container stopped"
    else
        log_info "No running container found"
    fi
    
    if docker ps -aq -f name=$CONTAINER_NAME | grep -q .; then
        docker rm $CONTAINER_NAME
        log_info "Container removed"
    fi
}

# Start new container
start_container() {
    log_info "Starting new container..."
    
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -p $PORT:8501 \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/logs:/app/logs \
        -v $(pwd)/config:/app/config \
        -e ENVIRONMENT=production \
        -e DEBUG=false \
        -e LOG_LEVEL=INFO \
        -e HOST=0.0.0.0 \
        -e PORT=8501 \
        -e MAX_FILE_SIZE_MB=100 \
        -e ENABLE_MONITORING=true \
        $DOCKER_IMAGE
    
    if [ $? -eq 0 ]; then
        log_info "Container started successfully"
    else
        log_error "Failed to start container"
        exit 1
    fi
}

# Check container health
check_health() {
    log_info "Checking container health..."
    
    # Wait for container to start
    sleep 10
    
    # Check if container is running
    if ! docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log_error "Container is not running"
        docker logs $CONTAINER_NAME
        exit 1
    fi
    
    # Check if application is responding
    for i in {1..30}; do
        if curl -f http://localhost:$PORT/_stcore/health &> /dev/null; then
            log_info "Application is healthy and responding"
            return 0
        fi
        log_info "Waiting for application to start... ($i/30)"
        sleep 2
    done
    
    log_error "Application failed to start or is not responding"
    docker logs $CONTAINER_NAME
    exit 1
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo "=================="
    echo "Application: $APP_NAME v$VERSION"
    echo "Container: $CONTAINER_NAME"
    echo "Port: $PORT"
    echo "URL: http://localhost:$PORT"
    echo ""
    
    # Show container status
    docker ps -f name=$CONTAINER_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # Show recent logs
    log_info "Recent logs:"
    docker logs --tail 10 $CONTAINER_NAME
}

# Cleanup old images
cleanup() {
    log_info "Cleaning up old images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old versions of this image
    docker images $DOCKER_IMAGE --format "{{.Tag}}" | grep -v latest | xargs -r docker rmi
}

# Main deployment function
deploy() {
    log_info "Starting deployment of $APP_NAME v$VERSION"
    echo "=============================================="
    
    check_docker
    check_directories
    build_image
    stop_container
    start_container
    check_health
    cleanup
    show_status
    
    log_info "Deployment completed successfully!"
    log_info "Application is available at: http://localhost:$PORT"
}

# Rollback function
rollback() {
    log_warn "Rolling back to previous version..."
    
    # Stop current container
    stop_container
    
    # Start previous version (if available)
    if docker images | grep -q "$DOCKER_IMAGE"; then
        log_info "Starting previous version..."
        start_container
        check_health
        log_info "Rollback completed"
    else
        log_error "No previous version available for rollback"
        exit 1
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [deploy|rollback|status|logs|stop]"
    echo ""
    echo "Commands:"
    echo "  deploy   - Deploy the application"
    echo "  rollback - Rollback to previous version"
    echo "  status   - Show deployment status"
    echo "  logs     - Show application logs"
    echo "  stop     - Stop the application"
    echo ""
}

# Handle command line arguments
case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    status)
        show_status
        ;;
    logs)
        docker logs -f $CONTAINER_NAME
        ;;
    stop)
        stop_container
        log_info "Application stopped"
        ;;
    *)
        usage
        exit 1
        ;;
esac
