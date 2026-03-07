#!/bin/bash
# Sync Agents with Specs Script
# Ensures agents reference relevant specifications

set -e

GITHUB_DIR=".github"
SPECS_DIR=".github/specs"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🔄 Agent-Spec Synchronization Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

sync_issues=0
sync_ok=0

# Check if specs directory exists
if [ ! -d "$SPECS_DIR" ]; then
    echo -e "${RED}Error: $SPECS_DIR not found${NC}"
    exit 1
fi

echo "Analyzing specification coverage..."
echo ""

# For each specification, check if relevant agents reference it
for spec_file in "$SPECS_DIR"/*.md; do
    if [ ! -f "$spec_file" ]; then
        continue
    fi
    
    spec_name=$(basename "$spec_file")
    spec_path="${spec_file#./}"
    
    # Extract keywords from spec name
    keywords=$(basename "$spec_file" .md | tr '-' ' ')
    
    # Find agents that mention these keywords but don't reference the spec
    found_issue=false
    
    # Check instruction files
    for agent_file in "$GITHUB_DIR"/instructions/*.instructions.md; do
        if [ ! -f "$agent_file" ]; then
            continue
        fi
        
        agent_name=$(basename "$agent_file")
        
        # Check if agent mentions keywords
        mentions_topic=false
        for keyword in $keywords; do
            if grep -qi "$keyword" "$agent_file" 2>/dev/null; then
                mentions_topic=true
                break
            fi
        done
        
        # Check if agent references the spec
        references_spec=false
        if grep -q "$spec_path" "$agent_file" 2>/dev/null; then
            references_spec=true
        fi
        
        # If mentions topic but doesn't reference spec, flag it
        if [ "$mentions_topic" = true ] && [ "$references_spec" = false ]; then
            if [ "$found_issue" = false ]; then
                echo -e "${YELLOW}Spec: $spec_name${NC}"
                found_issue=true
            fi
            echo -e "  ${BLUE}→${NC} $agent_name mentions topic but doesn't reference spec"
            sync_issues=$((sync_issues + 1))
        elif [ "$references_spec" = true ]; then
            sync_ok=$((sync_ok + 1))
        fi
    done
    
    # Check prompt files
    for agent_file in "$GITHUB_DIR"/prompts/*.prompt.md; do
        if [ ! -f "$agent_file" ]; then
            continue
        fi
        
        agent_name=$(basename "$agent_file")
        
        mentions_topic=false
        for keyword in $keywords; do
            if grep -qi "$keyword" "$agent_file" 2>/dev/null; then
                mentions_topic=true
                break
            fi
        done
        
        references_spec=false
        if grep -q "$spec_path" "$agent_file" 2>/dev/null; then
            references_spec=true
        fi
        
        if [ "$mentions_topic" = true ] && [ "$references_spec" = false ]; then
            if [ "$found_issue" = false ]; then
                echo -e "${YELLOW}Spec: $spec_name${NC}"
                found_issue=true
            fi
            echo -e "  ${BLUE}→${NC} $agent_name mentions topic but doesn't reference spec"
            sync_issues=$((sync_issues + 1))
        elif [ "$references_spec" = true ]; then
            sync_ok=$((sync_ok + 1))
        fi
    done
    
    # Check skill files
    for agent_file in "$GITHUB_DIR"/skills/*/SKILL.md; do
        if [ ! -f "$agent_file" ]; then
            continue
        fi
        
        agent_name=$(basename "$(dirname "$agent_file")")
        
        mentions_topic=false
        for keyword in $keywords; do
            if grep -qi "$keyword" "$agent_file" 2>/dev/null; then
                mentions_topic=true
                break
            fi
        done
        
        references_spec=false
        if grep -q "$spec_path" "$agent_file" 2>/dev/null; then
            references_spec=true
        fi
        
        if [ "$mentions_topic" = true ] && [ "$references_spec" = false ]; then
            if [ "$found_issue" = false ]; then
                echo -e "${YELLOW}Spec: $spec_name${NC}"
                found_issue=true
            fi
            echo -e "  ${BLUE}→${NC} $agent_name mentions topic but doesn't reference spec"
            sync_issues=$((sync_issues + 1))
        elif [ "$references_spec" = true ]; then
            sync_ok=$((sync_ok + 1))
        fi
    done
    
    if [ "$found_issue" = true ]; then
        echo ""
    fi
done

echo "Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Properly Referenced:${NC} $sync_ok"
echo -e "${YELLOW}Sync Issues Found:${NC} $sync_issues"

if [ "$sync_issues" -eq 0 ]; then
    echo -e "${GREEN}✓ All agents properly reference relevant specs!${NC}"
else
    echo ""
    echo "Recommendations:"
    echo "• Review flagged agents and add spec references"
    echo "• Add references in 'Related Documentation' sections"
    echo "• Format: → Complete guide: /path/to/spec.md"
fi

echo ""
