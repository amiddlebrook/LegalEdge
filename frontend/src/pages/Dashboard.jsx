import { useEffect, useMemo, useState } from 'react'

import { AlertBanner } from '../components/AlertBanner.jsx'
import { ConflictRiskCard } from '../components/ConflictRiskCard.jsx'
import { ForecastSignalCard } from '../components/ForecastSignalCard.jsx'
import { LegislationCard } from '../components/LegislationCard.jsx'
import { OpportunityCard } from '../components/OpportunityCard.jsx'
import { PortfolioSignalCard } from '../components/PortfolioSignalCard.jsx'
import { useApiCache } from '../context/ApiCacheContext.jsx'
import { api } from '../lib/api.js'
import { fallbackDashboard } from '../lib/fallbacks.js'

const sectors = ['Technology', 'Financial Services', 'Healthcare', 'Energy', 'Industrials']
const horizonOptions = [30, 45, 60, 90, 120]
const riskRatingOptions = ['low', 'balanced', 'medium', 'high']
const alertSeverityOptions = [
  { value: 'all', label: 'All severities' },
  { value: 'medium', label: 'Medium+' },
  { value: 'high', label: 'High only' },
  { value: 'critical', label: 'Critical only' },
]
const alertCategoryOptions = [
  { value: 'all', label: 'All categories' },
  { value: 'Legislation', label: 'Legislation' },
  { value: 'Congressional Trades', label: 'Congressional Trades' },
  { value: 'State Policy', label: 'State Policy' },
  { value: 'Infrastructure', label: 'Infrastructure' },
]

const defaultFilters = () => {
  const opportunityPrefs = fallbackDashboard.opportunityPreferences ?? {}
  const alertPrefs = fallbackDashboard.alertPreferences ?? {}

  return {
    sector: fallbackDashboard.sectorForecast?.sector ?? 'Technology',
    horizon: fallbackDashboard.sectorForecast?.horizonDays ?? 30,
    legislationLimit: 6,
    opportunityLimit: 6,
    conflictLimit: 4,
    alertSeverity: alertPrefs.min_severity ?? 'all',
    alertCategory: alertPrefs.categories?.[0] ?? 'all',
    riskRatings: Array.isArray(opportunityPrefs.risk_ratings)
      ? [...opportunityPrefs.risk_ratings]
      : [],
    minConviction: typeof opportunityPrefs.min_conviction === 'number'
      ? opportunityPrefs.min_conviction
      : 0.55,
    maxHorizonDays: opportunityPrefs.max_horizon_days ?? 60,
  }
}

