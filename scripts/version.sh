#!/bin/bash
# Version management script for Django SSLCOMMERZ package
# Usage: ./scripts/version.sh [bump_type]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get current version
get_current_version() {
    grep "__version__ = " sslcommerz/__init__.py | cut -d'"' -f2
}

# Bump version
bump_version() {
    local bump_type=$1
    local current_version=$(get_current_version)

    print_status "Current version: $current_version"

    # Parse version components
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    major=${VERSION_PARTS[0]}
    minor=${VERSION_PARTS[1]}
    patch=${VERSION_PARTS[2]}

    # Bump based on type
    case $bump_type in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
        *)
            print_error "Invalid bump type. Use: major, minor, or patch"
            exit 1
            ;;
    esac

    local new_version="$major.$minor.$patch"

    # Update files
    sed -i "s/__version__ = .*/__version__ = '$new_version'/" sslcommerz/__init__.py
    sed -i "s/version=.*/version='$new_version',/" setup.py

    print_success "Version bumped to: $new_version"
    echo "$new_version"
}

# Show current version
show_version() {
    local current_version=$(get_current_version)
    echo "Current version: $current_version"
}

# Main function
main() {
    local action=${1:-"show"}

    case $action in
        "show")
            show_version
            ;;
        "major"|"minor"|"patch")
            bump_version "$action"
            ;;
        *)
            echo "Usage: $0 [show|major|minor|patch]"
            echo ""
            echo "Commands:"
            echo "  show   Show current version"
            echo "  major  Bump major version (1.0.0 -> 2.0.0)"
            echo "  minor  Bump minor version (1.0.0 -> 1.1.0)"
            echo "  patch  Bump patch version (1.0.0 -> 1.0.1)"
            exit 1
            ;;
    esac
}

main "$@"
