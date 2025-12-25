# Instructions for Creating AgentOperatingSystem Pull Request

## Quick Start

All files needed for the AgentOperatingSystem PR are in this directory.

## What's in This Directory

```
tmp/AgentOperatingSystem-PR/
├── README.md                          # Overview and instructions
├── REFACTORING_README.md              # Detailed implementation guide (add to AOS repo)
├── MODULE_UPDATES.md                  # Required changes to existing __init__.py files
└── src/AgentOperatingSystem/
    ├── agents/
    │   ├── base_agent.py              # New: Generic BaseAgent class
    │   ├── leadership_agent.py        # New: LeadershipAgent
    │   └── manager.py                 # New: UnifiedAgentManager
    ├── services/
    │   ├── __init__.py                # New: Service exports
    │   └── interfaces.py              # New: Service interfaces
    ├── messaging/
    │   ├── envelope.py                # New: MessageEnvelope
    │   └── reliability.py             # New: RetryPolicy, CircuitBreaker
    └── monitoring/
        └── observability.py           # New: StructuredLogger, MetricsCollector
```

**Total**: 11 files (8 new Python files + 3 documentation files)

## How to Create the PR

### Step 1: Clone AgentOperatingSystem Repository

```bash
git clone https://github.com/ASISaga/AgentOperatingSystem.git
cd AgentOperatingSystem
```

### Step 2: Create New Branch

```bash
git checkout -b refactor/clean-infrastructure-separation
```

### Step 3: Copy Files from This Directory

```bash
# Copy all new source files
cp -r /path/to/BusinessInfinity/tmp/AgentOperatingSystem-PR/src/AgentOperatingSystem/* \
      ./src/AgentOperatingSystem/

# Copy the README for documentation
cp /path/to/BusinessInfinity/tmp/AgentOperatingSystem-PR/REFACTORING_README.md \
   ./REFACTORING_README.md
```

### Step 4: Update Existing __init__.py Files

Follow the instructions in `MODULE_UPDATES.md` to update:
- `src/AgentOperatingSystem/agents/__init__.py`
- `src/AgentOperatingSystem/messaging/__init__.py`
- `src/AgentOperatingSystem/monitoring/__init__.py`

### Step 5: Commit Changes

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
- Add REFACTORING_README.md with migration guide

Breaking changes: Yes - New classes alongside existing ones for backward compatibility
Consumer: BusinessInfinity will be updated accordingly

Implements specification from BusinessInfinity/AOS_REFACTORING_SPEC.md"
```

### Step 6: Push to GitHub

```bash
git push -u origin refactor/clean-infrastructure-separation
```

### Step 7: Create Pull Request on GitHub

1. Go to https://github.com/ASISaga/AgentOperatingSystem
2. Click "Pull requests" → "New pull request"
3. Select base: `main` and compare: `refactor/clean-infrastructure-separation`
4. Click "Create pull request"
5. Fill in the PR details:
   - **Title**: "Refactor AOS as Generic Agent Infrastructure Layer"
   - **Description**: Use content from `REFACTORING_README.md`
   - **Labels**: Add `breaking-change`, `refactoring`, `enhancement`
   - **Reviewers**: Add @ASISaga

## Alternative: Manual Upload via GitHub UI

If you prefer to use the GitHub web interface:

1. Go to https://github.com/ASISaga/AgentOperatingSystem
2. Navigate to the directory where files should go
3. Click "Add file" → "Upload files"
4. Upload files from this directory maintaining the structure
5. Create commit and pull request

## Files Summary

### New Python Files (8)
1. `agents/base_agent.py` - 2,674 bytes
2. `agents/leadership_agent.py` - 2,741 bytes
3. `agents/manager.py` - 2,577 bytes
4. `services/__init__.py` - 272 bytes
5. `services/interfaces.py` - 2,251 bytes
6. `messaging/envelope.py` - 2,210 bytes
7. `messaging/reliability.py` - 3,055 bytes
8. `monitoring/observability.py` - 2,193 bytes

**Total new code**: ~18 KB

### Documentation Files (3)
1. `README.md` - Quick start guide
2. `MODULE_UPDATES.md` - __init__.py update instructions
3. `REFACTORING_README.md` - Full implementation guide

### Files to Modify (3)
As detailed in `MODULE_UPDATES.md`:
1. `src/AgentOperatingSystem/agents/__init__.py`
2. `src/AgentOperatingSystem/messaging/__init__.py`
3. `src/AgentOperatingSystem/monitoring/__init__.py`

## After PR is Created

Once the PR is created and reviewed:

1. **Review**: @ASISaga reviews the changes
2. **Merge**: Merge the PR to main branch
3. **Release**: Create a new AOS version (v2.0.0 recommended)
4. **Update BusinessInfinity**: Update BI's dependencies to use new AOS version
5. **Migrate BusinessInfinity**: Follow `MIGRATION_GUIDE.md` to refactor BI code

## Testing

After creating the PR, recommended tests:
- ✅ Verify all imports work
- ✅ Run existing AOS test suite
- ✅ Add tests for new components
- ✅ Check backward compatibility

## Support Files in BusinessInfinity Repo

For reference and migration:
- `AOS_REFACTORING_SPEC.md` - Complete specification
- `MIGRATION_GUIDE.md` - Migration guide for consumers
- `REFACTORING_SUMMARY.md` - Overall vision and roadmap
- `REFACTORING_ANALYSIS.md` - Code classification analysis

## Questions?

Refer to the documentation files or reach out to @ASISaga.

---

**Created**: December 23, 2024
**Purpose**: AgentOperatingSystem refactoring PR
**Issue**: ASISaga/BusinessInfinity - "Refactor BusinessInfinity and AgentOperatingSystem together"