export function DashboardPage() {
  const { fetchResource, peek } = useApiCache()
  const [dashboard, setDashboard] = useState(() => mapDashboard(fallbackDashboard))
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState(defaultFilters)

  useEffect(() => {
    let aborted = false

    const alertParams = buildAlertParams(filters)
    const opportunityParams = buildOpportunityParams(filters)

    const snapshotKey = 'dashboard-snapshot'
    const alertsKey = `alerts-${filters.alertSeverity}-${filters.alertCategory}`
    const opportunitiesKey = `opportunities-${filters.opportunityLimit}-${filters.riskRatings
      .slice()
      .sort()
      .join('.')}-${filters.minConviction}-${filters.maxHorizonDays ?? 'any'}`
    const legislationKey = `legislation-${filters.legislationLimit}`
    const forecastKey = `forecast-${filters.sector}-${filters.horizon}`
    const conflictsKey = `conflicts-${filters.conflictLimit}`

    const cached = composeDashboard({
      snapshot: peek(snapshotKey),
      alertsPayload: peek(alertsKey),
      opportunitiesPayload: peek(opportunitiesKey),
      legislationPayload: peek(legislationKey),
      forecastPayload: peek(forecastKey),
      conflictsPayload: peek(conflictsKey),
      fallback: dashboard,
      filters,
    })

    if (cached !== dashboard) {
      setDashboard(cached)
      setStatus('success')
    }

    ;(async () => {
      try {
        setStatus(cached === dashboard ? 'loading' : 'refresh')
        const [
          snapshot,
          alertsPayload,
          opportunitiesPayload,
          legislationPayload,
          forecastPayload,
          conflictsPayload,
        ] = await Promise.all([
          fetchResource(snapshotKey, api.fetchDashboardSnapshot).catch(() => null),
          fetchResource(alertsKey, () => api.fetchAlerts({ ...alertParams, limit: 4 })).catch(() => null),
          fetchResource(opportunitiesKey, () =>
            api.fetchOpportunities({ ...opportunityParams, limit: filters.opportunityLimit }),
          ).catch(() => null),
          fetchResource(legislationKey, () => api.fetchLegislation({ limit: filters.legislationLimit })).catch(
            () => null,
          ),
          fetchResource(forecastKey, () =>
            api.fetchForecast({ sector: filters.sector, horizon_days: filters.horizon }),
          ).catch(() => null),
          fetchResource(conflictsKey, () => api.fetchPortfolioConflicts({ limit: filters.conflictLimit })).catch(
            () => null,
          ),
        ])

        if (aborted) return
        setDashboard((current) =>
          composeDashboard({
            snapshot,
            alertsPayload,
            opportunitiesPayload,
            legislationPayload,
            forecastPayload,
            conflictsPayload,
            fallback: current,
            filters,
          }),
        )
        setStatus('success')
        setError(null)
      } catch (err) {
        if (aborted) return
        setStatus(cached === dashboard ? 'error' : 'success')
        setError(err.message)
        if (cached === dashboard) {
          setDashboard(mapDashboard(fallbackDashboard))
        }
      }
    })()

    return () => {
      aborted = true
    }
  }, [fetchResource, peek, filters])

  const legislationRows = useMemo(
    () => dashboard.upcomingLegislation.slice(0, filters.legislationLimit),
    [dashboard.upcomingLegislation, filters.legislationLimit],
  )

  const toggleRiskRating = (value) => {
    setFilters((prev) => {
      const next = prev.riskRatings.includes(value)
        ? prev.riskRatings.filter((item) => item !== value)
        : [...prev.riskRatings, value]
      return { ...prev, riskRatings: next.sort() }
    })
  }

  return (
    <div className="mx-auto max-w-6xl space-y-16 px-6 pb-24 pt-16">
      {status === 'loading' || status === 'refresh' ? (
        <div className="rounded-xl border border-primary/40 bg-primary/10 px-4 py-2 text-sm text-primary">
          Synchronizing live policy intelligence...
        </div>
      ) : null}
      {status === 'error' ? (
        <div className="rounded-xl border border-red-500/50 bg-red-600/10 px-4 py-2 text-sm text-red-300">
          Unable to reach the API. Showing fallback data. {error}
        </div>
      ) : null}

      <section className="grid gap-8 lg:grid-cols-[1.2fr,1fr]">
        <div className="space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-primary">Investor cockpit</p>
          <h1 className="text-3xl font-semibold text-white sm:text-4xl">
            Live signals from policy momentum to portfolio action
          </h1>
          <p className="text-sm text-slate-300">
            Adjust horizon, risk appetite, and alert focus to tune LegalEdge recommendations. Data refreshes
            automatically when filters change.
          </p>
        </div>
        <div className="rounded-3xl border border-slate-800 bg-card-bg/60 p-6 text-sm text-slate-200">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-wide text-slate-400">Sector focus</span>
              <select
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 focus:border-primary focus:outline-none"
                value={filters.sector}
                onChange={(event) => setFilters((prev) => ({ ...prev, sector: event.target.value }))}
              >
                {sectors.map((sector) => (
                  <option key={sector} value={sector}>
                    {sector}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-wide text-slate-400">Forecast horizon</span>
              <select
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 focus:border-primary focus:outline-none"
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
            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-wide text-slate-400">Min conviction</span>
              <div className="flex items-center gap-3">
                <input
                  type="range"
                  min={0}
                  max={100}
                  step={5}
                  value={Math.round((filters.minConviction ?? 0) * 100)}
                  onChange={(event) =>
                    setFilters((prev) => ({ ...prev, minConviction: Number(event.target.value) / 100 }))
                  }
                  className="flex-1"
                />
                <span className="w-16 text-sm text-slate-200">
                  {Math.round((filters.minConviction ?? 0) * 100)}%
                </span>
              </div>
            </label>
            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-wide text-slate-400">Max horizon (days)</span>
              <input
                type="number"
                min={15}
                max={180}
                value={filters.maxHorizonDays ?? ''}
                onChange={(event) => {
                  const value = event.target.value
                  setFilters((prev) => ({
                    ...prev,
                    maxHorizonDays: value === '' ? null : Number(value),
                  }))
                }}
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 focus:border-primary focus:outline-none"
              />
            </label>
          </div>
        </div>
      </section>

      <section className="rounded-3xl border border-slate-800 bg-card-bg/60 p-6 text-sm text-slate-200">
        <div className="grid gap-6 lg:grid-cols-[1fr,1fr]">
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Alert controls</h2>
            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-wide text-slate-400">Minimum severity</span>
              <select
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 focus:border-primary focus:outline-none"
                value={filters.alertSeverity}
                onChange={(event) => setFilters((prev) => ({ ...prev, alertSeverity: event.target.value }))}
              >
                {alertSeverityOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-wide text-slate-400">Category focus</span>
              <select
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 focus:border-primary focus:outline-none"
                value={filters.alertCategory}
                onChange={(event) => setFilters((prev) => ({ ...prev, alertCategory: event.target.value }))}
              >
                {alertCategoryOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-white">Opportunity risk bands</h2>
            <div className="flex flex-wrap gap-2">
              {riskRatingOptions.map((rating) => {
                const active = filters.riskRatings.includes(rating)
                return (
                  <button
                    key={rating}
                    type="button"
                    onClick={() => toggleRiskRating(rating)}
                    className={`rounded-full border px-3 py-1 text-xs font-semibold transition ${
                      active
                        ? 'border-primary bg-primary/20 text-primary'
                        : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-primary/60 hover:text-primary'
                    }`}
                  >
                    {rating}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-2xl font-semibold text-white">Real-time alerts</h2>
          <span className="text-xs text-slate-500">{formatAlertFilters(dashboard.alertFilters)}</span>
        </div>
              {dashboard.opportunityMeta.scoringNotes ? (
                <span className="text-slate-400">{dashboard.opportunityMeta.scoringNotes}</span>
              ) : null}
              {dashboard.opportunityMeta.topDrivers?.length ? (
                <div className="flex flex-wrap gap-2">
                  {dashboard.opportunityMeta.topDrivers.slice(0, 3).map((driver) => (
                    <span
                      key={driver}
                      className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200"
                    >
                      {driver}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}

        <div className="grid gap-4 md:grid-cols-2">
          {dashboard.alerts.length ? (
            dashboard.alerts.slice(0, 4).map((alert) => <AlertBanner key={alert.id} {...alert} />)
          ) : (
            <p className="text-sm text-slate-400">No alerts match the current filters.</p>
          )}
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-2xl font-semibold text-white">Upcoming legislation</h2>
          <span className="text-xs text-slate-500">
            {dashboard.upcomingLegislation.length} bills tracked
          </span>
        </div>
        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {legislationRows.map((bill) => (
            <LegislationCard key={bill.billId} {...bill} />
          ))}
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-[1fr,1.2fr]">
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-2xl font-semibold text-white">Sector forecast</h2>
            <span className="text-xs text-slate-500">
              {dashboard.sectorForecast.generatedOn
                ? `Generated ${new Date(dashboard.sectorForecast.generatedOn).toLocaleDateString('en-US')}`
                : 'Pending'}
            </span>
          </div>
          <div className="space-y-4">
            {dashboard.sectorForecast.signals.length ? (
              dashboard.sectorForecast.signals.map((signal) => (
                <ForecastSignalCard key={signal.ticker} {...signal} />
              ))
            ) : (
              <p className="text-sm text-slate-400">No forecast signals available.</p>
            )}
          </div>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-2xl font-semibold text-white">Market opportunities</h2>
            <span className="text-xs text-slate-500">{formatOpportunityFilters(dashboard.opportunityFilters)}</span>
          </div>
          {(dashboard.opportunityMeta &&
            (dashboard.opportunityMeta.rankerVersion ||
              dashboard.opportunityMeta.scoringNotes ||
              (dashboard.opportunityMeta.topDrivers?.length ?? 0) > 0)) ? (
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-400">
              {dashboard.opportunityMeta.rankerVersion ? (
                <span className="rounded-full border border-slate-700/60 bg-slate-800/60 px-2 py-0.5 text-slate-200">
                  Ranker {dashboard.opportunityMeta.rankerVersion}
                </span>
              ) : null}
              {dashboard.opportunityMeta.scoringNotes ? (
                <span className="text-slate-400">{dashboard.opportunityMeta.scoringNotes}</span>
              ) : null}
              {dashboard.opportunityMeta.topDrivers?.length ? (
                <div className="flex flex-wrap gap-2">
                  {dashboard.opportunityMeta.topDrivers.slice(0, 3).map((driver) => (
                    <span
                      key={driver}
                      className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200"
                    >
                      {driver}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : null}

          <div className="grid gap-4 md:grid-cols-2">
            {dashboard.opportunities.length ? (
              dashboard.opportunities.slice(0, filters.opportunityLimit).map((item) => (
                <OpportunityCard key={item.ticker} {...item} />
              ))
            ) : (
              <p className="text-sm text-slate-400">No opportunities match the selected filters.</p>
            )}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-white">Congressional portfolio signals</h2>
        <div className="grid gap-4 md:grid-cols-2">
          {dashboard.portfolioSignals.map((signal) => (
            <PortfolioSignalCard key={signal.ticker} {...signal} />
          ))}
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-2xl font-semibold text-white">Potential conflict hotspots</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {dashboard.conflictRisks.slice(0, filters.conflictLimit).map((conflict) => (
            <ConflictRiskCard key={`${conflict.ticker}-${conflict.member}`} {...conflict} />
          ))}
        </div>
      </section>
    </div>
  )
}

function buildAlertParams(filters) {
  const params = {}
  if (filters.alertSeverity && filters.alertSeverity !== 'all') {
    params.min_severity = filters.alertSeverity
  }
  if (filters.alertCategory && filters.alertCategory !== 'all') {
    params.categories = [filters.alertCategory]
  }
  return params
}

function buildOpportunityParams(filters) {
  const params = {}
  if (filters.riskRatings?.length) {
    params.risk_ratings = filters.riskRatings
  }
  if (typeof filters.minConviction === 'number' && filters.minConviction > 0) {
    params.min_conviction = Number(filters.minConviction.toFixed(2))
  }
  if (filters.maxHorizonDays) {
    params.max_horizon_days = filters.maxHorizonDays
  }
  return params
}

function composeDashboard({
  snapshot,
  alertsPayload,
  opportunitiesPayload,
  legislationPayload,
  forecastPayload,
  conflictsPayload,
  fallback,
  filters,
}) {
  const base = fallback ?? mapDashboard(fallbackDashboard)
  const next = {
    upcomingLegislation: base.upcomingLegislation,
    sectorForecast: base.sectorForecast,
    portfolioSignals: base.portfolioSignals,
    conflictRisks: base.conflictRisks,
    alerts: base.alerts,
    opportunities: base.opportunities,
    alertFilters: base.alertFilters,
    opportunityFilters: base.opportunityFilters,
    opportunityMeta: base.opportunityMeta,
  }

  let changed = false

  if (snapshot?.upcoming_legislation?.length) {
    next.upcomingLegislation = snapshot.upcoming_legislation.map(mapBill)
    changed = true
  } else if (Array.isArray(legislationPayload) && legislationPayload.length) {
    next.upcomingLegislation = legislationPayload.map(mapBill)
    changed = true
  }

  const forecastSource = forecastPayload ?? snapshot?.sector_forecast
  if (forecastSource) {
    const estimatedAccuracy = forecastSource.estimated_accuracy ?? forecastSource.estimatedAccuracy ?? 0.72;
    const methodologySummary = forecastSource.methodology_summary ?? forecastSource.methodologySummary ?? 'Hybrid policy sentiment and price momentum baseline.';
    const drivers = forecastSource.drivers ?? [];
    next.sectorForecast = {
      sector: forecastSource.sector ?? filters.sector,
      horizonDays: forecastSource.horizon_days ?? forecastSource.horizonDays ?? filters.horizon,
      generatedOn: forecastSource.generated_on ?? forecastSource.generatedOn ?? new Date().toISOString(),
      estimatedAccuracy,
      methodologySummary,
      drivers,
      signals: (forecastSource.signals ?? []).map(mapForecastSignal),
    }
    changed = true
  }

  if (snapshot?.portfolio_signals?.length) {
    next.portfolioSignals = snapshot.portfolio_signals.map(mapPortfolioSignal)
    changed = true
  }

  if (Array.isArray(conflictsPayload) && conflictsPayload.length) {
    next.conflictRisks = conflictsPayload.map(mapConflict)
    changed = true
  }

  if (alertsPayload?.alerts?.length) {
    next.alerts = alertsPayload.alerts.map(mapAlert)
    next.alertFilters = alertsPayload.applied_filters ?? next.alertFilters
    changed = true
  }

  if (snapshot?.opportunity_metadata || snapshot?.opportunityMeta) {
    next.opportunityMeta = mapOpportunityMeta(
      snapshot.opportunity_metadata ?? snapshot.opportunityMeta,
    )
    changed = true
  }

  if (opportunitiesPayload?.opportunities?.length) {
    next.opportunities = opportunitiesPayload.opportunities.map(mapOpportunity)
    next.opportunityFilters = opportunitiesPayload.applied_filters ?? next.opportunityFilters
    changed = true
  }

  if (
    opportunitiesPayload &&
    (
      opportunitiesPayload.ranker_version ||
      opportunitiesPayload.scoring_notes ||
      (opportunitiesPayload.top_drivers ?? []).length
    )
  ) {
    next.opportunityMeta = mapOpportunityMeta({
      ranker_version: opportunitiesPayload.ranker_version,
      scoring_notes: opportunitiesPayload.scoring_notes,
      top_drivers: opportunitiesPayload.top_drivers,
    })
    changed = true
  }

  return changed ? next : base
}

function mapDashboard(payload) {
  if (!payload) {
    return {
      upcomingLegislation: [],
      sectorForecast: {
        sector: 'Technology',
        horizonDays: 30,
        generatedOn: new Date().toISOString(),
        estimatedAccuracy: 0.72,
        methodologySummary: 'Hybrid policy sentiment and price momentum baseline.',
        drivers: [],
        signals: [],
      },
      portfolioSignals: [],
      conflictRisks: [],
      alerts: [],
      opportunities: [],
      alertFilters: null,
      opportunityFilters: null,
      opportunityMeta: mapOpportunityMeta(),
    }
  }

  const rawForecast = payload.sectorForecast ?? payload.sector_forecast ?? {}
  const mappedForecast = {
    sector: rawForecast.sector ?? 'Technology',
    horizonDays: rawForecast.horizon_days ?? rawForecast.horizonDays ?? 30,
    generatedOn: rawForecast.generated_on ?? rawForecast.generatedOn ?? new Date().toISOString(),
    estimatedAccuracy:
      rawForecast.estimated_accuracy ?? rawForecast.estimatedAccuracy ?? 0.72,
    methodologySummary:
      rawForecast.methodology_summary ?? rawForecast.methodologySummary ??
      'Hybrid policy sentiment and price momentum baseline.',
    drivers: rawForecast.drivers ?? [],
    signals: (rawForecast.signals ?? []).map(mapForecastSignal),
  }

  return {
    upcomingLegislation: (payload.upcomingLegislation ?? payload.upcoming_legislation ?? []).map(mapBill),
    sectorForecast: mappedForecast,
    portfolioSignals: (payload.portfolioSignals ?? payload.portfolio_signals ?? []).map(mapPortfolioSignal),
    conflictRisks: (payload.conflictRisks ?? payload.conflict_risks ?? []).map(mapConflict),
    alerts: (payload.alerts ?? []).map(mapAlert),
    opportunities: (payload.opportunities ?? []).map(mapOpportunity),
    alertFilters:
      payload.alertFilters ?? payload.alert_preferences ?? payload.alertPreferences ?? null,
    opportunityFilters:
      payload.opportunityFilters ?? payload.opportunity_preferences ?? payload.opportunityPreferences ?? null,
    opportunityMeta: mapOpportunityMeta(
      payload.opportunityMeta ??
        payload.opportunity_meta ??
        payload.opportunityMetadata ??
        null,
    ),
  }
}
function mapBill(bill) {
  if (!bill) return null
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

function mapConflict(conflict) {
  return {
    ticker: conflict.ticker,
    member: conflict.member,
    chamber: conflict.chamber,
    transactionType: conflict.transaction_type ?? conflict.transactionType,
    transactionDate: conflict.transaction_date ?? conflict.transactionDate,
    amountRange: conflict.amount_range ?? conflict.amountRange,
    billTitle: conflict.bill_title ?? conflict.billTitle ?? 'Associated legislation pending',
    billStage: conflict.bill_stage ?? conflict.billStage ?? 'Pending',
    jurisdiction: conflict.jurisdiction ?? 'Federal',
    nextActionDate: conflict.next_action_date ?? conflict.nextActionDate ?? null,
    riskScore: conflict.risk_score ?? conflict.riskScore ?? 0,
    confidence: conflict.confidence ?? 0,
    rationale: conflict.rationale ?? 'Conflict rationale unavailable.',
  }
}

function mapAlert(alert) {
  return {
    id: alert.id ?? alert.alert_key ?? crypto.randomUUID(),
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
    compositeScore: item.composite_score ?? item.compositeScore ?? null,
    policyAlignment: item.policy_alignment ?? item.policyAlignment ?? null,
    conflictScore: item.conflict_score ?? item.conflictScore ?? null,
    policyAlpha: item.policy_alpha ?? item.policyAlpha ?? null,
    drivers: item.drivers ?? [],
    explanation: item.explanation ?? null,
    methodology: item.methodology ?? item.methodologySummary ?? null,
  }
}

function mapOpportunityMeta(meta) {
  const source = meta ?? {}
  const rawDrivers = source.topDrivers ?? source.top_drivers ?? []
  return {
    rankerVersion: source.rankerVersion ?? source.ranker_version ?? null,
    scoringNotes: source.scoringNotes ?? source.scoring_notes ?? null,
    topDrivers: Array.isArray(rawDrivers) ? [...rawDrivers] : [],
  }
}

function formatOpportunityFilters(filters) {
  if (!filters) return 'No filters applied'
  const items = []
  const risk = filters.risk_ratings ?? filters.riskRatings
  if (Array.isArray(risk) && risk.length) {
    items.push('Risk: ' + risk.join(', '))
  }
  const minConviction = filters.min_conviction ?? filters.minConviction
  if (typeof minConviction === 'number') {
    items.push('Min conviction: ' + Math.round(minConviction * 100) + '%')
  }
  const horizon = filters.max_horizon_days ?? filters.maxHorizonDays
  if (typeof horizon === 'number') {
    items.push('Horizon <= ' + horizon + 'd')
  }
  return items.length ? items.join(' | ') : 'No filters applied'
}

function formatAlertFilters(filters) {
  if (!filters) return 'No alert filters applied'
  const parts = []
  const minSeverity = filters.min_severity ?? filters.minSeverity
  if (minSeverity) {
    parts.push(`Min severity ${minSeverity}`)
  }
  const categories = filters.categories
  if (Array.isArray(categories) && categories.length) {
    parts.push(`Categories: ${categories.join(', ')}`)
  }
  return parts.length ? parts.join(' | ') : 'No alert filters applied'
}





