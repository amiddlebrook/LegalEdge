import { useEffect, useMemo, useState } from 'react'

import { AlertBanner } from '../components/AlertBanner.jsx'
import { DetailDrawer } from '../components/DetailDrawer.jsx'
import { ForecastSignalCard } from '../components/ForecastSignalCard.jsx'
import { LegislationCard } from '../components/LegislationCard.jsx'
import { OpportunityCard } from '../components/OpportunityCard.jsx'
import { PortfolioSignalCard } from '../components/PortfolioSignalCard.jsx'
import { api } from '../lib/api.js'
import { fallbackDashboard } from '../lib/fallbacks.js'

const sectors = ['Technology', 'Financial Services', 'Healthcare', 'Energy', 'Industrials']
const horizonOptions = [30, 45, 60, 90, 120]

export function DashboardPage() {
  const [dashboard, setDashboard] = useState(fallbackDashboard)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    sector: 'Technology',
    horizon: 30,
    legislationLimit: 6,
    opportunityLimit: 6,
  })
  const [drawerDetail, setDrawerDetail] = useState(null)

  useEffect(() => {
    let aborted = false
    ;(async () => {
      try {
        setStatus('loading')
        const [snapshot, alertsPayload, opportunitiesPayload, fallbackLegislation] = await Promise.all([
          api.fetchDashboardSnapshot().catch(() => null),
          api.fetchAlerts({ limit: filters.legislationLimit }).catch(() => null),
          api.fetchOpportunities({ limit: filters.opportunityLimit }).catch(() => null),
          api.fetchLegislation({ limit: filters.legislationLimit }).catch(() => null),
        ])

        const results = {
          upcomingLegislation: dashboard.upcomingLegislation,
          sectorForecast: dashboard.sectorForecast,
          portfolioSignals: dashboard.portfolioSignals,
          alerts: dashboard.alerts,
          opportunities: dashboard.opportunities,
        }

        if (snapshot) {
          results.upcomingLegislation = snapshot.upcoming_legislation.map(mapBill)
          results.portfolioSignals = (snapshot.portfolio_signals ?? []).map(mapPortfolioSignal)
          results.sectorForecast = {
            sector: snapshot.sector_forecast?.sector,
            horizonDays: snapshot.sector_forecast?.horizon_days,
            generatedOn: snapshot.sector_forecast?.generated_on,
            signals: (snapshot.sector_forecast?.signals ?? []).map(mapForecastSignal),
          }
        } else if (fallbackLegislation) {
          results.upcomingLegislation = fallbackLegislation.map(mapBill)
        }

        if (alertsPayload?.alerts) {
          results.alerts = alertsPayload.alerts.map(mapAlert)
        }

        if (opportunitiesPayload?.opportunities) {
          results.opportunities = opportunitiesPayload.opportunities.map(mapOpportunity)
        }

        try {
          const forecast = await api.fetchForecast({
            sector: filters.sector,
            horizon_days: filters.horizon,
          })
          results.sectorForecast = {
            sector: forecast.sector,
            horizonDays: forecast.horizon_days,
            generatedOn: forecast.generated_on,
            signals: (forecast.signals ?? []).map(mapForecastSignal),
          }
        } catch (forecastError) {
          console.debug('Forecast fetch failed, keeping previous snapshot', forecastError)
        }

        if (aborted) return
        setDashboard(results)
        setStatus('success')
        setError(null)
      } catch (err) {
        if (aborted) return
        setStatus('error')
        setError(err.message)
      }
    })()

    return () => {
      aborted = true
    }
  }, [filters.horizon, filters.legislationLimit, filters.opportunityLimit, filters.sector])

  const legislationRows = useMemo(
    () => dashboard.upcomingLegislation.slice(0, filters.legislationLimit),
    [dashboard.upcomingLegislation, filters.legislationLimit],
  )

  const openDrawer = (type, data) => {
    setDrawerDetail({ type, data })
  }

  const closeDrawer = () => setDrawerDetail(null)

  return (
    <div className="mx-auto max-w-6xl space-y-16 px-6 pb-24 pt-16">
      <section className="space-y-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-primary">Investor cockpit</p>
            <h1 className="text-3xl font-semibold text-white">Live signals from policy to portfolio</h1>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300">
            <label className="flex items-center gap-2">
              Sector
              <select
                className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-slate-100 focus:border-primary focus:outline-none"
                value={filters.sector}
                onChange={(event) =>
                  setFilters((prev) => ({ ...prev, sector: event.target.value }))
                }
              >
                {sectors.map((sector) => (
                  <option key={sector} value={sector}>
                    {sector}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-2">
              Horizon
              <select
                className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1 text-slate-100 focus:border-primary focus:outline-none"
                value={filters.horizon}
                onChange={(event) =>
                  setFilters((prev) => ({ ...prev, horizon: Number(event.target.value) }))
                }
              >
                {horizonOptions.map((option) => (
                  <option key={option} value={option}>
                    {option} days
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
        {status === 'loading' ? (
          <div className="rounded-xl border border-primary/40 bg-primary/10 px-4 py-2 text-sm text-primary">
            Syncing dashboard data...
          </div>
        ) : null}
        {status === 'error' ? (
          <div className="rounded-xl border border-red-500/50 bg-red-600/10 px-4 py-2 text-sm text-red-300">
            Unable to reach the API. Showing fallback data. {error}
          </div>
        ) : null}
      </section>

      <section>
        <div className="flex items-center justify-between gap-6">
          <h2 className="text-2xl font-semibold text-white">Active alerts</h2>
          <div className="flex items-center gap-3 text-xs">
            <button
              type="button"
              className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1 font-semibold text-slate-200 hover:border-primary"
              onClick={() => setFilters((prev) => ({ ...prev, legislationLimit: prev.legislationLimit + 2 }))}
            >
              Load more
            </button>
          </div>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {dashboard.alerts.map((alert) => (
            <button
              key={alert.id}
              type="button"
              onClick={() => openDrawer('alert', alert)}
              className="text-left"
            >
              <AlertBanner {...alert} />
            </button>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-white">Upcoming legislation</h2>
        <div className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-card-bg/60">
          <table className="w-full text-left text-sm text-slate-200">
            <thead className="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="px-4 py-3">Bill</th>
                <th className="px-4 py-3">Stage</th>
                <th className="px-4 py-3">Jurisdiction</th>
                <th className="px-4 py-3">Next action</th>
                <th className="px-4 py-3 text-right">Sentiment</th>
              </tr>
            </thead>
            <tbody>
              {legislationRows.map((bill) => (
                <tr
                  key={bill.billId}
                  className="cursor-pointer border-t border-slate-800/80 transition hover:bg-slate-900/60"
                  onClick={() => openDrawer('bill', bill)}
                >
                  <td className="px-4 py-3 font-semibold text-white">
                    <div>{bill.title}</div>
                    <p className="text-xs text-slate-400">{bill.billId}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-300">{bill.stage}</td>
                  <td className="px-4 py-3 text-slate-300">{bill.jurisdiction}</td>
                  <td className="px-4 py-3 text-slate-300">{formatDate(bill.nextActionDate)}</td>
                  <td className="px-4 py-3 text-right text-slate-300">
                    {formatPercent(bill.sentimentScore)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between gap-6">
          <h2 className="text-2xl font-semibold text-white">Market opportunity engine</h2>
          <button
            type="button"
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-200 hover:border-primary"
            onClick={() =>
              setFilters((prev) => ({ ...prev, opportunityLimit: Math.min(prev.opportunityLimit + 2, 12) }))
            }
          >
            Expand
          </button>
        </div>
        <div className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-card-bg/60">
          <table className="w-full text-left text-sm text-slate-200">
            <thead className="bg-slate-900/60 text-xs uppercase tracking-wide text-slate-400">
              <tr>
                <th className="px-4 py-3">Ticker</th>
                <th className="px-4 py-3">Thesis</th>
                <th className="px-4 py-3">Exp. return</th>
                <th className="px-4 py-3">Conviction</th>
                <th className="px-4 py-3">Risk</th>
              </tr>
            </thead>
            <tbody>
              {dashboard.opportunities.slice(0, filters.opportunityLimit).map((opportunity) => (
                <tr
                  key={opportunity.ticker}
                  className="cursor-pointer border-t border-slate-800/80 transition hover:bg-slate-900/60"
                  onClick={() => openDrawer('opportunity', opportunity)}
                >
                  <td className="px-4 py-3 font-semibold text-white">{opportunity.ticker}</td>
                  <td className="px-4 py-3 text-slate-300">{opportunity.thesis}</td>
                  <td className="px-4 py-3 text-slate-300">{formatPercent(opportunity.expectedReturnPct)}</td>
                  <td className="px-4 py-3 text-slate-300">{formatPercent(opportunity.conviction)}</td>
                  <td className="px-4 py-3 text-slate-300 capitalize">{opportunity.riskRating}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-white">Forecast spotlight</h2>
        <p className="mt-2 text-sm text-slate-400">
          {dashboard.sectorForecast.sector} sector · {dashboard.sectorForecast.horizonDays}-day horizon
        </p>
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

      <DetailDrawer open={Boolean(drawerDetail)} title={drawerTitle(drawerDetail)} onClose={closeDrawer}>
        {drawerDetail?.type === 'alert' ? <AlertDetail alert={drawerDetail.data} /> : null}
        {drawerDetail?.type === 'bill' ? <BillDetail bill={drawerDetail.data} /> : null}
        {drawerDetail?.type === 'opportunity' ? <OpportunityDetail opportunity={drawerDetail.data} /> : null}
      </DetailDrawer>
    </div>
  )
}

function AlertDetail({ alert }) {
  return (
    <div className="space-y-3 text-sm text-slate-200">
      <p className="text-xs uppercase tracking-wide text-slate-400">{alert.category}</p>
      <p className="text-sm text-slate-300">{alert.description}</p>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Severity</p>
        <p className="mt-1 text-sm text-slate-200 capitalize">{alert.severity}</p>
      </div>
      {alert.relatedEntities?.length ? (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Related entities</p>
          <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-200">
            {alert.relatedEntities.map((entity) => (
              <span key={entity} className="rounded-full border border-slate-700 px-3 py-1">
                {entity}
              </span>
            ))}
          </div>
        </div>
      ) : null}
      <p className="text-xs text-slate-400">Generated {formatDate(alert.createdAt)}</p>
    </div>
  )
}

function BillDetail({ bill }) {
  return (
    <div className="space-y-3 text-sm text-slate-200">
      <p className="text-xs uppercase tracking-wide text-slate-400">{bill.billId}</p>
      <p className="text-sm text-slate-300">{bill.summary}</p>
      <DetailList label="Stage" value={bill.stage} />
      <DetailList label="Jurisdiction" value={bill.jurisdiction} />
      <DetailList label="Next action" value={formatDate(bill.nextActionDate)} />
      <DetailList label="Committees" value={(bill.committees ?? []).join(', ') || 'N/A'} />
      <DetailList label="Sectors" value={(bill.sectors ?? []).join(', ') || 'N/A'} />
      <DetailList label="Sentiment" value={formatPercent(bill.sentimentScore)} />
      <DetailList label="Probability" value={formatPercent(bill.probabilityOfEnactment)} />
    </div>
  )
}

function OpportunityDetail({ opportunity }) {
  return (
    <div className="space-y-3 text-sm text-slate-200">
      <p className="text-xs uppercase tracking-wide text-slate-400">Ticker</p>
      <p className="text-lg font-semibold text-white">{opportunity.ticker}</p>
      <p className="text-sm text-slate-300">{opportunity.thesis}</p>
      <DetailList label="Expected return" value={formatPercent(opportunity.expectedReturnPct)} />
      <DetailList label="Conviction" value={formatPercent(opportunity.conviction)} />
      <DetailList label="Horizon" value={`${opportunity.horizonDays} days`} />
      <DetailList label="Risk" value={opportunity.riskRating} />
      {opportunity.catalysts?.length ? (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Catalysts</p>
          <ul className="mt-1 space-y-1 text-sm text-slate-200">
            {opportunity.catalysts.map((catalyst) => (
              <li key={catalyst}>• {catalyst}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  )
}

function DetailList({ label, value }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-sm text-slate-200">{value || 'N/A'}</p>
    </div>
  )
}

function drawerTitle(detail) {
  if (!detail) return ''
  if (detail.type === 'alert') return 'Policy alert detail'
  if (detail.type === 'bill') return detail.data.title
  if (detail.type === 'opportunity') return `Opportunity — ${detail.data.ticker}`
  return ''
}

function mapBill(bill) {
  return {
    billId: bill.bill_id ?? bill.billId,
    title: bill.title,
    stage: bill.stage,
    jurisdiction: bill.jurisdiction,
    summary: bill.summary,
    nextActionDate: bill.next_action_date ?? bill.nextActionDate,
    sentimentScore: bill.sentiment_score ?? bill.sentimentScore,
    probabilityOfEnactment: bill.probability_of_enactment ?? bill.probabilityOfEnactment,
    committees: bill.committees ?? [],
    sectors: bill.sectors ?? [],
  }
}

function mapForecastSignal(signal) {
  return {
    ticker: signal.ticker,
    thesis: signal.thesis,
    expectedReturnPct: signal.expected_return_pct ?? signal.expectedReturnPct,
    confidence: signal.confidence,
    catalysts: signal.catalysts ?? [],
  }
}

function mapPortfolioSignal(signal) {
  return {
    ticker: signal.ticker,
    signal: signal.signal,
    conviction: signal.conviction,
    rationale: signal.rationale,
    supportingTrades: (signal.supporting_trades ?? signal.supportingTrades ?? []).map((trade) => ({
      member: trade.member,
      chamber: trade.chamber,
      ticker: trade.ticker,
      transactionType: trade.transaction_type ?? trade.transactionType,
      transactionDate: trade.transaction_date ?? trade.transactionDate,
      amountRange: trade.amount_range ?? trade.amountRange,
      relatedBill: trade.related_bill ?? trade.relatedBill,
    })),
  }
}

function mapAlert(alert) {
  return {
    id: alert.id,
    category: alert.category,
    title: alert.title,
    description: alert.description,
    severity: alert.severity,
    createdAt: alert.created_at ?? alert.createdAt,
    relatedEntities: alert.related_entities ?? alert.relatedEntities ?? [],
  }
}

function mapOpportunity(item) {
  return {
    ticker: item.ticker,
    thesis: item.thesis,
    expectedReturnPct: item.expected_return_pct ?? item.expectedReturnPct,
    conviction: item.conviction,
    horizonDays: item.horizon_days ?? item.horizonDays,
    catalysts: item.catalysts ?? [],
    riskRating: item.risk_rating ?? item.riskRating ?? 'balanced',
  }
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return '–'
  }
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return '–'
  const scaled = Math.abs(numeric) <= 1 ? numeric * 100 : numeric
  return `${scaled.toFixed(1)}%`
}
function formatDate(value) {
  if (!value) return 'TBD'
  const dateValue = new Date(value)
  if (Number.isNaN(dateValue.valueOf())) return 'TBD'
  return dateValue.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
