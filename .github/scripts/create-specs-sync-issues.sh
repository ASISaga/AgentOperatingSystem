#!/usr/bin/env bash
# create-specs-sync-issues.sh
#
# Creates GitHub Issues in each target repository to request correction of
# .github/specs/repository.md (which currently contains the wrong spec).
#
# Usage:
#   GH_TOKEN=<pat> ./create-specs-sync-issues.sh [repo1,repo2,...]
#
# If no repos argument is given, all 6 affected repos are targeted.
# Requires: gh CLI authenticated via GH_TOKEN.

set -euo pipefail

ORG="ASISaga"
META_REPO_URL="https://github.com/ASISaga/agent-operating-system"
BRANCH="${BRANCH:-main}"
REPOS="${1:-leadership-agent,ceo-agent,cfo-agent,cto-agent,cso-agent,cmo-agent}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SPECS_DIR="$REPO_ROOT/docs/specs-sync"

declare -A SPEC_FILES=(
  ["leadership-agent"]="docs/specs-sync/leadership-agent-repository.md"
  ["ceo-agent"]="docs/specs-sync/ceo-agent-repository.md"
  ["cfo-agent"]="docs/specs-sync/cfo-agent-repository.md"
  ["cto-agent"]="docs/specs-sync/cto-agent-repository.md"
  ["cso-agent"]="docs/specs-sync/cso-agent-repository.md"
  ["cmo-agent"]="docs/specs-sync/cmo-agent-repository.md"
)

declare -A DOMAIN=(
  ["leadership-agent"]="library providing LeadershipAgent — the base class for all C-suite agents"
  ["ceo-agent"]="CEOAgent — Chief Executive Officer, boardroom orchestration coordinator"
  ["cfo-agent"]="CFOAgent — Chief Financial Officer, finance domain boardroom specialist"
  ["cto-agent"]="CTOAgent — Chief Technology Officer, technology domain boardroom specialist"
  ["cso-agent"]="CSOAgent — Chief Security Officer, security domain boardroom specialist"
  ["cmo-agent"]="CMOAgent — Chief Marketing Officer, marketing domain boardroom specialist"
)

IFS=',' read -ra TARGET_REPOS <<< "$REPOS"

for REPO in "${TARGET_REPOS[@]}"; do
  REPO=$(echo "$REPO" | xargs)  # trim whitespace

  SPEC_FILE_REL="${SPEC_FILES[$REPO]:-}"
  if [ -z "$SPEC_FILE_REL" ]; then
    echo "⚠️  Unknown repo: $REPO — skipping"
    continue
  fi

  SPEC_FILE_ABS="$REPO_ROOT/$SPEC_FILE_REL"
  if [ ! -f "$SPEC_FILE_ABS" ]; then
    echo "⚠️  Spec file not found: $SPEC_FILE_ABS — skipping $REPO"
    continue
  fi

  SPEC_CONTENT=$(cat "$SPEC_FILE_ABS")
  DESC="${DOMAIN[$REPO]}"

  ISSUE_TITLE="docs: fix .github/specs/repository.md — replace incorrect BusinessInfinity spec with correct ${REPO} spec"

  BODY_FILE=$(mktemp --tmpdir issue-body-XXXXXX.md)
  trap 'rm -f "$BODY_FILE"' EXIT

  cat > "$BODY_FILE" << BODY_MARKER
## Problem

The \`.github/specs/repository.md\` file in this repository currently contains the **BusinessInfinity** repository specification (\`SHA: a4aa2be7ae3caf206d21e8473e28c9c1065adae9\`). This is incorrect — it was deployed here by mistake during the initial specs synchronization across the ASISaga organization.

This file should describe **this repository**: the ${DESC}.

## Expected Fix

Replace the entire contents of \`.github/specs/repository.md\` with the correct specification authored in the AOS meta-repository.

The correct content is maintained at:
[\`${SPEC_FILE_REL}\`](${META_REPO_URL}/blob/${BRANCH}/${SPEC_FILE_REL})

<details>
<summary>📋 New <code>.github/specs/repository.md</code> content (click to expand)</summary>

\`\`\`markdown
${SPEC_CONTENT}
\`\`\`

</details>

## Why

Each repository in the ASISaga organisation uses \`.github/specs/repository.md\` as its **Neural Blueprint** — the primary reference for GitHub Copilot agents working in that repo. An incorrect spec causes the AI agent to reason about the wrong codebase, leading to incorrect code suggestions and architectural drift.

## How to Fix

1. Open \`.github/specs/repository.md\` in this repository
2. Replace the entire file content with the content shown in the collapsed section above (or copy from the meta-repo link)
3. Commit directly to \`main\` (or open a PR if branch protection is enabled)

## Context

This issue was created automatically by the [Create Specs Sync Issues](${META_REPO_URL}/actions/workflows/create-specs-sync-issues.yml) workflow in the [agent-operating-system](${META_REPO_URL}) meta-repository as part of a cross-organization specs synchronization audit.

**Audit result**: All 9 shared spec files are already in sync across all 16 repositories. Only \`repository.md\` needs updating in 6 repos:
\`leadership-agent\`, \`ceo-agent\`, \`cfo-agent\`, \`cto-agent\`, \`cso-agent\`, \`cmo-agent\`.
BODY_MARKER

  echo "📝 Creating issue in ${ORG}/${REPO}..."

  # Try with the 'documentation' label first; fall back without it if the
  # label does not exist in the target repo.
  if ISSUE_URL=$(gh issue create \
    --repo "${ORG}/${REPO}" \
    --title "$ISSUE_TITLE" \
    --body-file "$BODY_FILE" \
    --label "documentation" 2>&1); then
    echo "✅ Created (with label): $ISSUE_URL"
  else
    echo "ℹ️  'documentation' label not found — retrying without label"
    ISSUE_URL=$(gh issue create \
      --repo "${ORG}/${REPO}" \
      --title "$ISSUE_TITLE" \
      --body-file "$BODY_FILE")
    echo "✅ Created: $ISSUE_URL"
  fi

done

echo ""
echo "Done. Issues created in: $REPOS"
