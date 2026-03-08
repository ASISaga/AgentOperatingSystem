# Specs Synchronization — PR Tracking Document

**Created**: 2026-03-08  
**Status**: Pending  
**Scope**: `.github/specs/repository.md` corrections for 6 repositories

## Summary

All shared spec files (`agent-intelligence-framework.md`, `agents.md`, `enterprise-capabilities.md`, `instructions.md`, `prompts.md`, `skills.md`, `spec-driven-development.md`, `workflows.md`, `README.md`) are **already in sync** across all 16 repositories in the ASISaga organization — every repo carries the same file with the identical SHA checksum.

The only discrepancy is in `.github/specs/repository.md`. Six repositories contain the **wrong** `repository.md` — they all carry the `BusinessInfinity` spec (`SHA: a4aa2be7ae3caf206d21e8473e28c9c1065adae9`) instead of their own repo-specific content:

| Repository | Current `repository.md` content | Expected content |
|-----------|----------------------------------|-----------------|
| `leadership-agent` | BusinessInfinity spec (wrong) | `leadership-agent` spec |
| `ceo-agent` | BusinessInfinity spec (wrong) | `ceo-agent` spec |
| `cfo-agent` | BusinessInfinity spec (wrong) | `cfo-agent` spec |
| `cto-agent` | BusinessInfinity spec (wrong) | `cto-agent` spec |
| `cso-agent` | BusinessInfinity spec (wrong) | `cso-agent` spec |
| `cmo-agent` | BusinessInfinity spec (wrong) | `cmo-agent` spec |

## Repositories That Are Correct (No PR Needed)

| Repository | `repository.md` SHA | Status |
|-----------|-------------------|--------|
| `agent-operating-system` | `70966472c54c85deebdc9af05a6c0822919ecada` | ✅ Correct |
| `purpose-driven-agent` | `b7244d7bc585282cb0dc1d04a73770cb9dd0fc87` | ✅ Correct |
| `aos-kernel` | `181c13a84f8fecbd4530868f737d1e711dadf811` | ✅ Correct |
| `aos-intelligence` | `b8db024687357bb58ef605aa08e56938e2a45e15` | ✅ Correct |
| `aos-infrastructure` | `2dc84e6136d77c8c6e7b23c1783a929478197f6b` | ✅ Correct |
| `aos-dispatcher` | `0caf0f27ccf76e6b534549504c5781767fbd05af` | ✅ Correct |
| `aos-client-sdk` | `3bcf4a1362e5090a3fe8a110c7c8dadcd7a78a25` | ✅ Correct |
| `realm-of-agents` | `e3f9a71a995b8b113cd8025489e5346f4d8b6f81` | ✅ Correct |
| `mcp` | `f8e5306907f48f957c0f852dc7e535010e47d241` | ✅ Correct |
| `business-infinity` | `a4aa2be7ae3caf206d21e8473e28c9c1065adae9` | ✅ Correct |

## Required PRs

### 1. `ASISaga/leadership-agent`

**PR Title**: `docs: fix repository.md — replace BusinessInfinity spec with correct leadership-agent spec`

**PR Description**:

> The `.github/specs/repository.md` currently contains the `BusinessInfinity` repository specification, which was incorrectly deployed to this repository.
>
> This PR replaces it with the correct `leadership-agent` repository specification describing:
> - `LeadershipAgent` — the second level of the AOS agent inheritance hierarchy
> - Generic boardroom orchestration tools (`enroll_specialist_tools`, `get_specialist_tools`, `get_orchestration_instructions`)
> - Library-only nature (not deployed; consumed by C-suite agent repos)
> - Testing workflow and related repositories

**File to replace**: `.github/specs/repository.md`  
**New content**: See [`docs/specs-sync/leadership-agent-repository.md`](leadership-agent-repository.md) in this meta-repo

---

### 2. `ASISaga/ceo-agent`

**PR Title**: `docs: fix repository.md — replace BusinessInfinity spec with correct ceo-agent spec`

**PR Description**:

> The `.github/specs/repository.md` currently contains the `BusinessInfinity` repository specification, which was incorrectly deployed to this repository.
>
> This PR replaces it with the correct `ceo-agent` repository specification describing:
> - `CEOAgent` — the Chief Executive Officer agent extending `LeadershipAgent`
> - Boardroom orchestration coordinator role (`enroll_boardroom_tools`, `get_boardroom_tools`, `get_boardroom_instructions`)
> - Deployed as Azure Functions app registered with Foundry Agent Service
> - Testing workflow and related repositories

**File to replace**: `.github/specs/repository.md`  
**New content**: See [`docs/specs-sync/ceo-agent-repository.md`](ceo-agent-repository.md) in this meta-repo

---

### 3. `ASISaga/cfo-agent`

**PR Title**: `docs: fix repository.md — replace BusinessInfinity spec with correct cfo-agent spec`

**PR Description**:

