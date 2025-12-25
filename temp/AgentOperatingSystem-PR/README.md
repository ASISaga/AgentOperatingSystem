# AgentOperatingSystem Refactoring - PR Files

This directory contains all the files needed to create a Pull Request in the AgentOperatingSystem repository.

## What's Inside

This directory contains the complete implementation of the AOS refactoring as specified in `AOS_REFACTORING_SPEC.md`.

### New Files to Add to AOS Repository

```
src/AgentOperatingSystem/
├── agents/
│   ├── base_agent.py          # New: Generic BaseAgent class
│   ├── leadership_agent.py    # New: LeadershipAgent extending BaseAgent
│   └── manager.py             # New: UnifiedAgentManager
├── services/
│   ├── __init__.py            # New: Service module exports
│   └── interfaces.py          # New: Service interfaces (IStorageService, etc.)
├── messaging/
│   ├── envelope.py            # New: MessageEnvelope with correlation
│   └── reliability.py         # New: RetryPolicy and CircuitBreaker
└── monitoring/
    └── observability.py       # New: StructuredLogger and MetricsCollector
```

### Files to Modify in AOS Repository

You'll also need to update these existing files to export the new components:

1. **`src/AgentOperatingSystem/agents/__init__.py`**
   - Add imports for `base_agent`, `leadership_agent`, `manager`
   - Export new classes

2. **`src/AgentOperatingSystem/messaging/__init__.py`**
   - Add imports for `envelope`, `reliability`
   - Export `MessageEnvelope`, `RetryPolicy`, `CircuitBreaker`

3. **`src/AgentOperatingSystem/monitoring/__init__.py`**
   - Add import for `observability`
   - Export `StructuredLogger`, `MetricsCollector`

## How to Use These Files

### Option 1: Manual Copy to AOS Repository

1. Clone the AgentOperatingSystem repository:
   ```bash
   git clone https://github.com/ASISaga/AgentOperatingSystem.git
   cd AgentOperatingSystem
   ```

2. Create a new branch:
   ```bash
   git checkout -b refactor/clean-infrastructure-separation
   ```

3. Copy the files from this directory to the AOS repository:
   ```bash
   # From the BusinessInfinity/tmp/AgentOperatingSystem-PR directory
   cp -r src/AgentOperatingSystem/* <path-to-aos-repo>/src/AgentOperatingSystem/
   ```

4. Update the `__init__.py` files as described in `MODULE_UPDATES.md`

5. Add the `REFACTORING_README.md` to the AOS repository root

6. Commit and push:
   ```bash
   git add .
   git commit -m "Refactor AOS as generic agent infrastructure layer

- Add enhanced BaseAgent and LeadershipAgent classes
- Add UnifiedAgentManager for agent lifecycle management
- Add clean service interfaces (IStorageService, IMessagingService, etc.)
- Add MessageEnvelope with correlation/causation IDs
- Add reliability patterns (RetryPolicy, CircuitBreaker)
- Add observability foundation (StructuredLogger, MetricsCollector)
- Update module exports to include new components

Breaking changes: Yes - New classes alongside existing ones for backward compatibility
Consumer: BusinessInfinity will be updated accordingly

Implements specification from BusinessInfinity/AOS_REFACTORING_SPEC.md"
   
   git push -u origin refactor/clean-infrastructure-separation
   ```

7. Create a Pull Request on GitHub

### Option 2: Create PR Directly on GitHub

1. Go to https://github.com/ASISaga/AgentOperatingSystem
2. Create a new branch via the GitHub UI
3. Upload the files from this directory
4. Update the `__init__.py` files as needed
5. Create the Pull Request

## PR Details

**Title**: Refactor AOS as Generic Agent Infrastructure Layer

**Description**: (Use the content from `REFACTORING_README.md`)

**Labels**: breaking-change, refactoring, enhancement

**Reviewers**: @ASISaga

## Files Summary

- **8 new Python files** implementing all components
- **~18 KB** of new infrastructure code
- **3 module `__init__.py` files** need updates
- **1 README** for documentation

## Testing

After implementing these changes, you should:

1. Run existing AOS tests to ensure backward compatibility
2. Add new tests for the new components (examples in AOS_REFACTORING_SPEC.md)
3. Verify imports work correctly

## Next Steps After PR is Merged

1. Release a new version of AOS (v2.0.0 recommended due to breaking changes)
2. Update BusinessInfinity's `pyproject.toml` to use the new AOS version
3. Follow `MIGRATION_GUIDE.md` in BusinessInfinity repository to refactor BI code

## Support

For questions or issues, refer to:
- `AOS_REFACTORING_SPEC.md` in BusinessInfinity repo - Complete specification
- `MIGRATION_GUIDE.md` in BusinessInfinity repo - Migration instructions
- `REFACTORING_SUMMARY.md` in BusinessInfinity repo - Overall vision

---

**Created**: December 23, 2024
**For**: AgentOperatingSystem refactoring as specified in BusinessInfinity issue
