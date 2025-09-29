#!/bin/bash
# Deployment script for Django SSLCOMMERZ package
# Usage: ./scripts/deploy.sh [environment] [version]

set -e  # Exit on any error

# Configuration
PACKAGE_NAME="django-sslcommerz"
REPO_URL="https://github.com/your-username/django-sslcommerz.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate environment
validate_environment() {
    local env=$1
    if [[ ! "$env" =~ ^(test|staging|production)$ ]]; then
        print_error "Invalid environment. Use: test, staging, or production"
        exit 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi

    # Check pip
    if ! command_exists pip; then
        print_error "pip is required but not installed"
        exit 1
    fi

    # Check git
    if ! command_exists git; then
        print_error "git is required but not installed"
        exit 1
    fi

    # Check twine for PyPI deployment
    if ! pip show twine >/dev/null 2>&1; then
        print_warning "twine not found, installing..."
        pip install twine
    fi

    print_success "Prerequisites check completed"
}

# Function to setup virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."

    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    fi

    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -e .[dev]

    print_success "Virtual environment setup completed"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."

    # Activate virtual environment
    source venv/bin/activate

    # Run linting
    print_status "Running code quality checks..."
    flake8 sslcommerz/
    black --check sslcommerz/
    isort --check-only sslcommerz/

    # Run tests
    print_status "Running unit tests..."
    python -m pytest tests.py -v --cov=sslcommerz --cov-report=html

    # Run management command test
    print_status "Testing management commands..."
    export SSLCOMMERZ_STORE_ID="test_store"
    export SSLCOMMERZ_STORE_PASSWORD="test_password"
    export SSLCOMMERZ_IS_SANDBOX="true"

    cd test_project && python manage.py test_sslcommerz && cd ..

    print_success "All tests passed"
}

# Function to build package
build_package() {
    print_status "Building package..."

    # Clean previous builds
    rm -rf build/ dist/ *.egg-info/

    # Activate virtual environment
    source venv/bin/activate

    # Build package
    python -m build

    # Check package
    twine check dist/*

    print_success "Package built successfully"
}

# Function to deploy to PyPI
deploy_to_pypi() {
    local environment=$1
    local version=$2

    print_status "Deploying to PyPI ($environment)..."

    # Activate virtual environment
    source venv/bin/activate

    case $environment in
        "test")
            print_status "Deploying to Test PyPI..."
            twine upload --repository testpypi dist/* --verbose
            print_success "Deployed to Test PyPI: https://test.pypi.org/project/$PACKAGE_NAME/"
            ;;
        "production")
            print_status "Deploying to Production PyPI..."
            read -p "Are you sure you want to deploy to production PyPI? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                twine upload dist/* --verbose
                print_success "Deployed to Production PyPI: https://pypi.org/project/$PACKAGE_NAME/"
            else
                print_warning "Deployment cancelled"
                exit 0
            fi
            ;;
        *)
            print_error "Invalid deployment environment"
            exit 1
            ;;
    esac
}

# Function to create release tag
create_release_tag() {
    local version=$1

    print_status "Creating release tag v$version..."

    # Check if tag already exists
    if git tag -l | grep -q "v$version"; then
        print_warning "Tag v$version already exists"
        return
    fi

    # Create and push tag
    git tag -a "v$version" -m "Release version $version"
    git push origin "v$version"

    print_success "Release tag v$version created and pushed"
}

# Function to update version
update_version() {
    local new_version=$1

    print_status "Updating version to $new_version..."

    # Update version in __init__.py
    sed -i "s/__version__ = .*/__version__ = '$new_version'/" sslcommerz/__init__.py

    # Update version in setup.py
    sed -i "s/version=.*/version='$new_version',/" setup.py

    print_success "Version updated to $new_version"
}

# Function to validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_error "Invalid version format. Use semantic versioning (e.g., 1.0.0)"
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [ENVIRONMENT] [VERSION]"
    echo ""
    echo "ENVIRONMENT:"
    echo "  test        Deploy to Test PyPI"
    echo "  production  Deploy to Production PyPI"
    echo ""
    echo "VERSION:"
    echo "  Semantic version (e.g., 1.0.0)"
    echo ""
    echo "Examples:"
    echo "  $0 test 1.0.0-beta"
    echo "  $0 production 1.0.0"
}

# Main deployment function
main() {
    local environment=${1:-}
    local version=${2:-}

    # Show usage if no arguments
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi

    # Validate inputs
    validate_environment "$environment"

    if [ -n "$version" ]; then
        validate_version "$version"
    fi

    print_status "Starting deployment process..."
    print_status "Environment: $environment"
    print_status "Version: ${version:-'current'}"

    # Run deployment steps
    check_prerequisites
    setup_venv

    # Update version if provided
    if [ -n "$version" ]; then
        update_version "$version"
    fi

    run_tests
    build_package
    deploy_to_pypi "$environment" "$version"

    # Create release tag for production deployments
    if [ "$environment" = "production" ] && [ -n "$version" ]; then
        create_release_tag "$version"
    fi

    print_success "Deployment completed successfully!"

    # Show next steps
    echo ""
    print_status "Next steps:"
    echo "1. Verify the package on PyPI"
    echo "2. Test installation: pip install $PACKAGE_NAME"
    echo "3. Update documentation if needed"
    echo "4. Announce the release"
}

# Run main function with all arguments
main "$@"