> The `.github/specs/repository.md` currently contains the `BusinessInfinity` repository specification, which was incorrectly deployed to this repository.
>
> This PR replaces it with the correct `cfo-agent` repository specification describing:
> - `CFOAgent` — the Chief Financial Officer agent extending `LeadershipAgent`
> - Finance domain boardroom specialist using the `finance` LoRA adapter
> - Deployed as Azure Functions app registered with Foundry Agent Service
> - Testing workflow and related repositories

**File to replace**: `.github/specs/repository.md`  
**New content**: See [`docs/specs-sync/cfo-agent-repository.md`](cfo-agent-repository.md) in this meta-repo

---

### 4. `ASISaga/cto-agent`

**PR Title**: `docs: fix repository.md — replace BusinessInfinity spec with correct cto-agent spec`

**PR Description**:

> The `.github/specs/repository.md` currently contains the `BusinessInfinity` repository specification, which was incorrectly deployed to this repository.
>
> This PR replaces it with the correct `cto-agent` repository specification describing:
> - `CTOAgent` — the Chief Technology Officer agent extending `LeadershipAgent`
> - Technology domain boardroom specialist using the `technology` LoRA adapter
> - Deployed as Azure Functions app registered with Foundry Agent Service
> - Testing workflow and related repositories

**File to replace**: `.github/specs/repository.md`  
**New content**: See [`docs/specs-sync/cto-agent-repository.md`](cto-agent-repository.md) in this meta-repo

---

### 5. `ASISaga/cso-agent`

**PR Title**: `docs: fix repository.md — replace BusinessInfinity spec with correct cso-agent spec`

**PR Description**:

> The `.github/specs/repository.md` currently contains the `BusinessInfinity` repository specification, which was incorrectly deployed to this repository.
>
> This PR replaces it with the correct `cso-agent` repository specification describing:
> - `CSOAgent` — the Chief Security Officer agent extending `LeadershipAgent`
> - Security domain boardroom specialist using the `security` LoRA adapter
> - Deployed as Azure Functions app registered with Foundry Agent Service
> - Testing workflow and related repositories

**File to replace**: `.github/specs/repository.md`  
**New content**: See [`docs/specs-sync/cso-agent-repository.md`](cso-agent-repository.md) in this meta-repo

---

### 6. `ASISaga/cmo-agent`

**PR Title**: `docs: fix repository.md — replace BusinessInfinity spec with correct cmo-agent spec`

**PR Description**:

> The `.github/specs/repository.md` currently contains the `BusinessInfinity` repository specification, which was incorrectly deployed to this repository.
>
> This PR replaces it with the correct `cmo-agent` repository specification describing:
> - `CMOAgent` — the Chief Marketing Officer agent extending `LeadershipAgent`
> - Marketing domain boardroom specialist using the `marketing` LoRA adapter
> - Deployed as Azure Functions app registered with Foundry Agent Service
> - Testing workflow and related repositories

**File to replace**: `.github/specs/repository.md`  
**New content**: See [`docs/specs-sync/cmo-agent-repository.md`](cmo-agent-repository.md) in this meta-repo

---

## How to Apply

For each repository above:

1. Open the target repository on GitHub
2. Navigate to `.github/specs/repository.md`
3. Click **Edit** (pencil icon)
4. Replace the entire file content with the content from the corresponding file in `docs/specs-sync/` in this meta-repo
5. Use the PR title and description provided above
6. Create a PR and request review from repository maintainers

## Verification

After each PR is merged, verify the fix by checking the SHA of the updated `repository.md` is no longer `a4aa2be7ae3caf206d21e8473e28c9c1065adae9` (the BusinessInfinity spec SHA).

## Shared Specs Sync Status

All shared spec files are confirmed **in sync** across all 16 repositories (identical SHA):

| Spec File | SHA | Sync Status |
|-----------|-----|------------|
| `README.md` | `149c6f452a47dfe7633bed63d0dbf6ae98f82da5` | ✅ All repos |
| `agent-intelligence-framework.md` | `301dea14643e0a2fda81329ebe22385c2c4e0f77` | ✅ All repos |
| `agents.md` | `1dd7217e66b8aa09af6845763e46755faaaf821d` | ✅ All repos |
| `enterprise-capabilities.md` | `8c64b957ed190418b437f6defac272a1beb0910e` | ✅ All repos |
| `instructions.md` | `f846a9de3aadbe75cd27e31a017bddc702994578` | ✅ All repos |
| `prompts.md` | `7758d5448fb56e24eeab45a937e1aa305b879a31` | ✅ All repos |
| `skills.md` | `f59d7ef9cfab8b975f10a7fb2aec7fa01d3139a5` | ✅ All repos |
| `spec-driven-development.md` | `6e5325b48b744280ca99980e7fd02067d5db4909` | ✅ All repos |
| `workflows.md` | `476003213a55e7bfaa8c7e5d7b4d20888e55683f` | ✅ All repos |
