# LegalEdge Complete Setup Checklist

## 📋 Everything You Need to Set Up LegalEdge

This checklist covers all requirements for getting LegalEdge running in production, including APIs, infrastructure, and operational setup.

---

## 🌐 Domain & SSL Setup

### Required:
- [ ] **Domain Name**: Register a domain (e.g., `api.legaledge.com`)
- [ ] **SSL Certificate**: Create in AWS Certificate Manager
- [ ] **DNS Configuration**: Point domain to AWS load balancer

### Setup Commands:
```bash
# 1. Register domain (via your registrar)
# 2. Create SSL certificate
./setup-ssl-certificate.sh your-domain.com

# 3. Set up DNS validation (if using Route 53)
./setup-route53-validation.sh <certificate-arn>
```

---

## 🔑 API Keys & External Services

### Required APIs:

#### 1. OpenAI API (Required - Powers AI features)
- **Signup**: https://platform.openai.com/api-keys
- **Cost**: $50-200/month depending on usage
- **Features**: Legislation analysis, sentiment scoring, forecasting

#### 2. Email Service (Required - For alerts)
**Option A: Gmail (Quick setup)**
- Enable 2FA on Gmail account
- Generate App Password: Google Account → Security → App passwords

**Option B: SendGrid (Production-ready)**
- Signup: https://sendgrid.com
- Cost: Free tier (100 emails/day), $20/month for more

### Recommended APIs:

#### 3. Congress.gov API (Recommended - Official legislative data)
- **Signup**: https://api.data.gov/signup
- **Cost**: Free
- **Features**: Real legislative bills, votes, committee data

#### 4. News API (Recommended - Market context)
**Option A: NewsAPI.org**
- Signup: https://newsapi.org
- Cost: Free (1,000/day), $378/month unlimited

**Option B: Alpha Vantage**
- Signup: https://www.alphavantage.co/support/#api-key
- Cost: Free (500/day), $50/month premium

#### 5. Market Data API (Recommended - Financial data)
**Option A: Alpha Vantage**
- Same signup as news API above
- Cost: Free tier available

**Option B: Yahoo Finance**
- No API key required (use `yfinance` library)

### Quick Setup:
```bash
# Run this script for fastest setup
chmod +x quick-api-setup.sh
./quick-api-setup.sh
```

---

## 🏗️ Infrastructure Setup

### AWS Services Required:
- [ ] **VPC & Networking**: Private subnets for security
- [ ] **ECS Fargate**: Container orchestration
- [ ] **RDS PostgreSQL**: Database with encryption
- [ ] **ElastiCache Redis**: Caching and sessions
- [ ] **S3 Buckets**: File storage with lifecycle policies
- [ ] **CloudFront CDN**: Global content delivery
- [ ] **Load Balancer**: HTTPS traffic distribution
- [ ] **Secrets Manager**: Secure credential storage
- [ ] **CloudWatch**: Monitoring and alerting

### Setup Commands:
```bash
# Deploy all infrastructure
./deploy.sh production apply

# Verify deployment
./verify-deployment.sh production your-domain.com
```

---

## 🐳 Container Registry

### Choose One:

#### Option A: GitHub Container Registry (Free with GitHub)
```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Use in deployment
./deploy-docker.sh production ghcr.io/your-username
```

#### Option B: AWS Elastic Container Registry
```bash
# Create repository
aws ecr create-repository --repository-name legaledge-app --region us-east-1

# Login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Use in deployment
./deploy-docker.sh production <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

#### Option C: Docker Hub
```bash
# Login
docker login

