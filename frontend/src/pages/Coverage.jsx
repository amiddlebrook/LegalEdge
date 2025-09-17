import { useEffect, useState } from 'react'

import { useApiCache } from '../context/ApiCacheContext.jsx'
import { api } from '../lib/api.js'
import { fallbackCoverage } from '../lib/fallbacks.js'

const statusColors = {
  live: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  beta: 'bg-amber-500/20 text-amber-200 border-amber-500/30',
  planned: 'bg-slate-500/20 text-slate-200 border-slate-500/30',
}

export function CoveragePage() {
  const { fetchResource, peek } = useApiCache()
  const [coverage, setCoverage] = useState(() => mapCoverage(peek('coverage') ?? fallbackCoverage))
  const [status, setStatus] = useState(peek('coverage') ? 'success' : 'idle')
  const [error, setError] = useState(null)

  useEffect(() => {
    let aborted = false
    const cached = peek('coverage')

    if (cached) {
      setCoverage(mapCoverage(cached))
      setStatus('success')
    }

    ;(async () => {
      try {
        setStatus(cached ? 'refresh' : 'loading')
        const payload = await fetchResource('coverage', api.fetchCoverage)
        if (aborted) return
        setCoverage(mapCoverage(payload))
        setStatus('success')
        setError(null)
      } catch (err) {
        if (aborted) return
        setStatus(cached ? 'success' : 'error')
        setError(err.message)
        if (!cached) {
          setCoverage(mapCoverage(fallbackCoverage))
        }
      }
    })()

    return () => {
      aborted = true
    }
  }, [fetchResource, peek])

  return (
    <div className="mx-auto max-w-6xl space-y-16 px-6 pb-24 pt-16">
      {status === 'loading' || status === 'refresh' ? (
        <div className="rounded-xl border border-primary/40 bg-primary/10 px-4 py-2 text-sm text-primary">
          Synchronizing national, state, and municipal coverage...
        </div>
      ) : null}
      {status === 'error' ? (
        <div className="rounded-xl border border-red-500/50 bg-red-600/10 px-4 py-2 text-sm text-red-300">
          Unable to retrieve coverage insights. Showing fallback data. {error}
        </div>
      ) : null}

      <section className="grid gap-8 lg:grid-cols-[2fr,1fr]">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/40 bg-primary/10 px-4 py-1 text-sm text-primary">
            <span className="h-2 w-2 animate-pulse rounded-full bg-primary" aria-hidden="true" />
            Coverage heartbeat
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Policy coverage across federal, state, and local networks
          </h1>
          <p className="text-lg text-slate-300">
            LegalEdge continuously ingests legislative, regulatory, and disclosure feeds to maintain a
            multi-jurisdictional policy graph. Track how close we are to platform-wide SLAs in real time.
          </p>
          <div className="flex flex-wrap gap-3 text-xs text-slate-300">
            {coverage.dataSources.map((source) => (
              <span
                key={source}
                className="rounded-full border border-slate-700 bg-slate-900/60 px-3 py-1"
              >
                {source}
              </span>
            ))}
          </div>
        </div>
        <div className="rounded-3xl border border-slate-800 bg-card-bg/60 p-6 shadow-xl shadow-black/30">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Processing health snapshot
          </p>
          <dl className="mt-4 space-y-3 text-sm">
            <StatRow
              label="Current ingestion latency"
              value={formatMinutes(coverage.processingHealth.ingestionLatencyMinutes)}
            />
            <StatRow
              label="SLA target"
              value={formatMinutes(coverage.processingHealth.processingSlaMinutes)}
            />
            <StatRow label="Pipelines active" value={coverage.processingHealth.pipelinesActive} />
            <StatRow label="Detection backlog" value={coverage.processingHealth.detectionBacklog} />
            <StatRow
              label="Last ingestion run"
              value={formatRelativeTime(coverage.processingHealth.lastIngestionRun)}
            />
          </dl>
        </div>
      </section>

      <section>
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-white">Jurisdiction coverage</h2>
            <p className="text-sm text-slate-400">
              Track monitored bills, committee saturation, and progress toward coverage targets.
            </p>
          </div>
          {coverage.generatedAt ? (
            <span className="text-xs text-slate-500">
              Generated {formatRelativeTime(coverage.generatedAt)}
            </span>
          ) : null}
        </div>
        <div className="mt-6 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {coverage.jurisdictions.map((item) => (
            <article
              key={item.name}
              className="rounded-2xl border border-slate-800 bg-card-bg/60 p-5 shadow-lg shadow-black/20"
            >
              <header className="flex items-center justify-between text-sm">
                <h3 className="text-lg font-semibold text-white">{item.name}</h3>
                <span className="text-slate-400">{formatRelativeTime(item.lastUpdated)}</span>
              </header>
              <dl className="mt-4 space-y-2 text-sm text-slate-300">
                <StatRow label="Bills monitored" value={item.billsMonitored} />
                <StatRow label="Committees tracked" value={item.committeesTracked} />
                <StatRow label="Coverage achieved" value={formatPercent(item.coverageRatio)} />
              </dl>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-8 lg:grid-cols-[1.4fr,1fr]">
        <div>
          <h2 className="text-2xl font-semibold text-white">State programs</h2>
          <p className="mt-2 text-sm text-slate-400">
            Visibility into state rollouts with live feeds, beta pilots, and planned integrations.
          </p>
          <div className="mt-6 space-y-4">
            {coverage.statePrograms.map((program) => {
              const badgeClass = statusColors[program.status] ?? statusColors.planned
              const badge = ['rounded-full border px-2 py-0.5 text-xs font-medium', badgeClass].join(' ')
              return (
                <div
                  key={program.state}
                  className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-800 bg-card-bg/60 p-4"
                >
                  <div>
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-white">{program.state}</h3>
                      <span className={badge}>{program.status}</span>
                    </div>
                    <p className="mt-2 text-xs text-slate-400">
                      Feeds: {program.feeds.length ? program.feeds.join(', ') : 'In discovery'}
                    </p>
                  </div>
                  <span className="text-xs text-slate-500">
                    Synced {formatRelativeTime(program.lastSynced)}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-card-bg/60 p-6">
          <h2 className="text-2xl font-semibold text-white">Trade surveillance</h2>
          <p className="mt-2 text-sm text-slate-400">
            Congressional trading activity linked to pending policy.
          </p>
          <dl className="mt-6 space-y-3 text-sm">
            <StatRow label="Members under watch" value={coverage.tradeSurveillance.activeWatchlistMembers} />
            <StatRow label="Disclosures (7d)" value={coverage.tradeSurveillance.disclosuresLast7Days} />
            <StatRow
              label="Conflicts flagged (30d)"
              value={coverage.tradeSurveillance.conflictsFlaggedLast30Days}
            />
            <StatRow label="High-priority alerts" value={coverage.tradeSurveillance.highPriorityAlerts} />
          </dl>
        </div>
      </section>
    </div>
  )
}

function StatRow({ label, value }) {
  return (
    <div className="flex items-center justify-between text-slate-300">
      <dt>{label}</dt>
      <dd className="text-white">{value}</dd>
    </div>
  )
}

function mapCoverage(payload) {
  if (!payload) return fallbackCoverage

  const jurisdictions = (payload.jurisdictions ?? fallbackCoverage.jurisdictions).map((item) => ({
    name: item.name,
    billsMonitored: item.bills_monitored ?? item.billsMonitored ?? 0,
    committeesTracked: item.committees_tracked ?? item.committeesTracked ?? 0,
    coverageRatio: item.coverage_ratio ?? item.coverageRatio ?? 0,
    lastUpdated: item.last_updated ?? item.lastUpdated ?? new Date().toISOString(),
  }))

  const statePrograms = (payload.state_programs ?? payload.statePrograms ?? fallbackCoverage.statePrograms).map(
    (item) => ({
      state: item.state,
      status: item.status,
      lastSynced: item.last_synced ?? item.lastSynced ?? new Date().toISOString(),
      feeds: item.feeds ?? [],
    }),
  )

  const processing = payload.processing_health ?? payload.processingHealth ?? fallbackCoverage.processingHealth
  const trade = payload.trade_surveillance ?? payload.tradeSurveillance ?? fallbackCoverage.tradeSurveillance

  return {
    generatedAt: payload.generated_at ?? payload.generatedAt ?? fallbackCoverage.generatedAt,
    jurisdictions,
    statePrograms,
    processingHealth: {
      ingestionLatencyMinutes:
        processing.ingestion_latency_minutes ?? processing.ingestionLatencyMinutes ?? fallbackCoverage.processingHealth.ingestionLatencyMinutes,
      processingSlaMinutes:
        processing.processing_sla_minutes ?? processing.processingSlaMinutes ?? fallbackCoverage.processingHealth.processingSlaMinutes,
      pipelinesActive:
        processing.pipelines_active ?? processing.pipelinesActive ?? fallbackCoverage.processingHealth.pipelinesActive,
      lastIngestionRun:
        processing.last_ingestion_run ?? processing.lastIngestionRun ?? fallbackCoverage.processingHealth.lastIngestionRun,
      detectionBacklog:
        processing.detection_backlog ?? processing.detectionBacklog ?? fallbackCoverage.processingHealth.detectionBacklog,
    },
    tradeSurveillance: {
      activeWatchlistMembers:
        trade.active_watchlist_members ?? trade.activeWatchlistMembers ?? fallbackCoverage.tradeSurveillance.activeWatchlistMembers,
      disclosuresLast7Days:
        trade.disclosures_last_7_days ?? trade.disclosuresLast7Days ?? fallbackCoverage.tradeSurveillance.disclosuresLast7Days,
      conflictsFlaggedLast30Days:
        trade.conflicts_flagged_last_30_days ?? trade.conflictsFlaggedLast30Days ?? fallbackCoverage.tradeSurveillance.conflictsFlaggedLast30Days,
      highPriorityAlerts:
        trade.high_priority_alerts ?? trade.highPriorityAlerts ?? fallbackCoverage.tradeSurveillance.highPriorityAlerts,
    },
    dataSources: payload.data_sources ?? payload.dataSources ?? fallbackCoverage.dataSources,
  }
}

function formatMinutes(value) {
  if (value === null || value === undefined) return '-'
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return '-'
  return numeric.toFixed(1) + ' min'
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return '-'
  }
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return '-'
  return Math.round(numeric * 100) + '%'
}

function formatRelativeTime(value) {
  if (!value) return 'n/a'
  const date = new Date(value)
  if (Number.isNaN(date.valueOf())) return 'n/a'
  const minutes = Math.floor((Date.now() - date.getTime()) / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return minutes + ' min ago'
  const hours = Math.floor(minutes / 60)
  if (hours < 24) {
    const hourSuffix = hours === 1 ? '' : 's'
    return hours + ' hr' + hourSuffix + ' ago'
  }
  const days = Math.floor(hours / 24)
  const daySuffix = days === 1 ? '' : 's'
  return days + ' day' + daySuffix + ' ago'
}

