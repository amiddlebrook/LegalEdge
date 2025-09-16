import { useEffect, useState } from 'react'
import { AlertBanner } from './components/AlertBanner.jsx'
import { DataSourceBadge } from './components/DataSourceBadge.jsx'
import { FeatureCard } from './components/FeatureCard.jsx'
import { ForecastSignalCard } from './components/ForecastSignalCard.jsx'
import { LegislationCard } from './components/LegislationCard.jsx'
import { MetricCard } from './components/MetricCard.jsx'
import { OpportunityCard } from './components/OpportunityCard.jsx'
import { PortfolioSignalCard } from './components/PortfolioSignalCard.jsx'

const fallbackOverview = {
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

const fallbackDashboard = {
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
}

const fallbackAlerts = [
  {
    id: 'alert-hr1001',
    category: 'Legislation',
    title: 'House committee advances AI Accountability and Transparency Act',
    description: 'Committee markup scheduled for next week; compliance vendors projected to see increased demand.',
    severity: 'high',
    createdAt: new Date().toISOString(),
    relatedEntities: ['HR-1001', 'REGN'],
  },
]

const fallbackOpportunities = [
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
]

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

function App() {
  const [overview, setOverview] = useState(fallbackOverview)
  const [dashboard, setDashboard] = useState(fallbackDashboard)
  const [alerts, setAlerts] = useState(fallbackAlerts)
  const [opportunities, setOpportunities] = useState(fallbackOpportunities)

  const [overviewStatus, setOverviewStatus] = useState('idle')
  const [dashboardStatus, setDashboardStatus] = useState('idle')
  const [alertsStatus, setAlertsStatus] = useState('idle')
  const [opportunitiesStatus, setOpportunitiesStatus] = useState('idle')

  const [overviewError, setOverviewError] = useState(null)
  const [dashboardError, setDashboardError] = useState(null)
  const [alertsError, setAlertsError] = useState(null)
  const [opportunitiesError, setOpportunitiesError] = useState(null)

  useEffect(() => {
    let aborted = false

    const loadOverview = async () => {
      try {
        setOverviewStatus('loading')
        const response = await fetch(`${API_BASE_URL}/overview`)
        if (!response.ok) {
          throw new Error(`overview request failed (${response.status})`)
        }
        const payload = await response.json()
        if (aborted) return
        setOverview({
          hero: payload.hero,
          dataSources: payload.data_sources,
          features: payload.features,
          metrics: payload.metrics,
          workflow: payload.workflow,
        })
        setOverviewStatus('success')
        setOverviewError(null)
      } catch (err) {
        if (aborted) return
        setOverviewStatus('error')
        setOverviewError(err.message)
      }
    }

    const loadDashboard = async () => {
      try {
        setDashboardStatus('loading')
        const response = await fetch(`${API_BASE_URL}/dashboard/snapshot`)
        if (!response.ok) {
          throw new Error(`dashboard request failed (${response.status})`)
        }
        const payload = await response.json()
        if (aborted) return
        setDashboard({
          upcomingLegislation: (payload.upcoming_legislation ?? []).map((bill) => ({
            billId: bill.bill_id,
            title: bill.title,
            stage: bill.stage,
            jurisdiction: bill.jurisdiction,
            summary: bill.summary,
            nextActionDate: bill.next_action_date,
            sentimentScore: bill.sentiment_score,
            probabilityOfEnactment: bill.probability_of_enactment,
          })),
          sectorForecast: {
            sector: payload.sector_forecast?.sector,
            horizonDays: payload.sector_forecast?.horizon_days,
            generatedOn: payload.sector_forecast?.generated_on,
            signals: (payload.sector_forecast?.signals ?? []).map((signal) => ({
              ticker: signal.ticker,
              thesis: signal.thesis,
              expectedReturnPct: signal.expected_return_pct,
              confidence: signal.confidence,
              catalysts: signal.catalysts,
            })),
          },
          portfolioSignals: (payload.portfolio_signals ?? []).map((signal) => ({
            ticker: signal.ticker,
            signal: signal.signal,
            conviction: signal.conviction,
            rationale: signal.rationale,
            supportingTrades: (signal.supporting_trades ?? []).map((trade) => ({
              member: trade.member,
              chamber: trade.chamber,
              ticker: trade.ticker,
              transactionType: trade.transaction_type,
              transactionDate: trade.transaction_date,
              amountRange: trade.amount_range,
              relatedBill: trade.related_bill,
            })),
          })),
        })
        setDashboardStatus('success')
        setDashboardError(null)
      } catch (err) {
        if (aborted) return
        setDashboardStatus('error')
        setDashboardError(err.message)
      }
    }

    const loadAlerts = async () => {
      try {
        setAlertsStatus('loading')
        const response = await fetch(`${API_BASE_URL}/alerts`)
        if (!response.ok) {
          throw new Error(`alerts request failed (${response.status})`)
        }
        const payload = await response.json()
        if (aborted) return
        setAlerts((payload.alerts ?? []).map((alert) => ({
          id: alert.id,
          category: alert.category,
          title: alert.title,
          description: alert.description,
          severity: alert.severity,
          createdAt: alert.created_at,
          relatedEntities: alert.related_entities,
        })))
        setAlertsStatus('success')
        setAlertsError(null)
      } catch (err) {
        if (aborted) return
        setAlertsStatus('error')
        setAlertsError(err.message)
      }
    }

    const loadOpportunities = async () => {
      try {
        setOpportunitiesStatus('loading')
        const response = await fetch(`${API_BASE_URL}/opportunities`)
        if (!response.ok) {
          throw new Error(`opportunities request failed (${response.status})`)
        }
        const payload = await response.json()
        if (aborted) return
        setOpportunities((payload.opportunities ?? []).map((item) => ({
          ticker: item.ticker,
          thesis: item.thesis,
          expectedReturnPct: item.expected_return_pct,
          conviction: item.conviction,
          horizonDays: item.horizon_days,
          catalysts: item.catalysts,
          riskRating: item.risk_rating,
        })))
        setOpportunitiesStatus('success')
        setOpportunitiesError(null)
      } catch (err) {
        if (aborted) return
        setOpportunitiesStatus('error')
        setOpportunitiesError(err.message)
      }
    }

    loadOverview()
    loadDashboard()
    loadAlerts()
    loadOpportunities()

    return () => {
      aborted = true
    }
  }, [])

  const isLoading =
    overviewStatus === 'loading' ||
    dashboardStatus === 'loading' ||
    alertsStatus === 'loading' ||
    opportunitiesStatus === 'loading'

  const errors = [overviewError, dashboardError, alertsError, opportunitiesError].filter(Boolean)
  const hasError = errors.length > 0

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {isLoading ? (
        <div className="bg-primary/10 py-2 text-center text-sm text-primary">Syncing latest insights...</div>
      ) : null}
      {hasError ? (
        <div className="bg-red-600/10 py-2 text-center text-sm text-red-300">
          Unable to reach the API. Serving fallback data. {errors.join(' | ')}
        </div>
      ) : null}

      <header className="mx-auto flex max-w-6xl flex-col gap-10 px-6 pb-12 pt-16 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/40 bg-primary/10 px-4 py-1 text-sm text-primary">
            <span className="h-2 w-2 animate-pulse rounded-full bg-primary" aria-hidden="true" />
            {overview.hero.kicker}
          </div>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            {overview.hero.headline}
          </h1>
          <p className="mt-4 text-lg text-slate-300">{overview.hero.subheadline}</p>
          <div className="mt-6 flex flex-wrap gap-3">
            {overview.dataSources.map((source) => (
              <DataSourceBadge key={source} label={source} />
            ))}
          </div>
        </div>
        <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-card-bg/60 p-6 text-sm text-slate-200 shadow-xl shadow-black/30">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            AI Builder Prompt Highlights
          </p>
          <ul className="mt-4 space-y-3">
            {overview.hero.callouts.map((item) => (
              <li key={item} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary" aria-hidden="true" />
                {item}
              </li>
            ))}
          </ul>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-16 px-6 pb-20">
        <section>
          <h2 className="text-2xl font-semibold text-white">Active alerts</h2>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {alerts.map((alert) => (
              <AlertBanner key={alert.id} {...alert} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Live policy radar</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-2">
            {dashboard.upcomingLegislation.map((bill) => (
              <LegislationCard key={bill.billId} {...bill} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Market opportunity engine</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {opportunities.map((item) => (
              <OpportunityCard key={item.ticker} {...item} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Forecast spotlight</h2>
          <div className="mt-2 text-sm text-slate-400">
            {dashboard.sectorForecast.sector} sector - {dashboard.sectorForecast.horizonDays}-day horizon
          </div>
          <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {dashboard.sectorForecast.signals.map((signal) => (
              <ForecastSignalCard key={`${signal.ticker}-${signal.thesis}`} {...signal} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Portfolio intelligence</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-2">
            {dashboard.portfolioSignals.map((signal) => (
              <PortfolioSignalCard key={signal.ticker} {...signal} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Platform pillars</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {overview.features.map((feature) => (
              <FeatureCard key={feature.title} {...feature} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Success metrics</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-3">
            {overview.metrics.map((metric) => (
              <MetricCard key={metric.label} {...metric} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Workflow at a glance</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-4">
            {overview.workflow.map((step) => (
              <div
                key={step.title}
                className="rounded-2xl border border-slate-800 bg-card-bg/50 p-5 text-slate-200"
              >
                <h3 className="text-lg font-semibold text-white">{step.title}</h3>
                <p className="mt-3 text-sm text-slate-300">{step.body}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-800/60 bg-slate-950/80 py-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-6 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <span>&copy; {new Date().getFullYear()} LegalEdge. All rights reserved.</span>
          <span>Built with FastAPI + React + TailwindCSS on AWS-ready architecture.</span>
        </div>
      </footer>
    </div>
  )
}

export default App