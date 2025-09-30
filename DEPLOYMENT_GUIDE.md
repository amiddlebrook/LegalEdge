# LegalEdge Production Deployment Guide

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Domain Name** registered with a DNS provider
3. **SSL Certificate** from AWS Certificate Manager (ACM)

## SSL Certificate Setup

### 1. Create SSL Certificate in AWS Certificate Manager

1. Go to AWS Certificate Manager (ACM) in the AWS Console
2. Click "Request a certificate"
3. Choose "Request a public certificate"
4. Add your domain names:
   - Primary domain (e.g., `api.legaledge.com`)
   - Wildcard domain (e.g., `*.legaledge.com`) - optional but recommended
5. Choose DNS validation (recommended) or email validation
6. Review and request the certificate

### 2. DNS Validation (Recommended)

If you chose DNS validation:

1. ACM will provide CNAME records to add to your DNS
2. Add these records to your DNS provider
3. Wait for validation (can take up to 30 minutes)

### 3. Get Certificate ARN

1. Once validated, note the Certificate ARN from ACM
2. You'll use this as the `ssl_certificate_arn` variable

## Domain Configuration

### 1. Create Route 53 Hosted Zone (if needed)

If you're using Route 53:

1. Go to Route 53 in AWS Console
2. Create a hosted zone for your domain
3. Note the hosted zone ID

### 2. Update Terraform Variables

Create a `terraform.tfvars` file:

```hcl
aws_region = "us-east-1"
environment = "production"

# SSL & Domain Configuration
ssl_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
domain_name = "api.legaledge.com"
create_route53_record = true
route53_zone_id = "Z1234567890ABC"

# Cost and Budget Configuration
monthly_budget = 2000
budget_alert_emails = ["admin@legaledge.com", "devops@legaledge.com"]

# Production-specific settings
alarm_actions = ["arn:aws:sns:us-east-1:123456789012:legaledge-alerts"]
```

## Deployment Steps

### 1. Initialize Terraform

```bash
cd infrastructure
terraform init
```

### 2. Plan Deployment

```bash
terraform plan -var-file=../terraform.tfvars
```

### 3. Deploy Infrastructure

```bash
terraform apply -var-file=../terraform.tfvars
```

### 4. Build and Push Docker Images

```bash
# Build images
docker build -f Dockerfile.backend -t legaledge-backend:latest .
docker build -f Dockerfile -t legaledge-app:latest .

# Tag for your registry (example with GitHub Container Registry)
docker tag legaledge-app:latest ghcr.io/your-org/legaledge-app:latest
docker tag legaledge-backend:latest ghcr.io/your-org/legaledge-backend:latest

# Push to registry
docker push ghcr.io/your-org/legaledge-app:latest
docker push ghcr.io/your-org/legaledge-backend:latest
```

### 5. Update ECS Service

```bash
aws ecs update-service --cluster legaledge-production-cluster \
  --service legaledge-production-app --force-new-deployment
```

## Post-Deployment Verification

### 1. Health Checks

```bash
# Check load balancer health
curl -f https://your-domain.com/api/v1/health/status

# Check readiness
curl -f https://your-domain.com/api/v1/health/readiness
```

### 2. DNS Verification

```bash
# Check DNS resolution
nslookup your-domain.com

# Check SSL certificate
echo | openssl s_client -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### 3. Application Testing

```bash
# Test main endpoints
curl -f https://your-domain.com/api/v1/overview
curl -f https://your-domain.com/api/v1/dashboard/snapshot
```

## Security Considerations

### 1. SSL/TLS Best Practices

- Use strong SSL policies (already configured in Terraform)
- Enable HTTP Strict Transport Security (HSTS)
- Configure security headers in your application

### 2. Certificate Management

- Set up certificate renewal notifications
- Monitor certificate expiration (ACM handles renewal automatically)
- Use IAM policies to restrict certificate access

### 3. Domain Security

- Enable DNSSEC for your domain
- Use CAA records to restrict certificate authorities
- Monitor for subdomain takeovers

## Monitoring & Maintenance

### 1. Certificate Monitoring

ACM automatically renews certificates, but monitor:
- Certificate expiration dates
- Validation status
- Renewal notifications

### 2. Domain Monitoring

- DNS resolution
- SSL certificate validity
- Security headers

### 3. Cost Monitoring

- Set up billing alerts
- Monitor CloudFront costs if using CDN
- Track Route 53 query costs

## Troubleshooting

### Common Issues

1. **Certificate Validation Failed**
   - Check DNS records are correctly added
   - Wait for DNS propagation (up to 48 hours)
   - Verify domain ownership

2. **SSL Handshake Errors**
   - Verify certificate ARN is correct
   - Check load balancer security groups
   - Ensure certificate is in us-east-1 region

3. **DNS Resolution Issues**
   - Verify Route 53 records exist
   - Check DNS propagation
   - Validate hosted zone configuration

### Support Resources

- **AWS Documentation**: https://docs.aws.amazon.com/acm/
- **Route 53 Documentation**: https://docs.aws.amazon.com/Route53/
- **SSL Labs**: https://www.ssllabs.com/ssltest/ (test SSL configuration)

## Next Steps

After successful deployment:

1. Set up monitoring dashboards
2. Configure log aggregation
3. Set up backup verification
4. Plan for scaling and performance optimization
5. Implement security scanning and compliance checks
