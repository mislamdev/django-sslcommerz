# CI/CD Auto Deployment Documentation
# Django SSLCOMMERZ Package

## Overview

This document provides comprehensive documentation for the CI/CD pipeline and auto-deployment setup for the Django SSLCOMMERZ package. The CI/CD system is designed to ensure code quality, run comprehensive tests, and automatically deploy to PyPI.

## 🔄 CI/CD Pipeline Architecture

### Pipeline Overview
```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│   Code      │    │    Quality   │    │   Testing   │    │ Deployment   │
│   Commit    │───▶│   Assurance  │───▶│   Suite     │───▶│   Process    │
│             │    │              │    │             │    │              │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
```

### Workflow Triggers
- **Push to main/master/develop**: Full CI/CD pipeline
- **Pull Request**: Quality checks and testing only
- **Release Publication**: Production deployment to PyPI
- **Scheduled**: Weekly dependency updates and security scans

## 📁 File Structure

```
.github/
├── workflows/
│   ├── ci-cd.yml                    # Main CI/CD pipeline
│   ├── release.yml                  # Release management
│   ├── code-quality.yml             # Code quality checks
│   └── dependency-management.yml    # Dependency updates
scripts/
├── deploy.sh                        # Deployment script
├── setup-dev.sh                     # Development setup
├── test.sh                          # Testing script
└── version.sh                       # Version management
.pre-commit-config.yaml              # Pre-commit hooks
```

## 🚀 Getting Started

### 1. Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/django-sslcommerz.git
cd django-sslcommerz

# Run development setup script
./scripts/setup-dev.sh
```

### 2. Running Tests

```bash
# Run all tests
./scripts/test.sh

# Run specific test types
./scripts/test.sh unit           # Unit tests only
./scripts/test.sh integration    # Integration tests only
./scripts/test.sh quality        # Code quality checks
./scripts/test.sh security       # Security tests
```

### 3. Version Management

```bash
# Show current version
./scripts/version.sh show

# Bump version
./scripts/version.sh patch       # 1.0.0 -> 1.0.1
./scripts/version.sh minor       # 1.0.0 -> 1.1.0
./scripts/version.sh major       # 1.0.0 -> 2.0.0
```

### 4. Manual Deployment

```bash
# Deploy to test PyPI
./scripts/deploy.sh test 1.0.0-beta

# Deploy to production PyPI
./scripts/deploy.sh production 1.0.0
```

## 🔧 GitHub Actions Workflows

### Main CI/CD Pipeline (`ci-cd.yml`)

**Triggers:**
- Push to main/master/develop branches
- Pull requests to main/master
- Release publications

**Jobs:**
1. **Quality Assurance**: Linting, formatting, type checking
2. **Testing**: Unit tests, integration tests, coverage
3. **Documentation**: Build and deploy docs
4. **Build**: Package building and validation
5. **Deploy**: Automatic deployment to PyPI
6. **Security**: Vulnerability scanning
7. **Notification**: Status notifications

**Matrix Testing:**
- Python versions: 3.8, 3.9, 3.10, 3.11
- Django versions: 3.2, 4.0, 4.1, 4.2
- Database: PostgreSQL for integration tests

### Release Management (`release.yml`)

**Features:**
- Automated version bumping
- Changelog generation
- GitHub release creation
- Pull request creation for releases
- Post-release task management

**Usage:**
```yaml
# Manual trigger with version type selection
workflow_dispatch:
  inputs:
    version_type: [patch, minor, major]
    prerelease: [true, false]
```

### Code Quality (`code-quality.yml`)

**Checks:**
- **Linting**: flake8 with plugins
- **Formatting**: black code formatter
- **Import Sorting**: isort
- **Type Checking**: mypy with Django stubs
- **Security**: bandit security scanner
- **Documentation**: pydocstyle and interrogate
- **Complexity**: radon and xenon analysis

### Dependency Management (`dependency-management.yml`)

**Features:**
- Weekly dependency updates
- Security vulnerability scanning
- Automated pull requests for updates
- Safety and pip-audit checks

## 🛡️ Security & Quality

### Pre-commit Hooks

Automatically enforced before each commit:
- Code formatting (black)
- Import sorting (isort)
- Linting (flake8)
- Security checks (bandit)
- Type checking (mypy)
- Django checks
- Documentation style (pydocstyle)

### Security Scanning

- **Bandit**: Python security issues
- **Safety**: Known vulnerabilities in dependencies
- **Trivy**: Comprehensive vulnerability scanner
- **CodeQL**: GitHub's semantic code analysis

### Quality Metrics

- **Code Coverage**: Minimum 90% coverage required
- **Complexity**: Maximum complexity B rating
- **Documentation**: 80%+ docstring coverage
- **Type Hints**: Full type annotation

## 📦 Deployment Process

### Automatic Deployment

1. **Test PyPI**: Develops branch pushes
2. **Production PyPI**: Release publications

### Manual Deployment

```bash
# Step 1: Update version
./scripts/version.sh minor

