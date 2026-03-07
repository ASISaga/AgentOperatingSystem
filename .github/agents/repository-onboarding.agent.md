---
name: repository-onboarding
description: "Onboard new repositories with GitHub Copilot agent intelligence"
prompt: |
  Bootstrap complete agent intelligence system in new repository:
  1. Create .github/ structure (agents/, prompts/, skills/, instructions/, specs/, docs/)
  2. Generate copilot-instructions.md
  3. Set up path-specific instruction files per .github/specs/instructions.md
  4. Create agents per .github/specs/agents.md
  5. Create prompts per .github/specs/prompts.md
  6. Create skills per .github/specs/skills.md
  7. Configure validation scripts

  Use templates from .github/specs/agent-intelligence-framework.md and the four dedicated spec files:
  - .github/specs/agents.md - Agent file format and conventions
  - .github/specs/prompts.md - Prompt file format and conventions
  - .github/specs/skills.md - Skill file format and conventions
  - .github/specs/instructions.md - Instruction file format and conventions
tools: ['*']
---
