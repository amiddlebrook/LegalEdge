import { DataSourceBadge } from './components/DataSourceBadge.jsx'
import { FeatureCard } from './components/FeatureCard.jsx'
import { MetricCard } from './components/MetricCard.jsx'

const features = [
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
]

const dataSources = [
  'congress.gov',
  'State Legislature APIs',
  'SEC Form 4 & 13D',
  'News & RSS Feeds',
  'Custom client uploads',
]

const metrics = [
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
]

const workflow = [
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
]

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      <header className="mx-auto flex max-w-6xl flex-col gap-10 px-6 pb-12 pt-16 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/40 bg-primary/10 px-4 py-1 text-sm text-primary">
            <span className="h-2 w-2 rounded-full bg-primary animate-pulse" aria-hidden="true" />
            Real-time policy intelligence
          </div>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-white sm:text-5xl">
            LegalEdge brings predictive clarity to regulatory change.
          </h1>
          <p className="mt-4 text-lg text-slate-300">
            Connect legislation, regulatory actions, and congressional trades to understand how policy shifts will
            reverberate across portfolios before the market reacts.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            {dataSources.map((source) => (
              <DataSourceBadge key={source} label={source} />
            ))}
          </div>
        </div>
        <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-card-bg/60 p-6 text-sm text-slate-200 shadow-xl shadow-black/30">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            AI Builder Prompt Highlights
          </p>
          <ul className="mt-4 space-y-3">
            <li className="flex items-start gap-3">
              <span className="mt-1 h-2 w-2 rounded-full bg-primary" aria-hidden="true" />
              Continuously ingest cross-jurisdiction updates with minute-level latency.
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-1 h-2 w-2 rounded-full bg-primary" aria-hidden="true" />
              Correlate policy text with market performance signals and sector exposure.
            </li>
            <li className="flex items-start gap-3">
              <span className="mt-1 h-2 w-2 rounded-full bg-primary" aria-hidden="true" />
              Integrate congressional trading activity into actionable recommendations.
            </li>
          </ul>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-16 px-6 pb-20">
        <section>
          <h2 className="text-2xl font-semibold text-white">Platform pillars</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <FeatureCard key={feature.title} {...feature} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Success metrics</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-3">
            {metrics.map((metric) => (
              <MetricCard key={metric.label} {...metric} />
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-white">Workflow at a glance</h2>
          <div className="mt-6 grid gap-6 md:grid-cols-4">
            {workflow.map((step) => (
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
          <span>© {new Date().getFullYear()} LegalEdge. All rights reserved.</span>
          <span>Built with FastAPI + React + TailwindCSS on AWS-ready architecture.</span>
        </div>
      </footer>
    </div>
  )
}

export default App