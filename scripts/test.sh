#!/bin/bash
# Comprehensive testing script for Django SSLCOMMERZ package
# Usage: ./scripts/test.sh [test_type]

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

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    python -m pytest tests.py -v --cov=sslcommerz --cov-report=html --cov-report=xml
    print_success "Unit tests completed"
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."

    # Set test environment variables
    export SSLCOMMERZ_STORE_ID="test_store"
    export SSLCOMMERZ_STORE_PASSWORD="test_password"
    export SSLCOMMERZ_IS_SANDBOX="true"

    # Test Django management command
    cd test_project && python manage.py test_sslcommerz && cd ..

    print_success "Integration tests completed"
}

# Function to run code quality checks
run_quality_checks() {
    print_status "Running code quality checks..."

    # Linting with flake8
    flake8 sslcommerz/ --count --statistics

    # Code formatting check
    black --check sslcommerz/

    # Import sorting check
    isort --check-only sslcommerz/

    # Type checking
    mypy sslcommerz/ --ignore-missing-imports

    print_success "Code quality checks completed"
}

# Function to run security tests
run_security_tests() {
    print_status "Running security tests..."

    # Security analysis with bandit
    bandit -r sslcommerz/ -f json -o bandit-report.json

    # Safety check for dependencies
    safety check --json --output safety-report.json

    print_success "Security tests completed"
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."

    # Simple performance test for configuration loading
    python -c "
import time
from sslcommerz.config import get_config

start_time = time.time()
for _ in range(1000):
    config = get_config()
end_time = time.time()

print(f'Configuration loading: {(end_time - start_time) * 1000:.2f}ms for 1000 iterations')
"

    print_success "Performance tests completed"
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."

    run_quality_checks
    run_unit_tests
    run_integration_tests
    run_security_tests
    run_performance_tests

    print_success "All tests completed successfully!"
}

# Function to generate test report
generate_report() {
    print_status "Generating test report..."

    cat > test-report.md << EOF
# Test Report

Generated on: $(date)

## Test Results

### Unit Tests
- Coverage report: htmlcov/index.html
- XML report: coverage.xml

### Code Quality
- Linting: Passed
- Formatting: Passed
- Type checking: Passed

### Security
- Bandit report: bandit-report.json
- Safety report: safety-report.json

### Performance
- Configuration loading: Optimized

## Next Steps
1. Review coverage report
2. Address any security findings
3. Optimize performance bottlenecks
EOF

    print_success "Test report generated: test-report.md"
}

# Main function
main() {
    local test_type=${1:-"all"}

    print_status "Django SSLCOMMERZ Testing Suite"
    print_status "Test type: $test_type"

    case $test_type in
        "unit")
            run_unit_tests
            ;;
        "integration")
            run_integration_tests
            ;;
        "quality")
            run_quality_checks
            ;;
        "security")
            run_security_tests
            ;;
        "performance")
            run_performance_tests
            ;;
        "all")
            run_all_tests
            generate_report
            ;;
        *)
            echo "Usage: $0 [unit|integration|quality|security|performance|all]"
            echo ""
            echo "Test types:"
            echo "  unit         Run unit tests only"
            echo "  integration  Run integration tests only"
            echo "  quality      Run code quality checks only"
            echo "  security     Run security tests only"
            echo "  performance  Run performance tests only"
            echo "  all          Run all tests (default)"
            exit 1
            ;;
    esac
}

main "$@"
