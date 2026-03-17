# Tasks: Merge Parent Directories into Submodules

## Task 1: Copy kernel source code (src/ → aos-kernel)
- **Status**: Pending
- **Description**: Copy all parent-only .py files from kernel modules to aos-kernel/src/AgentOperatingSystem/
- **Expected Outcome**: All implementation files exist in aos-kernel
- **Dependencies**: None

## Task 2: Copy config files
- **Status**: Pending
- **Description**: Copy consolidated_config.json → aos-kernel, self_learning_config.json → aos-intelligence, example_app_registry.json → aos-client-sdk
- **Dependencies**: None

## Task 3: Copy data files (data/ → aos-intelligence)
- **Status**: Pending
- **Description**: Copy all 7 JSON knowledge/learning data files to aos-intelligence/data/
- **Dependencies**: None

## Task 4: Distribute docs
- **Status**: Pending
- **Description**: Copy/move doc files to appropriate submodule docs/ directories
- **Dependencies**: None

## Task 5: Distribute tests
- **Status**: Pending
- **Description**: Copy test files to appropriate submodule tests/ directories
- **Dependencies**: None

## Task 6: Merge unique deployment files
- **Status**: Pending
- **Description**: Copy parent-only deployment files to aos-infrastructure/deployment/
- **Dependencies**: None

## Task 7: Clean up parent directories
- **Status**: Pending
- **Description**: Remove src/, deployment/, config/, data/, docs/, tests/ from parent
- **Dependencies**: Tasks 1-6

## Task 8: Validate
- **Status**: Pending
- **Description**: Run git status, verify no data loss, test imports
- **Dependencies**: Task 7
