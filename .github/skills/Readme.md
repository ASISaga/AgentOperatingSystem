# Agent Operating System - Skills Catalog

This directory contains specialized skills for working with the Agent Operating System (AOS) codebase. Each skill is a focused collection of knowledge, patterns, and best practices for specific aspects of AOS development.

## Available Skills

### 1. [Perpetual Agents](perpetual-agents/SKILL.md)
**Expert knowledge for working with Perpetual Agents and PurposeDrivenAgents.**

**Use this skill when**:
- Creating new perpetual agents
- Modifying existing agent behavior
- Understanding agent state management
- Working with ContextMCPServer for state preservation
- Implementing purpose-driven decision making

**Key topics**:
- Perpetual vs task-based architecture
- Agent lifecycle management
- State persistence via ContextMCPServer
- Testing perpetual agents
- Common issues and solutions

### 2. [Azure Functions](azure-functions/SKILL.md)
**Expert knowledge for developing and deploying AOS on Azure Functions.**

**Use this skill when**:
- Deploying AOS to Azure Functions
- Working with function_app.py
- Debugging Azure Functions triggers
- Configuring Service Bus integration
- Testing Functions locally

**Key topics**:
- Azure Functions architecture
- Service Bus triggered functions
- HTTP and timer triggers
- Local development workflow
- Deployment and monitoring

### 3. [Async Python Testing](async-python-testing/SKILL.md)
**Expert knowledge for testing asynchronous Python code in AOS.**

**Use this skill when**:
- Writing tests for async functions
- Mocking async calls and Azure services
- Debugging async test failures
- Testing concurrent operations
- Understanding pytest-asyncio patterns

**Key topics**:
- Async test patterns
- Mocking with AsyncMock
- Testing perpetual agents
- Common async testing issues
- Best practices for async tests

### 4. [AOS Architecture](aos-architecture/SKILL.md)
**Expert knowledge of AOS architecture, components, and design patterns.**

**Use this skill when**:
- Understanding AOS architecture
- Working across multiple components
- Making architectural decisions
- Integrating new components
- Debugging cross-component issues

**Key topics**:
- Operating system paradigm
- Architectural layers (Application, Service, Kernel)
- Component interactions
- Design patterns (Circuit Breaker, State Machine, etc.)
- Data flow and event processing

### 5. [Code Refactoring](code-refactoring/SKILL.md)
**Expert knowledge for performing major version refactoring and removing backward compatibility.**

**Use this skill when**:
- Performing major version bumps
- Removing deprecated code
- Consolidating duplicate implementations
- Updating imports across codebase
- Cleaning up technical debt

**Key topics**:
- Backward compatibility removal
- Import migration strategies
- Class consolidation
- Documentation updates
- Testing refactored code

### 6. [Code Quality with Pylint](code-quality-pylint/SKILL.md)
**Expert knowledge for maintaining code quality using Pylint and best practices.**

**Use this skill when**:
- Running Pylint checks on code
- Fixing Pylint warnings and errors
- Ensuring code quality before commits
- Reviewing code quality in CI/CD
- Refactoring code to meet quality standards

**Key topics**:
- Pylint configuration and usage
- Common Pylint issues and fixes
- Type hints and async patterns
- Code quality best practices
- Integration with GitHub Copilot
- CI/CD quality checks

## How to Use Skills

Skills are designed to be discovered and used by AI coding agents. Each skill follows the Agent Skills format with a `SKILL.md` file containing:

1. **Description**: What the skill provides
2. **When to Use**: Specific scenarios where the skill applies
3. **Key Concepts**: Core knowledge and principles
4. **Code Patterns**: Reusable code examples
5. **Common Issues**: Problems and solutions
6. **Best Practices**: Recommended approaches
7. **File Locations**: Where to find relevant code
8. **Related Skills**: Connected skills for broader context

## Quick Reference

**For new contributors**:
- Start with [AOS Architecture](aos-architecture/SKILL.md) to understand the system
- Review [Perpetual Agents](perpetual-agents/SKILL.md) for agent concepts
- Check [Async Python Testing](async-python-testing/SKILL.md) for testing patterns

**For Azure deployment**:
- Use [Azure Functions](azure-functions/SKILL.md) for deployment guidance

**For testing**:
- Use [Async Python Testing](async-python-testing/SKILL.md) for all async test scenarios

**For code quality**:
- Use [Code Quality with Pylint](code-quality-pylint/SKILL.md) for maintaining code standards
- Review before committing and in code reviews

**For agent development**:
- Use [Perpetual Agents](perpetual-agents/SKILL.md) for agent implementation
- Reference [AOS Architecture](aos-architecture/SKILL.md) for system integration

## Skill Format

All skills in this repository follow the Agent Skills specification. Each skill is self-contained and includes:

- **SKILL.md**: Main skill content
- Clear descriptions and examples
- Contextual guidance on when to use the skill
- References to related code and documentation

## Contributing New Skills

When adding new skills:

1. Create a new directory in `.github/skills/`
2. Add a `SKILL.md` file following the existing pattern
3. Include practical examples from the AOS codebase
4. Link to related skills and documentation
5. Update this README with the new skill

## Additional Resources

- **Repository Instructions**: [.github/instructions/Readme.md](../instructions/Readme.md)
- **Main README**: [README.md](../../README.md)
- **Architecture**: [ARCHITECTURE.md](../../docs/architecture/ARCHITECTURE.md)
- **Contributing**: [CONTRIBUTING.md](../../docs/development/CONTRIBUTING.md)

---

> **Note**: These skills are specifically designed for the Agent Operating System codebase. They complement the general Agent Skills format with repository-specific knowledge and patterns.