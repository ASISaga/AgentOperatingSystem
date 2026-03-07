#!/bin/bash
# List Specs Script
# Lists all feature specs in specs/ directory with status

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SPECS_DIR="${1:-specs}"

echo -e "${BLUE}📋 Feature Specifications${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ ! -d "$SPECS_DIR" ]; then
    echo -e "${YELLOW}No specs/ directory found. Use the Spec Manager Agent (spec-create.prompt.md) to create the first feature spec.${NC}"
    echo ""
    echo "Next feature number: 001"
    exit 0
fi

max_num=0
spec_count=0

for dir in "$SPECS_DIR"/*/; do
    if [ ! -d "$dir" ]; then
        continue
    fi

    slug=$(basename "$dir")

    # Skip non-feature directories (those not starting with NNN-)
    if ! echo "$slug" | grep -qE '^[0-9]{3}-'; then
        continue
    fi

    num=$(echo "$slug" | grep -oE '^[0-9]{3}')
    # Use 10# prefix to force base-10 interpretation of zero-padded numbers (e.g. 008 → 8)
    num_int=$((10#$num))
    if [ "$num_int" -gt "$max_num" ]; then
        max_num=$num_int
    fi

    spec_count=$((spec_count + 1))

    # Check which files exist
    has_spec="[ ]"
    has_plan="[ ]"
    has_tasks="[ ]"
    [ -f "${dir}spec.md" ] && has_spec="[x]"
    [ -f "${dir}plan.md" ] && has_plan="[x]"
    [ -f "${dir}tasks.md" ] && has_tasks="[x]"

    # Determine status
    status=""
    if [ "$has_tasks" = "[x]" ]; then
        status="${GREEN}● ready${NC}"
    elif [ "$has_plan" = "[x]" ]; then
        status="${CYAN}● planned${NC}"
    elif [ "$has_spec" = "[x]" ]; then
        status="${YELLOW}● specified${NC}"
    else
        status="○ empty"
    fi

    echo -e "  $num  $slug"
    echo -e "       spec $has_spec  plan $has_plan  tasks $has_tasks  — $status"

    # Show any remaining clarification markers
    if [ -f "${dir}spec.md" ]; then
        nc_count=$(grep -c "\[NEEDS CLARIFICATION" "${dir}spec.md" 2>/dev/null || echo "0")
        if [ "$nc_count" -gt 0 ]; then
            echo -e "       ${YELLOW}⚠  $nc_count [NEEDS CLARIFICATION] marker(s) remaining${NC}"
        fi
    fi

    echo ""
done

if [ "$spec_count" -eq 0 ]; then
    echo -e "  ${YELLOW}No feature specs found in $SPECS_DIR/${NC}"
    echo ""
fi

next_num=$(printf "%03d" $((max_num + 1)))
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Total specs: ${spec_count}"
echo -e "  Next feature number: ${BLUE}${next_num}${NC}"
