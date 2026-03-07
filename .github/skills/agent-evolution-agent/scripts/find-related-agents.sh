#!/bin/bash
# Find Related Agents Script
# Identifies agents that should reference a given specification file

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <spec-file>"
    echo "Example: $0 .github/specs/workflows.md"
    exit 1
fi

SPEC_FILE="$1"
SPEC_NAME=$(basename "$SPEC_FILE" .md)
GITHUB_DIR=".github"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Finding agents related to: $SPEC_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Extract keywords from spec filename
extract_keywords() {
    echo "$SPEC_NAME" | tr '-' '\n' | grep -v "^$"
}

keywords=$(extract_keywords)

echo "Keywords extracted: $keywords"
echo ""

related_agents=()

# Function to check if file should reference spec
check_relevance() {
    local file="$1"
    local score=0
    
    # Check if file already references the spec
    if grep -q "$SPEC_FILE" "$file" 2>/dev/null; then
        echo "already-referenced"
        return
    fi
    
    # Check for keyword matches in filename
    local filename=$(basename "$file")
    for keyword in $keywords; do
        if echo "$filename" | grep -qi "$keyword"; then
            score=$((score + 1))
        fi
    done
    
    # Check for keyword matches in content
    for keyword in $keywords; do
        if grep -qi "$keyword" "$file" 2>/dev/null; then
            score=$((score + 1))
        fi
    done
    
    echo "$score"
}

echo "Checking Instruction Files:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for file in "$GITHUB_DIR"/instructions/*.instructions.md; do
    if [ -f "$file" ]; then
        relevance=$(check_relevance "$file")
        if [ "$relevance" = "already-referenced" ]; then
            echo -e "${GREEN}✓ $(basename "$file") - Already references spec${NC}"
        elif [ "$relevance" -gt 1 ]; then
            echo -e "${BLUE}→ $(basename "$file") - Relevance score: $relevance (should reference)${NC}"
            related_agents+=("$file")
        fi
    fi
done

echo ""
echo "Checking Agent Prompts:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for file in "$GITHUB_DIR"/prompts/*.prompt.md; do
    if [ -f "$file" ]; then
        relevance=$(check_relevance "$file")
        if [ "$relevance" = "already-referenced" ]; then
            echo -e "${GREEN}✓ $(basename "$file") - Already references spec${NC}"
        elif [ "$relevance" -gt 1 ]; then
            echo -e "${BLUE}→ $(basename "$file") - Relevance score: $relevance (should reference)${NC}"
            related_agents+=("$file")
        fi
    fi
done

echo ""
echo "Checking Agent Skills:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for file in "$GITHUB_DIR"/skills/*/SKILL.md; do
    if [ -f "$file" ]; then
        relevance=$(check_relevance "$file")
        if [ "$relevance" = "already-referenced" ]; then
            echo -e "${GREEN}✓ $(basename "$(dirname "$file")") - Already references spec${NC}"
        elif [ "$relevance" -gt 1 ]; then
            echo -e "${BLUE}→ $(basename "$(dirname "$file")") - Relevance score: $relevance (should reference)${NC}"
            related_agents+=("$file")
        fi
    fi
done

echo ""
echo "Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ${#related_agents[@]} -gt 0 ]; then
    echo "Found ${#related_agents[@]} agent(s) that should reference this spec:"
    for agent in "${related_agents[@]}"; do
        echo "  • $agent"
    done
    echo ""
    echo "Recommended action:"
    echo "Add the following to the 'Related Documentation' section:"
    echo "  → Complete guide: /$SPEC_FILE"
else
    echo "No agents found that need to reference this spec."
    echo "All related agents already reference it, or spec is too specialized."
fi

echo ""
