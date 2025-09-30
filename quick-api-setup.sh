#!/bin/bash
# LegalEdge Quick API Setup Script

set -e

echo "🚀 LegalEdge Quick API Setup"
echo "============================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}This script will help you quickly set up the essential APIs for LegalEdge.${NC}"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured. Please run: aws configure${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI configured${NC}"
echo ""

# 1. OpenAI API Key (Required)
echo -e "${YELLOW}🤖 Step 1: OpenAI API Setup (Required)${NC}"
echo "OpenAI powers LegalEdge's AI features for legislation analysis and forecasting."
echo ""
echo "📋 Instructions:"
echo "1. Go to: https://platform.openai.com/api-keys"
echo "2. Sign up/login to your OpenAI account"
echo "3. Create a new API key"
echo "4. Copy the key (starts with 'sk-')"
echo ""

read -p "Enter your OpenAI API Key: " OPENAI_API_KEY
OPENAI_API_KEY=$(echo "$OPENAI_API_KEY" | tr -d '[:space:]')

if [ -n "$OPENAI_API_KEY" ]; then
    # Store in AWS Secrets Manager
    aws secretsmanager create-secret \
        --name "legaledge-production-openai-key" \
        --secret-string "$OPENAI_API_KEY" \
        --description "OpenAI API key for LegalEdge AI features" \
        --region us-east-1 \
        --tags Key=Environment,Value=production Key=Project,Value=LegalEdge >/dev/null 2>&1

    echo -e "${GREEN}✅ OpenAI API key configured in Secrets Manager${NC}"
else
    echo -e "${RED}❌ OpenAI API key is required${NC}"
    exit 1
fi

echo ""

# 2. Email Setup (Required)
echo -e "${YELLOW}📧 Step 2: Email Setup (Required)${NC}"
echo "LegalEdge needs email to send alerts and notifications."
echo ""
echo "📋 Recommended: Gmail with App Password"
echo "1. Enable 2FA on your Gmail account"
echo "2. Generate App Password: Google Account → Security → App passwords"
echo "3. Choose 'Mail' and 'Other (custom name)' → LegalEdge"
echo ""

read -p "Enter your Gmail address: " EMAIL_USER
read -s -p "Enter your Gmail app password: " EMAIL_PASSWORD
echo ""

EMAIL_USER=$(echo "$EMAIL_USER" | tr -d '[:space:]')
EMAIL_PASSWORD=$(echo "$EMAIL_PASSWORD" | tr -d '[:space:]')

if [ -n "$EMAIL_USER" ] && [ -n "$EMAIL_PASSWORD" ]; then
    EMAIL_CONFIG=$(cat << EOF
{
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_user": "$EMAIL_USER",
    "smtp_password": "$EMAIL_PASSWORD"
}
EOF
    )

    aws secretsmanager create-secret \
        --name "legaledge-production-email-config" \
        --secret-string "$EMAIL_CONFIG" \
        --description "Email configuration for LegalEdge alerts" \
        --region us-east-1 \
        --tags Key=Environment,Value=production Key=Project,Value=LegalEdge >/dev/null 2>&1

    echo -e "${GREEN}✅ Email configuration set up${NC}"
else
    echo -e "${RED}❌ Email configuration is required${NC}"
    exit 1
fi

echo ""

# 3. Optional APIs
echo -e "${YELLOW}🟡 Step 3: Optional APIs (Recommended for enhanced features)${NC}"
echo ""

# Congress.gov API
read -p "Congress.gov API Key (press Enter to skip): " CONGRESS_API_KEY
CONGRESS_API_KEY=$(echo "$CONGRESS_API_KEY" | tr -d '[:space:]')

if [ -n "$CONGRESS_API_KEY" ]; then
    aws secretsmanager create-secret \
        --name "legaledge-production-congress-api" \
        --secret-string "$CONGRESS_API_KEY" \
        --description "Congress.gov API key for legislative data" \
        --region us-east-1 \
        --tags Key=Environment,Value=production Key=Project,Value=LegalEdge >/dev/null 2>&1

    echo -e "${GREEN}✅ Congress.gov API configured${NC}"
fi

# News API
read -p "News API Key (press Enter to skip): " NEWS_API_KEY
NEWS_API_KEY=$(echo "$NEWS_API_KEY" | tr -d '[:space:]')

if [ -n "$NEWS_API_KEY" ]; then
    aws secretsmanager create-secret \
        --name "legaledge-production-news-api" \
        --secret-string "$NEWS_API_KEY" \
        --description "News API key for LegalEdge" \
        --region us-east-1 \
        --tags Key=Environment,Value=production Key=Project,Value=LegalEdge >/dev/null 2>&1

    echo -e "${GREEN}✅ News API configured${NC}"
fi

# Market Data API
read -p "Market Data API Key (press Enter to skip): " MARKET_API_KEY
MARKET_API_KEY=$(echo "$MARKET_API_KEY" | tr -d '[:space:]')

if [ -n "$MARKET_API_KEY" ]; then
    aws secretsmanager create-secret \
        --name "legaledge-production-market-api" \
        --secret-string "$MARKET_API_KEY" \
        --description "Market data API key for LegalEdge" \
        --region us-east-1 \
        --tags Key=Environment,Value=production Key=Project,Value=LegalEdge >/dev/null 2>&1

    echo -e "${GREEN}✅ Market data API configured${NC}"
fi

echo ""

# 4. Generate application secrets
echo -e "${BLUE}🔐 Step 4: Generating application secrets...${NC}"

JWT_SECRET=$(openssl rand -hex 32)
APP_SECRET=$(openssl rand -hex 32)

aws secretsmanager create-secret \
    --name "legaledge-production-jwt-secret" \
    --secret-string "$JWT_SECRET" \
    --description "JWT secret key for LegalEdge authentication" \
    --region us-east-1 \
    --tags Key=Environment,Value=production Key=Project,Value=LegalEdge >/dev/null 2>&1

aws secretsmanager create-secret \
    --name "legaledge-production-app-secret" \
    --secret-string "$APP_SECRET" \
    --description "Application secret key for LegalEdge" \
    --region us-east-1 \
    --tags Key=Environment,Value=production Key=Project,Value=LegalEdge >/dev/null 2>&1

echo -e "${GREEN}✅ Application secrets generated${NC}"

echo ""

# 5. Summary
echo -e "${GREEN}🎉 API Setup Complete!${NC}"
echo ""
echo "📋 Configured APIs:"
echo "✅ OpenAI API (Required for AI features)"
echo "✅ Email service (Required for alerts)"
if [ -n "$CONGRESS_API_KEY" ]; then echo "✅ Congress.gov API (Enhanced legislative data)"; fi
if [ -n "$NEWS_API_KEY" ]; then echo "✅ News API (News integration)"; fi
if [ -n "$MARKET_API_KEY" ]; then echo "✅ Market data API (Financial data)"; fi
echo "✅ JWT secret key (Authentication)"
echo "✅ Application secret key (Security)"
echo ""

echo "💾 All secrets stored securely in AWS Secrets Manager"
echo ""

echo "🔍 To verify setup:"
echo "aws secretsmanager list-secrets --region us-east-1 --filter Name=legaledge-production"
echo ""

echo "🚀 Next steps:"
echo "1. Update terraform.tfvars with your domain and SSL certificate"
echo "2. Run: ./deploy.sh production apply"
echo "3. Run: ./verify-deployment.sh production your-domain.com"
echo ""

echo "📖 For detailed setup instructions, see: API_SETUP_GUIDE.md"
