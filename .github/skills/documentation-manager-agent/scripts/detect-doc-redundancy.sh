#!/usr/bin/env bash
# Documentation Redundancy Detection Script
# Detects duplicate or overlapping documentation files

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
DOCS_DIR="$REPO_ROOT/docs"

echo "🔍 Documentation Manager Agent - Redundancy Detection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

warnings=0

if [ ! -d "$DOCS_DIR" ]; then
    echo "❌ ERROR: /docs directory not found"
    exit 1
fi

echo "Scanning for redundant documentation..."
echo ""

# Check for similar filenames that might be duplicates
echo "📝 Similar Filenames:"
similar_found=0

# Find files with similar base names (ignoring -PART, -v, etc suffixes)
while IFS= read -r file; do
    basename_file=$(basename "$file" .md)
    # Remove common suffixes that indicate duplication
    base_name=$(echo "$basename_file" | sed -E 's/-(PART|SUMMARY|COMPLETE|FINAL|NEW|OLD|v[0-9]+.*|[0-9]+)$//')
    
    # Find other files with similar base name
    similar_files=$(find "$DOCS_DIR" -name "*.md" -type f | grep -v "^$file$" | grep -i "$base_name" || true)
    
    if [ -n "$similar_files" ]; then
        # Check if we've already reported this group
        if ! grep -q "$(basename "$file")" /tmp/doc_redundancy_reported 2>/dev/null; then
            echo "  ⚠️  Potential duplicates found:"
            echo "     - $(basename "$file")"
            echo "$similar_files" | while read -r sim; do
                echo "     - $(basename "$sim")"
                echo "$(basename "$sim")" >> /tmp/doc_redundancy_reported
            done
            echo "$(basename "$file")" >> /tmp/doc_redundancy_reported
            echo ""
            warnings=$((warnings + 1))
            similar_found=1
        fi
    fi
done < <(find "$DOCS_DIR" -name "*.md" -type f | grep -E '-(PART|SUMMARY|COMPLETE|FINAL|NEW|OLD|v[0-9])' || true)

# Clean up temp file
rm -f /tmp/doc_redundancy_reported

if [ $similar_found -eq 0 ]; then
    echo "  ✅ No similar filenames detected"
fi
echo ""

# Check for files with redundant prefixes/suffixes
echo "🏷️  Redundant Naming Patterns:"
redundant_patterns=0

# FINAL, COMPLETE, SUMMARY prefixes
if find "$DOCS_DIR" -type f \( -name "FINAL-*.md" -o -name "COMPLETE-*.md" -o -name "*-FINAL.md" -o -name "*-COMPLETE.md" \) 2>/dev/null | grep -v archive | grep -q .; then
    echo "  ⚠️  Found files with redundant prefixes/suffixes:"
    find "$DOCS_DIR" -type f \( -name "FINAL-*.md" -o -name "COMPLETE-*.md" -o -name "*-FINAL.md" -o -name "*-COMPLETE.md" \) | grep -v archive | sed 's|'"$DOCS_DIR"'/|     - |'
    echo "     Recommendation: Rename without FINAL/COMPLETE (put status inside file)"
    warnings=$((warnings + 1))
    redundant_patterns=1
fi

# Multiple PART files
part_files=$(find "$DOCS_DIR" -type f -name "*-PART-*.md" -o -name "*-PART[0-9]*.md" 2>/dev/null | grep -v archive || true)
if [ -n "$part_files" ]; then
    echo "  ⚠️  Found multi-part documentation:"
    echo "$part_files" | sed 's|'"$DOCS_DIR"'/|     - |'
    echo "     Recommendation: Consolidate into single comprehensive document"
    warnings=$((warnings + 1))
    redundant_patterns=1
fi

if [ $redundant_patterns -eq 0 ]; then
    echo "  ✅ No redundant naming patterns detected"
fi
echo ""

# Check for duplicate content (basic check based on file size and first few lines)
echo "📋 Content Similarity:"
content_duplicates=0

declare -A file_hashes
while IFS= read -r file; do
    # Create a simple hash of first 20 lines (excluding front matter)
    content_hash=$(grep -v "^---$" "$file" | head -20 | md5sum | cut -d' ' -f1)
    
    if [ -n "${file_hashes[$content_hash]}" ]; then
        echo "  ⚠️  Potentially similar content:"
        echo "     - ${file_hashes[$content_hash]}"
        echo "     - $file"
        echo "     Recommendation: Review and consolidate if duplicate"
        echo ""
        warnings=$((warnings + 1))
        content_duplicates=1
    else
        file_hashes[$content_hash]="$file"
    fi
done < <(find "$DOCS_DIR" -name "*.md" -type f -not -path "*/archive/*" 2>/dev/null || true)

if [ $content_duplicates -eq 0 ]; then
    echo "  ✅ No obvious content duplication detected"
fi
echo ""

# Check for old/new pairs
echo "🔄 Old/New File Pairs:"
old_new_found=0

# Find NEW files and check if OLD exists
while IFS= read -r file; do
    basename_file=$(basename "$file")
    old_version=$(echo "$basename_file" | sed 's/NEW/OLD/')
    
    if find "$DOCS_DIR" -name "$old_version" -type f | grep -q .; then
        echo "  ⚠️  Found OLD/NEW pair:"
        echo "     - OLD: $old_version"
        echo "     - NEW: $basename_file"
        echo "     Recommendation: Remove OLD version, rename NEW without suffix"
        warnings=$((warnings + 1))
        old_new_found=1
    fi
done < <(find "$DOCS_DIR" -name "*NEW*.md" -type f || true)

if [ $old_new_found -eq 0 ]; then
    echo "  ✅ No OLD/NEW pairs detected"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $warnings -eq 0 ]; then
    echo "✅ No redundancy detected"
    exit 0
else
    echo "⚠️  Found $warnings potential redundancy issue(s)"
    echo ""
    echo "Action items:"
    echo "  1. Review flagged files for actual duplication"
    echo "  2. Consolidate duplicate content into single source of truth"
    echo "  3. Archive outdated versions to /docs/archive/"
    echo "  4. Update cross-references to point to consolidated docs"
    exit 0
fi
