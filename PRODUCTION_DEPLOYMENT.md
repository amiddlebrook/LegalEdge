# 🚀 LegalEdge Production Deployment Guide

## Overview

This guide provides a complete, step-by-step process for deploying LegalEdge to production. The deployment is fully automated using Infrastructure as Code (Terraform) and containerization (Docker).

## Prerequisites

### 1. AWS Setup
- **AWS Account** with appropriate permissions (EC2, RDS, ECS, IAM, etc.)
- **AWS CLI** configured with access keys
- **Terraform** installed (v1.6.0+)

### 2. Domain & SSL
- **Domain name** registered (e.g., api.legaledge.com)
- **SSL certificate** ready in AWS Certificate Manager

### 3. Container Registry
- **Docker** installed and running
- **Container registry** access (GitHub CR, AWS ECR, or Docker Hub)

### 4. External APIs
- **OpenAI API key** (required for AI features)
- **Email service** credentials (required for alerts)
- **Other API keys** (optional: Congress.gov, News, Market Data)

## 📋 Deployment Checklist

- [ ] AWS account and permissions configured
- [ ] Domain name registered and accessible
- [ ] SSL certificate created in ACM
- [ ] Container registry access configured
- [ ] External API keys obtained
- [ ] Environment variables documented

## 🚀 Deployment Steps

### Step 1: SSL Certificate Setup

```bash
# Set up SSL certificate
chmod +x setup-ssl-certificate.sh
./setup-ssl-certificate.sh api.legaledge.com

# If using Route 53, also run DNS validation
./setup-route53-validation.sh <certificate-arn>
```

**Expected Output:**
```
✅ Certificate requested successfully: arn:aws:acm:us-east-1:123456789012:certificate/xxxx
📋 DNS Validation Records:
[DNS records to add to your DNS provider]
```

### Step 2: Secrets Configuration

```bash
# Set up production secrets
chmod +x setup-production-secrets.sh
./setup-production-secrets.sh production
```

**Interactive Setup:**
- Enter your OpenAI API key
- Configure email/SMTP settings
- Add optional API keys (Congress.gov, News, Market Data)

### Step 3: Infrastructure Deployment

```bash
# Update Terraform variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your actual values

# Deploy infrastructure
chmod +x deploy.sh
./deploy.sh production apply
```

**Expected Output:**
```
🏗️  LegalEdge Infrastructure Deployment
✅ AWS credentials configured
✅ Terraform initialized
✅ Terraform configuration valid
📋 Deployment Plan Summary: {create: 25, update: 0, delete: 0}
🚀 Applying Terraform deployment...
✅ Infrastructure deployment completed!
```

### Step 4: Application Deployment

```bash
# Build and push Docker images
chmod +x deploy-docker.sh
./deploy-docker.sh production ghcr.io/amiddlebrook

# Or for AWS ECR:
# ./deploy-docker.sh production 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

**Expected Output:**
```
🐳 LegalEdge Docker Build and Deployment
✅ Prerequisites check passed
✅ Registry authentication successful
✅ Frontend built successfully
✅ Backend image built successfully
✅ Application image built successfully
✅ Images pushed successfully
✅ ECS deployment completed
```

### Step 5: Deployment Verification

```bash
# Verify deployment
chmod +x verify-deployment.sh
./verify-deployment.sh production api.legaledge.com
```

**Expected Output:**
```
🔍 LegalEdge Deployment Verification
✅ PASSED: DNS resolution
✅ PASSED: SSL certificate
✅ PASSED: ECS cluster exists
✅ PASSED: ECS service exists
✅ PASSED: Load balancer exists
✅ PASSED: Health check endpoint
✅ PASSED: Application endpoints
🎉 All tests passed! LegalEdge is ready for production.
```

## 🔧 Configuration Files

### Required Configuration Updates

#### 1. `terraform.tfvars`
```hcl
aws_region = "us-east-1"
environment = "production"
domain_name = "api.legaledge.com"
ssl_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/xxxx"
route53_zone_id = "Z1234567890ABC"
budget_alert_emails = ["admin@legaledge.com"]
```

#### 2. Environment Variables (via Secrets Manager)
- `LEGALEDGE_OPENAI_API_KEY` - Your OpenAI API key
- `LEGALEDGE_EMAIL_CONFIG` - SMTP configuration
- `LEGALEDGE_JWT_SECRET_KEY` - Auto-generated JWT secret
- `LEGALEDGE_APP_SECRET_KEY` - Auto-generated app secret

## 📊 Post-Deployment Monitoring

### 1. Application Health
- **Health Check**: `https://your-domain.com/api/v1/health/status`
- **Readiness Check**: `https://your-domain.com/api/v1/health/readiness`
- **Dashboard**: `https://your-domain.com/api/v1/dashboard/snapshot`

