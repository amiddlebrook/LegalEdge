#!/bin/bash
# LegalEdge Secrets Management Setup Script

set -e

ENVIRONMENT=${1:-development}
REGION=${AWS_REGION:-us-east-1}

echo "🔐 Setting up secrets for LegalEdge $ENVIRONMENT environment..."

# Function to create or update a secret
create_secret() {
    local secret_name=$1
    local secret_value=$2
    local description=$3

    echo "Creating secret: $secret_name"

    # Check if secret exists
    if aws secretsmanager describe-secret --secret-id "$secret_name" --region "$REGION" >/dev/null 2>&1; then
        echo "  Updating existing secret..."
        aws secretsmanager update-secret \
            --secret-id "$secret_name" \
            --secret-string "$secret_value" \
            --region "$REGION"
    else
        echo "  Creating new secret..."
        aws secretsmanager create-secret \
            --name "$secret_name" \
            --secret-string "$secret_value" \
            --description "$description" \
            --region "$REGION" \
            --tags Key=Environment,Value="$ENVIRONMENT" Key=Project,Value=LegalEdge
    fi
}

# Database password (already handled by Terraform)
echo "✅ Database password secret managed by Terraform"

# JWT Secret Key
echo "🔑 Setting up JWT secret..."
create_secret \
    "legaledge-$ENVIRONMENT-jwt-secret" \
    "$(openssl rand -hex 32)" \
    "JWT secret key for LegalEdge authentication"

# Application Secret Key
echo "🔑 Setting up application secret..."
create_secret \
    "legaledge-$ENVIRONMENT-app-secret" \
    "$(openssl rand -hex 32)" \
    "Application secret key for LegalEdge"

# OpenAI API Key (if provided)
if [ ! -z "$OPENAI_API_KEY" ]; then
    echo "🤖 Setting up OpenAI API key..."
    create_secret \
        "legaledge-$ENVIRONMENT-openai-key" \
        "$OPENAI_API_KEY" \
        "OpenAI API key for LegalEdge AI features"
else
    echo "⚠️  OPENAI_API_KEY not provided, skipping OpenAI secret setup"
fi

# Email configuration (if provided)
if [ ! -z "$SMTP_PASSWORD" ]; then
    echo "📧 Setting up email configuration..."
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
    echo "⚠️  SMTP_PASSWORD not provided, skipping email secret setup"
fi

# External API Keys (if provided)
if [ ! -z "$CONGRESS_API_KEY" ]; then
    echo "🏛️  Setting up Congress API key..."
    create_secret \
        "legaledge-$ENVIRONMENT-congress-api" \
        "$CONGRESS_API_KEY" \
        "Congress.gov API key for legislative data"
fi

if [ ! -z "$NEWS_API_KEY" ]; then
    echo "📰 Setting up News API key..."
    create_secret \
        "legaledge-$ENVIRONMENT-news-api" \
        "$NEWS_API_KEY" \
        "News API key for LegalEdge"
fi

if [ ! -z "$MARKET_DATA_API_KEY" ]; then
    echo "📊 Setting up Market Data API key..."
    create_secret \
        "legaledge-$ENVIRONMENT-market-api" \
        "$MARKET_DATA_API_KEY" \
        "Market data API key for LegalEdge"
fi

echo "✅ Secrets setup completed!"
echo ""
echo "🔍 To view secrets (for verification):"
echo "aws secretsmanager list-secrets --region $REGION --filter Name=legaledge-$ENVIRONMENT"
echo ""
echo "🔄 To rotate a secret:"
echo "aws secretsmanager update-secret-version-stage --secret-id <secret-name> --version-stage AWSPENDING --remove-from-version-stage AWSCURRENT"
echo "aws secretsmanager update-secret --secret-id <secret-name> --secret-string '<new-value>'"
