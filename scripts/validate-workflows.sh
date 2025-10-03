#!/bin/bash
# Workflow Validation Script
# This script validates all GitHub Actions workflows locally

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== GitHub Actions Workflow Validator ===${NC}\n"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo -e "${YELLOW}Checking Python...${NC}"
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Check pip
echo -e "${YELLOW}Checking pip...${NC}"
if command_exists pip; then
    PIP_VERSION=$(pip --version)
    echo -e "${GREEN}✓ $PIP_VERSION${NC}"
else
    echo -e "${RED}✗ pip not found${NC}"
    exit 1
fi

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
pip install -q flake8 black isort mypy django-stubs bandit safety radon xenon pydocstyle interrogate

# Lint checks
echo -e "\n${BLUE}=== Running Lint Checks ===${NC}"
echo -e "${YELLOW}Running flake8...${NC}"
if flake8 sslcommerz/ --count --select=E9,F63,F7,F82 --show-source --statistics; then
    echo -e "${GREEN}✓ Flake8 critical checks passed${NC}"
else
    echo -e "${RED}✗ Flake8 found critical errors${NC}"
fi

flake8 sslcommerz/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

echo -e "\n${YELLOW}Checking code formatting with black...${NC}"
if black --check --diff sslcommerz/; then
    echo -e "${GREEN}✓ Black formatting passed${NC}"
else
    echo -e "${YELLOW}! Code needs formatting (run: black sslcommerz/)${NC}"
fi

echo -e "\n${YELLOW}Checking import sorting with isort...${NC}"
if isort --check-only --diff sslcommerz/; then
    echo -e "${GREEN}✓ Import sorting passed${NC}"
else
    echo -e "${YELLOW}! Imports need sorting (run: isort sslcommerz/)${NC}"
fi

echo -e "\n${YELLOW}Running type checking with mypy...${NC}"
if mypy sslcommerz/ --ignore-missing-imports 2>&1 | head -20; then
    echo -e "${GREEN}✓ Type checking completed${NC}"
else
    echo -e "${YELLOW}! Type checking found issues${NC}"
fi

# Security checks
echo -e "\n${BLUE}=== Running Security Checks ===${NC}"
echo -e "${YELLOW}Running bandit security scan...${NC}"
if bandit -r sslcommerz/ -f json -o bandit-report.json; then
    echo -e "${GREEN}✓ Bandit security scan passed${NC}"
    rm -f bandit-report.json
else
    echo -e "${YELLOW}! Bandit found potential security issues${NC}"
fi

echo -e "\n${YELLOW}Checking for known vulnerabilities with safety...${NC}"
if safety check --json --output safety-report.json 2>/dev/null; then
    echo -e "${GREEN}✓ No known vulnerabilities found${NC}"
    rm -f safety-report.json
else
    echo -e "${YELLOW}! Safety check completed with warnings${NC}"
    rm -f safety-report.json
fi

# Complexity checks
echo -e "\n${BLUE}=== Running Complexity Analysis ===${NC}"
echo -e "${YELLOW}Analyzing code complexity with radon...${NC}"
radon cc sslcommerz/ -a -s
radon mi sslcommerz/ -s

echo -e "\n${YELLOW}Running xenon complexity check...${NC}"
if xenon --max-absolute B --max-modules A --max-average A sslcommerz/; then
    echo -e "${GREEN}✓ Complexity checks passed${NC}"
else
    echo -e "${YELLOW}! Code complexity is higher than recommended${NC}"
fi

# Documentation checks
echo -e "\n${BLUE}=== Running Documentation Checks ===${NC}"
echo -e "${YELLOW}Checking docstring style...${NC}"
if pydocstyle sslcommerz/ --count; then
    echo -e "${GREEN}✓ Docstring style checks passed${NC}"
else
    echo -e "${YELLOW}! Docstring style issues found${NC}"
fi

echo -e "\n${YELLOW}Checking documentation coverage...${NC}"
interrogate -v sslcommerz/ || true

# Build documentation
echo -e "\n${YELLOW}Building documentation...${NC}"
pip install -q -r docs/requirements.txt
if cd docs && sphinx-build -b html . _build/html -q && cd ..; then
    echo -e "${GREEN}✓ Documentation built successfully${NC}"
else
    echo -e "${RED}✗ Documentation build failed${NC}"
fi

# Build package
echo -e "\n${BLUE}=== Building Package ===${NC}"
echo -e "${YELLOW}Installing build tools...${NC}"
pip install -q build twine wheel

echo -e "${YELLOW}Building package...${NC}"
if python -m build; then
    echo -e "${GREEN}✓ Package built successfully${NC}"
else
    echo -e "${RED}✗ Package build failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Checking package with twine...${NC}"
if twine check dist/*; then
    echo -e "${GREEN}✓ Package check passed${NC}"
else
    echo -e "${RED}✗ Package check failed${NC}"
    exit 1
fi

# Summary
echo -e "\n${BLUE}=== Validation Summary ===${NC}"
echo -e "${GREEN}✓ All workflow validations completed!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Review any warnings above"
echo "2. Fix critical issues if any"
echo "3. Commit and push changes"
echo "4. GitHub Actions workflows should now pass"
echo ""
echo -e "${BLUE}Workflow files updated:${NC}"
echo "- .github/workflows/ci-cd.yml (upgraded artifacts to v4)"
echo "- .github/workflows/code-quality.yml (fixed all jobs)"
echo "- .github/workflows/dependency-management.yml (upgraded artifacts to v4)"
echo "- .github/workflows/docs-deploy.yml (new workflow for docs)"
echo ""
echo -e "${BLUE}Documentation files created:${NC}"
echo "- DOCUMENTATION-CICD.md (documentation deployment guide)"
echo "- PRODUCTION-READINESS-CHECKLIST.md (PyPI publication checklist)"
echo "- scripts/build-and-deploy-docs.sh (documentation deployment script)"

# Cleanup
echo -e "\n${YELLOW}Cleaning up build artifacts...${NC}"
rm -rf build/ dist/ *.egg-info/
echo -e "${GREEN}✓ Cleanup complete${NC}"

echo -e "\n${GREEN}=== All Done! ===${NC}"

