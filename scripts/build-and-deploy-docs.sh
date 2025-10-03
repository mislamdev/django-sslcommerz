#!/bin/bash
# Script to build and optionally deploy documentation
# Usage: ./scripts/build-and-deploy-docs.sh [--deploy]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Django SSLCOMMERZ Documentation Builder ===${NC}"

# Check if we're in the project root
if [ ! -f "setup.py" ]; then
    echo -e "${RED}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q -r docs/requirements.txt

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf docs/_build

# Build documentation
echo -e "${YELLOW}Building documentation...${NC}"
cd docs

if sphinx-build -b html . _build/html -W --keep-going; then
    echo -e "${GREEN}✓ Documentation built successfully!${NC}"
else
    echo -e "${RED}✗ Documentation build failed!${NC}"
    exit 1
fi

cd ..

# Create .nojekyll for GitHub Pages
touch docs/_build/html/.nojekyll

# Check if deployment is requested
if [ "$1" = "--deploy" ]; then
    echo -e "${YELLOW}Deploying to GitHub Pages...${NC}"

    # Check if gh-pages branch exists
    if git show-ref --quiet refs/heads/gh-pages; then
        echo -e "${YELLOW}Updating gh-pages branch...${NC}"
    else
        echo -e "${YELLOW}Creating gh-pages branch...${NC}"
        git checkout --orphan gh-pages
        git reset --hard
        git commit --allow-empty -m "Initialize gh-pages branch"
        git checkout -
    fi

    # Deploy using ghp-import if available
    if command -v ghp-import &> /dev/null; then
        ghp-import -n -p -f docs/_build/html
        echo -e "${GREEN}✓ Documentation deployed to GitHub Pages!${NC}"
    else
        echo -e "${YELLOW}Installing ghp-import...${NC}"
        pip install ghp-import
        ghp-import -n -p -f docs/_build/html
        echo -e "${GREEN}✓ Documentation deployed to GitHub Pages!${NC}"
    fi
else
    echo -e "${GREEN}✓ Documentation ready at: docs/_build/html/index.html${NC}"
    echo -e "${YELLOW}To deploy to GitHub Pages, run: ./scripts/build-and-deploy-docs.sh --deploy${NC}"
fi

# Open documentation in browser (optional)
if [ "$2" = "--open" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open docs/_build/html/index.html
    elif command -v open &> /dev/null; then
        open docs/_build/html/index.html
    fi
fi

echo -e "${GREEN}=== Done! ===${NC}"

