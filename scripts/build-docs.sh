#!/bin/bash
# Documentation build and deployment script
# Usage: ./scripts/build-docs.sh [build|serve|deploy|clean]

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

# Function to install documentation dependencies
install_docs_deps() {
    print_status "Installing documentation dependencies..."

    pip install -q \
        sphinx \
        sphinx-rtd-theme \
        myst-parser \
        sphinxcontrib-httpdomain \
        sphinx-autodoc-typehints

    print_success "Documentation dependencies installed"
}

# Function to build documentation
build_docs() {
    print_status "Building documentation..."

    cd docs

    # Clean previous build
    rm -rf _build/

    # Build HTML documentation
    sphinx-build -b html . _build/html -W --keep-going

    cd ..

    print_success "Documentation built successfully"
    print_status "Documentation available at: docs/_build/html/index.html"
}

# Function to serve documentation locally
serve_docs() {
    print_status "Serving documentation locally..."

    if [ ! -d "docs/_build/html" ]; then
        print_warning "Documentation not built. Building now..."
        build_docs
    fi

    cd docs/_build/html

    print_success "Documentation server starting at http://localhost:8080"
    print_status "Press Ctrl+C to stop the server"

    python -m http.server 8080
}

# Function to deploy documentation to GitHub Pages
deploy_docs() {
    print_status "Deploying documentation to GitHub Pages..."

    # Check if we're in a git repository
    if [ ! -d ".git" ]; then
        print_error "Not in a git repository"
        exit 1
    fi

    # Check if gh-pages branch exists
    if ! git show-ref --verify --quiet refs/heads/gh-pages; then
        print_status "Creating gh-pages branch..."
        git checkout --orphan gh-pages
        git rm -rf .
        git commit --allow-empty -m "Initial gh-pages commit"
        git checkout main
    fi

    # Build documentation
    build_docs

    # Deploy to gh-pages
    print_status "Deploying to gh-pages branch..."

    # Save current branch
    CURRENT_BRANCH=$(git branch --show-current)

    # Switch to gh-pages and update
    git checkout gh-pages

    # Remove old files (keep .git and other important files)
    find . -maxdepth 1 ! -name '.git' ! -name '.gitignore' ! -name '.' -exec rm -rf {} +

    # Copy new documentation
    cp -r docs/_build/html/* .

    # Create .nojekyll file to bypass Jekyll processing
    touch .nojekyll

    # Commit and push
    git add .
    git commit -m "Update documentation $(date '+%Y-%m-%d %H:%M:%S')" || true
    git push origin gh-pages

    # Switch back to original branch
    git checkout $CURRENT_BRANCH

    print_success "Documentation deployed to GitHub Pages"
    print_status "Available at: https://your-username.github.io/django-sslcommerz/"
}

# Function to clean documentation build
clean_docs() {
    print_status "Cleaning documentation build..."

    rm -rf docs/_build/
    rm -rf docs/_autosummary/

    print_success "Documentation build cleaned"
}

# Function to check documentation for issues
check_docs() {
    print_status "Checking documentation for issues..."

    cd docs

    # Check for broken links (requires sphinx-linkcheck)
    sphinx-build -b linkcheck . _build/linkcheck

    # Check for spelling errors (requires sphinxcontrib-spelling)
    if pip show sphinxcontrib-spelling >/dev/null 2>&1; then
        sphinx-build -b spelling . _build/spelling
    else
        print_warning "sphinxcontrib-spelling not installed, skipping spell check"
    fi

    cd ..

    print_success "Documentation check completed"
}

# Function to generate API documentation
generate_api_docs() {
    print_status "Generating API documentation..."

    cd docs

    # Generate API documentation with sphinx-apidoc
    sphinx-apidoc -o . ../sslcommerz --force --module-first

    cd ..

    print_success "API documentation generated"
}

# Function to show documentation statistics
docs_stats() {
    print_status "Documentation statistics..."

    if [ -d "docs/_build/html" ]; then
        echo "HTML files: $(find docs/_build/html -name "*.html" | wc -l)"
        echo "Total size: $(du -sh docs/_build/html | cut -f1)"
    else
        print_warning "Documentation not built"
    fi

    echo "Source files: $(find docs -name "*.md" -o -name "*.rst" | wc -l)"
    echo "Python files: $(find sslcommerz -name "*.py" | wc -l)"
}

# Main function
main() {
    local action=${1:-"build"}

    print_status "Django SSLCOMMERZ Documentation Builder"
    print_status "Action: $action"

    case $action in
        "build")
            install_docs_deps
            build_docs
            ;;
        "serve")
            install_docs_deps
            serve_docs
            ;;
        "deploy")
            install_docs_deps
            deploy_docs
            ;;
        "clean")
            clean_docs
            ;;
        "check")
            install_docs_deps
            check_docs
            ;;
        "api")
            install_docs_deps
            generate_api_docs
            ;;
        "stats")
            docs_stats
            ;;
        "all")
            install_docs_deps
            clean_docs
            generate_api_docs
            build_docs
            check_docs
            docs_stats
            ;;
        *)
            echo "Usage: $0 [build|serve|deploy|clean|check|api|stats|all]"
            echo ""
            echo "Commands:"
            echo "  build   Build documentation (default)"
            echo "  serve   Serve documentation locally"
            echo "  deploy  Deploy to GitHub Pages"
            echo "  clean   Clean build directory"
            echo "  check   Check for issues"
            echo "  api     Generate API docs"
            echo "  stats   Show statistics"
            echo "  all     Run all commands"
            exit 1
            ;;
    esac
}

main "$@"
