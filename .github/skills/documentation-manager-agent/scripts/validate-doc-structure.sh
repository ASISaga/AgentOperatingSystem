#!/usr/bin/env bash
# Documentation Structure Validation Script
# Validates documentation organization and required files

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
DOCS_DIR="$REPO_ROOT/docs"

echo "📚 Documentation Manager Agent - Structure Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

warnings=0
errors=0

# Check if docs directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo "❌ ERROR: /docs directory not found"
    exit 1
fi

echo "Checking documentation structure..."
echo ""

# Check for required files in docs root
echo "📄 Required Files:"
required_files=("README.md" "INDEX.md")
for file in "${required_files[@]}"; do
    if [ -f "$DOCS_DIR/$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
        errors=$((errors + 1))
    fi
done
echo ""

# Check for required directories
echo "📁 Required Directories:"
required_dirs=("guides" "specifications" "archive")
for dir in "${required_dirs[@]}"; do
    if [ -d "$DOCS_DIR/$dir" ]; then
        echo "  ✅ $dir/ exists"
    else
        echo "  ⚠️  $dir/ missing (recommended)"
        warnings=$((warnings + 1))
    fi
done
echo ""

# Check archive subdirectories
if [ -d "$DOCS_DIR/archive" ]; then
    echo "📦 Archive Organization:"
    archive_dirs=("implementations" "audits" "refactorings")
    for dir in "${archive_dirs[@]}"; do
        if [ -d "$DOCS_DIR/archive/$dir" ]; then
            echo "  ✅ archive/$dir/ exists"
        else
            echo "  ⚠️  archive/$dir/ missing (recommended)"
            warnings=$((warnings + 1))
        fi
    done
    echo ""
fi

# Check for misplaced implementation/summary files in active docs
echo "🔍 Checking for Misplaced Files:"
misplaced=0

# Check root level for implementation summaries
if find "$DOCS_DIR" -maxdepth 1 -type f -name "*IMPLEMENTATION*.md" -o -name "*SUMMARY*.md" -o -name "*COMPLETE*.md" -o -name "*FINAL*.md" 2>/dev/null | grep -q .; then
    echo "  ⚠️  Found potential implementation/summary files in /docs root:"
    find "$DOCS_DIR" -maxdepth 1 -type f \( -name "*IMPLEMENTATION*.md" -o -name "*SUMMARY*.md" -o -name "*COMPLETE*.md" -o -name "*FINAL*.md" \) -exec basename {} \; | sed 's/^/     - /'
    echo "     Consider moving to /docs/archive/implementations/"
    warnings=$((warnings + 1))
    misplaced=1
fi

# Check guides/ for implementation summaries
if [ -d "$DOCS_DIR/guides" ]; then
    if find "$DOCS_DIR/guides" -type f \( -name "*IMPLEMENTATION*.md" -o -name "*SUMMARY*.md" -o -name "*COMPLETE*.md" \) 2>/dev/null | grep -q .; then
        echo "  ⚠️  Found potential implementation/summary files in /docs/guides:"
        find "$DOCS_DIR/guides" -type f \( -name "*IMPLEMENTATION*.md" -o -name "*SUMMARY*.md" -o -name "*COMPLETE*.md" \) -exec basename {} \; | sed 's/^/     - /'
        echo "     Consider moving to /docs/archive/implementations/"
        warnings=$((warnings + 1))
        misplaced=1
    fi
fi

# Check specifications/ for implementation summaries
if [ -d "$DOCS_DIR/specifications" ]; then
    if find "$DOCS_DIR/specifications" -type f \( -name "*IMPLEMENTATION*.md" -o -name "*SUMMARY*.md" -o -name "*COMPLETE*.md" \) 2>/dev/null | grep -q .; then
        echo "  ⚠️  Found potential implementation/summary files in /docs/specifications:"
        find "$DOCS_DIR/specifications" -type f \( -name "*IMPLEMENTATION*.md" -o -name "*SUMMARY*.md" -o -name "*COMPLETE*.md" \) -exec basename {} \; | sed 's/^/     - /'
        echo "     Consider moving to /docs/archive/implementations/"
        warnings=$((warnings + 1))
        misplaced=1
    fi
fi

if [ $misplaced -eq 0 ]; then
    echo "  ✅ No misplaced implementation/summary files found"
fi
echo ""

# Check for version-numbered files in active docs
echo "🔢 Checking for Version-Numbered Files:"
version_files=0
if find "$DOCS_DIR" -type f -name "*-v[0-9]*.md" -o -name "*-v[0-9]*.[0-9]*.md" 2>/dev/null | grep -v archive | grep -q .; then
    echo "  ⚠️  Found version-numbered files in active documentation:"
    find "$DOCS_DIR" -type f \( -name "*-v[0-9]*.md" -o -name "*-v[0-9]*.[0-9]*.md" \) | grep -v archive | sed 's|'"$DOCS_DIR"'/|     - |'
    echo "     Consider renaming (put version inside file) or archiving"
    warnings=$((warnings + 1))
    version_files=1
fi

if [ $version_files -eq 0 ]; then
    echo "  ✅ No version-numbered files in active docs"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $errors -eq 0 ] && [ $warnings -eq 0 ]; then
    echo "✅ Documentation structure is valid"
    exit 0
elif [ $errors -eq 0 ]; then
    echo "⚠️  Structure validation passed with $warnings warning(s)"
    exit 0
else
    echo "❌ Structure validation failed with $errors error(s) and $warnings warning(s)"
    exit 1
fi
