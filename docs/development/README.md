# Development Documentation

This directory contains comprehensive documentation for developers and operators working with the Agent Operating System (AOS).

---

## 📚 Quick Navigation

### For Developers

**Getting Started:**
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - Complete contribution guidelines, code standards, and development workflow
- **[REFACTORING.md](./REFACTORING.md)** - System refactoring documentation and architecture evolution
- **[MIGRATION.md](./MIGRATION.md)** - Migration guide for upgrading between versions

**Repository Architecture:**
- **[REPOSITORY_SPLIT_PLAN.md](./REPOSITORY_SPLIT_PLAN.md)** ⭐ - Detailed plan for splitting into multiple focused repositories

### For DevOps/Operators

**Deployment Documentation:**
- **[DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md)** ⭐ - **Start here!** Comprehensive deployment strategy covering all phases from pre-deployment to production readiness
- **[DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md)** ⭐ - Detailed task checklists for every deployment phase with actionable items

**Infrastructure:**
- **[../../deployment/README.md](../../deployment/README.md)** - Deployment infrastructure overview and quick start
- **[../../deployment/ORCHESTRATOR_USER_GUIDE.md](../../deployment/ORCHESTRATOR_USER_GUIDE.md)** - Python orchestrator usage guide
- **[../../deployment/REGIONAL_REQUIREMENTS.md](../../deployment/REGIONAL_REQUIREMENTS.md)** - Azure region capabilities and requirements
- **[../../deployment/QUICKSTART.md](../../deployment/QUICKSTART.md)** - Fast deployment reference

---

## 📋 Document Purposes

### DEPLOYMENT_PLAN.md
**Purpose:** Complete deployment strategy document  
**Use When:** Planning or executing any deployment (dev, staging, production)  
**Contains:**
- Pre-deployment phase (tools, configuration, authentication)
- Infrastructure deployment phase (orchestrator usage, resource verification)
- Application deployment phase (code deployment, configuration)
- Post-deployment phase (health checks, functional testing)
- Production readiness phase (security hardening, monitoring, DR)
- Rollback procedures
- Deployment architecture diagrams
- Security considerations
- Monitoring and observability setup
- Disaster recovery planning

### DEPLOYMENT_TASKS.md
**Purpose:** Actionable task checklists for deployment execution  
**Use When:** Actually performing a deployment (companion to DEPLOYMENT_PLAN.md)  
**Contains:**
- Pre-deployment tasks (prerequisites, configuration, team communication)
- Infrastructure deployment tasks (validation, resource group, deployment)
- Application deployment tasks (code preparation, secrets, function apps)
- Post-deployment verification tasks (health checks, functional testing)
- Production readiness tasks (security hardening, monitoring, backup)
- Ongoing operations tasks (daily, weekly, monthly, quarterly)
- Environment-specific checklists (dev, staging, prod)
- Emergency rollback checklist

### CONTRIBUTING.md
**Purpose:** Developer contribution guidelines  
**Use When:** Contributing code, documentation, or fixes  
**Contains:**
- Code of conduct
- Development setup
- Code standards (PEP 8, type hints, docstrings)
- Testing requirements
- Commit message conventions
- Pull request process
- Deployment workflow (links to deployment docs)

### REFACTORING.md
**Purpose:** System refactoring history and architecture evolution  
**Use When:** Understanding system architecture changes and migration status  
**Contains:**
- Refactoring overview and completion status
- Changes to base agent classes
- Service interfaces
- Core system components migration
- Import changes for different versions
- Architecture principles
- Usage examples

### MIGRATION.md
**Purpose:** Version upgrade guide  
**Use When:** Upgrading from one version to another  
**Contains:**
- Agent Framework upgrade instructions
- Breaking changes between versions
- Migration steps
- Testing checklist

---

## 🚀 Quick Start Paths

### "I want to deploy AOS for the first time"

1. **Read:** [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) - Understand the complete deployment process
2. **Follow:** [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md) - Use the pre-deployment checklist
3. **Execute:** [../../deployment/QUICKSTART.md](../../deployment/QUICKSTART.md) - Deploy with orchestrator
4. **Verify:** [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md) - Use post-deployment verification checklist

### "I want to deploy to production"

1. **Review:** [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) - Sections on Production Readiness and Security
2. **Checklist:** [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md) - Production Environment Checklist
3. **Test in staging first:** Deploy to staging, validate thoroughly
4. **Follow production checklist:** Complete all production readiness tasks
5. **Execute:** Use Python orchestrator with production parameters
6. **Monitor:** 24-48 hour post-deployment monitoring period

### "I want to contribute code"

1. **Read:** [CONTRIBUTING.md](./CONTRIBUTING.md) - Complete contribution guidelines
2. **Setup:** Follow development setup instructions
3. **Code:** Follow code standards and testing requirements
4. **Submit:** Create PR following guidelines

### "I need to troubleshoot a deployment"

