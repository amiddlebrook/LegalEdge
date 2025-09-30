#!/bin/bash
# LegalEdge Route 53 DNS Validation Setup Script

set -e

# Configuration
CERT_ARN=${1:-}
REGION=${AWS_REGION:-us-east-1}
DOMAIN_NAME=${2:-api.legaledge.com}

if [ -z "$CERT_ARN" ]; then
    echo "❌ Certificate ARN is required as first argument"
    echo "Usage: $0 <certificate-arn> [domain-name]"
    exit 1
fi

echo "🌐 Setting up Route 53 DNS validation for LegalEdge..."
echo "Certificate ARN: $CERT_ARN"
echo "Domain: $DOMAIN_NAME"
echo "Region: $REGION"

# Function to extract domain from certificate ARN or use provided domain
get_domain_from_cert() {
    local cert_arn=$1

    # Get certificate details
    DOMAIN=$(aws acm describe-certificate \
        --certificate-arn "$cert_arn" \
        --region "$REGION" \
        --query 'Certificate.DomainName' \
        --output text)

    if [ "$DOMAIN" = "None" ] || [ -z "$DOMAIN" ]; then
        echo "❌ Could not extract domain from certificate"
        return 1
    fi

    echo "$DOMAIN"
}

# Function to get or create hosted zone
get_hosted_zone_id() {
    local domain=$1

    # Try to find existing hosted zone
    HOSTED_ZONE_ID=$(aws route53 list-hosted-zones \
        --query "HostedZones[?Name==\`$domain.\`].Id" \
        --output text)

    if [ -n "$HOSTED_ZONE_ID" ] && [ "$HOSTED_ZONE_ID" != "None" ]; then
        echo "✅ Found existing hosted zone: $HOSTED_ZONE_ID"
        echo "$HOSTED_ZONE_ID"
        return 0
    fi

    # Create new hosted zone if it doesn't exist
    echo "🚀 Creating new hosted zone for $domain..."

    # Note: This requires proper IAM permissions
    # You might need to create the hosted zone manually in AWS Console
    echo "❌ No hosted zone found for $domain"
    echo "Please create a hosted zone in Route 53 manually:"
    echo "1. Go to Route 53 Console"
    echo "2. Create Hosted Zone for: $domain"
    echo "3. Copy the Hosted Zone ID"
    echo "4. Run: export HOSTED_ZONE_ID=<your-zone-id>"
    echo "5. Run this script again"

    exit 1
}

# Function to create DNS validation records
create_validation_records() {
    local cert_arn=$1
    local hosted_zone_id=$2

    echo "📝 Creating DNS validation records..."

    # Get validation options
    VALIDATION_OPTIONS=$(aws acm describe-certificate \
        --certificate-arn "$cert_arn" \
        --region "$REGION" \
        --query 'Certificate.DomainValidationOptions' \
        --output json)

    # Create Route 53 record changes
    CHANGES="["
    FIRST=true

    # Process each validation option
    while read -r option; do
        if [ "$option" != "None" ] && [ -n "$option" ]; then
            DOMAIN=$(echo "$option" | jq -r '.DomainName // empty')
            RECORD_NAME=$(echo "$option" | jq -r '.ResourceRecord.Name // empty')
            RECORD_VALUE=$(echo "$option" | jq -r '.ResourceRecord.Value // empty')

            if [ -n "$DOMAIN" ] && [ -n "$RECORD_NAME" ] && [ -n "$RECORD_VALUE" ]; then
                if [ "$FIRST" = false ]; then
                    CHANGES="$CHANGES,"
                fi

                CHANGES="$CHANGES{
                    \"Action\": \"UPSERT\",
                    \"ResourceRecordSet\": {
                        \"Name\": \"$RECORD_NAME\",
                        \"Type\": \"CNAME\",
                        \"TTL\": 300,
                        \"ResourceRecords\": [
                            {
                                \"Value\": \"$RECORD_VALUE\"
                            }
                        ]
                    }
                }"
                FIRST=false
                echo "✅ Added validation record for $DOMAIN"
            fi
        fi
    done < <(echo "$VALIDATION_OPTIONS" | jq -c '.[]')

    CHANGES="$CHANGES]"

    # Apply changes to Route 53
    echo "🔄 Applying DNS validation records to Route 53..."

    aws route53 change-resource-record-sets \
        --hosted-zone-id "$hosted_zone_id" \
        --change-batch "{
            \"Changes\": $CHANGES
        }" \
        --query 'ChangeInfo.Id' \
        --output text

    echo "✅ DNS validation records created successfully!"
}

# Main execution
echo "🔍 Determining domain and hosted zone..."

# Get domain from certificate if not provided
if [ -z "$DOMAIN_NAME" ] || [ "$DOMAIN_NAME" = "api.legaledge.com" ]; then
    DOMAIN_NAME=$(get_domain_from_cert "$CERT_ARN")
    if [ $? -ne 0 ]; then
        echo "❌ Failed to get domain from certificate"
        exit 1
    fi
fi

echo "📋 Using domain: $DOMAIN_NAME"

# Get or create hosted zone
HOSTED_ZONE_ID=$(get_hosted_zone_id "$DOMAIN_NAME")
if [ $? -ne 0 ]; then
    exit 1
fi

# Create validation records
echo ""
echo "🔧 Creating DNS validation records..."
create_validation_records "$CERT_ARN" "$HOSTED_ZONE_ID"

echo ""
echo "⏳ Waiting for DNS propagation and certificate validation..."
echo "This can take up to 30 minutes..."

# Wait for certificate validation
aws acm wait certificate-validated \
    --certificate-arn "$CERT_ARN" \
    --region "$REGION"

echo ""
echo "✅ Certificate validation completed!"
echo ""
echo "📋 Summary:"
echo "- Certificate ARN: $CERT_ARN"
echo "- Domain: $DOMAIN_NAME"
echo "- Hosted Zone ID: $HOSTED_ZONE_ID"
echo ""
echo "💾 For Terraform deployment, use these values:"
echo "ssl_certificate_arn = \"$CERT_ARN\""
echo "domain_name = \"$DOMAIN_NAME\""
echo "route53_zone_id = \"$HOSTED_ZONE_ID\""
echo ""
echo "🚀 Ready for Terraform deployment!"
