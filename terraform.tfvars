# LegalEdge Production Terraform Variables
# IMPORTANT: Update these values with your actual configuration

# AWS Configuration
aws_region = "us-east-1"
environment = "production"

# Domain and SSL Configuration (UPDATE THESE!)
domain_name = "your-domain.com"
ssl_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/certificate-arn-here"

# DNS Configuration (Optional)
create_route53_record = true
route53_zone_id = "Z1234567890ABC"  # Update with your hosted zone ID

# Cost and Budget Configuration
monthly_budget = 2000
budget_alert_emails = [
    "your-email@domain.com"
]

# Alerting Configuration (Optional)
alarm_actions = []

# Docker Image Configuration
app_image = "your-registry/legaledge-app:latest"
