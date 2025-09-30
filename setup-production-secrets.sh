#!/bin/bash
# LegalEdge Production Secrets Setup Script

set -e

# Configuration
ENVIRONMENT=${1:-production}
REGION=${AWS_REGION:-us-east-1}

echo "🔐 Setting up production secrets for LegalEdge $ENVIRONMENT environment..."
echo "Region: $REGION"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to prompt for secret input
prompt_secret() {
    local secret_name=$1
    local description=$2
    local current_value=${3:-}

    echo -e "${BLUE}🔑 $description${NC}"
    if [ -n "$current_value" ]; then
        echo "Current value: [HIDDEN]"
    fi

    read -p "Enter $secret_name (or press Enter to skip): " value
    value=$(echo "$value" | tr -d '[:space:]')

    if [ -z "$value" ] && [ -z "$current_value" ]; then
        echo -e "${YELLOW}⚠️  Skipping $secret_name${NC}"
        return 1
    fi

    if [ -z "$value" ]; then
        echo -e "${GREEN}✅ Using existing value for $secret_name${NC}"
        echo "$current_value"
    else
        echo -e "${GREEN}✅ Set new value for $secret_name${NC}"
        echo "$value"
    fi
}

# Function to create or update secret
create_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3

    echo -e "${BLUE}📦 Creating secret: $secret_name${NC}"

    # Check if secret exists
    if aws secretsmanager describe-secret --secret-id "$secret_name" --region "$REGION" >/dev/null 2>&1; then
        echo "  Updating existing secret..."
        aws secretsmanager update-secret \
            --secret-id "$secret_name" \
            --secret-string "$secret_value" \
            --region "$REGION" >/dev/null
    else
        echo "  Creating new secret..."
        aws secretsmanager create-secret \
            --name "$secret_name" \
            --secret-string "$secret_value" \
            --description "$description" \
            --region "$REGION" \
            --tags Key=Environment,Value="$ENVIRONMENT" Key=Project,Value=LegalEdge >/dev/null
    fi

    echo -e "${GREEN}✅ Secret $secret_name configured${NC}"
}

echo ""
echo -e "${YELLOW}🔧 LegalEdge Production Secrets Setup${NC}"
echo "This script will help you configure all external API keys and secrets needed for LegalEdge."
echo "You can skip any secrets you don't have by pressing Enter."
echo ""

# 1. OpenAI API Key (Required for AI features)
echo -e "${YELLOW}🤖 OpenAI Configuration (Required for AI/ML features)${NC}"
read -p "Enter your OpenAI API Key: " OPENAI_API_KEY
OPENAI_API_KEY=$(echo "$OPENAI_API_KEY" | tr -d '[:space:]')

if [ -n "$OPENAI_API_KEY" ]; then
    create_secret \
        "legaledge-$ENVIRONMENT-openai-key" \
        "$OPENAI_API_KEY" \
        "OpenAI API key for LegalEdge AI/ML features"
else
    echo -e "${RED}❌ OpenAI API key is required for LegalEdge to function${NC}"
    exit 1
fi

# 2. Email Configuration (Required for alerts)
echo ""
echo -e "${YELLOW}📧 Email Configuration (Required for alerts and notifications)${NC}"
read -p "Enter SMTP Host (e.g., smtp.gmail.com): " SMTP_HOST
read -p "Enter SMTP Port (e.g., 587): " SMTP_PORT
read -p "Enter SMTP Username/Email: " SMTP_USER
read -s -p "Enter SMTP Password: " SMTP_PASSWORD
echo ""

SMTP_HOST=$(echo "$SMTP_HOST" | tr -d '[:space:]')
SMTP_PORT=$(echo "$SMTP_PORT" | tr -d '[:space:]')
SMTP_USER=$(echo "$SMTP_USER" | tr -d '[:space:]')
SMTP_PASSWORD=$(echo "$SMTP_PASSWORD" | tr -d '[:space:]')

