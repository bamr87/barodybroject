# Minimal Cost Infrastructure Migration

This directory contains the **minimal cost** infrastructure configuration for Barodybroject.

## 💰 Cost Comparison

| Component | Previous Setup | Minimal Setup | Monthly Savings |
|-----------|----------------|---------------|-----------------|
| **Compute** | Container Apps (~$6-15) | App Service B1 ($13) | $0-2 |
| **Container Registry** | ACR Basic (~$5) | Docker Hub Free | **$5** |
| **Database** | PostgreSQL B1ms ($12.41) | PostgreSQL B1ms ($12.41) | $0 |
| **Key Vault** | ~$0.50 | Removed | **$0.50** |
| **Monitoring** | App Insights (~$2-5) | App Service logs | **$2-5** |
| **Dashboard** | ~$1 | Removed | **$1** |
| **Total Monthly** | **~$27-37** | **~$25** | **$8-15 (30-40%)** |

## 📁 Files

- `main.bicep` - Minimal infrastructure (App Service + PostgreSQL only)
- `main.bicep.backup` - Original Container Apps configuration
- `main.parameters.json` - Simplified parameters
- `main.parameters.json.backup` - Original parameters
- `app/app-service.bicep` - App Service module (B1 tier)
- `app/db-postgres-minimal.bicep` - Minimal PostgreSQL configuration

## 🚀 Deployment Steps

### 1. Build and Push Docker Image to Docker Hub

```bash
# Login to Docker Hub
docker login

# Build the image
cd /Users/bamr87/github/barodybroject
docker build -t bamr87/barodybroject:latest -f src/Dockerfile src/

# Push to Docker Hub
docker push bamr87/barodybroject:latest
```

### 2. Set Environment Variables

```bash
# Ensure required variables are set
azd env set DB_PASSWORD "your-secure-password"
azd env set DOCKER_IMAGE "bamr87/barodybroject:latest"
```

### 3. Deploy Infrastructure

```bash
# Provision infrastructure
azd provision

# Or full deployment
azd up
```

## 🔧 What Changed

### Removed (Cost Savings):
- ❌ Azure Container Registry (~$5/month)
- ❌ Container Apps Environment (~$6/month)
- ❌ Key Vault (~$0.50/month)
- ❌ Application Insights (~$2-5/month)
- ❌ Monitoring Dashboard (~$1/month)

### Added (Minimal Cost):
- ✅ App Service Plan B1 ($13.14/month)
- ✅ App Service (Linux container support)

### Kept (No Change):
- ✅ PostgreSQL Flexible Server B1ms ($12.41/month)
- ✅ Resource Group (free)

## 📊 Infrastructure Components

### App Service (B1 Tier)
- **Cost**: $13.14/month
- **Resources**: 1 vCPU, 1.75 GB RAM
- **Storage**: 10 GB
- **Features**:
  - Docker container support
  - Custom domains & SSL
  - Auto-scaling (vertical)
  - 99.95% SLA

### PostgreSQL Flexible Server (Burstable B1ms)
- **Cost**: $12.41/month
- **Resources**: 1 vCPU, 2 GiB RAM
- **Storage**: 32 GB (minimum)
- **Features**:
  - 7-day backup retention
  - Point-in-time restore
  - 99.9% SLA

## 🔄 Rolling Back

If you need to revert to the original infrastructure:

```bash
# Restore original files
cp infra/main.bicep.backup infra/main.bicep
cp infra/main.parameters.json.backup infra/main.parameters.json

# Re-deploy
azd up
```

## 📈 Scaling Up Later

When your traffic grows, you can easily scale:

### Vertical Scaling (App Service)
```bash
# Upgrade to S1 tier (2 cores, 3.5 GB RAM)
az appservice plan update --name <plan-name> --resource-group <rg-name> --sku S1
```

### Horizontal Scaling (Database)
```bash
# Upgrade to General Purpose tier
az postgres flexible-server update --name <server-name> --resource-group <rg-name> --tier GeneralPurpose --sku-name Standard_D2s_v3
```

### Re-add Services
Uncomment sections in `main.bicep` to add:
- Key Vault for advanced secret management
- Application Insights for detailed monitoring
- Container Registry for private images

## 🛠️ Troubleshooting

### Issue: Docker image not found
**Solution**: Ensure image is pushed to Docker Hub and is public, or configure Docker Hub credentials in App Service.

### Issue: Database connection fails
**Solution**: Check firewall rules in PostgreSQL allow Azure services (0.0.0.0).

### Issue: App Service not starting
**Solution**: 
1. Check logs: `az webapp log tail --name <app-name> --resource-group <rg-name>`
2. Verify `WEBSITES_PORT=8000` is set
3. Ensure Dockerfile exposes port 8000

## 📞 Support

For issues or questions:
1. Check Azure Portal diagnostics
2. Review App Service logs
3. Verify Docker image works locally
4. Check PostgreSQL connection from local machine

## 🎯 Next Steps

1. ✅ Deploy the minimal infrastructure
2. Monitor costs in Azure Cost Management
3. Set up alerts for unexpected cost increases
4. Consider Azure Reserved Instances for 30% additional savings
5. Plan for scaling when traffic increases

---

**Estimated Monthly Cost**: ~$25.55 USD  
**Previous Cost**: ~$32-37 USD  
**Savings**: 30-40% reduction
