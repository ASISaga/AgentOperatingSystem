#!/bin/bash
# Spec Validation Script
# Validates a specification file for completeness and quality

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SPEC_FILE="${1}"

if [ -z "$SPEC_FILE" ]; then
    echo "Usage: validate-spec.sh <spec-file>"
    echo "Example: validate-spec.sh specs/001-my-feature/spec.md"
    exit 1
fi

if [ ! -f "$SPEC_FILE" ]; then
    echo -e "${RED}✗ File not found: $SPEC_FILE${NC}"
    exit 1
fi

BASENAME=$(basename "$SPEC_FILE")
echo -e "${BLUE}🔍 Validating: $SPEC_FILE${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

errors=0
warnings=0

check_pass() { echo -e "${GREEN}  ✓ $1${NC}"; }
check_fail() { echo -e "${RED}  ✗ $1${NC}"; errors=$((errors + 1)); }
check_warn() { echo -e "${YELLOW}  ⚠ $1${NC}"; warnings=$((warnings + 1)); }

# --- Clarification markers ---
echo ""
echo "📋 Clarification Markers"
clarification_count=$(grep -c "\[NEEDS CLARIFICATION" "$SPEC_FILE" 2>/dev/null || echo "0")
if [ "$clarification_count" -gt 0 ]; then
    check_fail "$clarification_count [NEEDS CLARIFICATION] marker(s) must be resolved"
    grep -n "\[NEEDS CLARIFICATION" "$SPEC_FILE" | while IFS= read -r line; do
        echo -e "    ${YELLOW}Line: $line${NC}"
    done
else
    check_pass "No [NEEDS CLARIFICATION] markers"
fi

# --- spec.md specific checks ---
if [ "$BASENAME" = "spec.md" ]; then
    echo ""
    echo "📋 Spec Structure"

    # Required sections
    for section in "## Overview" "## User Stories" "## Acceptance Criteria" "## Non-Functional Requirements" "## Out of Scope"; do
        if grep -q "^$section" "$SPEC_FILE" 2>/dev/null; then
            check_pass "Section present: $section"
        else
            check_fail "Missing required section: $section"
        fi
    done

    echo ""
    echo "📋 User Story Quality"
    # Check user story format: "As a ... I want ... so that"
    story_count=$(grep -c "^- As a" "$SPEC_FILE" 2>/dev/null || echo "0")
    if [ "$story_count" -gt 0 ]; then
        check_pass "$story_count user story/stories found"
        # Check for incomplete user stories
        incomplete=$(grep "^- As a" "$SPEC_FILE" | grep -v "so that" | wc -l)
        if [ "$incomplete" -gt 0 ]; then
            check_warn "$incomplete user story/stories missing 'so that <benefit>'"
        fi
    else
        check_fail "No user stories found (format: '- As a <role>, I want <goal>, so that <benefit>')"
    fi

    echo ""
    echo "📋 Implementation Discipline"
    # Check for implementation details that should not be in spec.md
    # Keywords suggesting technology choices; extend TECH_KEYWORDS as needed
    TECH_KEYWORDS='react|vue|angular|postgresql|mongodb|redis|kubernetes|docker'
    if grep -qiE "$TECH_KEYWORDS" "$SPEC_FILE" 2>/dev/null; then
        check_warn "Possible technology/implementation details found in spec.md (keep spec technology-agnostic)"
    else
        check_pass "No obvious technology implementation details"
    fi
fi

# --- plan.md specific checks ---
if [ "$BASENAME" = "plan.md" ]; then
    echo ""
    echo "📋 Plan Structure"

    for section in "## Phase -1" "## Simplicity Gate" "## Anti-Abstraction Gate" "## Integration-First Gate"; do
        if grep -q "$section" "$SPEC_FILE" 2>/dev/null; then
            check_pass "Section present: $section"
        else
            check_fail "Missing required section: $section"
        fi
    done

    echo ""
    echo "📋 Constitutional Gates"
    # Check that gates have been evaluated (have checkbox content)
    unchecked=$(grep -c "^\- \[ \]" "$SPEC_FILE" 2>/dev/null || echo "0")
    if [ "$unchecked" -gt 0 ]; then
        check_warn "$unchecked gate checkbox(es) not yet evaluated"
    else
        check_pass "All gate checkboxes evaluated"
    fi
fi

# --- tasks.md specific checks ---
if [ "$BASENAME" = "tasks.md" ]; then
    echo ""
    echo "📋 Tasks Structure"

    task_count=$(grep -c "^\- \[" "$SPEC_FILE" 2>/dev/null || echo "0")
    parallel_count=$(grep -c "\[P\]" "$SPEC_FILE" 2>/dev/null || echo "0")

    if [ "$task_count" -gt 0 ]; then
        check_pass "$task_count task(s) found"
    else
        check_fail "No tasks found"
    fi

    if [ "$parallel_count" -gt 0 ]; then
        check_pass "$parallel_count parallel task(s) marked [P]"
    else
        check_warn "No parallel tasks marked [P] — check if parallelisation is possible"
    fi

    # Check for vague tasks
    vague=$(grep -c "implement the feature\|do the work\|finish it" "$SPEC_FILE" 2>/dev/null || echo "0")
    if [ "$vague" -gt 0 ]; then
        check_fail "$vague vague task(s) found — break down into atomic tasks"
    else
        check_pass "No obviously vague tasks"
    fi
fi

# --- Summary ---
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$errors" -gt 0 ]; then
    echo -e "${RED}❌ Validation FAILED: $errors error(s), $warnings warning(s)${NC}"
    exit 1
elif [ "$warnings" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Validation PASSED with $warnings warning(s)${NC}"
    exit 0
else
    echo -e "${GREEN}✅ Validation PASSED${NC}"
    exit 0
fi