### 2. AWS Resources
- **ECS Service**: Monitor task health and auto-scaling
- **RDS Database**: Check connections and performance
- **Load Balancer**: Monitor target health and response times
- **CloudWatch**: Review logs and metrics

### 3. Cost Monitoring
- **Daily Costs**: Track via CloudWatch dashboard
- **Budget Alerts**: Configured for 80%, 90%, 100% of budget
- **Resource Optimization**: Monitor for right-sizing opportunities

## 🔒 Security Considerations

### 1. Secrets Management
- All sensitive data stored in AWS Secrets Manager
- Automatic rotation configured for database credentials
- IAM permissions restricted to minimum required

### 2. Network Security
- VPC isolation with private subnets for application
- Security groups restrict access to necessary ports only
- SSL/TLS encryption for all data in transit

### 3. Compliance
- Audit logging enabled for all access
- Data encryption at rest and in transit
- Compliance-ready retention policies

## 🚨 Troubleshooting

### Common Issues

#### 1. ECS Tasks Not Starting
```bash
# Check ECS service status
aws ecs describe-services --cluster legaledge-production-cluster --services legaledge-production-app

# Check CloudWatch logs
aws logs tail /ecs/legaledge-production-app --follow
```

#### 2. SSL Certificate Issues
```bash
# Check certificate status
aws acm describe-certificate --certificate-arn <certificate-arn>

# Verify DNS validation
nslookup <domain>
```

#### 3. Database Connection Issues
```bash
# Test database connectivity
aws rds describe-db-instances --db-instance-identifier legaledge-production-db

# Check security groups
aws ec2 describe-security-groups --group-ids <security-group-id>
```

#### 4. High Costs
```bash
# Check cost monitoring dashboard
aws cloudwatch describe-dashboards --dashboard-names legaledge-production-cost-monitoring

# Review budget status
aws budgets describe-budget --budget-name legaledge-production-monthly-budget
```

## 📞 Support & Operations

### Daily Operations
- Monitor application health and performance
- Review security logs for unusual activity
- Check cost trends and optimization opportunities

### Weekly Operations
- Review application logs for errors
- Test backup restoration procedures
- Update security patches if needed

### Monthly Operations
- Review and optimize costs
- Update SSL certificates if needed
- Conduct full application testing

### Emergency Procedures

#### Rollback Deployment
```bash
aws ecs update-service --cluster legaledge-production-cluster \
    --service legaledge-production-app \
    --task-definition legaledge-production-app:previous \
    --force-new-deployment
```

#### Scale Down Resources
```bash
aws ecs update-service --cluster legaledge-production-cluster \
    --service legaledge-production-app \
    --desired-count 1
```

## 🎯 Success Metrics

### Technical Metrics
- **Uptime**: >99.9% availability
- **Response Time**: <500ms average API response time
- **Error Rate**: <0.1% error rate
- **Cost Efficiency**: Within 10% of budget projections

### Business Metrics
- **Data Accuracy**: >95% accuracy in forecasts and insights
- **User Engagement**: Active users and session duration
- **Scalability**: Handles 10x current load without issues

## 🚀 Production Launch

Once all verification tests pass:

1. **Enable monitoring** and alerting
2. **Set up backup verification** schedules
3. **Document operational procedures** for the team
4. **Conduct end-user testing** if applicable
5. **Monitor initial usage** and performance

## 📚 Documentation

- **API Documentation**: Available at `/docs` endpoint
- **User Guide**: `docs/user-guide/user-guide.md`
- **Operations Guide**: This deployment guide
- **Security Guide**: `SECRETS_MANAGEMENT.md`
- **Cost Guide**: `COST_OPTIMIZATION.md`

---

**🎉 Congratulations! Your LegalEdge platform is now live in production!**

For questions or issues, contact the development team or refer to the troubleshooting section above.

**Deployment Completed**: $(date)
**Version**: 1.0.0
**Status**: ✅ Production Ready
