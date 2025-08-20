# Scripts Directory

This directory contains various scripts to help with deployment and management of the BarodyBroject application.

## Azure Deployment Scripts

### `azure-deployment-setup.py`
Interactive Python script for setting up a new Azure deployment after running `azd up`. This comprehensive script handles:

- **Prerequisites Check**: Verifies Azure CLI and azd are installed and configured
- **Environment Discovery**: Automatically detects your Azure resources and configuration
- **Database Migrations**: Runs Django migrations to set up the database schema
- **Static Files**: Collects static files for proper CSS/JS serving
- **Admin User Creation**: Interactive creation of Django superuser accounts
- **CMS Setup**: Configures initial Django CMS pages and site settings
- **Health Checks**: Verifies the application is working correctly

**Usage:**
```bash
# From project root
python3 scripts/azure-deployment-setup.py

# Or use the wrapper script
./scripts/setup-deployment.sh
```

**Features:**
- Interactive prompts with colored output
- Error handling and recovery options
- Automatic resource detection
- Comprehensive health checks
- User-friendly progress indicators

### `setup-deployment.sh`
Simple shell script wrapper for the Python setup script. Provides basic environment checks and runs the main setup script.

**Usage:**
```bash
./scripts/setup-deployment.sh
```

## Other Scripts

### `azure-setup.py`
Legacy Azure setup script (consider using the new `azure-deployment-setup.py` instead).

### `setup-azure.sh`
Shell script for Azure resource setup.

### `add_current_ip_rule.py`
Script to add your current IP address to Azure firewall rules.

### `setup_aurora_serverless.py`
Script for setting up Aurora Serverless database (for AWS deployments).

### `version-manager.sh`
Script for managing application versions.

## Prerequisites

Before running the Azure deployment scripts, ensure you have:

1. **Azure CLI** installed and configured
   ```bash
   # Install Azure CLI (macOS)
   brew install azure-cli
   
   # Login to Azure
   az login
   ```

2. **Azure Developer CLI (azd)** installed
   ```bash
   # Install azd (macOS)
   brew install azd
   ```

3. **Successful deployment** with `azd up`
   ```bash
   # Deploy the application first
   azd up
   ```

## Typical Workflow

1. **Initial Deployment**
   ```bash
   # Deploy infrastructure and application
   azd up
   ```

2. **Post-Deployment Setup**
   ```bash
   # Run the interactive setup script
   ./scripts/setup-deployment.sh
   ```

3. **Verification**
   - Visit your application URL
   - Log into the admin panel
   - Verify CMS functionality

## Troubleshooting

### Common Issues

**Script can't find resources:**
- Ensure you're in the correct project directory
- Verify `azd up` completed successfully
- Check that you're logged into the correct Azure account

**Migrations fail:**
- Check database connectivity
- Verify the database server is running
- Ensure proper environment variables are set

**Permission errors:**
- Verify Azure CLI permissions
- Check resource group access
- Ensure container app is running

**Connection timeouts:**
- Check Azure Container App status
- Verify networking and firewall rules
- Try running commands directly with `az containerapp exec`

### Getting Help

If you encounter issues:

1. Check the Azure portal for resource status
2. Review container app logs: `az containerapp logs show --name <app-name> --resource-group <rg-name>`
3. Verify environment variables: `azd env get-values`
4. Test connectivity: `curl -I <app-url>`

## Contributing

When adding new scripts:

1. Follow the existing naming conventions
2. Add appropriate error handling
3. Include usage documentation
4. Make scripts executable: `chmod +x script-name.py`
5. Update this README with script descriptions
