# Getting Started with LegalEdge

Welcome to LegalEdge! This guide will help you get up and running with our AI-powered legislative intelligence platform in just a few minutes.

## Quick Start (5 Minutes)

### 1. Create Your Account
1. Go to [legaledge.com](https://legaledge.com)
2. Click **"Get Started"** or **"Sign Up"**
3. Choose your plan (start with Free to explore)
4. Enter your email and create a password
5. Check your email and verify your account

### 2. Complete Setup Wizard
The setup wizard will guide you through the basics:

**Step 1: Portfolio Setup**
- Add your current investments (ticker symbols)
- We'll analyze them for legislative risks
- Don't worry - you can add more later

**Step 2: Alert Preferences**
- Choose topics you're interested in (AI, Healthcare, Finance, etc.)
- Set your preferred notification methods
- You can customize these later

**Step 3: Platform Tour**
- Quick overview of key features
- Dashboard walkthrough
- Tips for getting the most value

### 3. Explore Your Dashboard
Your dashboard shows:
- Portfolio risk analysis
- Relevant legislation
- Market opportunities
- Active alerts

## Detailed Setup Guide

### Account Creation & Verification

#### Sign Up Process
1. **Visit LegalEdge**: Go to [legaledge.com](https://legaledge.com)
2. **Choose Plan**: Select the plan that fits your needs
3. **Enter Details**:
   - Email address (must be unique)
   - Username (for your account URL)
   - Secure password (minimum 8 characters)
   - Full name (optional)

#### Email Verification
1. Check your email for a verification link
2. Click the link to activate your account
3. You'll be redirected to log in
4. Complete the setup wizard

#### Plan Options
- **Free**: Basic legislative tracking, 1 portfolio, email alerts
- **Pro**: Unlimited portfolios, advanced analytics, priority support
- **Enterprise**: Everything plus API access, custom integrations

### Initial Configuration

#### First Login
1. Go to [legaledge.com/login](https://legaledge.com/login)
2. Enter your email and password
3. Complete two-factor authentication (if enabled)
4. Start the setup wizard

#### Setup Wizard Steps

**Portfolio Creation**
```
🎯 Create Your First Portfolio

Name: Tech Growth Portfolio
Description: Technology companies with growth potential
Holdings:
- AAPL (Apple Inc.) - 100 shares
- MSFT (Microsoft) - 50 shares
- GOOGL (Alphabet) - 25 shares
```

**Alert Configuration**
```
📢 Set Up Your Alerts

Topics: Artificial Intelligence, Technology Regulation
Jurisdictions: Federal, California
Notification: Email, In-app
Severity: Medium and above
```

**Preferences**
```
⚙️ Final Setup

Time zone: Eastern Time
Currency: USD
Default view: Dashboard
Email frequency: Daily digest
```

### Adding Your Investment Data

#### Manual Entry
1. Go to **Portfolios** → **New Portfolio**
2. Enter portfolio name and description
3. Add holdings:
   - Ticker symbol (e.g., AAPL)
   - Number of shares
   - Purchase price (optional)
   - Purchase date (optional)

#### CSV Import (Pro/Enterprise)
1. Prepare CSV file with columns:
   ```
   Ticker,Shares,Purchase Price,Purchase Date
   AAPL,100,150.25,2024-01-15
   MSFT,50,300.00,2024-01-10
   ```
2. Go to **Portfolios** → **Import**
3. Upload your CSV file
4. Review and confirm the import

#### API Integration (Enterprise)
Use our REST API to automatically sync your portfolio:

```python
import requests

def import_portfolio(api_key, portfolio_data):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.post(
        "https://api.legaledge.com/v1/portfolios/import",
        json=portfolio_data,
        headers=headers
    )
    return response.json()
```

### Setting Up Alerts & Notifications

#### Basic Alert Setup
1. Go to **Alerts** → **New Alert**
2. Choose alert type:
   - **Legislation**: Track specific bills or topics
   - **Market**: Monitor market-moving events
   - **Portfolio**: Get notified of conflicts or opportunities

3. Configure criteria:
   - Keywords (artificial intelligence, healthcare reform)
   - Jurisdictions (federal, specific states)
   - Severity levels (low, medium, high, critical)

#### Notification Channels
- **Email**: Receive alerts via email
- **SMS**: Text notifications (Pro/Enterprise)
- **Webhook**: API callbacks for automation
- **In-app**: Dashboard notifications
- **Slack**: Team chat integration (Enterprise)

#### Advanced Configuration
- **Smart Filters**: AI-powered alert relevance scoring
- **Quiet Hours**: Suppress notifications during off-hours
- **Digest Mode**: Bundle alerts into daily/weekly summaries
- **Escalation**: Increase urgency for critical alerts

### Understanding Your Dashboard

#### Overview Section
- **Portfolio Health**: Overall risk and performance
- **Active Alerts**: Items requiring attention
- **Recent Legislation**: Latest relevant bills
- **Market Opportunities**: Potential investments

#### Navigation Guide
- **Dashboard**: Main overview
- **Portfolios**: Manage your investments
- **Legislation**: Browse and search bills
- **Alerts**: Configure and view notifications
- **Analytics**: Detailed analysis and reports
- **Settings**: Account and preferences

### First Analysis Results

#### Portfolio Analysis
Within minutes, you'll see:
- **Risk Assessment**: Overall portfolio risk score
- **Sector Breakdown**: Industry diversification
- **Conflict Analysis**: Legislation affecting your holdings
- **Recommendations**: Suggested actions

#### Sample Output
```
📊 Portfolio Analysis Complete

Overall Risk: Medium (6.5/10)
Key Findings:
- Tech sector concentration: 85%
- 3 potential legislative conflicts identified
- 2 market opportunities detected
- Rebalancing recommended for better diversification

🔗 Relevant Legislation:
- AI Regulation Act (HB-1234) - Medium impact
- Data Privacy Bill (SB-567) - Low impact
- Tech Innovation Act (HB-890) - High opportunity potential
```

## Next Steps & Best Practices

### Day 1: Explore & Learn
- Review your portfolio analysis
- Check the sample legislation
- Set up 2-3 relevant alerts
- Explore the dashboard features

### Week 1: Build Your Workflow
- Add all your investment accounts
- Create topic-specific alerts
- Set up notification preferences
- Learn keyboard shortcuts and tips

### Month 1: Optimize & Integrate
- Customize your dashboard layout
- Create saved searches and filters
- Set up automated reports
- Integrate with other tools

### Tips for Success
1. **Start Small**: Begin with your main portfolio and a few key topics
2. **Review Regularly**: Check alerts and analysis weekly
3. **Stay Focused**: Don't over-subscribe to too many alerts
4. **Use Filters**: Leverage our advanced filtering to reduce noise
5. **Ask Questions**: Contact support for help and feedback

## Getting Help

### Resources Available
- **Interactive Tour**: Click "Take Tour" on your dashboard
- **Video Tutorials**: Available in the help center
- **Knowledge Base**: Comprehensive documentation
- **Live Chat**: Available during business hours
- **Email Support**: support@legaledge.com

### Common Questions
- **Q: How often is data updated?**
  - A: Legislative data updates every 6 hours, market data is real-time

- **Q: Can I export my data?**
  - A: Yes, go to Settings → Export Data

- **Q: How do I cancel or change my plan?**
  - A: Visit Settings → Subscription

## Platform Shortcuts

### Keyboard Shortcuts
- `Ctrl/Cmd + K`: Quick search
- `Ctrl/Cmd + N`: New portfolio/alert
- `Ctrl/Cmd + /`: Show shortcuts
- `Esc`: Close modals

### Quick Actions
- **Search**: Use the search bar in the top navigation
- **Quick Add**: Use the "+" button for new items
- **Bulk Actions**: Select multiple items for batch operations

## Mobile Access

LegalEdge works great on mobile devices:
- **Responsive Design**: Optimized for all screen sizes
- **Mobile App**: Available on iOS and Android (Pro/Enterprise)
- **Push Notifications**: Get alerts on your phone
- **Offline Mode**: Basic functionality without internet

## Security & Privacy

Your data security is our priority:
- **Bank-level encryption** for all data
- **SOC 2 compliance** for security standards
- **GDPR compliant** data handling
- **Regular security audits** and updates

You can delete your account anytime from Settings → Account → Delete Account.

---

🎉 **Congratulations!** You're now ready to use LegalEdge to make smarter investment decisions with the power of AI-driven legislative intelligence.

**Next Recommended Actions:**
1. ✅ Complete the setup wizard
2. ⏳ Review your portfolio analysis
3. ⏳ Set up your first alerts
4. ⏳ Explore the sample data
5. ⏳ Contact support if you need help

**Questions?** Reach out to support@legaledge.com or use the live chat in the bottom-right corner.

Welcome to LegalEdge! 🚀
