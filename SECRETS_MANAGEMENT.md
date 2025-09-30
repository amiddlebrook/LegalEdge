# LegalEdge Secrets Management Guide

## Overview

LegalEdge uses AWS Secrets Manager to securely store and manage sensitive configuration data such as API keys, database credentials, and encryption keys. This guide covers setup, rotation, and best practices for secrets management.

## Secrets Structure

### Database Credentials
- **Secret Name**: `legaledge-{environment}-db-password`
- **Content**: PostgreSQL username and password
- **Managed by**: Terraform (automatically created and rotated)

### Application Secrets
- **Secret Name**: `legaledge-{environment}-jwt-secret`
- **Content**: JWT signing secret (32-byte hex string)
- **Purpose**: Authentication token signing

- **Secret Name**: `legaledge-{environment}-app-secret`
- **Content**: General application secret (32-byte hex string)
- **Purpose**: Session encryption and CSRF protection

### External API Keys
- **Secret Name**: `legaledge-{environment}-openai-key`
- **Content**: OpenAI API key
- **Purpose**: AI/ML model access

- **Secret Name**: `legaledge-{environment}-congress-api`
- **Content**: Congress.gov API key
- **Purpose**: Legislative data access

- **Secret Name**: `legaledge-{environment}-news-api`
- **Content**: News API key
- **Purpose**: News and RSS feed access

- **Secret Name**: `legaledge-{environment}-market-api`
- **Content**: Market data API key
- **Purpose**: Financial data access

### Email Configuration
- **Secret Name**: `legaledge-{environment}-email-config`
- **Content**: SMTP configuration (host, port, credentials)
- **Purpose**: Alert notifications

## Setup Instructions

### 1. Initial Setup

Run the secrets setup script:

```bash
# Set environment variables for your API keys
export OPENAI_API_KEY="sk-your-openai-key"
export CONGRESS_API_KEY="your-congress-api-key"
export NEWS_API_KEY="your-news-api-key"
export MARKET_DATA_API_KEY="your-market-api-key"
export SMTP_PASSWORD="your-smtp-password"
export SMTP_HOST="smtp.your-provider.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@domain.com"

# Run setup script
chmod +x setup-secrets.sh
./setup-secrets.sh production
```

### 2. Manual Secret Creation

For individual secrets:

```bash
# Create JWT secret
aws secretsmanager create-secret \
    --name "legaledge-production-jwt-secret" \
    --secret-string "$(openssl rand -hex 32)" \
    --description "JWT secret key for LegalEdge authentication" \
    --region us-east-1 \
    --tags Key=Environment,Value=production Key=Project,Value=LegalEdge

# Create OpenAI API key secret
aws secretsmanager create-secret \
    --name "legaledge-production-openai-key" \
    --secret-string "sk-your-actual-openai-api-key" \
    --description "OpenAI API key for LegalEdge AI features" \
    --region us-east-1 \
    --tags Key=Environment,Value=production Key=Project,Value=LegalEdge
```

### 3. Update ECS Task Definition

After creating secrets, update the ECS task definition to include them:

```bash
aws ecs update-service \
    --cluster legaledge-production-cluster \
    --service legaledge-production-app \
    --force-new-deployment
```

## Environment Variables Mapping

The application expects these environment variables, which are populated from Secrets Manager:

```python
# In your application configuration
LEGALEDGE_JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # From legaledge-{env}-jwt-secret
LEGALEDGE_SECRET_KEY = os.getenv("APP_SECRET_KEY")      # From legaledge-{env}-app-secret
LEGALEDGE_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # From legaledge-{env}-openai-key
# ... other secrets
```

## Secret Rotation

### Automated Rotation (Recommended)

1. **Database Password**: Handled automatically by Terraform/RDS
2. **Application Secrets**: Use the provided rotation script

### Manual Rotation

```bash
# 1. Get current secret value
CURRENT_SECRET=$(aws secretsmanager get-secret-value \
    --secret-id "legaledge-production-jwt-secret" \
    --region us-east-1 \
    --query 'SecretString' --output text)

# 2. Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# 3. Update secret
aws secretsmanager update-secret \
    --secret-id "legaledge-production-jwt-secret" \
    --secret-string "$NEW_SECRET" \
    --region us-east-1

# 4. Update version stage to make it current
aws secretsmanager update-secret-version-stage \
    --secret-id "legaledge-production-jwt-secret" \
    --version-stage AWSCURRENT \
    --remove-from-version-stage AWSPENDING \
    --region us-east-1

# 5. Redeploy ECS service
aws ecs update-service \
    --cluster legaledge-production-cluster \
    --service legaledge-production-app \
    --force-new-deployment
```

### Rotation Script

Use the provided rotation script for bulk operations:

```bash
chmod +x rotate-secrets.sh
./rotate-secrets.sh production
```