if [ -n "$SMTP_HOST" ] && [ -n "$SMTP_PORT" ] && [ -n "$SMTP_USER" ] && [ -n "$SMTP_PASSWORD" ]; then
    EMAIL_CONFIG=$(cat << EOF
{
    "smtp_host": "$SMTP_HOST",
    "smtp_port": $SMTP_PORT,
    "smtp_user": "$SMTP_USER",
    "smtp_password": "$SMTP_PASSWORD"
}
EOF
    )
    create_secret \
        "legaledge-$ENVIRONMENT-email-config" \
        "$EMAIL_CONFIG" \
        "Email configuration for LegalEdge alerts"
else
    echo -e "${RED}❌ Email configuration is required for LegalEdge alerts${NC}"
    exit 1
fi

# 3. Congress.gov API Key (Optional but recommended)
echo ""
echo -e "${YELLOW}🏛️  Congress.gov API Configuration (Optional - enhances legislative data)${NC}"
read -p "Enter Congress.gov API Key (or press Enter to skip): " CONGRESS_API_KEY
CONGRESS_API_KEY=$(echo "$CONGRESS_API_KEY" | tr -d '[:space:]')

if [ -n "$CONGRESS_API_KEY" ]; then
    create_secret \
        "legaledge-$ENVIRONMENT-congress-api" \
        "$CONGRESS_API_KEY" \
        "Congress.gov API key for enhanced legislative data"
fi

# 4. News API Key (Optional)
echo ""
echo -e "${YELLOW}📰 News API Configuration (Optional - for news integration)${NC}"
read -p "Enter News API Key (or press Enter to skip): " NEWS_API_KEY
NEWS_API_KEY=$(echo "$NEWS_API_KEY" | tr -d '[:space:]')

if [ -n "$NEWS_API_KEY" ]; then
    create_secret \
        "legaledge-$ENVIRONMENT-news-api" \
        "$NEWS_API_KEY" \
        "News API key for LegalEdge news integration"
fi

# 5. Market Data API Key (Optional)
echo ""
echo -e "${YELLOW}📊 Market Data API Configuration (Optional - for enhanced market data)${NC}"
read -p "Enter Market Data API Key (or press Enter to skip): " MARKET_DATA_API_KEY
MARKET_DATA_API_KEY=$(echo "$MARKET_DATA_API_KEY" | tr -d '[:space:]')

if [ -n "$MARKET_DATA_API_KEY" ]; then
    create_secret \
        "legaledge-$ENVIRONMENT-market-api" \
        "$MARKET_DATA_API_KEY" \
        "Market data API key for LegalEdge financial data"
fi

# 6. Application Secrets (Required)
echo ""
echo -e "${YELLOW}🔐 Application Security Secrets (Required)${NC}"

# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)
create_secret \
    "legaledge-$ENVIRONMENT-jwt-secret" \
    "$JWT_SECRET" \
    "JWT secret key for LegalEdge authentication"

# Generate application secret
APP_SECRET=$(openssl rand -hex 32)
create_secret \
    "legaledge-$ENVIRONMENT-app-secret" \
    "$APP_SECRET" \
    "Application secret key for LegalEdge"

echo ""
echo -e "${GREEN}🎉 Production secrets setup completed!${NC}"
echo ""
echo "📋 Summary of configured secrets:"
echo "- ✅ OpenAI API key"
echo "- ✅ Email configuration"
if [ -n "$CONGRESS_API_KEY" ]; then echo "- ✅ Congress.gov API key"; fi
if [ -n "$NEWS_API_KEY" ]; then echo "- ✅ News API key"; fi
if [ -n "$MARKET_DATA_API_KEY" ]; then echo "- ✅ Market data API key"; fi
echo "- ✅ JWT secret key"
echo "- ✅ Application secret key"
echo ""
echo "🔍 To verify secrets were created:"
echo "aws secretsmanager list-secrets --region $REGION --filter Name=legaledge-$ENVIRONMENT"
echo ""
echo "🚀 Next steps:"
echo "1. Update terraform.tfvars with your domain and SSL certificate ARN"
echo "2. Run Terraform deployment: cd infrastructure && terraform apply"
echo "3. Deploy the application with Docker and ECS"
