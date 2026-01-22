# Agent Prompts for AOS

This directory contains specialized agent prompts/personas for working with the Agent Operating System (AOS) codebase. These prompts define expert roles that AI coding agents can adopt to provide focused assistance.

## Available Agent Prompts

### 1. [Python Expert](python-expert.md)
**Specialization**: Python development for AOS

**Expertise**:
- Python 3.8+ features and async/await programming
- Perpetual agent implementation patterns
- PurposeDrivenAgent and ContextMCPServer usage
- Testing with pytest-asyncio
- Azure SDK integration

**Use for**:
- Writing new Python code
- Refactoring existing code
- Implementing agent logic
- Code quality improvements
- Python-specific debugging

### 2. [Azure & Cloud Expert](azure-expert.md)
**Specialization**: Azure infrastructure and deployment

**Expertise**:
- Azure Functions deployment and configuration
- Azure Service Bus integration
- Azure Storage services (Blob, Table, Queue)
- Application Insights monitoring
- Serverless architecture patterns

**Use for**:
- Azure Functions configuration
- Cloud deployment issues
- Service Bus integration
- Storage configuration
- Monitoring and troubleshooting
- Security and cost optimization

### 3. [Testing Expert](testing-expert.md)
**Specialization**: Testing and quality assurance

**Expertise**:
- pytest and pytest-asyncio
- Async testing patterns
- Mocking Azure services
- Testing perpetual agents
- Integration testing strategies

**Use for**:
- Writing new tests
- Debugging test failures
- Improving test coverage
- Setting up test fixtures
- Testing async code
- Integration testing

## How to Use These Prompts

### For AI Coding Agents
These prompts can be used to provide context to AI coding agents when working on specific types of tasks:

```
# When working on Python code
Use the Python Expert prompt to guide development with AOS-specific patterns

# When configuring Azure
Use the Azure & Cloud Expert prompt for deployment and infrastructure

# When writing tests
Use the Testing Expert prompt for comprehensive test strategies
```

### For Developers
Developers can reference these prompts to understand:
- Best practices for different aspects of AOS
- Common patterns and anti-patterns
- Expert-level guidance on specific topics

## Prompt Structure

Each prompt includes:

1. **Role**: The expert persona and specialization
2. **Expertise Areas**: Specific knowledge domains
3. **Guidelines**: Principles and best practices
4. **Common Tasks**: Frequently performed operations with examples
5. **Best Practices**: Checklists and recommendations
6. **Common Mistakes**: What to avoid
7. **Resources**: Links to relevant documentation

## When to Use Which Prompt

| Task | Recommended Prompt |
|------|-------------------|
| Implementing new agent | Python Expert |
| Writing async functions | Python Expert |
| Configuring Azure Functions | Azure & Cloud Expert |
| Setting up Service Bus | Azure & Cloud Expert |
| Writing tests | Testing Expert |
| Debugging test failures | Testing Expert |
| Deployment issues | Azure & Cloud Expert |
| Code quality improvements | Python Expert |
| Performance optimization | Azure & Cloud Expert |
| Mocking strategies | Testing Expert |

## Combining Prompts

For complex tasks, you may need to combine expertise from multiple prompts:

**Example: Deploying a new agent**
1. Python Expert: Implement the agent code
2. Testing Expert: Write comprehensive tests
3. Azure & Cloud Expert: Deploy to Azure Functions

**Example: Troubleshooting production issue**
1. Azure & Cloud Expert: Check Azure monitoring
2. Python Expert: Review code for issues
3. Testing Expert: Add regression tests

## Integration with Skills

These prompts complement the skills in `.github/skills/`:

- **Prompts**: Define expert personas and general guidance
- **Skills**: Provide detailed, procedural knowledge for specific tasks

**Recommended workflow**:
1. Choose appropriate prompt based on task type
2. Reference relevant skill for detailed procedures
3. Apply prompt guidelines to skill patterns

## Contributing

When adding new prompts:

1. Focus on a specific expertise area
2. Include practical examples from AOS
3. Reference related skills and documentation
4. Follow the established prompt structure
5. Update this README

## Related Resources

- **Skills**: [.github/skills/](../skills/)
- **Instructions**: [.github/instructions/Readme.md](../instructions/Readme.md)
- **Main README**: [README.md](../../README.md)
- **Architecture**: [ARCHITECTURE.md](../../ARCHITECTURE.md)

---

> **Note**: These prompts are specifically designed for the Agent Operating System codebase and incorporate AOS-specific patterns, architecture, and best practices.
