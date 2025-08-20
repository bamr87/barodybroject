# Azure Deployment Setup Examples

This file contains examples of what the setup script will do and what prompts you'll see.

## Example Setup Run

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║         Azure Deployment Setup for BarodyBroject        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

This script will help you set up your Django application after deployment.
It will run migrations, create admin users, and configure your app.

Do you want to continue with the setup? (y/n): y

============================================================
                   Checking Prerequisites                   
============================================================
✓ Azure CLI is installed
✓ Azure Developer CLI (azd) is installed
✓ Logged into Azure as: user@example.com

============================================================
                Getting Environment Information             
============================================================
✓ Environment: my-app-prod
✓ Resource Group: rg-my-app-prod
✓ Location: eastus2
✓ Container App: src
✓ App URL: https://src.example.azurecontainerapps.io

============================================================
              Testing Application Connectivity             
============================================================
✓ Application is responding

============================================================
                Running Database Migrations                
============================================================
This will run Django migrations to set up the database schema.
Do you want to run migrations? (y/n): y
Running migrations...
✓ Migrations completed successfully

============================================================
                 Collecting Static Files                   
============================================================
This will collect static files for proper CSS/JS serving.
Do you want to collect static files? (y/n): y
Collecting static files...
✓ Static files collected successfully

============================================================
                Creating Superuser Account                 
============================================================
A superuser account is needed to access the Django admin panel.
Do you want to create a superuser account? (y/n): y
Enter username for superuser: admin
Enter email for superuser: admin@example.com
Enter password for superuser: [hidden]
Confirm password: [hidden]
Creating superuser...
✓ Superuser 'admin' created successfully
ℹ Admin URL: https://src.example.azurecontainerapps.io/admin/

============================================================
                  Setting Up CMS Pages                     
============================================================
This will create initial CMS pages and configure the site.
Do you want to set up initial CMS pages? (y/n): y
Setting up CMS pages...
✓ CMS pages set up successfully

============================================================
                  Running Health Check                     
============================================================
✓ Main application is responding
✓ Admin panel is accessible

============================================================
               Deployment Setup Complete                   
============================================================

Your Django application is now set up!

Application Details:
  • App URL: https://src.example.azurecontainerapps.io
  • Admin URL: https://src.example.azurecontainerapps.io/admin/
  • Resource Group: rg-my-app-prod
  • Container App: src

Next Steps:
  1. Visit your application URL to verify it's working
  2. Log into the admin panel with your superuser account
  3. Configure your Django CMS pages and content
  4. Set up any additional configuration as needed

Remember to:
  • Regularly backup your database
  • Monitor your Azure costs
  • Keep your dependencies updated
```

## Common Prompts and Responses

### Prerequisites Check
The script will verify that you have:
- Azure CLI installed and logged in
- Azure Developer CLI (azd) installed
- Successfully deployed with `azd up`

### Environment Detection
The script automatically detects:
- Your resource group name
- Container app name
- Application URL
- Azure environment settings

### Migration Prompts
```
Do you want to run migrations? (y/n): y
```
- Choose 'y' for new deployments
- Choose 'n' if migrations were already run

### Static Files Prompts
```
Do you want to collect static files? (y/n): y
```
- Usually choose 'y' to ensure CSS/JS work properly
- Safe to run multiple times

### Superuser Creation
```
Enter username for superuser: admin
Enter email for superuser: admin@example.com
Enter password for superuser: [minimum 8 characters]
Confirm password: [same password]
```
- Choose a secure username and password
- Email should be valid for admin notifications

### CMS Setup
```
Do you want to set up initial CMS pages? (y/n): y
```
- Choose 'y' for new deployments
- Creates a home page and configures site settings

## Error Handling

The script handles common errors gracefully:

### If migrations fail:
```
✗ Migrations failed
Migrations failed. Continue anyway? (y/n):
```

### If superuser creation fails:
```
✗ Superuser creation failed
Superuser creation failed. Continue anyway? (y/n):
```

### If prerequisites are missing:
```
✗ Azure CLI is not installed or not in PATH
```
The script will exit and show installation instructions.

## Manual Commands

If you prefer to run commands manually, here are the equivalents:

### Run migrations:
```bash
az containerapp exec --name <app-name> --resource-group <rg-name> --command "python manage.py migrate"
```

### Collect static files:
```bash
az containerapp exec --name <app-name> --resource-group <rg-name> --command "python manage.py collectstatic --noinput"
```

### Create superuser:
```bash
az containerapp exec --name <app-name> --resource-group <rg-name> --command "python manage.py createsuperuser"
```

## Tips

1. **Run from project root**: The script works best when run from the project root directory
2. **Have credentials ready**: Know what username/password you want for the admin user
3. **Check connectivity**: Ensure you have internet access and Azure permissions
4. **Be patient**: Some operations (especially migrations) can take a few minutes
