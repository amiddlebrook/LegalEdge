# 🚀 LegalEdge Complete Launch Instructions

Here's your comprehensive guide to launch LegalEdge as a fully functional SaaS product. This document covers everything needed to go from development to production.

## 📋 Complete Launch Checklist

### **Phase 1: Infrastructure & Security Setup**

#### 1. **AWS Account Configuration**
- Create AWS account at https://aws.amazon.com
- Set up AWS CLI with `aws configure`
- Create IAM user with appropriate permissions (EC2, ECS, RDS, S3, Route53, ACM, Secrets Manager)
- Enable billing alerts and set up consolidated billing if needed

#### 2. **Domain & SSL Setup**
- Register domain (e.g., `legaledge.com`) at Namecheap, GoDaddy, or similar
- Create AWS Route53 hosted zone for your domain
- Request SSL certificate in AWS Certificate Manager for your domain
- Validate SSL certificate via DNS records

#### 3. **External API Configuration**
**Required APIs:**
- **OpenAI API** (https://platform.openai.com):
  - Sign up and get API key
  - Set up billing (starts at ~$50/month for production use)

- **Email Service** (choose one):
  - **SendGrid** (recommended): Sign up at https://sendgrid.com, get API key
  - **Amazon SES**: Request production access in AWS console
  - **Gmail**: Use app passwords for development only

**Optional but Recommended:**
- **Congress.gov API**: Free government API for legislative data
- **News API**: NewsAPI.org or Alpha Vantage for market context
- **Market Data API**: Alpha Vantage or Financial Modeling Prep

#### 4. **Secrets Management**
Create secrets in AWS Secrets Manager:
```bash
# JWT Secret
aws secretsmanager create-secret \
    --name "legaledge-production-jwt-secret" \
    --secret-string "$(openssl rand -hex 32)"

# OpenAI API Key
aws secretsmanager create-secret \
    --name "legaledge-production-openai-key" \
    --secret-string "sk-your-openai-key-here"
```

### **Phase 2: Infrastructure Deployment**

#### 5. **Terraform Configuration**
Update `terraform.tfvars` with your actual values:
```hcl
aws_region = "us-east-1"
environment = "production"
domain_name = "your-domain.com"
ssl_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/your-cert-arn"
route53_zone_id = "YOUR_HOSTED_ZONE_ID"
monthly_budget = 2000
budget_alert_emails = ["admin@yourdomain.com"]
app_image = "your-registry/legaledge-app:latest"
```

#### 6. **Deploy Infrastructure**
```bash
cd infrastructure
terraform init
terraform plan -var-file=../terraform.tfvars
terraform apply -var-file=../terraform.tfvars
```

#### 7. **Docker Images**
```bash
# Build and tag images
docker build -f Dockerfile.backend -t legaledge-backend:latest .
docker build -f Dockerfile -t legaledge-app:latest .

# Push to your registry (GitHub Container Registry example)
docker tag legaledge-app:latest ghcr.io/your-username/legaledge-app:latest
docker push ghcr.io/your-username/legaledge-app:latest
```

### **Phase 3: Application Deployment**

#### 8. **Deploy Application**
```bash
# Update ECS service to use new image
aws ecs update-service \
    --cluster legaledge-production-cluster \
    --service legaledge-production-app \
    --force-new-deployment
```

#### 9. **DNS Configuration**
- Point your domain to the load balancer created by Terraform
- Update CNAME records for API and frontend subdomains

### **Phase 4: Production Validation**

#### 10. **Health Checks**
- Verify API endpoints: `https://api.yourdomain.com/health`
- Check frontend: `https://yourdomain.com`
- Monitor ECS service health and scaling

#### 11. **API Testing**
Test key endpoints:
- `GET /api/v1/overview` - Platform overview
- `GET /api/v1/legislation/upcoming` - Legislative data
- `GET /api/v1/health/status` - System health

#### 12. **Background Jobs**
Ensure Celery workers are running for:
- Data ingestion (every 30 minutes)
- ML model retraining (every 6 hours)
- Alert processing (every 5 minutes)

## 🌐 **Production URLs & Access Points**

After deployment, your application will be available at:
- **Frontend**: `https://yourdomain.com`
- **API Base**: `https://api.yourdomain.com`
- **API Documentation**: `https://api.yourdomain.com/docs`
- **Health Check**: `https://api.yourdomain.com/health`

## 📊 **Key Services & APIs**

### **Core Application Services**
- **FastAPI Backend**: REST API server
- **React Frontend**: User interface
- **PostgreSQL Database**: Data storage
- **Redis Cache**: Session storage and caching
- **Celery Workers**: Background task processing

### **External Integrations**
- **OpenAI**: AI/ML model inference
- **Congress.gov**: Legislative data
- **News APIs**: Market context
- **Market Data APIs**: Financial information
- **Email Service**: Notifications

## 🔧 **Monitoring & Maintenance**

### **Built-in Monitoring**
- **CloudWatch**: Infrastructure metrics
- **ECS**: Container health
- **RDS**: Database performance
- **Custom Dashboards**: Application-specific metrics

### **Background Jobs**
- **Data Ingestion**: Fetches legislative data every 30 minutes
- **Model Retraining**: Updates ML models every 6 hours
- **Alert Processing**: Processes notifications every 5 minutes
- **Data Cleanup**: Archives old data daily

## 💰 **Estimated Monthly Costs**

**AWS Infrastructure** (~$300-500/month):
- ECS Fargate: $50-100
- RDS PostgreSQL: $50-100
- ElastiCache Redis: $20-50
- S3 + CloudFront: $20-50
- Load Balancer + Route53: $20-50
- CloudWatch + Monitoring: $20-50

**External APIs** (~$100-300/month):
- OpenAI: $50-200
- Email Service: $20-50
- Optional APIs: $30-50

**Total First Month**: $400-800

## 🚨 **Critical Launch Checklist**

- [ ] AWS account with proper IAM permissions
- [ ] Domain registered and DNS configured
- [ ] SSL certificate validated
- [ ] All API keys configured in Secrets Manager
- [ ] Terraform variables updated with real values
- [ ] Docker images built and pushed
- [ ] Application deployed and healthy
- [ ] DNS records pointing to load balancer
- [ ] Email notifications working
- [ ] Background workers operational
- [ ] Monitoring dashboards accessible
- [ ] End-to-end testing completed

## 📚 **Documentation & Support**

**Available Documentation:**
- **API Documentation**: `https://api.yourdomain.com/docs`
- **User Guide**: `/docs/user-guide/`
- **Deployment Guide**: `/docs/deployment/`
- **Support Center**: `/docs/support/`

**Support Channels:**
- **Status Page**: `https://status.yourdomain.com`
- **Support Email**: `support@yourdomain.com`
- **Documentation**: `https://docs.yourdomain.com`

## 🎯 **Post-Launch Optimization**

1. **Monitor API costs** and usage patterns
2. **Set up billing integration** for user subscriptions
3. **Configure customer support** channels
4. **Implement user onboarding** flows
5. **Set up analytics** and telemetry
6. **Plan iterative releases** based on user feedback

## 🚨 **Quick Start Commands**

### **For AWS Setup:**
```bash
# Configure AWS CLI
aws configure

# Create hosted zone (if using Route53)
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Create SSL certificate
aws acm request-certificate --domain-name yourdomain.com --validation-method DNS
```

### **For API Setup:**
```bash
# OpenAI API
export OPENAI_API_KEY="sk-your-key-here"

# SendGrid Email
export SENDGRID_API_KEY="SG.your-sendgrid-key"

# Create secrets
aws secretsmanager create-secret --name "legaledge-production-openai-key" --secret-string "$OPENAI_API_KEY"
aws secretsmanager create-secret --name "legaledge-production-email-config" --secret-string '{"smtp_host":"smtp.sendgrid.net","smtp_port":587,"smtp_user":"apikey","smtp_password":"'$SENDGRID_API_KEY'"}'
```

### **For Deployment:**
```bash
# Build and push images
docker build -f Dockerfile -t legaledge-app:latest .
docker tag legaledge-app:latest ghcr.io/your-username/legaledge-app:latest
docker push ghcr.io/your-username/legaledge-app:latest

# Deploy infrastructure
cd infrastructure
terraform apply -var-file=../terraform.tfvars

# Deploy application
aws ecs update-service --cluster legaledge-production-cluster --service legaledge-production-app --force-new-deployment
```

This launch process will result in a fully functional LegalEdge platform capable of serving real users with legislative intelligence, portfolio analysis, and market forecasting capabilities.

## 📞 **Need Help?**

If you encounter issues during launch:
1. Check the [Deployment Guide](DEPLOYMENT_GUIDE.md) for detailed steps
2. Review the [API Setup Guide](../setup/API_SETUP_GUIDE.md) for external integrations
3. Consult the [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues
4. Contact support at support@yourdomain.com

---
*Last Updated: $(date)*
*LegalEdge Launch Instructions v2.0*
