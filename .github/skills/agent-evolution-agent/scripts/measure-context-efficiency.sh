#!/bin/bash
# Measure Context Efficiency Script
# Calculates context window efficiency for a specific agent

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <agent-file>"
    echo "Example: $0 .github/instructions/python.instructions.md"
    exit 1
fi

AGENT_FILE="$1"

if [ ! -f "$AGENT_FILE" ]; then
    echo "Error: File not found: $AGENT_FILE"
    exit 1
fi

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "📊 Context Window Efficiency Analysis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Agent: $(basename "$AGENT_FILE")"
echo ""

# Calculate metrics
total_lines=$(wc -l < "$AGENT_FILE")
total_chars=$(wc -c < "$AGENT_FILE")
spec_references=$(grep -cE "\.github/specs/|/docs/specifications/" "$AGENT_FILE" 2>/dev/null || echo "0")
doc_references=$(grep -c "/docs/" "$AGENT_FILE" 2>/dev/null || echo "0")
code_blocks=$(grep -c '```' "$AGENT_FILE" 2>/dev/null || echo "0")
code_blocks=$((code_blocks / 2)) # Each block has opening and closing

# Estimate token count (rough: 1 token ≈ 4 chars)
estimated_tokens=$((total_chars / 4))

# Count different content types
headers=$(grep -c '^#' "$AGENT_FILE" 2>/dev/null || echo "0")
lists=$(grep -c '^[-*]' "$AGENT_FILE" 2>/dev/null || echo "0")

echo "Size Metrics:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total Lines: $total_lines"
echo "Total Characters: $total_chars"
echo "Estimated Tokens: ~$estimated_tokens"
echo ""

echo "Content Structure:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Headers: $headers"
echo "List Items: $lists"
echo "Code Blocks: $code_blocks"
echo ""

echo "Reference Metrics:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Spec References (.github/specs/ or /docs/specifications/): $spec_references"
echo "Total Doc References (/docs/): $doc_references"
echo ""

# Calculate efficiency scores
spec_density=0
if [ "$total_lines" -gt 0 ]; then
    spec_density=$((spec_references * 100 / total_lines))
fi

# Determine optimal ranges based on agent type
optimal_lines=400
if echo "$AGENT_FILE" | grep -q "instructions"; then
    optimal_lines=200
elif echo "$AGENT_FILE" | grep -q "SKILL.md"; then
    optimal_lines=150
fi

echo "Efficiency Analysis:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Line count assessment
if [ "$total_lines" -le "$optimal_lines" ]; then
    echo -e "${GREEN}✓ Line Count:${NC} $total_lines / $optimal_lines (optimal)"
else
    excess=$((total_lines - optimal_lines))
    echo -e "${YELLOW}⚠ Line Count:${NC} $total_lines / $optimal_lines (+$excess lines)"
fi

# Spec reference assessment
if [ "$spec_references" -ge 3 ]; then
    echo -e "${GREEN}✓ Spec References:${NC} $spec_references (excellent)"
elif [ "$spec_references" -ge 1 ]; then
    echo -e "${YELLOW}⚠ Spec References:${NC} $spec_references (good, target ≥3)"
else
    echo -e "${RED}✗ Spec References:${NC} $spec_references (needs improvement)"
fi

# Spec density assessment
if [ "$spec_density" -ge 2 ]; then
    echo -e "${GREEN}✓ Spec Density:${NC} ${spec_density}% (high leverage)"
elif [ "$spec_density" -ge 1 ]; then
    echo -e "${YELLOW}⚠ Spec Density:${NC} ${spec_density}% (moderate)"
else
    echo -e "${RED}✗ Spec Density:${NC} ${spec_density}% (low)"
fi

# Context efficiency score (0-100)
efficiency_score=0

# Line count contributes 40%
if [ "$total_lines" -le "$optimal_lines" ]; then
    efficiency_score=$((efficiency_score + 40))
else
    # Penalty for exceeding optimal
    penalty=$((total_lines - optimal_lines))
    penalty=$((penalty * 40 / optimal_lines))
    if [ "$penalty" -lt 40 ]; then
        efficiency_score=$((efficiency_score + 40 - penalty))
    fi
fi

# Spec references contribute 40%
if [ "$spec_references" -ge 5 ]; then
    efficiency_score=$((efficiency_score + 40))
elif [ "$spec_references" -ge 3 ]; then
    efficiency_score=$((efficiency_score + 30))
elif [ "$spec_references" -ge 1 ]; then
    efficiency_score=$((efficiency_score + 15))
fi

# Spec density contributes 20%
if [ "$spec_density" -ge 2 ]; then
    efficiency_score=$((efficiency_score + 20))
elif [ "$spec_density" -ge 1 ]; then
    efficiency_score=$((efficiency_score + 10))
fi

echo ""
echo "Overall Context Efficiency Score:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$efficiency_score" -ge 80 ]; then
    echo -e "${GREEN}🎯 $efficiency_score/100 - EXCELLENT${NC}"
    echo "This agent is highly optimized for context window efficiency."
elif [ "$efficiency_score" -ge 60 ]; then
    echo -e "${BLUE}👍 $efficiency_score/100 - GOOD${NC}"
    echo "This agent is well-optimized but has room for improvement."
elif [ "$efficiency_score" -ge 40 ]; then
    echo -e "${YELLOW}⚠ $efficiency_score/100 - NEEDS IMPROVEMENT${NC}"
    echo "This agent should be refactored to improve efficiency."
else
    echo -e "${RED}✗ $efficiency_score/100 - POOR${NC}"
    echo "This agent requires significant refactoring."
fi

echo ""
echo "Recommendations:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$total_lines" -gt "$optimal_lines" ]; then
    echo "• Extract detailed content to .github/specs/ or /docs/specifications/"
    echo "• Keep only activation logic and workflows in agent"
fi

if [ "$spec_references" -lt 3 ]; then
    echo "• Add more references to .github/specs/ (agents.md, skills.md, prompts.md, instructions.md)"
    echo "• Replace inline knowledge with spec links"
fi

if [ "$code_blocks" -gt 5 ]; then
    echo "• Consider moving large code examples to spec files"
    echo "• Keep only minimal examples in agent prompts"
fi

echo ""
