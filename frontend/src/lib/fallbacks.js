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
      billId: 'LR-1000',
      title: 'AI Accountability and Transparency Act',
      stage: 'Committee',
      jurisdiction: 'Federal',
      summary: 'Establishes reporting standards for AI-driven trading systems.',
      committees: ['House Energy & Commerce'],
      sectors: ['Technology', 'Financial Services'],
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
        expectedReturnPct: 0.042,
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
          relatedBill: 'LR-1000',
        },
      ],
    },
  ],
  conflictRisks: [
    {
      ticker: 'AIT',
      member: 'Sen. Jane Doe',
      chamber: 'Senate',
      transactionType: 'BUY',
      transactionDate: new Date().toISOString(),
      amountRange: '$50k-$100k',
      billId: 'LR-1000',
      billTitle: 'AI Accountability and Transparency Act',
      billStage: 'Committee',
      jurisdiction: 'Federal',
      nextActionDate: new Date(Date.now() + 7 * 86400000).toISOString(),
      riskScore: 0.72,
      confidence: 0.65,
      rationale: 'Senate accumulation ahead of AI accountability markup signals conflict exposure.',
    },
  ],
  alerts: [
    {
      id: 'alert-hr1000',
      category: 'Legislation',
      title: 'House committee advances AI Accountability and Transparency Act',
      description: 'Committee markup scheduled for next week; compliance vendors projected to see increased demand.',
      severity: 'high',
      createdAt: new Date().toISOString(),
      relatedEntities: ['LR-1000', 'AIT'],
    },
  ],
  alertPreferences: { min_severity: 'medium' },
  opportunities: [
    {
      ticker: 'AIT',
      thesis: 'Public sector AI procurement umbrella drives top-line growth.',
      expectedReturnPct: 0.072,
      conviction: 0.7,
      horizonDays: 45,
      catalysts: ['Federal AI procurement bill', 'Defense modernization roadmap'],
      riskRating: 'medium',
    },
    {
      ticker: 'REGN',
      thesis: 'Regtech vendors positioned to win compliance modernization budgets.',
      expectedReturnPct: 0.064,
      conviction: 0.68,
      horizonDays: 60,
      catalysts: ['SEC modernization tracker', 'Global transparency directives'],
      riskRating: 'balanced',
    },
  ],
  opportunityPreferences: { risk_ratings: ['medium', 'balanced'], min_conviction: 0.6, max_horizon_days: 60 },
}

export const fallbackCoverage = {
  generatedAt: new Date().toISOString(),
  jurisdictions: [
    {
      name: 'Federal',
      billsMonitored: 128,
      committeesTracked: 46,
      coverageRatio: 0.85,
      lastUpdated: new Date().toISOString(),
    },
    {
      name: 'California',
      billsMonitored: 42,
      committeesTracked: 18,
      coverageRatio: 0.7,
      lastUpdated: new Date(Date.now() - 9 * 60000).toISOString(),
    },
    {
      name: 'New York City',
      billsMonitored: 21,
      committeesTracked: 9,
      coverageRatio: 0.6,
      lastUpdated: new Date(Date.now() - 12 * 60000).toISOString(),
    },
  ],
  statePrograms: [
    {
      state: 'California',
      status: 'live',
      lastSynced: new Date(Date.now() - 9 * 60000).toISOString(),
      feeds: ['Assembly Privacy & Consumer Protection', 'Senate Judiciary'],
    },
    {
      state: 'Texas',
      status: 'beta',
      lastSynced: new Date(Date.now() - 14 * 60000).toISOString(),
      feeds: ['Senate Business & Commerce'],
    },
    {
      state: 'Florida',
      status: 'planned',
      lastSynced: new Date(Date.now() - 2 * 3600000).toISOString(),
      feeds: ['House Commerce Committee'],
    },
  ],
  processingHealth: {
    ingestionLatencyMinutes: 3.2,
    processingSlaMinutes: 5,
    pipelinesActive: 12,
    lastIngestionRun: new Date(Date.now() - 3 * 60000).toISOString(),
    detectionBacklog: 4,
  },
  tradeSurveillance: {
    activeWatchlistMembers: 38,
    disclosuresLast7Days: 62,
    conflictsFlaggedLast30Days: 11,
    highPriorityAlerts: 7,
  },
  dataSources: [
    'congress.gov',
    'State legislature portals',
    'SEC EDGAR & financial disclosures',
    'Municipal open data feeds',
    'Real-time news and RSS signals',
  ],
}


