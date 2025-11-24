# Migration Documentation

This directory contains comprehensive migration documentation for the Barodybroject Django application, particularly focused on the v0.2.0 release changes.

## Contents

### Major Migrations

- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - Comprehensive v0.2.0 migration guide
  - Database migration procedures
  - Template system migrations
  - Infrastructure migrations
  - Application configuration changes
  - Rollback procedures

- **[CMS_REMOVAL_GUIDE.md](./CMS_REMOVAL_GUIDE.md)** - Django CMS removal documentation
  - Rationale for CMS removal
  - Detailed changes by component (settings, models, views, templates)
  - Impact assessment
  - Restoration guide for future CMS re-integration
  - Preservation strategy (commenting vs deletion)

## Migration Strategy

The v0.2.0 release involves significant architectural changes:

### What Changed

1. **Django CMS Removal**: Temporarily disabled to simplify deployment
2. **Infrastructure Migration**: Moved from App Service to Container Apps
3. **Port Standardization**: Unified port configuration across all environments
4. **Template Modernization**: Converted from CMS-integrated to pure Django templates

### What Was Preserved

- ✅ Core database models (Post, Category, Tag)
- ✅ User authentication system
- ✅ Admin interface functionality
- ✅ REST API endpoints
- ✅ All CMS code (commented, not deleted)

## Quick Start

### For Existing Deployments

1. **Backup your database**:
   ```bash
   pg_dump barodydb > backup_pre_v0.2.0.sql
   ```

2. **Review migration guide**:
   - Read [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) completely
   - Understand database migration impact
   - Review template changes

3. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Update templates** (if customized):
   - Remove CMS template tags
   - Convert placeholders to blocks
   - Update navigation structure

### For New Deployments

New deployments start with the simplified architecture:
- No CMS dependencies
- Pure Django template system
- Container Apps infrastructure

See [../deployment/DEPLOYMENT-GUIDE-MINIMAL.md](../deployment/DEPLOYMENT-GUIDE-MINIMAL.md) for deployment instructions.

## CMS Restoration

The CMS removal was implemented as **temporary commenting** rather than permanent deletion. To restore CMS functionality:

1. Uncomment CMS-related code in:
   - `settings.py` - INSTALLED_APPS and MIDDLEWARE
   - `models.py` - CMS plugin models
   - `admin.py` - CMS admin mixins
   - `views.py` - CMS imports
   - `urls.py` - CMS URL patterns

2. Restore CMS templates:
   - Uncomment CMS template tags
   - Add back placeholders and toolbars

3. Apply CMS migrations:
   ```bash
   python manage.py migrate cms
   python manage.py migrate menus
   ```

For detailed restoration instructions, see [CMS_REMOVAL_GUIDE.md](./CMS_REMOVAL_GUIDE.md).

## Migration Categories

### 1. Database Migrations
- Core models preserved
- CMS tables intact but unused
- No data loss strategy

### 2. Template System
- Pure Django template inheritance
- Bootstrap 5.3.3 integration
- Responsive design preserved

### 3. Infrastructure
- App Service → Container Apps
- Port standardization (8000)
- Environment configuration updates

### 4. Application Configuration
- Simplified INSTALLED_APPS
- Reduced MIDDLEWARE stack
- Updated template context processors

## Rollback Procedures

Each migration guide includes rollback procedures:

- **Database**: Restore from backup
- **Templates**: Git revert to v0.1.x
- **Infrastructure**: Redeploy previous version
- **CMS**: Uncomment all CMS code

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for detailed rollback instructions.

## Related Documentation

- [Deployment Documentation](../deployment/) - Deployment guides and results
- [Infrastructure Testing](../INFRASTRUCTURE_TESTING.md) - Validation procedures
- [CHANGELOG](../changelog/CHANGELOG.md) - Version history

## Testing Migrations

Before applying migrations to production:

1. **Test in development container**:
   ```bash
   docker-compose -f .devcontainer/docker-compose_dev.yml up
   ```

2. **Run migration validation**:
   ```bash
   python manage.py migrate --plan
   python manage.py check
   ```

3. **Test core functionality**:
   ```bash
   python manage.py test
   ```

4. **Verify data integrity**:
   - Check post count
   - Verify user authentication
   - Test admin access

## Support

For migration issues:
- Review detailed guides in this directory
- Check [../TROUBLESHOOTING.md](../../README.md#troubleshooting)
- Create issue with `migration` label on GitHub