1. **Check:** [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md#rollback-procedures) - Rollback procedures
2. **Review:** Deployment audit logs in `deployment/audit/`
3. **Consult:** [../../deployment/README.md#troubleshooting](../../deployment/README.md#troubleshooting) - Common issues
4. **Emergency:** [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md#emergency-rollback-checklist) - Emergency rollback

### "I need to understand the architecture changes"

1. **Start:** [REFACTORING.md](./REFACTORING.md) - System evolution and architecture
2. **Review:** [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md#deployment-architecture) - Current deployment architecture
3. **Reference:** [../architecture/ARCHITECTURE.md](../architecture/ARCHITECTURE.md) - Detailed architecture docs

---

## 📖 Related Documentation

### Repository-Wide Documentation
- **[Main README](../../README.md)** - Project overview and quick start
- **[Architecture Documentation](../architecture/ARCHITECTURE.md)** - Detailed system architecture
- **[API Reference](../reference/)** - API documentation
- **[Testing Guide](../testing.md)** - Testing infrastructure

### Deployment Infrastructure
- **[deployment/](../../deployment/)** - All deployment infrastructure and templates
- **[deployment/modules/](../../deployment/modules/)** - Bicep modules for Azure resources
- **[deployment/orchestrator/](../../deployment/orchestrator/)** - Python orchestrator implementation
- **[deployment/parameters/](../../deployment/parameters/)** - Environment parameter files

---

## 🎯 Common Scenarios

### Scenario: First Development Deployment

**Goal:** Deploy AOS to Azure for the first time in development environment

**Documents to use:**
1. [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) - Read Pre-Deployment and Infrastructure Deployment phases
2. [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md) - Follow Pre-Deployment Tasks and Infrastructure Deployment Tasks for dev environment
3. [../../deployment/QUICKSTART.md](../../deployment/QUICKSTART.md) - Quick command reference

**Estimated time:** 2-4 hours (first time)

### Scenario: Production Deployment

**Goal:** Deploy AOS to production with full security and monitoring

**Documents to use:**
1. [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md) - All sections, especially Production Readiness Phase
2. [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md) - Production Environment Checklist + Production Readiness Tasks
3. [../../deployment/REGIONAL_REQUIREMENTS.md](../../deployment/REGIONAL_REQUIREMENTS.md) - Ensure Tier 1 region selected

**Estimated time:** 1 day (including security hardening and DR setup)

### Scenario: Code Contribution

**Goal:** Contribute a new feature or bug fix

**Documents to use:**
1. [CONTRIBUTING.md](./CONTRIBUTING.md) - Complete development workflow
2. [REFACTORING.md](./REFACTORING.md) - Understand current architecture
3. [../testing.md](../testing.md) - Testing requirements

**Estimated time:** Varies by contribution

### Scenario: Troubleshooting Failed Deployment

**Goal:** Diagnose and fix deployment issues

**Documents to use:**
1. [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md#rollback-procedures) - Rollback procedures
2. [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md#emergency-rollback-checklist) - Emergency rollback steps
3. [../../deployment/README.md#troubleshooting](../../deployment/README.md#troubleshooting) - Common issues and solutions

**Estimated time:** 30 minutes to 4 hours depending on issue

### Scenario: Ongoing Operations

**Goal:** Maintain deployed AOS infrastructure

**Documents to use:**
1. [DEPLOYMENT_TASKS.md](./DEPLOYMENT_TASKS.md#ongoing-operations-tasks) - Daily, weekly, monthly, quarterly checklists
2. [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md#monitoring-and-observability) - Monitoring setup and queries

**Estimated time:** 
- Daily: 15 minutes
- Weekly: 30 minutes
- Monthly: 1-2 hours
- Quarterly: Half day

---

## 🔄 Document Relationships

```
DEPLOYMENT_PLAN.md (Strategy)
    ↓
    Guides overall deployment approach
    ↓
DEPLOYMENT_TASKS.md (Execution)
    ↓
    Actionable checklists for each phase
    ↓
../../deployment/ (Infrastructure)
    ↓
    Bicep templates, orchestrator, scripts
    ↓
CONTRIBUTING.md (Development)
    ↓
    Code contribution and standards
    ↓
REFACTORING.md (Architecture)
    ↓
    System evolution and design
```

---

## 📞 Getting Help

### For Deployment Issues
1. Check [DEPLOYMENT_PLAN.md](./DEPLOYMENT_PLAN.md#troubleshooting) troubleshooting section
2. Review [../../deployment/README.md](../../deployment/README.md#troubleshooting) common issues
3. Check deployment audit logs in `deployment/audit/`
4. Open GitHub issue with deployment logs

### For Development Issues
1. Check [CONTRIBUTING.md](./CONTRIBUTING.md#getting-help) getting help section
2. Search existing GitHub issues
3. Ask in GitHub Discussions
4. Tag issue with appropriate labels

### For Architecture Questions
1. Review [REFACTORING.md](./REFACTORING.md) for recent changes
2. Check [../architecture/ARCHITECTURE.md](../architecture/ARCHITECTURE.md) for detailed docs
3. Search GitHub Discussions

---

## 📝 Document Maintenance

**Update Frequency:**
- **DEPLOYMENT_PLAN.md**: Quarterly review, update when infrastructure changes
- **DEPLOYMENT_TASKS.md**: Quarterly review, update when processes change
- **CONTRIBUTING.md**: Update when development practices change
- **REFACTORING.md**: Update when major refactoring occurs
- **MIGRATION.md**: Update with each major version release

**Last Updated:** February 13, 2026  
**Next Review:** May 13, 2026  
**Maintained By:** AOS Platform Team

---

## 📊 Documentation Metrics

| Document | Lines | Size | Sections | Checklists |
|----------|-------|------|----------|------------|
| DEPLOYMENT_PLAN.md | ~1200 | ~44KB | 11 | 0 |
| DEPLOYMENT_TASKS.md | ~1400 | ~41KB | 7 | 15+ |
| CONTRIBUTING.md | ~600 | ~16KB | 10 | 0 |
| REFACTORING.md | ~200 | ~7KB | 5 | 0 |
| MIGRATION.md | ~80 | ~2KB | 2 | 1 |

---

**Thank you for contributing to and using the Agent Operating System!** 🎉

*Together, we're building the foundation for intelligent automation.*
