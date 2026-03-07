#!/bin/bash
# Agent Self-Improvement Recommendations
# Generates actionable recommendations for improving agent quality

set -e

GITHUB_DIR=".github"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "💡 Agent Self-Improvement Recommendations v1.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

recommendations_count=0

# Function to analyze and recommend for a file
analyze_file() {
    local file="$1"
    local agent_name=$(basename "$file" | sed 's/\.prompt\.md$//;s/\.instructions\.md$//')
    
    if [ -f "$file" ] && [ "$(basename "$file")" = "SKILL.md" ]; then
        agent_name=$(basename "$(dirname "$file")")
    fi
    
    local lines=$(wc -l < "$file" 2>/dev/null || echo "0")
    local spec_refs=$(grep -cE "\.github/specs/|/docs/specifications/" "$file" 2>/dev/null || echo "0")
    local total_doc_refs=$(grep -c "/docs/" "$file" 2>/dev/null || echo "0")
    
    # Ensure numeric values
    lines=${lines:-0}
    spec_refs=${spec_refs:-0}
    total_doc_refs=${total_doc_refs:-0}
    
    # Determine thresholds
    local optimal_lines=400
    if echo "$file" | grep -q "instructions"; then
        optimal_lines=200
    elif echo "$file" | grep -q "SKILL.md"; then
        optimal_lines=150
    fi
    
    local has_recommendations=false
    local priority="low"
    
    # Check for issues and generate recommendations
    if [ "$lines" -gt "$optimal_lines" ] || [ "$spec_refs" -lt 3 ]; then
        has_recommendations=true
        
        # Determine priority
        if [ "$lines" -gt $((optimal_lines * 2)) ] || [ "$spec_refs" -eq 0 ]; then
            priority="high"
        elif [ "$lines" -gt $((optimal_lines + optimal_lines / 2)) ] || [ "$spec_refs" -lt 2 ]; then
            priority="medium"
        fi
        
        # Output recommendations
        local color="$YELLOW"
        [ "$priority" = "high" ] && color="$RED"
        
        echo -e "${color}[$priority] $agent_name${NC}"
        echo "  File: $file"
        echo "  Lines: $lines / $optimal_lines (target)"
        echo "  Spec Refs: $spec_refs (target: ≥3)"
        echo ""
        echo "  Recommendations:"
        
        if [ "$lines" -gt "$optimal_lines" ]; then
            excess=$((lines - optimal_lines))
            echo "    1. Extract $excess+ lines of static content to .github/specs/ or /docs/specifications/"
            echo "       - Look for: detailed examples, comprehensive lists, reference tables"
            echo "       - Keep: activation logic, workflows, minimal examples"
            recommendations_count=$((recommendations_count + 1))
        fi
        
        if [ "$spec_refs" -lt 3 ]; then
            needed=$((3 - spec_refs))
            echo "    2. Add $needed+ spec reference(s)"
            echo "       - Run: ./.github/skills/agent-evolution-agent/scripts/find-related-agents.sh"
            echo "       - Add to 'Related Documentation' or 'References' section"
            echo "       - Format: → Complete guide: .github/specs/X.md"
            recommendations_count=$((recommendations_count + 1))
        fi
        
        # Check for potential extractable content
        local code_blocks=$(grep -c '```' "$file" 2>/dev/null || echo "0")
        code_blocks=$((code_blocks / 2))
        if [ "$code_blocks" -gt 5 ]; then
            echo "    3. Large code examples detected ($code_blocks blocks)"
            echo "       - Move detailed examples to spec files"
            echo "       - Keep only 1-2 minimal examples inline"
            recommendations_count=$((recommendations_count + 1))
        fi
        
        # Check for long lists
        local list_items=$(grep -c '^[-*]' "$file" 2>/dev/null || echo "0")
        if [ "$list_items" -gt 30 ]; then
            echo "    4. Extensive lists detected ($list_items items)"
            echo "       - Extract comprehensive lists to spec files"
            echo "       - Keep only critical items inline with '→ See X.md for complete list'"
            recommendations_count=$((recommendations_count + 1))
        fi
        
        echo ""
        echo "  Dogfooding Principle Applied:"
        echo "    This agent should practice what it preaches:"
        if echo "$file" | grep -q "docs"; then
            echo "    - Docs agents enforce spec references → Reference, don't duplicate"
        else
            echo "    - Code agents enforce clean separation → Minimize inline content, maximize spec refs"
        fi
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
    fi
}

# Analyze all agent files
echo "Analyzing instruction files..."
for file in "$GITHUB_DIR"/instructions/*.instructions.md; do
    [ -f "$file" ] && analyze_file "$file"
done

echo "Analyzing agent prompts..."
for file in "$GITHUB_DIR"/prompts/*.prompt.md; do
    [ -f "$file" ] && analyze_file "$file"
done

echo "Analyzing agent skills..."
for file in "$GITHUB_DIR"/skills/*/SKILL.md; do
    [ -f "$file" ] && analyze_file "$file"
done

# Summary
echo ""
echo "Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$recommendations_count" -gt 0 ]; then
    echo -e "${YELLOW}Generated $recommendations_count recommendation(s)${NC}"
    echo ""
    echo "Next Steps:"
    echo "1. Prioritize high-priority items first"
    echo "2. For each agent:"
    echo "   a. Create/update relevant spec in .github/specs/ or /docs/specifications/"
    echo "   b. Extract content from agent to spec"
    echo "   c. Add spec reference to agent"
    echo "   d. Run: pytest tests/ -v (validate)"
    echo "3. Re-run this script to verify improvements"
    echo "4. Run: ./.github/skills/agent-evolution-agent/scripts/audit-agent-quality.sh"
else
    echo -e "${GREEN}✓ All agents meet quality standards!${NC}"
    echo "No improvements needed at this time."
fi

echo ""