# Step 2: Run tests
./scripts/test.sh

# Step 3: Deploy
./scripts/deploy.sh production $(./scripts/version.sh show)
```

### Deployment Environments

| Environment | Trigger | URL |
|-------------|---------|-----|
| Test PyPI | develop branch | https://test.pypi.org/project/django-sslcommerz/ |
| Production PyPI | release publication | https://pypi.org/project/django-sslcommerz/ |

## 🔐 Secrets Management

### Required GitHub Secrets

```bash
# PyPI deployment
PYPI_API_TOKEN=pypi-xxxxxxxxxxxx
TEST_PYPI_API_TOKEN=pypi-xxxxxxxxxxxx

# Code coverage
CODECOV_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Optional: Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/xxx
```

### Setting Up Secrets

1. Go to repository Settings → Secrets and variables → Actions
2. Add the required secrets
3. Configure environments for production deployment

## 📊 Monitoring & Reporting

### Coverage Reports
- **HTML Report**: `htmlcov/index.html`
- **XML Report**: `coverage.xml`
- **Codecov Integration**: Automatic upload

### Security Reports
- **Bandit**: `bandit-report.json`
- **Safety**: `safety-report.json`
- **Trivy**: SARIF format to GitHub Security

### Quality Reports
- **Complexity**: Radon CC and MI reports
- **Documentation**: Interrogate coverage
- **Type Coverage**: mypy reports

## 🚨 Troubleshooting

### Common Issues

1. **Test Failures**
   ```bash
   # Debug failing tests
   ./scripts/test.sh unit -v -s
   ```

2. **Deployment Failures**
   ```bash
   # Check package build
   python -m build
   twine check dist/*
   ```

3. **Pre-commit Issues**
   ```bash
   # Fix formatting issues
   pre-commit run --all-files
   ```

### Debug Commands

```bash
# Check CI/CD status
gh workflow list
gh run list

# View logs
gh run view [run-id] --log

# Re-run failed jobs
gh run rerun [run-id]
```

## 🔄 Workflow Optimization

### Performance Improvements

1. **Caching**: pip, mypy, and test dependencies
2. **Matrix Optimization**: Exclude incompatible combinations
3. **Parallel Jobs**: Run independent jobs concurrently
4. **Artifact Sharing**: Upload/download build artifacts

### Resource Management

- **Runners**: Ubuntu latest for cost efficiency
- **Timeout**: 30 minutes maximum per job
- **Concurrency**: Cancel previous runs on new pushes

## 📈 Metrics & Analytics

### Key Metrics Tracked

- **Build Success Rate**: Target 95%+
- **Test Coverage**: Target 90%+
- **Security Issues**: Target 0 high/critical
- **Deployment Time**: Target <10 minutes
- **Code Quality Score**: Target A rating

### Monitoring Tools

- **GitHub Actions**: Built-in workflow monitoring
- **Codecov**: Coverage tracking and trends
- **Dependabot**: Dependency security alerts
- **GitHub Security**: Vulnerability alerts

## 🎯 Best Practices

### Development Workflow

1. **Feature Branches**: Always work on feature branches
2. **Pull Requests**: Required for main branch changes
3. **Code Review**: Minimum one approval required
4. **Pre-commit**: Use hooks to catch issues early

### Release Process

1. **Semantic Versioning**: Follow SemVer (MAJOR.MINOR.PATCH)
2. **Changelog**: Maintain detailed changelog
3. **Testing**: Full test suite before release
4. **Documentation**: Update docs with new features

### Security Guidelines

1. **Secrets**: Never commit secrets to repository
2. **Dependencies**: Keep dependencies updated
3. **Scanning**: Regular security scans
4. **Permissions**: Minimal required permissions

## 📞 Support & Maintenance

### Regular Maintenance Tasks

- **Weekly**: Dependency updates review
- **Monthly**: Security scan review
- **Quarterly**: CI/CD optimization review
- **Annually**: Full security audit

### Getting Help

1. **Documentation**: Check this guide first
2. **Issues**: Create GitHub issue for bugs
3. **Discussions**: Use GitHub discussions for questions
4. **Security**: Use security@yourproject.com for security issues

## 🔮 Future Enhancements

### Planned Improvements

1. **Multi-environment Testing**: Add staging environment
2. **Performance Testing**: Automated performance benchmarks
3. **Blue-Green Deployment**: Zero-downtime deployments
4. **Canary Releases**: Gradual rollout mechanism
5. **Integration Testing**: Real SSLCOMMERZ API testing

### Contributing

See the [Contributing Guide](CONTRIBUTING.md) for detailed information on how to contribute to the project and extend the CI/CD pipeline.

---

*This documentation is automatically updated with each release. Last updated: $(date)*
