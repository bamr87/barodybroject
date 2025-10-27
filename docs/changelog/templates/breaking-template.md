---
title: "[BREAKING] - Brief Description"
type: "breaking"
version: "X.Y.Z"
date: "YYYY-MM-DD"
author: "Author Name <email@domain.com>"
reviewers: []
related_issues: []
related_prs: []
impact: "high"
breaking: true
migration_required: true
deprecation_notice: "X.Y.Z"
removal_version: "X+1.Y.Z"
---

# Breaking Change: [Breaking Change Title]

> **⚠️ BREAKING CHANGE**: This update includes breaking changes that require user action before upgrading.

## 🚨 Breaking Change Summary

### What Changed
Clear, non-technical description of what functionality changed or was removed.

### Who Is Affected
- **API Users**: Specific endpoints or response formats changed
- **Configuration Users**: Settings or environment variables modified
- **Database Users**: Schema changes requiring migration
- **Integration Partners**: External integrations affected
- **End Users**: UI or workflow changes

### Impact Level
- **Critical**: Application will not work without changes
- **High**: Major functionality will break
- **Medium**: Some features will be degraded
- **Low**: Minor compatibility issues

### Timeline
- **Deprecation Notice**: Version when deprecation was announced
- **Breaking Change**: Current version implementing the change
- **Support End**: When old functionality support ends completely

## 📋 Detailed Changes

### API Breaking Changes

#### Removed Endpoints
```bash
# REMOVED in v2.0.0
DELETE /api/v1/legacy-endpoint
GET    /api/v1/old-data-format

# REPLACED WITH
DELETE /api/v2/new-endpoint
GET    /api/v2/enhanced-data-format
```

#### Modified Request/Response Formats
```json
// BEFORE (v1.x)
{
  "user_id": 123,
  "user_name": "john_doe",
  "created": "2025-01-27"
}

// AFTER (v2.0)
{
  "id": 123,
  "username": "john_doe",
  "createdAt": "2025-01-27T10:00:00Z",
  "profile": {
    "email": "john@example.com",
    "status": "active"
  }
}
```

#### Authentication Changes
```bash
# BEFORE: API Key in header
curl -H "X-API-Key: your-key" https://api.example.com/data

# AFTER: Bearer token authentication
curl -H "Authorization: Bearer your-jwt-token" https://api.example.com/data
```

### Configuration Breaking Changes

#### Environment Variables
```bash
# REMOVED
DATABASE_URL=postgres://...
REDIS_URL=redis://...

# REPLACED WITH
DATABASE_CONNECTION_STRING=postgres://...
CACHE_CONNECTION_STRING=redis://...
```

#### Configuration File Format
```yaml
# BEFORE (config.yml)
database:
  host: localhost
  port: 5432
  name: mydb

# AFTER (config.yml)
connections:
  primary_db:
    type: postgresql
    host: localhost
    port: 5432
    database: mydb
    ssl: required
```

### Database Schema Changes

#### Table Structure Changes
```sql
-- REMOVED COLUMNS
ALTER TABLE users DROP COLUMN old_field;
ALTER TABLE posts DROP COLUMN deprecated_status;

-- ADDED REQUIRED COLUMNS
ALTER TABLE users ADD COLUMN email VARCHAR(255) NOT NULL;
ALTER TABLE posts ADD COLUMN status_id INTEGER NOT NULL;

-- RENAMED TABLES
ALTER TABLE user_profiles RENAME TO user_details;
```

#### Data Model Changes
```python
# BEFORE
class User(models.Model):
    username = models.CharField(max_length=50)
    created = models.DateField()
    is_active = models.BooleanField()

# AFTER
class User(models.Model):
    username = models.CharField(max_length=100)  # Increased length
    created_at = models.DateTimeField()          # Changed field name and type
    status = models.CharField(max_length=20)     # Replaced boolean with choices
```

### Code API Breaking Changes

#### Method Signatures
```python
# BEFORE
def process_data(data, format='json'):
    return parse_data(data, format)

# AFTER
def process_data(data: Dict[str, Any], 
                output_format: Literal['json', 'xml'] = 'json',
                validate: bool = True) -> ProcessedData:
    if validate:
        validate_input(data)
    return parse_data(data, output_format)
```

