import { useEffect, useMemo, useState } from 'react'

import { AlertBanner } from '../components/AlertBanner.jsx'
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
    signalLimit: 6,
  })

  useEffect(() => {
    let aborted = false
    ;(async () => {
      try {
        setStatus('loading')
        const [snapshot, alertsPayload, opportunitiesPayload, legislationFallback] = await Promise.all([
          api.fetchDashboardSnapshot().catch(() => null),
          api.fetchAlerts({ limit: filters.legislationLimit }).catch(() => null),
          api.fetchOpportunities({ limit: filters.signalLimit }).catch(() => null),
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
          results.sectorForecast = {
            sector: snapshot.sector_forecast?.sector,
            horizonDays: snapshot.sector_forecast?.horizon_days,
            generatedOn: snapshot.sector_forecast?.generated_on,
            signals: (snapshot.sector_forecast?.signals ?? []).map(mapForecastSignal),
          }
          results.portfolioSignals = (snapshot.portfolio_signals ?? []).map(mapPortfolioSignal)
        } else if (legislationFallback) {
          results.upcomingLegislation = legislationFallback.map(mapBill)
        }

        if (alertsPayload?.alerts) {
          results.alerts = alertsPayload.alerts.map(mapAlert)
        }

        if (opportunitiesPayload?.opportunities) {
          results.opportunities = opportunitiesPayload.opportunities.map(mapOpportunity)
        }

        // Fetch sector-specific forecast if filters changed
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
  }, [filters.horizon, filters.legislationLimit, filters.sector, filters.signalLimit])

  const legislationRows = useMemo(() => dashboard.upcomingLegislation.slice(0, filters.legislationLimit), [
    dashboard.upcomingLegislation,
    filters.legislationLimit,
  ])

  return (
    <div className="mx-auto max-w-6xl space-y-16 px-6 pb-20 pt-16">
      <section className="space-y-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <h1 className="text-3xl font-semibold text-white">Investor Dashboard</h1>
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
          <button
            type="button"
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-200 hover:border-primary"
            onClick={() => setFilters((prev) => ({ ...prev, legislationLimit: prev.legislationLimit + 2 }))}
          >
            Show more
          </button>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {dashboard.alerts.map((alert) => (
            <AlertBanner key={alert.id} {...alert} />
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-white">Upcoming legislation</h2>
        <div className="mt-6 grid gap-6 md:grid-cols-2">
          {legislationRows.map((bill) => (
            <LegislationCard key={bill.billId} {...bill} />
          ))}
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between gap-6">
          <h2 className="text-2xl font-semibold text-white">Market opportunity engine</h2>
          <button
            type="button"
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-200 hover:border-primary"
            onClick={() =>
              setFilters((prev) => ({ ...prev, signalLimit: Math.min(prev.signalLimit + 2, 12) }))
            }
          >
            Expand
          </button>
        </div>
        <div className="mt-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {dashboard.opportunities
            .slice(0, filters.signalLimit)
            .map((opportunity) => (
              <OpportunityCard key={opportunity.ticker} {...opportunity} />
            ))}
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold text-white">Forecast spotlight</h2>
        <p className="mt-2 text-sm text-slate-400">
          {dashboard.sectorForecast.sector} sector ·{' '}
          {dashboard.sectorForecast.horizonDays}-day horizon
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
    </div>
  )
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