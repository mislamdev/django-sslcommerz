# Documentation CI/CD Guide

This guide explains how the automated documentation generation and deployment works for the Django SSLCOMMERZ package.

## Overview

The project uses Sphinx for documentation generation and GitHub Actions for automated deployment to GitHub Pages. Documentation is automatically built and deployed whenever changes are pushed to the main branch.

## Documentation Structure

```
docs/
├── conf.py                 # Sphinx configuration
├── requirements.txt        # Documentation dependencies
├── index.md               # Documentation homepage
├── installation.md        # Installation guide
├── quickstart.md          # Quick start guide
├── configuration.md       # Configuration reference
├── api_reference.md       # API documentation
├── examples.md            # Usage examples
├── contributing.md        # Contribution guide
├── deployment.md          # Deployment guide
├── changelog.md           # Changelog
└── _static/              # Static assets (CSS, images)
```

## Automated Workflows

### 1. Documentation Deployment Workflow

**File:** `.github/workflows/docs-deploy.yml`

**Triggers:**
- Push to `main` or `master` branch
- Changes to `docs/**` or `sslcommerz/**` files
- Manual trigger via workflow_dispatch

**Process:**
1. Checks out the repository
2. Sets up Python 3.10
3. Installs project and documentation dependencies
4. Builds documentation with Sphinx
5. Deploys to GitHub Pages
6. Uploads documentation artifacts

**Configuration:**
```yaml
on:
  push:
    branches: [ main, master ]
    paths:
      - 'docs/**'
      - 'sslcommerz/**'
```

### 2. CI/CD Pipeline Documentation Job

**File:** `.github/workflows/ci-cd.yml`

The main CI/CD pipeline includes a documentation build job that:
- Validates documentation can be built without errors
- Ensures all dependencies are correctly specified
- Deploys to GitHub Pages on successful main branch builds

## Local Development

### Building Documentation Locally

#### Option 1: Using the build script
```bash
# Build documentation
./scripts/build-docs.sh build

# Serve documentation locally
./scripts/build-docs.sh serve

# Clean build artifacts
./scripts/build-docs.sh clean

# Generate API documentation
./scripts/build-docs.sh api

# Run all checks
./scripts/build-docs.sh all
```

#### Option 2: Using the deployment script
```bash
# Build only
./scripts/build-and-deploy-docs.sh

# Build and deploy to GitHub Pages
./scripts/build-and-deploy-docs.sh --deploy

# Build, deploy, and open in browser
./scripts/build-and-deploy-docs.sh --deploy --open
```

#### Option 3: Manual build
```bash
# Install dependencies
pip install -r docs/requirements.txt

# Build documentation
cd docs
sphinx-build -b html . _build/html

# Serve locally
cd _build/html
python -m http.server 8080
```

### Live Reload Development

For live documentation editing with auto-reload:

```bash
pip install sphinx-autobuild
cd docs
sphinx-autobuild . _build/html --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` to see live updates as you edit.

## GitHub Pages Setup

### Initial Setup

1. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages`
   - Folder: `/ (root)`

2. **Configure Custom Domain (Optional):**
   ```bash
   echo "yourdomain.com" > docs/_build/html/CNAME
   ```

3. **Set Repository Secrets:**
   - `GITHUB_TOKEN` is automatically provided
   - No additional secrets needed for basic deployment

### Accessing Documentation

After deployment, documentation will be available at:
- `https://<username>.github.io/django-sslcommerz/`

## Documentation Dependencies

**File:** `docs/requirements.txt`

Core dependencies:
- `sphinx>=6.0.0` - Documentation generator
- `sphinx-rtd-theme>=1.3.0` - Read the Docs theme
- `myst-parser>=2.0.0` - Markdown support for Sphinx
- `sphinx-autodoc-typehints>=1.24.0` - Type hints in documentation
- `sphinx-autobuild>=2021.3.14` - Live reload for development

## Sphinx Configuration

**File:** `docs/conf.py`

Key configurations:

### Extensions
```python
extensions = [
    'sphinx.ext.autodoc',        # Auto-generate docs from docstrings
    'sphinx.ext.napoleon',       # Google/NumPy docstring support
    'sphinx.ext.viewcode',       # Add source code links
    'sphinx.ext.intersphinx',    # Link to other documentation
    'sphinx.ext.githubpages',    # GitHub Pages support
    'myst_parser',               # Markdown support
]
```

### Theme Configuration
```python
html_theme = 'sphinx_rtd_theme'
```

### MyST Parser Settings
Enables enhanced Markdown features:
- Colon fences
- Definition lists
- Math equations
- Task lists
- And more

## Writing Documentation

### Docstring Format

Use Google-style docstrings:

```python
def payment_session(amount, currency="BDT"):
    """
    Initialize a payment session.
    
    Args:
        amount (float): Payment amount
        currency (str): Currency code. Defaults to "BDT".
    
    Returns:
        dict: Payment session details with gateway URL
        
    Raises:
        ValueError: If amount is invalid
        
    Example:
        >>> session = payment_session(1000.00)
        >>> print(session['GatewayPageURL'])
    """
    pass
```

### Markdown Files

Use MyST-enhanced Markdown for documentation pages:

```markdown
# Page Title

## Section

Regular markdown content with enhancements:

:::{note}
This is a note admonition
:::

:::{warning}
This is a warning
:::

`inline-code` and code blocks:

\`\`\`python
# Python code example
client = SSLCommerzClient()
\`\`\`
```

## Troubleshooting

### Build Failures

**Issue:** Sphinx build fails with import errors
```bash
# Solution: Ensure all dependencies are installed
pip install -r requirements.txt
pip install -r docs/requirements.txt
```

**Issue:** Module not found during build
```bash
# Solution: Check sys.path in docs/conf.py
sys.path.insert(0, os.path.abspath('..'))
```

**Issue:** Theme not found
```bash
# Solution: Install the theme
pip install sphinx-rtd-theme
```

### Deployment Issues

**Issue:** GitHub Pages shows 404
- Check that `gh-pages` branch exists
- Ensure `.nojekyll` file is present
- Verify GitHub Pages is enabled in repository settings

**Issue:** Old version still showing
- GitHub Pages can cache for up to 10 minutes
- Force refresh with Ctrl+F5 (or Cmd+Shift+R on Mac)
- Check that the workflow completed successfully

**Issue:** Workflow fails with permission error
- Ensure GitHub Actions has write permissions
- Go to Settings → Actions → General → Workflow permissions
- Select "Read and write permissions"

## CI/CD Workflow Status

Check workflow status at:
- `https://github.com/<username>/django-sslcommerz/actions`

### Workflow Badges

Add badges to README.md:

```markdown
![Documentation](https://github.com/<username>/django-sslcommerz/workflows/Documentation%20Deployment/badge.svg)
```

## Best Practices

1. **Write Clear Docstrings:**
   - Use Google or NumPy style consistently
   - Include examples where helpful
   - Document all parameters and return values

2. **Update Documentation with Code:**
   - Update docs when changing APIs
   - Add examples for new features
   - Keep changelog current

3. **Test Locally Before Pushing:**
   - Build documentation locally
   - Check for warnings and errors
   - Verify all links work

4. **Use Semantic Versioning:**
   - Update version in `docs/conf.py`
   - Keep in sync with package version

5. **Review Generated Documentation:**
   - Check auto-generated API docs
   - Ensure formatting is correct
   - Verify code examples render properly

## Advanced Features

### Auto-generating API Documentation

```bash
sphinx-apidoc -o docs/api sslcommerz --force
```

### Building Other Formats

```bash
# PDF (requires LaTeX)
cd docs
sphinx-build -b latex . _build/latex
cd _build/latex && make

# EPUB
sphinx-build -b epub . _build/epub

# Man pages
sphinx-build -b man . _build/man
```

### Custom CSS

Add custom styles in `docs/_static/custom.css`:

```css
.rst-content code {
    color: #e74c3c;
}
```

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
- [MyST Parser Guide](https://myst-parser.readthedocs.io/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

## Support

For issues with documentation:
1. Check the troubleshooting section above
2. Review workflow logs in GitHub Actions
3. Open an issue on GitHub with the `documentation` label