#### Class Interface Changes
```python
# BEFORE
class DataProcessor:
    def __init__(self, config_file):
        self.config = load_config(config_file)
    
    def process(self, data):
        return self._internal_process(data)

# AFTER
class DataProcessor:
    def __init__(self, config: ProcessorConfig):
        self.config = config
    
    def process(self, data: InputData) -> ProcessedData:
        return self._internal_process(data)
    
    # Removed: _internal_process is now private implementation
```

## 🔄 Migration Guide

### Automated Migration Tools

#### Database Migration
```bash
# Run automatic database migration
python manage.py migrate_to_v2

# Verify migration success
python manage.py check_migration_status
```

#### Configuration Migration
```bash
# Convert old configuration format
python manage.py migrate_config --input config.old.yml --output config.yml

# Validate new configuration
python manage.py validate_config config.yml
```

#### Code Migration Script
```bash
# Automated code updates (where possible)
python scripts/migrate_v1_to_v2.py --source src/ --backup backup/

# Manual review required for:
# - Custom API integrations
# - Complex business logic
# - Third-party integrations
```

### Manual Migration Steps

#### Step 1: Update Dependencies
```bash
# Update package.json or requirements.txt
npm install package-name@^2.0.0
# OR
pip install package-name>=2.0.0

# Remove deprecated dependencies
npm uninstall deprecated-package
pip uninstall deprecated-package
```

#### Step 2: Update Configuration
```bash
# 1. Backup current configuration
cp config.yml config.yml.backup

# 2. Update configuration format
# Use migration guide to convert:
# old_setting: value
# TO:
# new_settings:
#   parameter: value

# 3. Update environment variables
export NEW_VAR_NAME=$OLD_VAR_NAME
unset OLD_VAR_NAME
```

#### Step 3: Update API Calls
```javascript
// BEFORE
fetch('/api/v1/users')
  .then(response => response.json())
  .then(users => {
    users.forEach(user => {
      console.log(user.user_name);
    });
  });

// AFTER
fetch('/api/v2/users', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
  .then(response => response.json())
  .then(users => {
    users.forEach(user => {
      console.log(user.username);
    });
  });
```

#### Step 4: Update Database Schema
```bash
# 1. Backup database
pg_dump mydb > backup_$(date +%Y%m%d).sql

# 2. Run migration
python manage.py migrate

# 3. Verify data integrity
python manage.py check_data_integrity
```

### Migration Validation

#### Pre-Migration Checklist
- [ ] Current system backed up completely
- [ ] Migration scripts tested in staging environment
- [ ] Rollback procedure documented and tested
- [ ] Team trained on new APIs and workflows
- [ ] Customer communication prepared

#### Migration Testing
```bash
# Test suite for migration validation
python -m pytest tests/migration/
python -m pytest tests/api/v2/
python -m pytest tests/integration/

# Performance validation
python scripts/performance_baseline.py --before-migration
python scripts/performance_baseline.py --after-migration
```

#### Post-Migration Validation
- [ ] All services start successfully
- [ ] API endpoints respond correctly
- [ ] Database queries perform as expected
- [ ] User workflows function properly
- [ ] Integration tests pass

## ⚠️ Common Migration Issues

### Issue 1: Authentication Failures
**Problem**: Old API keys no longer work
```bash
# Solution: Generate new JWT tokens
curl -X POST /api/auth/token \
  -d '{"username": "user", "password": "pass"}' \
  -H "Content-Type: application/json"
```

### Issue 2: Data Format Errors
**Problem**: Client expects old JSON format
```python
# Temporary compatibility layer (remove in v2.1)
def legacy_user_format(user_data):
    return {
        "user_id": user_data["id"],
        "user_name": user_data["username"],
        "created": user_data["createdAt"].split("T")[0]
    }
```

### Issue 3: Configuration Loading Errors
**Problem**: Old configuration keys not recognized
```yaml
# Use configuration mapping during transition
legacy_mapping:
  DATABASE_URL: connections.primary_db.connection_string
  REDIS_URL: connections.cache.connection_string
```

### Issue 4: Database Query Failures
**Problem**: Queries reference renamed columns
```python
# Update all queries
# BEFORE
User.objects.filter(created__gte=date)

# AFTER
User.objects.filter(created_at__gte=datetime)
```

