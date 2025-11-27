---
agent: agent
mode: agent
description: "Review changes, run tests, update documentation, bump version, and publish"
---

# Commit & Publish Workflow

Review open changes, run appropriate tests, create/update documentation, update the changelog, bump the version according to semantic versioning, and prepare for publication.

## Task Overview

Execute the complete release pipeline for the current changes in the repository.

## Step 1: Review Open Changes

1. **Analyze Git Changes**:
   - Run `git status` to identify all modified, added, and deleted files
   - Run `git diff --cached` for staged changes and `git diff` for unstaged changes
   - Categorize changes by type:
     - **Features**: New functionality added
     - **Bug Fixes**: Issues resolved
     - **Breaking Changes**: Changes that break backward compatibility
     - **Documentation**: Documentation updates
     - **Refactoring**: Code improvements without functionality changes
     - **Dependencies**: Package version updates
     - **Tests**: Test additions or modifications
     - **UI/UX**: Template, CSS, or JavaScript changes

2. **Summarize Changes**:
   - Create a concise summary of all changes
   - Identify the impact level (major, minor, patch)
   - Note any breaking changes that require migration

## Step 2: Run Appropriate Tests

1. **Identify Test Requirements**:
   - Based on changed files, determine which tests to run
   - For Django models/views changes → run Django tests
   - For template changes → run template rendering tests
   - For API changes → run API tests
   - For all changes → run full test suite

2. **Execute Tests**:
   ```bash
   # Run Django tests in development container
   docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py test
   
   # Run pytest with coverage
   docker-compose -f .devcontainer/docker-compose_dev.yml exec python python -m pytest --cov=parodynews
   ```

3. **Verify Test Results**:
   - Ensure all tests pass before proceeding
   - If tests fail, stop and report the failures
   - Document test coverage percentage

## Step 3: Create/Update Documentation

1. **Update Affected README Files**:
   - Follow README-First, README-Last principle
   - Update any README.md files in directories with changed files
   - Ensure all new features are documented

2. **Update Docstrings**:
   - Verify all new/modified functions have proper docstrings
   - Use Google-style docstrings format
   - Include Args, Returns, Raises, and Examples sections

3. **Update API Documentation**:
   - If API endpoints changed, update API documentation
   - Document request/response formats with examples

## Step 4: Update CHANGELOG.md

1. **Determine Version Type** based on changes:
   - **MAJOR** (X.0.0): Breaking changes, API incompatibilities
   - **MINOR** (0.X.0): New features, backward-compatible
   - **PATCH** (0.0.X): Bug fixes, minor improvements

2. **Add Changelog Entry** following Keep a Changelog format:
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD
   
   ### Added
   - New features
   
   ### Changed
   - Changes to existing functionality
   
   ### Deprecated
   - Features marked for removal
   
   ### Removed
   - Removed features
   
   ### Fixed
   - Bug fixes
   
   ### Security
   - Security updates
   ```

3. **Reference Issues/PRs** if applicable

## Step 5: Bump Version

1. **Update VERSION file**:
   ```bash
   echo "X.Y.Z" > VERSION
   ```

2. **Update pyproject.toml**:
   - Update `version = "X.Y.Z"` in `[project]` section

3. **Verify Version Consistency**:
   - Ensure VERSION file matches pyproject.toml
   - Check CHANGELOG.md has entry for new version

## Step 6: Prepare for Publication

1. **Stage All Changes**:
   ```bash
   git add -A
   ```

2. **Create Semantic Commit Message**:
   Format: `<type>(<scope>): <description>`
   
   Types:
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code style changes
   - `refactor`: Code refactoring
   - `test`: Test additions/changes
   - `chore`: Maintenance tasks
   - `breaking`: Breaking changes

3. **Commit Changes**:
   ```bash
   git commit -m "<type>(<scope>): <description>

   <detailed description of changes>

   - Change 1
   - Change 2
   - Change 3

   Closes #<issue-number> (if applicable)"
   ```

4. **Create Git Tag** (for releases):
   ```bash
   git tag -a v<X.Y.Z> -m "Release v<X.Y.Z>: <summary>"
   ```

5. **Push Changes**:
   ```bash
   git push origin main
   git push origin --tags
   ```

## Success Criteria

- [ ] All tests pass with no failures
- [ ] Test coverage maintained or improved
- [ ] All changed code has proper documentation
- [ ] CHANGELOG.md updated with new version entry
- [ ] VERSION file updated to new version
- [ ] pyproject.toml version matches VERSION file
- [ ] Git commit follows semantic commit format
- [ ] Changes pushed to remote repository
- [ ] Git tag created for releases (optional)

## Output Format

After completing all steps, provide a summary:

```markdown
## Release Summary

**Version**: X.Y.Z (from X.Y.Z)
**Type**: MAJOR | MINOR | PATCH
**Date**: YYYY-MM-DD

### Changes Included
- [ ] Feature 1
- [ ] Fix 1
- [ ] etc.

### Test Results
- Total Tests: X
- Passed: X
- Failed: X
- Coverage: X%

### Files Modified
- path/to/file1.py
- path/to/file2.html

### Documentation Updated
- [ ] README.md
- [ ] CHANGELOG.md
- [ ] API docs

### Commit Information
- Hash: <commit-hash>
- Message: <commit-message>
- Tag: v<version> (if created)
```

## Rollback Procedure

If issues are discovered after publication:

1. Revert the commit:
   ```bash
   git revert <commit-hash>
   ```

2. Delete the tag (if created):
   ```bash
   git tag -d v<version>
   git push origin :refs/tags/v<version>
   ```

3. Create a patch release with the fix

---

**Note**: Always run tests in the Docker development container to ensure environment consistency. Never publish without passing tests.