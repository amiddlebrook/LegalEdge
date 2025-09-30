#!/bin/bash
# LegalEdge SSL Certificate Setup Script

set -e

# Configuration
REGION=${AWS_REGION:-us-east-1}
DOMAIN_NAME=${1:-api.legaledge.com}
ENVIRONMENT=${2:-production}

echo "🔒 Setting up SSL certificate for LegalEdge..."
echo "Domain: $DOMAIN_NAME"
echo "Region: $REGION"
echo "Environment: $ENVIRONMENT"

# Function to check if certificate exists
check_certificate() {
    local domain=$1
    echo "Checking for existing certificate for $domain..."

    CERT_ARN=$(aws acm list-certificates \
        --region "$REGION" \
        --query "CertificateSummaryList[?DomainName==\`$domain\`].CertificateArn" \
        --output text)

    if [ -n "$CERT_ARN" ] && [ "$CERT_ARN" != "None" ]; then
        echo "✅ Found existing certificate: $CERT_ARN"
        return 0
    else
        echo "❌ No certificate found for $domain"
        return 1
    fi
}

# Function to request new certificate
request_certificate() {
    local domain=$1
    local include_wildcard=${2:-false}

    echo "📝 Requesting new certificate for $domain..."

    # Build domain validation options
    DOMAINS_TO_VALIDATE="DomainName=$domain"
    if [ "$include_wildcard" = "true" ]; then
        WILDCARD_DOMAIN="*.$domain"
        DOMAINS_TO_VALIDATE="$DOMAINS_TO_VALIDATE,SubjectAlternativeNames.member.1=$WILDCARD_DOMAIN"
        echo "Including wildcard domain: $WILDCARD_DOMAIN"
    fi

    # Request certificate
    CERT_ARN=$(aws acm request-certificate \
        --region "$REGION" \
        --domain-name "$domain" \
        --subject-alternative-names "*.$domain" \
        --validation-method DNS \
        --idempotency-token "legaledge-$ENVIRONMENT-$(date +%s)" \
        --query 'CertificateArn' \
        --output text)

    echo "✅ Certificate requested successfully: $CERT_ARN"

    # Wait for certificate to be issued
    echo "⏳ Waiting for certificate validation..."
    aws acm wait certificate-validated \
        --certificate-arn "$CERT_ARN" \
        --region "$REGION"

    echo "✅ Certificate validated and ready!"
    echo "$CERT_ARN"
}

# Function to get DNS validation records
get_validation_records() {
    local cert_arn=$1

    echo "📋 Getting DNS validation records..."

    # Get certificate details with validation options
    aws acm describe-certificate \
        --certificate-arn "$CERT_ARN" \
        --region "$REGION" \
        --query 'Certificate.DomainValidationOptions' \
        --output json
}

# Main execution
echo "🔍 Checking for existing certificate..."

if check_certificate "$DOMAIN_NAME"; then
    echo "✅ Using existing certificate: $CERT_ARN"
else
    echo "🚀 Requesting new certificate..."
    CERT_ARN=$(request_certificate "$DOMAIN_NAME" true)

    echo ""
    echo "📋 DNS Validation Records:"
    get_validation_records "$CERT_ARN"

    echo ""
    echo "⚠️  IMPORTANT: Add the DNS validation records above to your DNS provider"
    echo "For Route 53, run: ./setup-route53-validation.sh $CERT_ARN"
    echo ""
    echo "🔄 After adding DNS records, the certificate will auto-validate (can take up to 30 minutes)"
fi

# Save certificate ARN for Terraform
echo ""
echo "💾 Certificate ARN for Terraform:"
echo "ssl_certificate_arn = \"$CERT_ARN\""
echo ""
echo "Add this to your terraform.tfvars file or export as:"
echo "export SSL_CERTIFICATE_ARN=\"$CERT_ARN\""

# Test certificate (if domain is accessible)
if [ -n "$CERT_ARN" ]; then
    echo ""
    echo "🔍 Certificate Details:"
    aws acm describe-certificate \
        --certificate-arn "$CERT_ARN" \
        --region "$REGION" \
        --query 'Certificate.[DomainName, SubjectAlternativeNames, Status, InUseBy]' \
        --output table
fi

echo ""
echo "✅ SSL certificate setup completed!"
echo "Next steps:"
echo "1. Add DNS validation records (if new certificate)"
echo "2. Update terraform.tfvars with certificate ARN"
echo "3. Run Terraform deployment"
