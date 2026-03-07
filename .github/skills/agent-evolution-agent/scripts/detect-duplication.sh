#!/bin/bash
# Duplication Detection Script
# Finds duplicate content across agent files to enforce zero-duplication principle

set -e

GITHUB_DIR=".github"
TEMP_DIR="/tmp/agent-duplication-check-$$"
mkdir -p "$TEMP_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔍 Agent Duplication Detection v1.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Applying dogfooding principle: Code agents enforce clean separation of concerns → Agents enforce zero-duplication"
echo ""

# Collect all agent files
agent_files=()
for file in "$GITHUB_DIR"/instructions/*.instructions.md; do
    [ -f "$file" ] && agent_files+=("$file")
done
for file in "$GITHUB_DIR"/prompts/*.prompt.md; do
    [ -f "$file" ] && agent_files+=("$file")
done
for file in "$GITHUB_DIR"/skills/*/SKILL.md; do
    [ -f "$file" ] && agent_files+=("$file")
done

total_duplicates=0
files_with_duplicates=0

# Function to extract content blocks (paragraphs of 3+ lines)
extract_blocks() {
    local file="$1"
    awk '
        /^```/ { in_code=!in_code; next }
        in_code { next }
        /^---$/ && NR==1 { in_frontmatter=1; next }
        /^---$/ && in_frontmatter { in_frontmatter=0; next }
        in_frontmatter { next }
        /^#/ { next }
        /^$/ { if (buffer) { print buffer; buffer="" }; next }
        { buffer = buffer ? buffer " " $0 : $0 }
        END { if (buffer) print buffer }
    ' "$file" | \
    awk 'length > 100' # Only blocks with 100+ chars
}

# Create fingerprints for each file
echo "Analyzing ${#agent_files[@]} agent files for duplicate content..."
echo ""

declare -A block_sources
duplicate_pairs=()

for file in "${agent_files[@]}"; do
    file_name=$(basename "$file" | sed 's/\.instructions\.md$//;s/\.prompt\.md$//')
    if [ "$(basename "$file")" = "SKILL.md" ]; then
        file_name=$(basename "$(dirname "$file")")
    fi
    
    while IFS= read -r block; do
        [ -z "$block" ] && continue
        
        # Create a normalized fingerprint
        fingerprint=$(echo "$block" | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]')
        
        # Check if we've seen this before
        if [ -n "${block_sources[$fingerprint]}" ]; then
            # Found a duplicate
            source_file="${block_sources[$fingerprint]}"
            if [ "$source_file" != "$file_name" ]; then
                total_duplicates=$((total_duplicates + 1))
                duplicate_pairs+=("$source_file|$file_name|$block")
            fi
        else
            block_sources[$fingerprint]="$file_name"
        fi
    done < <(extract_blocks "$file")
done

# Report findings
if [ "$total_duplicates" -gt 0 ]; then
    echo -e "${YELLOW}Found $total_duplicates duplicate content block(s)${NC}"
    echo ""
    echo "Duplicate Content:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    declare -A seen_pairs
    for pair in "${duplicate_pairs[@]}"; do
        IFS='|' read -r source target content <<< "$pair"
        pair_key="${source}_${target}"
        
        if [ -z "${seen_pairs[$pair_key]}" ]; then
            seen_pairs[$pair_key]=1
            echo -e "${BLUE}Duplicate between:${NC}"
            echo "  Source: $source"
            echo "  Target: $target"
            echo "  Content preview: $(echo "$content" | cut -c 1-80)..."
            echo ""
        fi
    done
    
    echo "Recommendations:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "• Extract shared content to /docs/specifications/"
    echo "• Replace duplicates with spec references"
    echo "• Use format: → Complete guide: /docs/specifications/X.md"
    echo ""
    echo -e "${YELLOW}⚠ Duplication detected - refactoring recommended${NC}"
    exit_code=1
else
    echo -e "${GREEN}✓ No significant duplicate content found!${NC}"
    echo ""
    echo "All agents maintain zero-duplication principle."
    exit_code=0
fi

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
exit $exit_code
