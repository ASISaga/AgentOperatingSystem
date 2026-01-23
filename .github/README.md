# Copilot Agent Onboarding for AOS

Welcome to the Agent Operating System (AOS) repository! This directory contains comprehensive onboarding materials to help AI coding agents work efficiently with this codebase.

## 📚 Directory Structure

```
.github/
├── README.md                    # This file - main onboarding entry point
├── instructions/                # General repository instructions
│   └── Readme.md               # Comprehensive onboarding guide
├── skills/                      # Specialized skills for specific tasks
│   ├── perpetual-agents/       # Working with perpetual agents
│   ├── azure-functions/        # Azure Functions deployment
│   ├── async-python-testing/   # Testing async Python code
│   ├── aos-architecture/       # Understanding AOS architecture
│   └── Readme.md               # Skills catalog
└── prompts/                     # Expert agent personas
    ├── python-expert.md        # Python development expertise
    ├── azure-expert.md         # Azure/cloud expertise
    ├── testing-expert.md       # Testing expertise
    └── README.md               # Prompts catalog
```

## 🚀 Quick Start

### First Time Here?
1. Read [instructions/Readme.md](instructions/Readme.md) - Complete onboarding guide
2. Review [skills/aos-architecture/SKILL.md](skills/aos-architecture/SKILL.md) - Understand the system
3. Check [skills/perpetual-agents/SKILL.md](skills/perpetual-agents/SKILL.md) - Learn about agents

### Working on Code?
1. Use [prompts/python-expert.md](prompts/python-expert.md) for Python development
2. Reference [skills/perpetual-agents/SKILL.md](skills/perpetual-agents/SKILL.md) for agent patterns
3. See [skills/async-python-testing/SKILL.md](skills/async-python-testing/SKILL.md) for testing

### Deploying to Azure?
1. Use [prompts/azure-expert.md](prompts/azure-expert.md) for deployment guidance
2. Reference [skills/azure-functions/SKILL.md](skills/azure-functions/SKILL.md) for details

### Writing Tests?
1. Use [prompts/testing-expert.md](prompts/testing-expert.md) for testing strategy
2. Reference [skills/async-python-testing/SKILL.md](skills/async-python-testing/SKILL.md) for patterns

## 🎯 What is AOS?

**Agent Operating System (AOS)** is a production-ready operating system for AI agents built on Microsoft Azure. The key architectural difference is **PERSISTENCE**:

- **Traditional frameworks**: Temporary sessions that start, execute, and terminate
- **AOS**: Perpetual agents that register once and run indefinitely

This fundamental difference makes AOS a true "operating system" - agents are like daemon processes, not short-lived scripts.

## 📖 Resources by Topic

### Understanding AOS
- **Architecture**: [skills/aos-architecture/SKILL.md](skills/aos-architecture/SKILL.md)
- **Main README**: [../README.md](../README.md)
- **Architecture Doc**: [../docs/architecture/ARCHITECTURE.md](../docs/architecture/ARCHITECTURE.md)

### Agent Development
- **Perpetual Agents**: [skills/perpetual-agents/SKILL.md](skills/perpetual-agents/SKILL.md)
- **Python Guide**: [prompts/python-expert.md](prompts/python-expert.md)
- **Examples**: [../examples/](../examples/)

### Testing
- **Testing Guide**: [skills/async-python-testing/SKILL.md](skills/async-python-testing/SKILL.md)
- **Testing Expert**: [prompts/testing-expert.md](prompts/testing-expert.md)
- **Test Files**: [../tests/](../tests/)

### Azure & Deployment
- **Azure Functions**: [skills/azure-functions/SKILL.md](skills/azure-functions/SKILL.md)
- **Azure Expert**: [prompts/azure-expert.md](prompts/azure-expert.md)
- **Function App**: [../function_app.py](../function_app.py)

### Contributing
- **Contributing Guide**: [../docs/development/CONTRIBUTING.md](../docs/development/CONTRIBUTING.md)
- **Development Docs**: [../docs/development.md](../docs/development.md)

## 🔑 Key Concepts Quick Reference

### Perpetual vs Task-Based
```python
# Task-Based (Traditional)
agent = create_agent()
result = agent.run(task)
# Agent terminates, state lost

# Perpetual (AOS)
agent = LeadershipAgent(...)  # Or GenericPurposeDrivenAgent
await agent.initialize()  # ContextMCPServer created
manager.register_agent(agent)
# Agent runs forever, state persists via ContextMCPServer
```

### Core Technologies
- **Language**: Python 3.8+
- **Platform**: Microsoft Azure (Functions, Service Bus, Storage)
- **Framework**: Microsoft Agent Framework
- **Async**: asyncio for concurrent operations
- **Testing**: pytest with pytest-asyncio

### File Locations
- **Source Code**: `src/AgentOperatingSystem/`
- **Tests**: `tests/`
- **Examples**: `examples/`
- **Docs**: `docs/`
- **Azure Functions**: `function_app.py`
- **Configuration**: `pyproject.toml`, `host.json`

## 🛠️ Common Tasks

### Run Tests
```bash
pytest tests/
```

### Install Dependencies
```bash
pip install -e ".[full]"
```

### Run Azure Functions Locally
```bash
func start
```

