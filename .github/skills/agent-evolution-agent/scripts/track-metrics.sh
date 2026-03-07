#!/bin/bash
# Metrics Tracking Script
# Tracks agent quality metrics over time for continuous learning

set -e

GITHUB_DIR=".github"
METRICS_DIR=".github/metrics"
METRICS_FILE="$METRICS_DIR/history.log"

mkdir -p "$METRICS_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "📈 Agent Metrics Tracking v1.0"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Calculate current metrics
total_agents=0
agents_optimal=0
total_context_score=0
total_lines=0
total_spec_refs=0

count_spec_references() {
    local file="$1"
    local count=$(grep -cE "\.github/specs/|/docs/specifications/" "$file" 2>/dev/null || echo "0")
    echo "$count" | tr -d ' \n\t\r'
}

get_line_count() {
    local file="$1"
    wc -l < "$file" 2>/dev/null | tr -d ' \n\t\r'
}

audit_agent() {
    local file="$1"
    
    total_agents=$((total_agents + 1))
    
    local lines=$(get_line_count "$file")
    local spec_refs=$(count_spec_references "$file")
    
    # Ensure numeric values
    lines=${lines:-0}
    spec_refs=${spec_refs:-0}
    
    total_lines=$((total_lines + lines))
    total_spec_refs=$((total_spec_refs + spec_refs))
    
    local spec_percentage=0
    if [ "$spec_refs" -gt 0 ] 2>/dev/null; then
        spec_percentage=$((spec_refs * 20))
        if [ "$spec_percentage" -gt 100 ]; then
            spec_percentage=100
        fi
    fi
    
    total_context_score=$((total_context_score + spec_percentage))
    
    # Determine optimal threshold
    local optimal_lines=400
    if echo "$file" | grep -q "instructions"; then
        optimal_lines=200
    elif echo "$file" | grep -q "SKILL.md"; then
        optimal_lines=150
    fi
    
    if [ "$lines" -le "$optimal_lines" ] 2>/dev/null && [ "$spec_refs" -ge 3 ] 2>/dev/null; then
        agents_optimal=$((agents_optimal + 1))
    fi
}

# Audit all agents
for file in "$GITHUB_DIR"/instructions/*.instructions.md; do
    [ -f "$file" ] && audit_agent "$file"
done

for file in "$GITHUB_DIR"/prompts/*.prompt.md; do
    [ -f "$file" ] && audit_agent "$file"
done

for file in "$GITHUB_DIR"/skills/*/SKILL.md; do
    [ -f "$file" ] && audit_agent "$file"
done

# Calculate aggregate metrics
avg_spec_coverage=0
avg_lines=0
context_efficiency=0

if [ "$total_agents" -gt 0 ]; then
    avg_spec_coverage=$((total_context_score / total_agents))
    avg_lines=$((total_lines / total_agents))
    
    # Context efficiency score (0-100)
    optimal_percentage=$((agents_optimal * 100 / total_agents))
    context_efficiency=$(((optimal_percentage + avg_spec_coverage) / 2))
fi

# Get timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Record metrics
echo "$timestamp,$total_agents,$agents_optimal,$avg_spec_coverage,$avg_lines,$context_efficiency,$total_spec_refs" >> "$METRICS_FILE"

# Display current metrics
echo "Current Metrics ($(date '+%Y-%m-%d')):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total Agents: $total_agents"
echo "Optimal Agents: $agents_optimal ($optimal_percentage%)"
echo "Average Spec Coverage: $avg_spec_coverage%"
echo "Average Lines per Agent: $avg_lines"
echo "Context Efficiency Score: $context_efficiency/100"
echo "Total Spec References: $total_spec_refs"
echo ""

# Show trend if we have historical data
if [ -f "$METRICS_FILE" ]; then
    line_count=$(wc -l < "$METRICS_FILE")
    if [ "$line_count" -gt 1 ]; then
        echo "Trend Analysis:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Get previous entry
        prev_line=$(tail -n 2 "$METRICS_FILE" | head -n 1)
        IFS=',' read -r prev_date prev_agents prev_optimal prev_coverage prev_lines prev_efficiency prev_refs <<< "$prev_line"
        
        # Calculate changes
        optimal_change=$((agents_optimal - prev_optimal))
        coverage_change=$((avg_spec_coverage - prev_coverage))
        efficiency_change=$((context_efficiency - prev_efficiency))
        refs_change=$((total_spec_refs - prev_refs))
        
        # Display with colors
        display_change() {
            local label="$1"
            local change="$2"
            local current="$3"
            
            if [ "$change" -gt 0 ]; then
                echo -e "  ${GREEN}↑ $label: +$change ($current)${NC}"
            elif [ "$change" -lt 0 ]; then
                echo -e "  ${RED}↓ $label: $change ($current)${NC}"
            else
                echo -e "  ${BLUE}→ $label: No change ($current)${NC}"
            fi
        }
        
        echo "  Since: $prev_date"
        display_change "Optimal Agents" "$optimal_change" "$agents_optimal"
        display_change "Spec Coverage" "$coverage_change" "${avg_spec_coverage}%"
        display_change "Context Efficiency" "$efficiency_change" "${context_efficiency}/100"
        display_change "Spec References" "$refs_change" "$total_spec_refs"
        echo ""
        
        # Overall assessment
        if [ "$efficiency_change" -gt 5 ]; then
            echo -e "${GREEN}🎯 Excellent progress! System is improving.${NC}"
        elif [ "$efficiency_change" -gt 0 ]; then
            echo -e "${BLUE}👍 Good progress! Keep improving.${NC}"
        elif [ "$efficiency_change" -eq 0 ]; then
            echo -e "${YELLOW}⚠ No change. Consider running improvements.${NC}"
        else
            echo -e "${RED}⚠ Efficiency decreased! Review recent changes.${NC}"
        fi
    else
        echo "Baseline established. Run again later to see trends."
    fi
fi

echo ""
echo "Metrics saved to: $METRICS_FILE"

# Show last 5 entries if requested
if [ "$1" = "--history" ]; then
    echo ""
    echo "Historical Data (last 5 entries):"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Date                | Agents | Optimal | Coverage | Efficiency"
    echo "--------------------+--------+---------+----------+-----------"
    tail -n 5 "$METRICS_FILE" | while IFS=',' read -r date agents optimal coverage lines efficiency refs; do
        printf "%-19s | %-6s | %-7s | %-8s | %-10s\n" "$date" "$agents" "$optimal" "${coverage}%" "${efficiency}/100"
    done
fi

echo ""
