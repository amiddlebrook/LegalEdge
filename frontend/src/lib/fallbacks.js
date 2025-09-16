export const fallbackOverview = {
  hero: {
    kicker: 'Real-time policy intelligence',
    headline: 'LegalEdge brings predictive clarity to regulatory change.',
    subheadline:
      'Connect legislation, regulatory actions, and congressional trades to understand how policy shifts will reverberate across portfolios before the market reacts.',
    callouts: [
      'Continuously ingest cross-jurisdiction updates with minute-level latency.',
      'Correlate policy text with market performance signals and sector exposure.',
      'Integrate congressional trading activity into actionable recommendations.',
    ],
  },
  dataSources: [
    'congress.gov',
    'State Legislature APIs',
    'SEC Form 4 & 13D',
    'News & RSS Feeds',
    'Custom client uploads',
  ],
  features: [
    {
      title: 'Legislative Tracking',
      description:
        'Monitor bills, committees, and regulatory actions across federal, state, and local jurisdictions.',
      items: [
        'Real-time ingestion from congress.gov and state portals',
        'Policy heat-maps segmented by sector',
        'Committee workflows with auto-prioritization',
      ],
    },
    {
      title: 'AI-Powered Forecasting',
      description:
        'Transformer models correlate policy language with historical market responses to surface predictive insights.',
      items: [
        'Context aware embeddings and scenario simulation',
        'Ticker, sector, and thematic exposure scoring',
        'Confidence curves delivered through the API',
      ],
    },
    {
      title: 'Congressional Portfolio Tracker',
      description:
        'Track and normalize congressional trades to reveal possible conflicts or early market signals.',
      items: [
        'Automatic pairing of disclosures with pending legislation',
        'Conflict alerts for client portfolios',
        'Audit-ready history with SOC2-aligned retention',
      ],
    },
  ],
  metrics: [
    {
      label: 'Prediction Accuracy Goal',
      value: '70%+',
      helper: 'Target precision for market impact forecasts',
    },
    {
      label: 'Retention Target',
      value: '85%+',
      helper: 'Annual customer retention objective',
    },
    {
      label: 'Processing SLA',
      value: '< 5 min',
      helper: 'Legislation ingestion-to-insight target',
    },
  ],
  workflow: [
    {
      title: 'Ingest',
      body: 'Stream legislative updates, regulatory notices, and disclosure filings into a normalized warehouse.',
    },
    {
      title: 'Enrich',
      body: 'Apply NLP entity extraction, labeling, and market correlation scoring for every policy object.',
    },
    {
      title: 'Forecast',
      body: 'Run transformer-based models to project outcomes and quantify risk-adjusted opportunities.',
    },
    {
      title: 'Act',
      body: 'Deliver alerts, API payloads, and dashboard updates tailored to venture, hedge, and retail personas.',
    },
  ],
}

export const fallbackDashboard = {
  upcomingLegislation: [
    {
      billId: 'HR-1001',
      title: 'AI Accountability and Transparency Act',
      stage: 'Committee',
      jurisdiction: 'Federal',
      summary: 'Establishes reporting standards for AI-driven trading systems.',
      nextActionDate: new Date().toISOString(),
      sentimentScore: 0.42,
      probabilityOfEnactment: 0.31,
    },
  ],
  sectorForecast: {
    sector: 'Technology',
    horizonDays: 30,
    generatedOn: new Date().toISOString(),
    signals: [
      {
        ticker: 'AIQ',
        thesis: 'AI infrastructure demand rises as compliance burdens climb.',
        expectedReturnPct: 4.2,
        confidence: 0.58,
        catalysts: ['Federal disclosure mandates', 'State AI audits'],
      },
    ],
  },
  portfolioSignals: [
    {
      ticker: 'AIQ',
      signal: 'Accumulating',
      conviction: 0.7,
      rationale: 'Trading activity aligns with pro-AI procurement bill.',
      supportingTrades: [
        {
          member: 'Sen. Jane Doe',
          chamber: 'Senate',
          ticker: 'AIQ',
          transactionType: 'BUY',
          transactionDate: new Date().toISOString(),
          amountRange: '$50k-$100k',
          relatedBill: 'S.4242',
        },
      ],
    },
  ],
  alerts: [
    {
      id: 'alert-hr1001',
      category: 'Legislation',
      title: 'House committee advances AI Accountability and Transparency Act',
      description: 'Committee markup scheduled for next week; compliance vendors projected to see increased demand.',
      severity: 'high',
      createdAt: new Date().toISOString(),
      relatedEntities: ['HR-1001', 'REGN'],
    },
  ],
  opportunities: [
    {
      ticker: 'REGN',
      thesis: 'Regtech providers set to benefit from mandatory AI compliance reporting mandates.',
      expectedReturnPct: 6.8,
      conviction: 0.67,
      horizonDays: 45,
      catalysts: ['SEC modernization', 'State privacy rules'],
      riskRating: 'medium',
    },
    {
      ticker: 'AIQ',
      thesis: 'AI infrastructure ETF gains from public sector procurement reforms favoring automation vendors.',
      expectedReturnPct: 5.4,
      conviction: 0.62,
      horizonDays: 30,
      catalysts: ['Federal AI procurement bill', 'Defense modernization budget'],
      riskRating: 'medium',
    },
  ],
}