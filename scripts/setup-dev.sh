#!/bin/bash
# Development setup script for Django SSLCOMMERZ package
# Usage: ./scripts/setup-dev.sh

set -e

# Colors for output
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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in virtual environment
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Not running in a virtual environment"
        print_status "Creating virtual environment..."
        python3 -m venv .venv
        source .venv/bin/activate
        print_success "Virtual environment created and activated"
    else
        print_success "Running in virtual environment: $VIRTUAL_ENV"
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."

    # Upgrade pip
    pip install --upgrade pip

    # Install core dependencies
    pip install -r requirements.txt

    # Install development dependencies
    pip install -e .[dev]

    # Install additional development tools
    pip install pre-commit

    print_success "Dependencies installed"
}

# Setup pre-commit hooks
setup_pre_commit() {
    print_status "Setting up pre-commit hooks..."

    # Install pre-commit hooks
    pre-commit install

    print_success "Pre-commit hooks installed"
}

# Create environment file
create_env_file() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please update .env file with your SSLCOMMERZ credentials"
    else
        print_status ".env file already exists"
    fi
}

# Run initial tests
run_initial_tests() {
    print_status "Running initial tests..."

    # Run code quality checks
    flake8 sslcommerz/ --count --exit-zero --max-complexity=10 --max-line-length=127

    # Run basic tests
    python -m pytest tests.py -v --tb=short

    print_success "Initial tests completed"
}

# Setup database for testing
setup_test_db() {
    print_status "Setting up test database..."

    cd test_project
    python manage.py migrate
    cd ..

    print_success "Test database setup completed"
}

# Main setup function
main() {
    print_status "Setting up development environment for Django SSLCOMMERZ..."

    check_venv
    install_dependencies
    setup_pre_commit
    create_env_file
    setup_test_db
    run_initial_tests

    print_success "Development environment setup completed!"

    echo ""
    print_status "Next steps:"
    echo "1. Update .env file with your SSLCOMMERZ credentials"
    echo "2. Run tests: python -m pytest tests.py"
    echo "3. Test management command: cd test_project && python manage.py test_sslcommerz"
    echo "4. Start developing!"
}

main "$@"