## Access Control

### IAM Permissions

The ECS task execution role needs these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue"
            ],
            "Resource": [
                "arn:aws:secretsmanager:us-east-1:123456789012:secret:legaledge-production-*"
            ]
        }
    ]
}
```

### Secret-Specific Permissions

For enhanced security, create secret-specific permissions:

```bash
# Create policy for specific secrets only
cat > legaledge-secrets-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "secretsmanager:GetSecretValue",
            "Resource": [
                "arn:aws:secretsmanager:us-east-1:123456789012:secret:legaledge-production-jwt-secret-*",
                "arn:aws:secretsmanager:us-east-1:123456789012:secret:legaledge-production-app-secret-*",
                "arn:aws:secretsmanager:us-east-1:123456789012:secret:legaledge-production-db-password-*"
            ]
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name "LegalEdgeSecretsAccess" \
    --policy-document file://legaledge-secrets-policy.json
```

## Monitoring & Compliance

### Secret Usage Monitoring

1. **CloudTrail Logging**: All secret access is logged
2. **CloudWatch Alarms**: Set up alarms for unusual access patterns
3. **Access Reports**: Use AWS Config for compliance reporting

### Compliance Features

- **Encryption at Rest**: All secrets encrypted with AWS KMS
- **Automatic Rotation**: Database credentials auto-rotate
- **Access Logging**: Full audit trail of secret access
- **Retention Policies**: Configurable secret retention

## Troubleshooting

### Common Issues

1. **Secret Not Accessible**
   ```bash
   # Check IAM permissions
   aws iam simulate-principal-policy \
       --policy-source-arn "arn:aws:iam::123456789012:role/ecs-task-role" \
       --action-names "secretsmanager:GetSecretValue" \
       --resource-arns "arn:aws:secretsmanager:us-east-1:123456789012:secret:legaledge-production-*"
   ```

2. **Secret Rotation Failed**
   ```bash
   # Check secret version stages
   aws secretsmanager describe-secret \
       --secret-id "legaledge-production-jwt-secret" \
       --region us-east-1

   # Force rotation if needed
   aws secretsmanager update-secret-version-stage \
       --secret-id "legaledge-production-jwt-secret" \
       --version-stage AWSCURRENT \
       --remove-from-version-stage AWSPENDING
   ```

3. **ECS Tasks Can't Access Secrets**
   ```bash
   # Check task execution role
   aws ecs describe-task-definition \
       --task-definition legaledge-production-app \
       --region us-east-1

   # Verify secrets are mounted in container
   aws ecs describe-services \
       --cluster legaledge-production-cluster \
       --services legaledge-production-app \
       --region us-east-1
   ```

## Security Best Practices

### 1. Principle of Least Privilege
- Only grant access to specific secrets needed
- Use temporary credentials when possible
- Regularly review and audit secret access

### 2. Secret Lifecycle
- Rotate secrets regularly (database passwords auto-rotate)
- Use different secrets for different environments
- Implement automatic secret rotation where possible

### 3. Monitoring and Alerting
- Set up CloudWatch alarms for secret access patterns
- Monitor for secrets that haven't been rotated recently
- Alert on unusual access patterns or locations

### 4. Compliance
- Use encryption for all secrets
- Implement proper access controls
- Maintain audit logs for compliance requirements

## Emergency Procedures

### 1. Immediate Secret Revocation

If a secret is compromised:

```bash
# Block all access to the secret
aws secretsmanager update-secret-version-stage \
    --secret-id "legaledge-production-compromised-secret" \
    --version-stage AWSDENIED \
    --remove-from-version-stage AWSCURRENT

# Create new secret immediately
aws secretsmanager create-secret \
    --name "legaledge-production-compromised-secret-NEW" \
    --secret-string "$(openssl rand -hex 32)" \
    --description "Emergency replacement for compromised secret" \
    --region us-east-1
```

### 2. Application Rollback

If secret rotation causes issues:

```bash
# Roll back to previous version
aws secretsmanager update-secret-version-stage \
    --secret-id "legaledge-production-jwt-secret" \
    --version-stage AWSCURRENT \
    --move-to-version-stage AWSPENDING

# Redeploy application to pick up old secret
aws ecs update-service \
    --cluster legaledge-production-cluster \
    --service legaledge-production-app \
    --force-new-deployment
```

## Support and Maintenance

### Regular Tasks

1. **Weekly**: Review secret access logs
2. **Monthly**: Rotate application secrets
3. **Quarterly**: Review and update IAM policies
4. **Annually**: Audit all secrets and remove unused ones

### Tools and Scripts

- `setup-secrets.sh`: Initial secrets setup
- `rotate-secrets.sh`: Bulk secret rotation
- `audit-secrets.py`: Secret access auditing

For questions or issues, contact the DevOps team or check the LegalEdge operations documentation.
