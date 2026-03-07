#!/bin/bash
# Create Feature Branch Script
# Creates a numbered feature branch and directory for a new spec

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DESCRIPTION="${1}"
SPECS_DIR="${2:-specs}"

if [ -z "$DESCRIPTION" ]; then
    echo "Usage: create-feature-branch.sh \"<feature description>\" [specs-dir]"
    echo "Example: create-feature-branch.sh \"Real-time agent status dashboard\""
    exit 1
fi

# Determine next feature number
max_num=0
if [ -d "$SPECS_DIR" ]; then
    for dir in "$SPECS_DIR"/*/; do
        if [ -d "$dir" ]; then
            slug=$(basename "$dir")
            if echo "$slug" | grep -qE '^[0-9]{3}-'; then
                num=$(echo "$slug" | grep -oE '^[0-9]{3}')
                num_int=$((10#$num))
                if [ "$num_int" -gt "$max_num" ]; then
                    max_num=$num_int
                fi
            fi
        fi
    done
fi

next_num=$(printf "%03d" $((max_num + 1)))

# Generate slug from description
# lowercase, hyphens, max 5 words, no stop words (a, an, the, conjunctions, prepositions, auxiliaries)
STOP_WORDS=(a an the and or but in on at to for of with by from as is are was were be been being have has had do does did will would could should may might shall must can)

slug=""
word_count=0

for word in $DESCRIPTION; do
    # lowercase
    word_lower=$(echo "$word" | tr '[:upper:]' '[:lower:]')
    # remove non-alphanumeric
    word_clean=$(echo "$word_lower" | sed 's/[^a-z0-9]//g')

    if [ -z "$word_clean" ]; then
        continue
    fi

    # skip stop words
    is_stop=false
    for stop in "${STOP_WORDS[@]}"; do
        if [ "$word_clean" = "$stop" ]; then
            is_stop=true
            break
        fi
    done

    if $is_stop; then
        continue
    fi

    if [ "$word_count" -ge 5 ]; then
        break
    fi

    if [ -z "$slug" ]; then
        slug="$word_clean"
    else
        slug="${slug}-${word_clean}"
    fi
    word_count=$((word_count + 1))
done

if [ -z "$slug" ]; then
    slug="feature"
fi

BRANCH_NAME="${next_num}-${slug}"
FEATURE_DIR="${SPECS_DIR}/${BRANCH_NAME}"

echo -e "${BLUE}🌿 Creating feature branch: $BRANCH_NAME${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create git branch
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
        echo -e "${YELLOW}  ⚠ Branch $BRANCH_NAME already exists, switching to it${NC}"
        git checkout "$BRANCH_NAME"
    else
        git checkout -b "$BRANCH_NAME"
        echo -e "${GREEN}  ✓ Created branch: $BRANCH_NAME${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ Not a git repository — skipping branch creation${NC}"
fi

# Create feature directory
mkdir -p "$FEATURE_DIR/contracts"
echo -e "${GREEN}  ✓ Created directory: $FEATURE_DIR${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Branch:    ${BLUE}$BRANCH_NAME${NC}"
echo -e "  Directory: ${BLUE}$FEATURE_DIR${NC}"
echo -e "  Next step: populate $FEATURE_DIR/spec.md from .github/templates/spec.md"
