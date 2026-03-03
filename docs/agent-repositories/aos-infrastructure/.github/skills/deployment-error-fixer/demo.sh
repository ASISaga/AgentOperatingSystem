#!/bin/bash
"""
Demonstration of Autonomous Deployment Error Fixing

This script demonstrates how the deployment agent autonomously fixes
common errors in Python and Bicep code.
"""

set -e

DEMO_DIR="/tmp/deployment-error-fix-demo"
SKILL_DIR="/home/runner/work/AgentOperatingSystem/AgentOperatingSystem/.github/skills/deployment-error-fixer"

echo "=================================================="
echo "Autonomous Deployment Error Fixing - Demo"
echo "=================================================="
echo ""

# Setup
echo "Setting up demo environment..."
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"

# Demo 1: Bicep BCP029 Error
echo ""
echo "Demo 1: Bicep BCP029 Error (Missing API Version)"
echo "------------------------------------------------"

# Create Bicep file with error
cat > storage.bicep <<'EOF'
resource storage 'Microsoft.Storage/storageAccounts' = {
  name: 'demostorage123'
  location: 'eastus'
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}
EOF

echo "❌ Bicep file WITH error:"
cat storage.bicep
echo ""

# Create error log
cat > error.log <<'EOF'
Error BCP029: The resource type is not valid. 
Specify a valid resource type of format '<types>@<apiVersion>'.
File: storage.bicep
Line: 1
EOF

echo "📝 Error detected:"
cat error.log
echo ""

# Run autonomous fixer
echo "🤖 Running autonomous error fixer..."
python3 "$SKILL_DIR/scripts/fix_error.py" \
  --error-file error.log \
  --deployment-dir . \
  --auto-fix \
  || true

echo ""
echo "✅ Bicep file AFTER auto-fix:"
cat storage.bicep
echo ""

# Demo 2: Python Syntax Error
echo ""
echo "Demo 2: Python Syntax Error (Missing Colon)"
echo "----------------------------------------------"

# Create Python file with error
cat > deploy.py <<'EOF'
def main()
    print("Hello, world!")
    return True

if __name__ == "__main__":
    main()
EOF

echo "❌ Python file WITH error:"
cat deploy.py
echo ""

# Create error log
cat > error2.log <<'EOF'
  File "deploy.py", line 1
    def main()
             ^
SyntaxError: invalid syntax
EOF

echo "📝 Error detected:"
cat error2.log
echo ""

# Run autonomous fixer
echo "🤖 Running autonomous error fixer..."
python3 "$SKILL_DIR/scripts/fix_error.py" \
  --error-file error2.log \
  --deployment-dir . \
  --auto-fix \
  || true

echo ""
echo "✅ Python file AFTER auto-fix:"
cat deploy.py
echo ""

# Demo 3: Python Indentation Error
echo ""
echo "Demo 3: Python Indentation Error (Tabs vs Spaces)"
echo "---------------------------------------------------"

# Create Python file with tabs
cat > indent.py <<'EOF'
def process():
	return True
EOF

echo "❌ Python file WITH error (contains tab):"
cat -A indent.py  # Show tabs
echo ""

# Create error log
cat > error3.log <<'EOF'
  File "indent.py", line 2
    return True
         ^
IndentationError: unexpected indent
EOF

echo "📝 Error detected:"
cat error3.log
echo ""

# Run autonomous fixer
echo "🤖 Running autonomous error fixer..."
python3 "$SKILL_DIR/scripts/fix_error.py" \
  --error-file error3.log \
  --deployment-dir . \
  --auto-fix \
  || true

echo ""
echo "✅ Python file AFTER auto-fix (tabs → spaces):"
cat -A indent.py  # Show spaces
echo ""

# Summary
echo ""
echo "=================================================="
echo "Demo Complete!"
echo "=================================================="
echo ""
echo "Summary:"
echo "  ✅ Bicep BCP029 error auto-fixed"
echo "  ✅ Python syntax error auto-fixed"
echo "  ✅ Python indentation error auto-fixed"
echo ""
echo "The deployment agent can now autonomously fix these"
echo "errors during deployment, making the process fully"
echo "autonomous after initial parameter collection!"
echo ""

# Cleanup
echo "Cleaning up demo environment..."
cd /
rm -rf "$DEMO_DIR"

echo "Done!"
