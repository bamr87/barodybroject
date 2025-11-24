# 🚀 Quick Deployment Guide - Minimal Cost Setup

## Prerequisites

- [x] Azure CLI installed and logged in
- [x] Azure Developer CLI (azd) installed
- [x] Docker Desktop installed and running
- [x] Docker Hub account (free tier)

## Step-by-Step Deployment

### 1️⃣ Prepare Docker Image

```bash
# Navigate to project root
cd /Users/bamr87/github/barodybroject

# Login to Docker Hub
docker login
# Enter your Docker Hub username and password

# Build the Docker image
docker build -t yourusername/barodybroject:latest -f src/Dockerfile src/

# Push to Docker Hub (make it public for free hosting)
docker push yourusername/barodybroject:latest

# Verify image is accessible
docker pull yourusername/barodybroject:latest
```

### 2️⃣ Configure Azure Environment

```bash
# Check current azd environment
azd env list

# Set required environment variables
azd env set DB_PASSWORD "YourSecurePassword123!"
azd env set DOCKER_IMAGE "yourusername/barodybroject:latest"

# Verify settings
azd env get-values
```

### 3️⃣ Deploy to Azure

```bash
# Preview changes (dry run)
azd provision --preview

# Deploy infrastructure only
azd provision

# Or deploy everything (infrastructure + app)
azd up
```

### 4️⃣ Verify Deployment

```bash
# Get the app URL from outputs
azd env get-values | grep APP_SERVICE_URL

# Test the application
curl https://your-app.azurewebsites.net

# Check logs if needed
az webapp log tail \
  --name $(azd env get-values | grep APP_SERVICE_NAME | cut -d'=' -f2 | tr -d '"') \
  --resource-group $(azd env get-values | grep RESOURCE_GROUP_NAME | cut -d'=' -f2 | tr -d '"')
```

## 📊 Expected Resources Created

✅ Resource Group: `rg-barody-prod-1`  
✅ App Service Plan (B1): `plan-<random>`  
✅ App Service: `app-<random>`  
✅ PostgreSQL Flexible Server (B1ms): `psql-<random>`  
✅ PostgreSQL Database: `barodydb`

## 💰 Cost Breakdown

| Resource | SKU | Monthly Cost |
|----------|-----|--------------|
| App Service Plan | B1 (1 core, 1.75GB RAM) | $13.14 |
| PostgreSQL Server | B1ms (1 core, 2GB RAM, 32GB storage) | $12.41 |
| **Total** | | **$25.55** |

## 🔍 Troubleshooting

### Issue: Docker build fails

**Error**: `Cannot connect to Docker daemon`

**Solution**:
```bash
# Start Docker Desktop
open -a Docker

# Wait for Docker to start, then retry
docker ps
```

### Issue: Docker Hub push fails

**Error**: `denied: requested access to the resource is denied`

**Solution**:
```bash
# Ensure you're logged in
docker logout
docker login

# Use correct username (must match Docker Hub account)
docker tag yourusername/barodybroject:latest yourusername/barodybroject:latest
docker push yourusername/barodybroject:latest
```

### Issue: azd provision fails with "parameter not found"

**Error**: `Parameter 'databasePassword' not found`

**Solution**:
```bash
# Set all required parameters
azd env set DB_PASSWORD "YourPassword123!"
azd env set DOCKER_IMAGE "yourusername/barodybroject:latest"

# Retry
azd provision
```

### Issue: App Service can't pull Docker image

**Error**: `Failed to pull image`

**Solution**:
```bash
# Ensure Docker image is PUBLIC on Docker Hub
# OR configure credentials in App Service:

az webapp config container set \
  --name <app-name> \
  --resource-group <rg-name> \
  --docker-registry-server-url https://index.docker.io \
  --docker-registry-server-user yourusername \
  --docker-registry-server-password yourpassword
```

### Issue: Database connection fails

**Error**: `Connection refused` or `Timeout`

**Solution**:
```bash
# Check PostgreSQL firewall rules
az postgres flexible-server firewall-rule list \
  --name <server-name> \
  --resource-group <rg-name>

# Ensure Azure services are allowed (0.0.0.0 rule exists)
# This is configured automatically in db-postgres-minimal.bicep
```

## 🎯 Next Steps After Deployment

1. **Configure Custom Domain** (optional)
   ```bash
   az webapp config hostname add \
     --webapp-name <app-name> \
     --resource-group <rg-name> \
     --hostname yourdomain.com
   ```

2. **Enable SSL Certificate** (free with App Service)
   ```bash
   az webapp config ssl bind \
     --name <app-name> \
     --resource-group <rg-name> \
     --certificate-name <cert-name> \
     --ssl-type SNI
   ```

3. **Set Up Continuous Deployment**
   - Configure GitHub Actions to build and push to Docker Hub
   - App Service can auto-deploy on new image push

4. **Monitor Costs**
   ```bash
   # View cost analysis in Azure Portal
   az consumption usage list \
     --start-date 2025-01-01 \
     --end-date 2025-01-31
   ```

5. **Set Budget Alerts**
   - Go to Azure Portal > Cost Management
   - Set budget alert at $30/month

## 🔄 Updating the Application

### Push Updates via Docker Hub

```bash
# Make code changes
# Build new image
docker build -t yourusername/barodybroject:latest -f src/Dockerfile src/

# Push to Docker Hub
docker push yourusername/barodybroject:latest

# Restart App Service to pull new image
az webapp restart \
  --name <app-name> \
  --resource-group <rg-name>
```

### Direct Deployment via azd

```bash
# Update code and redeploy
azd deploy

# Or full update (infrastructure + code)
azd up
```

## 📞 Getting Help

- **Azure Portal**: https://portal.azure.com
- **Cost Management**: Portal > Cost Management + Billing
- **App Service Logs**: Portal > App Service > Log stream
- **Database Monitoring**: Portal > PostgreSQL server > Metrics

## ✅ Success Checklist

- [ ] Docker image built and pushed to Docker Hub
- [ ] Azure environment variables configured
- [ ] `azd provision --preview` runs successfully
- [ ] `azd provision` completes without errors
- [ ] App Service URL is accessible
- [ ] Database connection works
- [ ] Costs appear in Azure Cost Management (~$25/month)

---

**Ready to Deploy?** Run `azd up` and you're live in minutes! 🎉
