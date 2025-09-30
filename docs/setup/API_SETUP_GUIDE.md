# LegalEdge External API Setup Guide

## Overview

LegalEdge integrates with several external APIs to provide comprehensive legislative intelligence and market insights. This guide covers all required and optional APIs, setup procedures, and integration details.

## 📋 Required APIs

### 1. OpenAI API (Required)
**Purpose**: Powers AI/ML features including legislation analysis, sentiment scoring, and market forecasting.

#### Setup Instructions:

1. **Create OpenAI Account**
   - Go to https://platform.openai.com
   - Sign up for an account (requires email verification)

2. **Get API Key**
   - Navigate to "API Keys" in your dashboard
   - Click "Create new secret key"
   - Copy the generated key (format: `sk-...`)

3. **Billing Setup**
   - Add payment method in "Billing" section
   - Start with Pay-as-you-go (no upfront commitment)

#### Cost Structure:
- **GPT-4**: ~$0.03 per 1K tokens (input/output combined)
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Estimated Monthly Cost**: $50-200 depending on usage

#### Integration:
```bash
# During deployment, run:
export OPENAI_API_KEY="sk-your-actual-key-here"
./setup-production-secrets.sh production
```

---

### 2. Email Service (Required)
**Purpose**: Sends alerts, notifications, and reports to users.

#### Option A: Gmail (Recommended for Development)
1. **Enable 2FA** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → App passwords
   - Generate password for "Mail"

#### Option B: SendGrid (Recommended for Production)
1. **Sign up**: https://sendgrid.com
2. **Verify domain** (optional but recommended)
3. **Get API Key** from SendGrid dashboard

#### Option C: Amazon SES (Cost-effective for high volume)
1. **AWS Account** with SES access
2. **Request production access** (required for sending emails)
3. **Get SMTP credentials** from SES console

