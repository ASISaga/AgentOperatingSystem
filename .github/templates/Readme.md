# Templates

Specification templates for the Spec-Driven Development (SDD) workflow. Used as structural guides by the Spec Manager Agent when creating feature documents.

→ **SDD principles**: `.github/specs/spec-driven-development.md`
→ **Spec manager agent**: `.github/agents/spec-manager.agent.md`

## Available Templates

| Template | Stage | Purpose |
|----------|-------|---------|
| `plan.md` | Plan (Stage 2) | Implementation plan: Phase -1 constitutional gates, technology choices, implementation phases |
| `tasks.md` | Tasks (Stage 3) | Task list: atomic tasks with parallelisation groups and verification steps |
| `research.md` | Plan (Stage 2) | Research document: library options, benchmarks, security considerations |
| `data-model.md` | Plan (Stage 2) | Data model: entity schemas, relationships, validation rules |

## Usage

The Spec Manager Agent uses these templates as structural guides when creating spec documents. Invoke the appropriate workflow:

| To create … | Invoke … |
|-------------|---------|
| Feature spec (`spec.md`) | `spec-create.prompt.md` |
| Implementation plan + supporting docs | `spec-plan.prompt.md` |
| Executable task list | `spec-tasks.prompt.md` |

## Template Design Principles (from SDD)

- **Clarification markers** surface all ambiguities: `[NEEDS CLARIFICATION: <question>]`
- **Constitutional gates** enforce Articles III, VII, VIII, IX before planning
- **Test-first ordering** ensures contracts precede implementation
- **Completeness checklists** act as self-review quality gates
- **Abstraction discipline** keeps spec.md technology-free
