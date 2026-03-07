#!/usr/bin/env bash
# Documentation Link Validation Script
# Validates internal markdown links and references

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"

echo "🔗 Documentation Manager Agent - Link Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to check links in a markdown file
check_links() {
    local file="$1"
    local file_dir="$(dirname "$file")"
    local warnings=0
    
    if [ ! -f "$file" ]; then
        echo "❌ File not found: $file"
        return 1
    fi
    
    echo "Checking links in: $(basename "$file")"
    
    # Extract markdown links [text](path) and check if target exists
    while IFS= read -r line; do
        # Extract the link path
        link=$(echo "$line" | sed -n 's/.*(\([^)]*\)).*/\1/p')
        
        # Skip empty links, external URLs, and anchors only
        if [ -z "$link" ] || [[ "$link" =~ ^https?:// ]] || [[ "$link" =~ ^mailto: ]] || [[ "$link" =~ ^# ]]; then
            continue
        fi
        
        # Handle anchor links (path#anchor)
        link_path="${link%%#*}"
        anchor="${link#*#}"
        
        # Skip if it's just an anchor (starts with #)
        if [ -z "$link_path" ]; then
            continue
        fi
        
        # Resolve relative path
        if [[ "$link_path" == /* ]]; then
            # Absolute path from repo root
            target_file="$REPO_ROOT$link_path"
        else
            # Relative path from current file
            target_file="$(cd "$file_dir" && realpath -m "$link_path" 2>/dev/null || echo "$file_dir/$link_path")"
        fi
        
        # Check if target exists
        if [ ! -e "$target_file" ]; then
            echo "  ❌ Broken link: $link"
            echo "     Referenced in: $file"
            echo "     Target not found: $target_file"
            warnings=$((warnings + 1))
        fi
    done < <(grep -oE '\[([^\]]*)\]\(([^)]+)\)' "$file" || true)
    
    if [ $warnings -eq 0 ]; then
        echo "  ✅ All links valid"
    else
        echo "  ⚠️  Found $warnings broken link(s)"
    fi
    
    return $warnings
}

# Main execution
warnings=0

if [ $# -eq 0 ]; then
    # Check all markdown files in docs/
    echo "Checking all documentation files..."
    echo ""
    
    while IFS= read -r file; do
        check_links "$file" || warnings=$((warnings + $?))
        echo ""
    done < <(find "$REPO_ROOT/docs" -name "*.md" -type f 2>/dev/null || true)
    
elif [ -d "$1" ]; then
    # Check all markdown files in specified directory
    target_dir="$1"
    echo "Checking files in: $target_dir"
    echo ""
    
    while IFS= read -r file; do
        check_links "$file" || warnings=$((warnings + $?))
        echo ""
    done < <(find "$target_dir" -name "*.md" -type f 2>/dev/null || true)
    
elif [ -f "$1" ]; then
    # Check single file
    check_links "$1" || warnings=$?
    echo ""
else
    echo "❌ Invalid path: $1"
    exit 1
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $warnings -eq 0 ]; then
    echo "✅ All links are valid"
    exit 0
else
    echo "⚠️  Found $warnings broken link(s)"
    echo ""
    echo "Fix broken links by:"
    echo "  1. Updating the link path"
    echo "  2. Creating the missing target file"
    echo "  3. Moving/archiving referenced content properly"
    exit 1
fi
