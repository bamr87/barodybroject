#!/bin/bash

# Script to organize documentation files into proper structure
# Moves files from root directory to organized docs/ structure

set -e

echo "📚 Organizing documentation files..."

# Create directory structure
mkdir -p docs/{migration,infrastructure,deployment,troubleshooting,reports}

# Function to move files using git mv if in git repo, otherwise mv
move_file() {
    local source="$1"
    local destination="$2"
    
    if [ ! -f "$source" ]; then
        echo "⚠️  Warning: $source not found (skipping)"
        return 0
    fi
    
    echo "📄 Moving $source → $destination"
    
    # Create destination directory if it doesn't exist
    mkdir -p "$(dirname "$destination")"
    
    # Use git mv if we're in a git repository, otherwise use regular mv
    if [ -d ".git" ]; then
        git mv "$source" "$destination"
    else
        mv "$source" "$destination"
    fi
}

# Move files to organized structure
move_file "MIGRATION_GUIDE.md" "docs/migration/v0.2.0-guide.md"
move_file "CMS_REMOVAL_GUIDE.md" "docs/migration/cms-removal.md"
move_file "INFRASTRUCTURE_CHANGES.md" "docs/infrastructure/v0.2.0-changes.md"
move_file "DEPLOYMENT-SUCCESS.md" "docs/reports/v0.2.0-deployment-success.md"
move_file "DEPLOYMENT-GUIDE-MINIMAL.md" "docs/deployment/minimal-guide.md"
move_file "QUOTA_ISSUE_SOLUTIONS.md" "docs/troubleshooting/azure-quota.md"
move_file "WORKFLOW_REVIEW_COMPLETE.md" "docs/reports/workflow-review-2025-10.md"

echo "✅ Documentation organization complete!"
echo ""
echo "📋 Summary:"
echo "   • Migration guides: docs/migration/"
echo "   • Infrastructure docs: docs/infrastructure/"
echo "   • Deployment guides: docs/deployment/"
echo "   • Troubleshooting: docs/troubleshooting/"
echo "   • Reports: docs/reports/"
echo ""
echo "🔍 Next steps:"
echo "   • Review organized documentation in docs/"
echo "   • Update any internal links in documentation"
echo "   • Commit the reorganized structure"

# Optional: Update links in README.md and other files
if command -v sed >/dev/null 2>&1; then
    echo "🔗 Updating documentation links..."
    
    # Update links in main README if it exists
    if [ -f "README.md" ]; then
        # Update common documentation links
        sed -i.bak 's|MIGRATION_GUIDE\.md|docs/migration/v0.2.0-guide.md|g' README.md
        sed -i.bak 's|CMS_REMOVAL_GUIDE\.md|docs/migration/cms-removal.md|g' README.md
        sed -i.bak 's|INFRASTRUCTURE_CHANGES\.md|docs/infrastructure/v0.2.0-changes.md|g' README.md
        sed -i.bak 's|DEPLOYMENT-SUCCESS\.md|docs/reports/v0.2.0-deployment-success.md|g' README.md
        sed -i.bak 's|DEPLOYMENT-GUIDE-MINIMAL\.md|docs/deployment/minimal-guide.md|g' README.md
        
        # Clean up backup file
        rm -f README.md.bak
        
        echo "   ✅ Updated links in README.md"
    fi
fi

echo ""
echo "🎉 Documentation cleanup complete!"