### Deploy to Azure
```bash
func azure functionapp publish <function-app-name>
```

## 📋 Task-Based Navigation

| I want to... | Go to... |
|-------------|----------|
| Understand the architecture | [aos-architecture skill](skills/aos-architecture/SKILL.md) |
| Create a new agent | [perpetual-agents skill](skills/perpetual-agents/SKILL.md) |
| Write tests | [async-python-testing skill](skills/async-python-testing/SKILL.md) |
| Deploy to Azure | [azure-functions skill](skills/azure-functions/SKILL.md) |
| Get Python help | [python-expert prompt](prompts/python-expert.md) |
| Get Azure help | [azure-expert prompt](prompts/azure-expert.md) |
| Get testing help | [testing-expert prompt](prompts/testing-expert.md) |
| Understand perpetual agents | [perpetual-agents skill](skills/perpetual-agents/SKILL.md) |
| Learn the codebase | [instructions/Readme.md](instructions/Readme.md) |

## 🎓 Learning Path

### For New Contributors
1. **Day 1**: Read [instructions/Readme.md](instructions/Readme.md)
2. **Day 2**: Study [skills/aos-architecture/SKILL.md](skills/aos-architecture/SKILL.md)
3. **Day 3**: Review [skills/perpetual-agents/SKILL.md](skills/perpetual-agents/SKILL.md)
4. **Day 4**: Explore [examples/](../examples/)
5. **Day 5**: Run tests and make a small change

### For Bug Fixes
1. Write a failing test
2. Fix the code (use [prompts/python-expert.md](prompts/python-expert.md))
3. Verify the test passes
4. Run full test suite

### For New Features
1. Understand architecture ([skills/aos-architecture/SKILL.md](skills/aos-architecture/SKILL.md))
2. Design feature (follow patterns in [skills/perpetual-agents/SKILL.md](skills/perpetual-agents/SKILL.md))
3. Implement code (use [prompts/python-expert.md](prompts/python-expert.md))
4. Write tests (use [skills/async-python-testing/SKILL.md](skills/async-python-testing/SKILL.md))
5. Update documentation

## 💡 How to Use These Materials

### Instructions
**Purpose**: General guidance on working with the repository
**When to use**: First time setup, understanding the codebase
**Location**: [instructions/](instructions/)

### Skills
**Purpose**: Detailed, procedural knowledge for specific tasks
**When to use**: Performing specific operations (creating agents, testing, deploying)
**Location**: [skills/](skills/)

### Prompts
**Purpose**: Expert personas for focused assistance
**When to use**: Getting specialized guidance (Python, Azure, Testing)
**Location**: [prompts/](prompts/)

### Example Workflow
1. **Start**: Read relevant instruction guide
2. **Learn**: Study applicable skill
3. **Execute**: Apply skill patterns with prompt guidance
4. **Validate**: Test using testing skill
5. **Deploy**: Use Azure skill if needed

## ⚠️ Important Reminders

### Always Remember
- **Agents are perpetual**: Design for long-running operation, not one-off tasks
- **State persists**: Use ContextMCPServer for all agent state
- **Async everywhere**: Almost all code is async, use `await`
- **Test thoroughly**: Write async tests with proper cleanup
- **Mock Azure**: Don't rely on real Azure services in unit tests
- **Clean resources**: Always cleanup in tests and agents

### Common Pitfalls
- Forgetting to `await` async functions
- Not using ContextMCPServer for state
- Blocking I/O in async functions
- Not cleaning up test resources
- Using MagicMock instead of AsyncMock
- Hardcoding Azure credentials

## 🔗 External Resources

- **Microsoft Agent Framework**: https://github.com/microsoft/agent-framework
- **Azure Functions Python**: https://learn.microsoft.com/azure/azure-functions/functions-reference-python
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **Azure SDK for Python**: https://learn.microsoft.com/python/azure/
- **MCP Protocol**: https://modelcontextprotocol.io/

## 📞 Getting Help

1. **Documentation**: Start with files in this directory
2. **Examples**: Check [examples/](../examples/) for working code
3. **Tests**: Look at [tests/](../tests/) for usage patterns
4. **Issues**: Check GitHub issues for similar problems
5. **Contributing**: See [CONTRIBUTING.md](../docs/development/CONTRIBUTING.md) for guidelines

## ✅ Pre-Commit Checklist

Before committing code:
- [ ] Tests pass: `pytest tests/`
- [ ] Pylint checks pass: `pylint src/AgentOperatingSystem --fail-under=5.0`
- [ ] Code quality score maintained or improved
- [ ] Code follows patterns in relevant skill
- [ ] Async/await used correctly
- [ ] State uses ContextMCPServer
- [ ] Resources cleaned up properly
- [ ] No hardcoded secrets
- [ ] Documentation updated if needed
- [ ] Followed guidance from relevant prompt

## 🎉 You're Ready!

You now have access to:
- **Comprehensive instructions** for understanding the codebase
- **Specialized skills** for specific tasks
- **Expert prompts** for focused guidance

Start with [instructions/Readme.md](instructions/Readme.md) and refer back to this guide as needed.

---

**Remember**: AOS is an operating system for AI agents, not a framework. Think in terms of persistent processes, event-driven architecture, and long-running state.
