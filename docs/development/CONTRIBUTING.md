# Contributing to Agent Operating System (AOS)

Thank you for your interest in contributing to the Agent Operating System! This document provides guidelines and information for contributors.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Contribution Types](#contribution-types)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

---

## 📜 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct:

### Our Pledge

- **Be Respectful** - Value each other's ideas, styles, and viewpoints
- **Be Collaborative** - Work together to resolve conflicts
- **Be Inclusive** - Welcome newcomers and encourage diverse perspectives
- **Be Professional** - Keep discussions focused and constructive

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling, insulting, or derogatory comments
- Public or private harassment
- Publishing others' private information without permission

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Azure account (for testing cloud features)
- Familiarity with async Python programming

### Quick Start

```bash
# 1. Fork the repository on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/AgentOperatingSystem.git
cd AgentOperatingSystem

# 3. Add upstream remote
git remote add upstream https://github.com/ASISaga/AgentOperatingSystem.git

# 4. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -e ".[full]"
pip install -r requirements-dev.txt  # Development dependencies

# 6. Run tests to verify setup
pytest tests/
```

---

## 💻 Development Setup

### Recommended Tools

- **IDE**: VS Code, PyCharm, or similar
- **Python**: 3.8, 3.9, 3.10, 3.11 (test on multiple versions)
- **Linters**: ruff, black, mypy
- **Testing**: pytest, pytest-asyncio

### VS Code Configuration

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

### Environment Variables

Create a `.env` file for local development:

```bash
# Azure Configuration (use test environment)
AOS_SUBSCRIPTION_ID=your-test-subscription-id
AOS_RESOURCE_GROUP=aos-dev
AOS_LOCATION=westus2

# Development Settings
AOS_LOG_LEVEL=DEBUG
AOS_ENABLE_TRACING=true
AOS_ENV=development
```

---

## 🤝 How to Contribute

### Ways to Contribute

1. **🐛 Report Bugs** - Found a bug? Open an issue
2. **💡 Suggest Features** - Have an idea? We'd love to hear it
3. **📖 Improve Documentation** - Docs can always be better
4. **🔧 Fix Issues** - Check out issues labeled `good first issue`
5. **✨ Add Features** - Implement new capabilities
6. **🧪 Write Tests** - Help improve code coverage
7. **🎨 Create Examples** - Show how to use AOS

### Finding Work

- **Good First Issues**: [Issues labeled `good first issue`](https://github.com/ASISaga/AgentOperatingSystem/labels/good%20first%20issue)
- **Help Wanted**: [Issues labeled `help wanted`](https://github.com/ASISaga/AgentOperatingSystem/labels/help%20wanted)
- **Documentation**: [Issues labeled `documentation`](https://github.com/ASISaga/AgentOperatingSystem/labels/documentation)

---

## 📝 Contribution Types

### Bug Fixes

1. Check if bug is already reported
2. If not, create detailed bug report
3. Reference issue in your PR
4. Include test that reproduces bug
5. Fix the bug
6. Verify test now passes

### New Features

1. Open feature request issue first
2. Discuss design and approach
3. Get approval from maintainers
4. Implement feature with tests
5. Update documentation
6. Submit PR for review

### Documentation

1. Identify documentation gap
2. Write clear, concise content
3. Include code examples
4. Test all code examples
5. Submit PR

---

## 🔄 Development Workflow

### 1. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/amazing-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code following our [Code Standards](#code-standards)
- Add/update tests
- Update documentation
- Run linters and tests locally

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add amazing feature"

# See Commit Messages section for conventions
```

### 4. Push and Create PR

```bash
# Push to your fork
git push origin feature/amazing-feature

# Open PR on GitHub
# Fill out PR template completely
```

---

## 📐 Code Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 100 characters (not 79)
- **Imports**: Use absolute imports, grouped and sorted
- **Formatting**: Use `black` formatter
- **Type Hints**: Required for all public APIs
- **Docstrings**: Google style docstrings

### Example Code

```python
"""Module docstring describing purpose."""

from typing import Dict, List, Optional
import asyncio

from AgentOperatingSystem.storage import UnifiedStorageManager


class MyAgent:
    """Single-line class docstring.
    
    Longer description if needed.
    
    Attributes:
        name: Agent name
        config: Configuration dictionary
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """Initialize agent.
        
        Args:
            name: Agent identifier
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
    
    async def process(self, data: Dict) -> List[str]:
        """Process data and return results.
        
        Args:
            data: Input data dictionary
            
        Returns:
            List of processed results
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Implementation
        return []
```

### Code Quality Tools

```bash
# Format code
black src/ tests/

# Check style
ruff src/ tests/

# Type checking
mypy src/ tests/

# Run all checks
make lint  # or: pre-commit run --all-files
```

---

## 🧪 Testing Requirements

### Test Coverage

- **Minimum Coverage**: 80% for new code
- **Critical Paths**: 100% coverage required
- **Integration Tests**: Required for new features
- **Documentation Tests**: All examples must be tested

### Writing Tests

```python
import pytest
from AgentOperatingSystem.storage import UnifiedStorageManager


class TestStorageManager:
    """Tests for UnifiedStorageManager."""
    
    @pytest.fixture
    async def storage(self):
        """Create storage manager for testing."""
        manager = UnifiedStorageManager()
        yield manager
        # Cleanup if needed
    
    @pytest.mark.asyncio
    async def test_save_and_load(self, storage):
        """Test saving and loading data."""
        # Arrange
        data = {"key": "value"}
        
        # Act
        await storage.save(key="test", value=data, storage_type="blob")
        result = await storage.load(key="test", storage_type="blob")
        
        # Assert
        assert result == data
    
    @pytest.mark.asyncio
    async def test_save_invalid_type_raises_error(self, storage):
        """Test that invalid storage type raises error."""
        with pytest.raises(ValueError, match="Invalid storage type"):
            await storage.save(key="test", value={}, storage_type="invalid")
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_storage.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_storage.py::TestStorageManager::test_save_and_load

# Run integration tests only
pytest -m integration

# Run fast tests only (skip integration)
pytest -m "not integration"
```

---

## 📚 Documentation

### Documentation Requirements

- **Code**: All public APIs must have docstrings
- **Tests**: Complex test logic should have comments
- **Features**: New features need documentation updates
- **Examples**: Include runnable code examples
- **Specifications**: Update relevant specification docs

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """Short one-line description.
    
    Longer description with more details about what the function does.
    Can span multiple lines.
    
    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to 0.
    
    Returns:
        True if successful, False otherwise.
        
    Raises:
        ValueError: If param1 is empty
        TypeError: If param2 is not an integer
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

### Documentation Structure

```
docs/
├── README.md                    # Documentation index
├── quickstart.md               # Getting started guide
├── architecture.md             # System architecture
├── development.md              # Development guide
├── configuration.md            # Configuration reference
├── specifications/             # Technical specifications
│   ├── README.md              # Specifications index
│   ├── auth.md                # Authentication spec
│   ├── storage.md             # Storage spec
│   └── ...
└── examples/                   # Code examples
    ├── basic_agent.py
    └── ...
```

---

## 🚀 Deployment

### Deployment Documentation

For comprehensive deployment guidance, see:

- **[DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md)** - Complete deployment strategy, procedures, and architecture
- **[DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md)** - Detailed task checklists for all deployment phases
- **[deployment/README.md](../../deployment/README.md)** - Deployment infrastructure overview
- **[deployment/ORCHESTRATOR_USER_GUIDE.md](../../deployment/ORCHESTRATOR_USER_GUIDE.md)** - Python orchestrator usage guide
- **[deployment/QUICKSTART.md](../../deployment/QUICKSTART.md)** - Quick deployment reference

### Deployment Workflow

```bash
# 1. Prepare environment
cd deployment

# 2. Review and customize parameters
vim parameters/dev.bicepparam

# 3. Deploy with orchestrator (recommended)
python3 deploy.py \
  -g "rg-aos-dev" \
  -l "eastus" \
  -t "main-modular.bicep" \
  -p "parameters/dev.bicepparam"

# 4. Verify deployment
az resource list --resource-group "rg-aos-dev" --output table
```

### Deployment Best Practices

- **Always test in dev first**: dev → staging → production
- **Use the Python orchestrator**: Provides quality gates, health checks, and audit trail
- **Review what-if output**: Understand changes before deploying
- **Document deployments**: Use Git SHA tracking and audit logs
- **Follow the task checklists**: See [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md)

---

## 💬 Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **perf**: Performance improvements
- **test**: Adding/updating tests
- **chore**: Maintenance tasks
- **ci**: CI/CD changes

### Examples

```bash
# Feature
git commit -m "feat(storage): add support for Cosmos DB backend"

# Bug fix
git commit -m "fix(auth): resolve token expiration issue"

# Documentation
git commit -m "docs(api): add examples for ML pipeline usage"

# With body and footer
git commit -m "feat(mcp): add GitHub MCP integration

Add support for GitHub MCP server integration including
tool discovery and execution.

Closes #123"
```

### Scope Guidelines

- `storage` - Storage system changes
- `auth` - Authentication/authorization
- `messaging` - Messaging infrastructure
- `ml` - ML pipeline
- `mcp` - MCP integration
- `orchestration` - Orchestration engine
- `governance` - Governance system
- `reliability` - Reliability patterns
- `observability` - Monitoring/tracing
- `docs` - Documentation
- `tests` - Test changes

---

## 🔀 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Breaking change

## Testing
Describe testing done

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests
- [ ] All tests pass
```

### Review Process

1. **Automated Checks**: CI/CD runs tests and linters
2. **Code Review**: At least one maintainer reviews
3. **Feedback**: Address review comments
4. **Approval**: Maintainer approves PR
5. **Merge**: Maintainer merges when ready

### PR Guidelines

- **Keep PRs Small**: < 400 lines changed ideal
- **One Feature Per PR**: Don't mix multiple features
- **Clear Description**: Explain what and why
- **Link Issues**: Reference related issues
- **Respond Promptly**: Address feedback quickly

---

## 👥 Community

### Communication Channels

- **GitHub Discussions**: [Ask questions, share ideas](https://github.com/ASISaga/AgentOperatingSystem/discussions)
- **GitHub Issues**: [Report bugs, request features](https://github.com/ASISaga/AgentOperatingSystem/issues)
- **Pull Requests**: [Contribute code](https://github.com/ASISaga/AgentOperatingSystem/pulls)

### Getting Help

- Check existing documentation
- Search GitHub issues
- Ask in GitHub Discussions
- Tag issues with `question` label

### Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project README

---

## 🏆 Becoming a Maintainer

Active, high-quality contributors may be invited to become maintainers. Maintainers:

- Review and merge PRs
- Triage issues
- Guide project direction
- Mentor new contributors

Interested? Demonstrate consistent, quality contributions and express interest to current maintainers.

---

## 📄 License

By contributing to AOS, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](LICENSE) file).

---

## ❓ Questions?

If you have questions about contributing:
- Open a [GitHub Discussion](https://github.com/ASISaga/AgentOperatingSystem/discussions)
- Reach out to maintainers
- Check our [FAQ](docs/FAQ.md)

---

**Thank you for contributing to Agent Operating System!** 🎉

*Together, we're building the foundation for intelligent automation.*