#### Configuration Example:
```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

---

## 🟡 Optional but Recommended APIs

### 3. Congress.gov API
**Purpose**: Provides official legislative data, bill texts, and congressional information.

#### Setup Instructions:

1. **Register for API Key**
   - Go to https://api.data.gov/signup
   - Request access to Congress.gov API
   - Approval typically takes 1-2 business days

2. **Get API Key**
   - Once approved, you'll receive an API key via email
   - Key format: `YOUR_API_KEY_HERE`

#### Cost: Free (government API)

#### Integration:
```bash
export CONGRESS_API_KEY="your-congress-api-key"
./setup-production-secrets.sh production
```

#### Rate Limits:
- 1,000 requests per hour per IP
- 10,000 requests per hour for authenticated users

---

### 4. News API
**Purpose**: Provides news articles and RSS feeds for market context and policy analysis.

#### Recommended Options:

#### Option A: NewsAPI.org (Most Popular)
1. **Sign up**: https://newsapi.org
2. **Get API Key** from dashboard
3. **Choose plan**: Free (1,000 requests/day) or paid ($378/month)

#### Option B: Alpha Vantage News (Financial Focus)
1. **Sign up**: https://www.alphavantage.co/support/#api-key
2. **Get free API key** (500 requests/day)
3. **Upgrade for more capacity** if needed

#### Integration:
```bash
export NEWS_API_KEY="your-news-api-key"
./setup-production-secrets.sh production
```

#### Cost Comparison:
- **NewsAPI.org**: Free tier (1K/day), $378/month unlimited
- **Alpha Vantage**: Free tier (500/day), $50/month premium

---

### 5. Market Data API
**Purpose**: Provides stock prices, market data, and financial metrics for forecasting.

#### Recommended Options:

#### Option A: Alpha Vantage (Free Tier Available)
1. **Sign up**: https://www.alphavantage.co/support/#api-key
2. **Get free API key** (5 requests/min, 500/day)
3. **Upgrade to premium** ($50/month) for higher limits

#### Option B: Financial Modeling Prep (Cost-effective)
1. **Sign up**: https://financialmodelingprep.com
2. **Choose plan**: Free (250 requests/day) or paid ($14.99/month)

#### Option C: Yahoo Finance (No API key required)
- Use `yfinance` Python library (no API key needed)
- Rate limits apply (don't abuse)

#### Integration:
```bash
export MARKET_DATA_API_KEY="your-market-api-key"
./setup-production-secrets.sh production
```

---

## 🔧 API Integration Details

### Secrets Manager Structure

All API keys are stored securely in AWS Secrets Manager:

```bash
# After setup, secrets are available as:
legaledge-production-openai-key
legaledge-production-email-config
legaledge-production-congress-api    # Optional
legaledge-production-news-api        # Optional
legaledge-production-market-api      # Optional
```

### Application Integration

The application automatically loads these from environment variables:

```python
# In your application (automatically configured)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # From Secrets Manager
CONGRESS_API_KEY = os.getenv("CONGRESS_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
MARKET_DATA_API_KEY = os.getenv("MARKET_DATA_API_KEY")
```

### Error Handling

The application gracefully handles missing optional APIs:

- **Congress.gov API**: Falls back to mock legislative data
- **News API**: Uses cached/static news data
- **Market Data API**: Uses historical data or mock prices

---

## 💰 Cost Planning

### Monthly Cost Estimates:

| API | Free Tier | Paid Tier | Usage |
|-----|-----------|-----------|-------|
| **OpenAI** | ❌ | $50-200 | Required for AI features |
| **Email (SendGrid)** | 100/day | $20/month | Required for alerts |
| **Congress.gov** | ✅ Unlimited | Free | Official government data |
| **NewsAPI.org** | 1,000/day | $378/month | News integration |
| **Alpha Vantage** | 500/day | $50/month | Market data |

### Recommended Budget Allocation:

**Startup Phase** (First 3 months):
- OpenAI: $100/month
- Email: $20/month
- Total: $120/month

**Growth Phase** (After 3 months):
- OpenAI: $200/month
- Email: $20/month
- News API: $50/month (if needed)
- Market Data: $50/month (if needed)
- Total: $320/month

---

## 🚀 Setup Script Usage

Use the provided setup script for easy configuration:

```bash
# Make script executable
chmod +x setup-production-secrets.sh

# Run interactive setup
./setup-production-secrets.sh production

# The script will prompt for:
# 1. OpenAI API key (required)
# 2. Email configuration (required)
# 3. Congress.gov API key (optional)
# 4. News API key (optional)
# 5. Market data API key (optional)
```

---

## 🔍 API Feature Mapping

| Feature | Required APIs | Fallback Behavior |
|---------|---------------|-------------------|
| **Legislation Analysis** | OpenAI | Reduced accuracy analysis |
| **Market Forecasting** | OpenAI + Market Data | Historical data only |
| **Sentiment Scoring** | OpenAI | Rule-based scoring |
| **Alert Notifications** | Email Service | No alerts sent |
| **Live Legislative Data** | Congress.gov | Mock/demo data |
| **News Integration** | News API | Static news content |
| **Real-time Market Data** | Market Data API | Delayed/cached data |

---

## ⚙️ Configuration Verification

After setup, verify API integration:

```bash
# Check if APIs are responding
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Test email configuration
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
server.sendmail('from@example.com', 'to@example.com', 'Test email')
print('Email test successful')
"
```

---

## 🔄 API Management

### Monitoring API Usage:

```bash
# Check OpenAI usage
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/usage

# Monitor costs in OpenAI dashboard
# Check rate limits for other APIs
```

### Rotating API Keys:

```bash
# Update secrets in AWS Secrets Manager
aws secretsmanager update-secret \
    --secret-id "legaledge-production-openai-key" \
    --secret-string "sk-your-new-key-here"

# Redeploy application to pick up new key
aws ecs update-service --cluster legaledge-production-cluster \
    --service legaledge-production-app --force-new-deployment
```

---

## 🛠️ Troubleshooting

### Common Issues:

1. **OpenAI API Key Invalid**
   - Verify key format starts with `sk-`
   - Check if key has been revoked
   - Ensure billing is set up

2. **Email Delivery Failed**
   - Check SMTP credentials
   - Verify email provider allows app passwords
   - Check spam/junk folder

3. **Rate Limits Exceeded**
   - Implement caching for repeated requests
   - Add exponential backoff for retries
   - Consider upgrading API plans

4. **API Keys Not Loading**
   - Verify Secrets Manager permissions
   - Check ECS task execution role
   - Redeploy application

---

## 📞 Support Contacts

### API Provider Support:
- **OpenAI**: https://help.openai.com
- **SendGrid**: https://support.sendgrid.com
- **Congress.gov**: https://api.data.gov/support
- **NewsAPI**: https://newsapi.org/support
- **Alpha Vantage**: https://www.alphavantage.co/support

### LegalEdge Support:
- For integration issues: Contact development team
- For API cost concerns: Review COST_OPTIMIZATION.md

---

## 🎯 Recommended Setup Order

1. **Start with required APIs** (OpenAI + Email)
2. **Set up free government APIs** (Congress.gov)
3. **Add paid APIs as needed** based on feature requirements
4. **Monitor usage and costs** regularly
5. **Optimize and upgrade** based on actual usage patterns

This setup will give you a fully functional LegalEdge platform with room to scale API usage as your needs grow.
