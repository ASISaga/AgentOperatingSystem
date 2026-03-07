#!/usr/bin/env bash
# Documentation Metadata Validation Script
# Validates version headers and last updated dates

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"

echo "📅 Documentation Manager Agent - Metadata Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to check metadata in a file
check_metadata() {
    local file="$1"
    local warnings=0
    
    if [ ! -f "$file" ]; then
        echo "❌ File not found: $file"
        return 1
    fi
    
    echo "Checking metadata: $(basename "$file")"
    
    # Check for "Last Updated" date
    if ! grep -qE '\*?Last Updated:?\*?' "$file" && ! grep -qE 'Last Updated:' "$file"; then
        echo "  ⚠️  Missing 'Last Updated' date"
        warnings=$((warnings + 1))
    else
        # Extract and validate date format
        last_updated=$(grep -E '\*?Last Updated:?\*?' "$file" | head -1 || true)
        if [ -n "$last_updated" ]; then
            # Check if date is in reasonable format (YYYY-MM-DD)
            if ! echo "$last_updated" | grep -qE '20[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])'; then
                echo "  ⚠️  'Last Updated' date format unclear: $last_updated"
                echo "     Expected format: YYYY-MM-DD (e.g., 2026-02-10)"
                warnings=$((warnings + 1))
            else
                # Check if date is very old (more than 180 days)
                date_str=$(echo "$last_updated" | grep -oE '20[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])')
                if command -v date >/dev/null 2>&1; then
                    date_epoch=$(date -d "$date_str" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$date_str" +%s 2>/dev/null || echo "0")
                    current_epoch=$(date +%s)
                    days_old=$(( (current_epoch - date_epoch) / 86400 ))
                    
                    if [ "$days_old" -gt 180 ]; then
                        echo "  ⚠️  'Last Updated' date is $days_old days old"
                        echo "     Consider reviewing if content is still current"
                        warnings=$((warnings + 1))
                    fi
                fi
            fi
        fi
    fi
    
    # Check for version information
    has_version=0
    if grep -qE '\*?Version:?\*?|^##?\s+Version' "$file"; then
        has_version=1
    fi
    
    # For specifications and guides, version info is recommended
    if [[ "$file" =~ /specifications/ ]] || [[ "$file" =~ /guides/ ]]; then
        if [ $has_version -eq 0 ]; then
            echo "  ⚠️  No version information found (recommended for specs/guides)"
            warnings=$((warnings + 1))
        fi
    fi
    
    # Check for version history section in files with version
    if [ $has_version -eq 1 ]; then
        if ! grep -qE '^##\s+Version History' "$file"; then
            echo "  ℹ️  Consider adding 'Version History' section"
        fi
    fi
    
    # Check if file has been recently modified in git
    if command -v git >/dev/null 2>&1 && [ -d "$REPO_ROOT/.git" ]; then
        # Get last commit date for this file
        last_commit=$(git -C "$REPO_ROOT" log -1 --format="%cd" --date=short -- "$file" 2>/dev/null || true)
        
        if [ -n "$last_commit" ]; then
            # Compare with Last Updated in file
            if grep -qE '\*?Last Updated:?\*?' "$file"; then
                file_date=$(grep -E '\*?Last Updated:?\*?' "$file" | head -1 | grep -oE '20[0-9]{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])' || true)
                
                if [ -n "$file_date" ]; then
                    # Check if git commit is more recent than documented date
                    if [[ "$last_commit" > "$file_date" ]]; then
                        days_diff=$(( ($(date -d "$last_commit" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$last_commit" +%s 2>/dev/null || echo "0") - $(date -d "$file_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$file_date" +%s 2>/dev/null || echo "0")) / 86400 ))
                        
                        if [ "$days_diff" -gt 7 ]; then
                            echo "  ⚠️  File modified on $last_commit but 'Last Updated' shows $file_date"
                            echo "     Update the 'Last Updated' date to reflect recent changes"
                            warnings=$((warnings + 1))
                        fi
                    fi
                fi
            fi
        fi
    fi
    
    if [ $warnings -eq 0 ]; then
        echo "  ✅ Metadata is valid"
    else
        echo "  ⚠️  Found $warnings metadata issue(s)"
    fi
    
    return $warnings
}

# Main execution
warnings=0

if [ $# -eq 0 ]; then
    echo "❌ ERROR: No path specified"
    echo ""
    echo "Usage:"
    echo "  $0 <file.md>           # Check single file"
    echo "  $0 <directory>         # Check all .md files in directory"
    echo "  $0 docs/specifications # Common usage"
    exit 1
fi

if [ -d "$1" ]; then
    # Check all markdown files in specified directory
    target_dir="$1"
    echo "Checking files in: $target_dir"
    echo ""
    
    while IFS= read -r file; do
        check_metadata "$file" || warnings=$((warnings + $?))
        echo ""
    done < <(find "$target_dir" -name "*.md" -type f 2>/dev/null || true)
    
elif [ -f "$1" ]; then
    # Check single file
    check_metadata "$1" || warnings=$?
    echo ""
else
    echo "❌ Invalid path: $1"
    exit 1
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $warnings -eq 0 ]; then
    echo "✅ All metadata is valid"
    exit 0
else
    echo "⚠️  Found $warnings metadata issue(s)"
    echo ""
    echo "Metadata best practices:"
    echo "  1. Include 'Last Updated: YYYY-MM-DD' at end of file"
    echo "  2. Add version information for specifications/guides"
    echo "  3. Update dates when making significant changes"
    echo "  4. Consider adding 'Version History' section for major docs"
    exit 0
fi
