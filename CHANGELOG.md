# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-27

### Added
- **Azure Container Apps Deployment**: Successfully deployed to Azure Container Apps as alternative to App Service quota limitations
- **Comprehensive Deployment Documentation**: Added `DEPLOYMENT-GUIDE-MINIMAL.md` with step-by-step Azure deployment instructions
- **Deployment Success Documentation**: Added `DEPLOYMENT-SUCCESS.md` documenting successful Container Apps deployment process
- **Quota Issue Solutions**: Added `QUOTA_ISSUE_SOLUTIONS.md` with comprehensive troubleshooting for Azure quota limitations
- **Docker Configuration**: Added new `Dockerfile` optimized for Container Apps deployment
- **Minimal Cost Infrastructure**: Added Azure Bicep templates for cost-optimized deployment:
  - `infra/minimal/app-service.bicep` - B1 tier App Service configuration
  - `infra/minimal/db-postgres-minimal.bicep` - Burstable PostgreSQL configuration
  - `infra/minimal/main.bicep` - Minimal cost deployment template
- **Template Validation**: Added `src/parodynews/templates/test.html` for deployment testing
- **Azure CLI Configuration**: Enhanced `azure.yaml` with Container Apps configuration

### Changed
- **🔧 Port Configuration**: Standardized application port from 80 to 8000 across all deployment configurations
  - Updated `infra/app/src.bicep` targetPort and PORT environment variable
  - Updated container configuration for consistency
- **🎨 Template System Overhaul**: Completely refactored Django templates to remove CMS dependencies
  - `base.html`: Removed all CMS template tags (`cms_tags`, `menu_tags`, `sekizai_tags`)
  - Streamlined template structure with pure Bootstrap 5.3.3 implementation
  - Removed CMS placeholder tags and menu generation
- **🗄️ Database Configuration**: Updated `infra/main.parameters.json` with minimal cost PostgreSQL settings
- **📦 Infrastructure Parameters**: Refined deployment parameters for cost optimization

### Removed
- **🚫 Django CMS Dependencies**: Systematic removal of CMS functionality across entire application
  - **Settings**: Commented out 36 CMS-related apps in `INSTALLED_APPS`:
    - `cms`, `menus`, `sekizai`, `djangocms_admin_style`
    - All CMS plugin apps (`djangocms_text_ckeditor`, `djangocms_link`, etc.)
  - **Models**: Disabled CMS-dependent models in `src/parodynews/models.py`:
    - Commented out `Entry` model with CMS placeholders
    - Commented out `PostPluginModel` CMS plugin model
  - **Admin**: Removed CMS admin integration in `src/parodynews/admin.py`:
    - Commented out `FrontendEditableAdminMixin` imports and usage
    - Simplified admin interface without CMS dependencies
  - **Views**: Cleaned up CMS imports in `src/parodynews/views.py`:
    - Commented out CMS-related imports and functionality
  - **URLs**: Disabled CMS URL patterns in `src/barodybroject/urls.py`:
    - Commented out CMS URL includes and i18n patterns
  - **Templates**: Complete CMS template tag removal across all templates
- **Legacy Docker Configuration**: Removed outdated Docker Compose configurations
- **Unused Documentation**: Cleaned up deprecated deployment documentation

### Fixed
- **🔗 Port Mismatch Issues**: Resolved port configuration conflicts between infrastructure and application
- **🚀 Deployment Consistency**: Fixed deployment issues by standardizing on Container Apps approach
- **📝 Template Rendering**: Resolved CMS template tag errors by systematic removal
- **💰 Cost Optimization**: Addressed quota limitations with minimal cost infrastructure alternatives

### Security
- **🔐 Environment Variables**: Improved secret management in Container Apps deployment
- **🛡️ Database Security**: Enhanced PostgreSQL security configuration in minimal deployment

### Documentation
- **📚 Deployment Guides**: Complete deployment documentation with multiple Azure options
- **🏗️ Infrastructure Documentation**: Comprehensive Bicep template documentation
- **🔄 Migration Guides**: Documentation for CMS removal and restoration processes
- **💸 Cost Management**: Detailed cost optimization strategies and quota management

### Technical Details
- **Framework**: Django 4.2.20 with streamlined dependencies
- **Infrastructure**: Azure Container Apps with PostgreSQL
- **Deployment**: Bicep Infrastructure as Code with minimal cost configuration
- **Frontend**: Bootstrap 5.3.3 with pure Django templates
- **Container**: Docker-optimized for Azure Container Apps

---

## Release Notes for v0.2.0

This major release represents a significant architectural shift in the Barodybroject application:

### 🎯 **Major Achievement: Successful Azure Deployment**
After overcoming initial quota limitations with Azure App Service, we successfully deployed to Azure Container Apps, providing a robust and scalable platform for the parody news generator.

### 🔧 **CMS Removal Strategy**
The systematic removal of Django CMS was implemented with careful commenting rather than deletion, allowing for potential future restoration while immediately resolving deployment conflicts and simplifying the application architecture.

### 💰 **Cost Optimization Focus**
All infrastructure changes prioritize minimal cost deployment options while maintaining functionality, making the project accessible for development and small-scale production use.

### 🚀 **Deployment Success**
The application is now successfully running on Azure Container Apps with:
- Reliable PostgreSQL database connectivity
- Consistent port configuration (8000)
- Streamlined template system
- Comprehensive deployment documentation

### 🔄 **Future Considerations**
- CMS functionality can be restored by uncommenting the systematically marked code sections
- Infrastructure can be scaled up by switching from minimal to standard Bicep templates
- Template system is ready for enhanced UI development with Bootstrap foundation

---

*For detailed deployment instructions, see [DEPLOYMENT-GUIDE-MINIMAL.md](DEPLOYMENT-GUIDE-MINIMAL.md)*
*For troubleshooting, see [QUOTA_ISSUE_SOLUTIONS.md](QUOTA_ISSUE_SOLUTIONS.md)*
*For deployment success details, see [DEPLOYMENT-SUCCESS.md](DEPLOYMENT-SUCCESS.md)*