#!/bin/bash

# Create directory structure
mkdir -p docs/migration
mkdir -p docs/infrastructure
mkdir -p docs/deployment
mkdir -p docs/troubleshooting
mkdir -p docs/reports

# Function to move file using git mv if available, else mv
move_file() {
    if [ -f "$1" ]; then
        echo "Moving $1 to $2..."
        if [ -d ".git" ]; then
            git mv "$1" "$2"
        else
            mv "$1" "$2"
        fi
    else
        echo "Warning: $1 not found (skipping)"
    fi
}

# Move files to organized locations
move_file "CMS_REMOVAL_GUIDE.md" "docs/migration/cms-removal.md"
move_file "MIGRATION_GUIDE.md" "docs/migration/v0.2.0-guide.md"
move_file "INFRASTRUCTURE_CHANGES.md" "docs/infrastructure/v0.2.0-changes.md"
move_file "QUOTA_ISSUE_SOLUTIONS.md" "docs/troubleshooting/azure-quota.md"
move_file "DEPLOYMENT-GUIDE-MINIMAL.md" "docs/deployment/minimal-guide.md"
move_file "DEPLOYMENT-SUCCESS.md" "docs/reports/v0.2.0-deployment-success.md"
move_file "WORKFLOW_REVIEW_COMPLETE.md" "docs/reports/workflow-review-2025-10.md"

echo "Documentation organized successfully."
