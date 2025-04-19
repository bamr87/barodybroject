#!/usr/bin/env bash
# scripts/version-manager.sh - A tool to manage Docker image versioning

set -e

# Default values
DOCKER_REPO="amrabdel/barody-python"
VERSION_FILE="VERSION"
CURRENT_VERSION=$(cat $VERSION_FILE 2>/dev/null || echo "0.1.0")

# Display current version
echo "Current version: $CURRENT_VERSION"

# Function to bump version
bump_version() {
    local version_part=$1
    local current=$CURRENT_VERSION
    
    IFS='.' read -r major minor patch <<< "$current"
    
    case $version_part in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Invalid version part. Use 'major', 'minor', or 'patch'"
            exit 1
            ;;
    esac
    
    local new_version="$major.$minor.$patch"
    echo "$new_version" > $VERSION_FILE
    echo "Version bumped to $new_version"
    return 0
}

# Function to build and tag Docker image
build_and_tag() {
    local version=$CURRENT_VERSION
    local date_tag=$(date +'%Y%m%d')
    local git_sha=$(git rev-parse --short HEAD)
    
    echo "Building Docker image with tags:"
    echo "  - $DOCKER_REPO:latest"
    echo "  - $DOCKER_REPO:$version"
    echo "  - $DOCKER_REPO:$version-$date_tag"
    echo "  - $DOCKER_REPO:$version-$git_sha"
    
    docker build -f .devcontainer/Dockerfile_dev \
                 -t $DOCKER_REPO:latest \
                 -t $DOCKER_REPO:$version \
                 -t $DOCKER_REPO:$version-$date_tag \
                 -t $DOCKER_REPO:$version-$git_sha \
                 .
                 
    echo "Docker image built successfully"
}

# Function to push Docker image to registry
push_images() {
    local version=$CURRENT_VERSION
    local date_tag=$(date +'%Y%m%d')
    local git_sha=$(git rev-parse --short HEAD)
    
    echo "Pushing Docker images to registry..."
    
    docker push $DOCKER_REPO:latest
    docker push $DOCKER_REPO:$version
    docker push $DOCKER_REPO:$version-$date_tag
    docker push $DOCKER_REPO:$version-$git_sha
    
    echo "Docker images pushed successfully"
}

# Display help
display_help() {
    echo "Docker Image Version Manager"
    echo ""
    echo "Usage:"
    echo "  $0 [command]"
    echo ""
    echo "Commands:"
    echo "  current               Show current version"
    echo "  bump [major|minor|patch]  Bump version number"
    echo "  build                 Build Docker image with version tags"
    echo "  push                  Push Docker image to registry"
    echo "  all [major|minor|patch]   Bump version, build and push"
    echo "  help                  Show this help message"
    echo ""
}

# Main script logic
case $1 in
    current)
        # Already shown at the beginning
        ;;
    bump)
        bump_version "${2:-patch}"
        ;;
    build)
        build_and_tag
        ;;
    push)
        push_images
        ;;
    all)
        bump_version "${2:-patch}"
        build_and_tag
        push_images
        ;;
    help|*)
        display_help
        ;;
esac

exit 0