# Use in deployment
./deploy-docker.sh production your-dockerhub-username
```

---

## 💳 Billing & Costs

### Estimated Monthly Costs:
- **AWS Infrastructure**: $590-1,180 (ECS, RDS, S3, etc.)
- **OpenAI API**: $50-200 (depending on usage)
- **Email Service**: $0-20 (SendGrid/Gmail)
- **Optional APIs**: $0-100 (News, Market data)
- **Domain**: $10-20/year
- **SSL Certificate**: Free (AWS ACM)

### Total First Month: $650-1,520

---

## 🔒 Security Setup

### Required Security Measures:
- [ ] **AWS IAM Roles**: Proper permissions for ECS tasks
- [ ] **VPC Security Groups**: Restrict network access
- [ ] **KMS Encryption**: Encrypt all data at rest
- [ ] **Secrets Rotation**: Automated credential rotation
- [ ] **Audit Logging**: CloudTrail enabled

### Setup:
- Automatically configured via Terraform
- Secrets Manager handles credential rotation
- Security groups restrict access to necessary ports only

---

## 📊 Monitoring Setup

### Required Monitoring:
- [ ] **Application Health Checks**: `/api/v1/health/status`
- [ ] **Performance Metrics**: Response times, error rates
- [ ] **Cost Monitoring**: Budget alerts and usage tracking
- [ ] **Security Monitoring**: Access logs and threat detection
- [ ] **Backup Monitoring**: Automated backup verification

### Setup:
- CloudWatch dashboards automatically created
- Cost monitoring alerts configured
- Performance metrics collected automatically

---

## 🚨 Alerting Setup

### Required Alerts:
- [ ] **Application Health**: Service down/unhealthy
- [ ] **Cost Thresholds**: 80%, 90%, 100% of budget
- [ ] **Security Events**: Unauthorized access attempts
- [ ] **Performance Issues**: High response times, errors
- [ ] **Backup Failures**: Database backup issues

### Setup:
- Configured via Terraform
- Email alerts sent to specified addresses
- Slack notifications (optional)

---

## 📚 Documentation Setup

### Required Documentation:
- [ ] **API Documentation**: Available at `/docs`
- [ ] **User Guide**: How to use LegalEdge features
- [ ] **Operations Guide**: Deployment and maintenance
- [ ] **Security Guide**: Compliance and access controls
- [ ] **Troubleshooting Guide**: Common issues and solutions

### Setup:
- Documentation automatically deployed
- Available at your domain after deployment

---

## ✅ Final Verification Checklist

### Before Going Live:

#### Infrastructure ✅
- [ ] Domain resolves correctly
- [ ] SSL certificate validated
- [ ] Load balancer healthy
- [ ] Database accessible
- [ ] Redis cluster running

#### Application ✅
- [ ] All API endpoints responding
- [ ] Health checks passing
- [ ] AI features working (OpenAI)
- [ ] Email alerts functional
- [ ] Error handling working

#### Operations ✅
- [ ] Monitoring dashboards accessible
- [ ] Cost tracking configured
- [ ] Backup procedures tested
- [ ] Security measures active

#### Documentation ✅
- [ ] API docs available
- [ ] User guides complete
- [ ] Operations procedures documented
- [ ] Support contacts listed

---

## 🎯 Minimum Viable Setup

**To get LegalEdge running with core features:**

1. **Domain + SSL** ✅
2. **OpenAI API** ✅ (Required for AI features)
3. **Email service** ✅ (Required for alerts)
4. **AWS infrastructure** ✅ (Via Terraform)
5. **Basic monitoring** ✅ (Auto-configured)

**Optional enhancements:**
6. **Congress.gov API** (Better legislative data)
7. **News API** (Market context)
8. **Market data API** (Enhanced forecasting)

---

## 🚀 Launch Sequence

```bash
# 1. Set up APIs (5-10 minutes)
./quick-api-setup.sh

# 2. Deploy infrastructure (15-20 minutes)
./deploy.sh production apply

# 3. Build and deploy application (10-15 minutes)
./deploy-docker.sh production your-registry

# 4. Verify everything works (5 minutes)
./verify-deployment.sh production your-domain.com

# 5. Monitor and optimize (ongoing)
# Check costs, performance, and usage regularly
```

---

## 📞 Support & Resources

### Getting Help:
- **API Setup Issues**: See `API_SETUP_GUIDE.md`
- **Deployment Problems**: Check `PRODUCTION_DEPLOYMENT.md`
- **Cost Questions**: Review `COST_OPTIMIZATION.md`
- **Operations**: See `DEPLOYMENT_CHECKLIST.md`

### Important Notes:
- ⏱️ **Setup Time**: 30-45 minutes for complete setup
- 💰 **First Month Cost**: $650-1,520 (depending on API usage)
- 🔒 **Security**: Enterprise-grade security included
- 📈 **Scalability**: Auto-scaling handles growth automatically

---

**🎉 You're ready to launch LegalEdge!** This checklist ensures you have everything needed for a successful production deployment.