## 🔄 Rollback Procedures

### Emergency Rollback
```bash
# 1. Stop current version
docker-compose down

# 2. Restore previous version
git checkout v1.9.9
docker-compose up -d

# 3. Restore database (if needed)
pg_restore --clean --if-exists backup_before_migration.sql
```

### Gradual Rollback
```bash
# 1. Enable feature flag to use old API
export USE_LEGACY_API=true

# 2. Route traffic back to v1 endpoints
# Update load balancer configuration

# 3. Monitor for stability
# Ensure all services are healthy
```

### Data Rollback
```sql
-- Rollback database schema changes
-- (Only if data loss is acceptable)
DROP TABLE new_user_details;
ALTER TABLE user_details RENAME TO user_profiles;
ALTER TABLE users DROP COLUMN email;
```

## 📅 Deprecation Timeline

### Version History
- **v1.8.0** (2024-10-01): Deprecation warnings added
- **v1.9.0** (2024-12-01): Migration tools released
- **v2.0.0** (2025-01-27): Breaking changes implemented
- **v2.1.0** (2025-04-01): Legacy compatibility removed

### Support Timeline
- **v1.x Support**: Extended until July 2025
- **Critical Bugs**: Fixed in both v1.x and v2.x until July 2025
- **Security Issues**: Patched in both versions until July 2025
- **New Features**: Only added to v2.x branch

### End-of-Life Notice
- **Final v1.x Release**: July 31, 2025
- **End of Support**: July 31, 2025
- **Security Updates Only**: Until January 31, 2026
- **Complete EOL**: January 31, 2026

## 📞 Support and Resources

### Migration Support
- **Documentation**: [Migration Guide](../migration/v1-to-v2.md)
- **Support Channel**: #migration-support on Slack
- **Office Hours**: Daily 2-4 PM EST for migration questions
- **Video Tutorial**: [YouTube Migration Walkthrough](https://youtube.com/watch)

### Community Resources
- **Migration Forum**: [Community Discussion](https://forum.example.com/migration)
- **Example Migrations**: [GitHub Repository](https://github.com/example/migration-examples)
- **Migration Checklist**: [Downloadable PDF](https://example.com/migration-checklist.pdf)

### Professional Services
- **Migration Consulting**: Available for complex environments
- **Custom Migration Tools**: Development for enterprise customers
- **Training Sessions**: Team training on new APIs and workflows
- **Priority Support**: Expedited support during migration

## 🔗 Additional Resources

### Documentation
- [Complete Migration Guide](../migration/comprehensive-guide.md)
- [API v2 Documentation](../api/v2/overview.md)
- [Configuration Reference](../configuration/v2-settings.md)
- [Troubleshooting Guide](../troubleshooting/migration-issues.md)

### Tools and Scripts
- [Migration Validation Tools](https://github.com/example/migration-tools)
- [Configuration Converter](https://github.com/example/config-converter)
- [API Compatibility Tester](https://github.com/example/api-tester)

### Issues and Discussions
- Breaking Change Discussion: #123
- Migration Implementation: #456
- Community Feedback: #789

---

## ✅ Breaking Change Release Checklist

### Pre-Release
- [ ] Deprecation warnings in place for 3+ versions
- [ ] Migration tools developed and tested
- [ ] Documentation complete and reviewed
- [ ] Community notified with sufficient lead time
- [ ] Customer communication sent

### Release Day
- [ ] Migration guide published
- [ ] Support team briefed and ready
- [ ] Monitoring enhanced for migration issues
- [ ] Rollback procedures tested and ready
- [ ] Community channels monitored

### Post-Release
- [ ] Migration success rate monitored
- [ ] User feedback collected and addressed
- [ ] Common issues documented
- [ ] Additional tooling developed as needed
- [ ] Success metrics tracked

### Follow-up
- [ ] Migration completion rate tracked
- [ ] Legacy system sunset planned
- [ ] Lessons learned documented
- [ ] Process improvements identified
- [ ] Next breaking change planning begins

---

**Template Version**: 1.0.0  
**Last Updated**: January 27, 2025  
**Template Maintainer**: Barodybroject Team

> **CRITICAL NOTE**: Breaking changes require extensive planning, communication, and support. Use this template to ensure all stakeholders are properly informed and supported through the migration process.