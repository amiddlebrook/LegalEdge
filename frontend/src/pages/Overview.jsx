import { useEffect, useState } from 'react'

import { DataSourceBadge } from '../components/DataSourceBadge.jsx'
import { FeatureCard } from '../components/FeatureCard.jsx'
import { MetricCard } from '../components/MetricCard.jsx'
import { useApiCache } from '../context/ApiCacheContext.jsx'
import { api } from '../lib/api.js'
import { fallbackOverview } from '../lib/fallbacks.js'

export function OverviewPage() {
  const { fetchResource, peek } = useApiCache()
  const [overview, setOverview] = useState(() => mapOverview(peek('overview') ?? fallbackOverview))
  const [status, setStatus] = useState(peek('overview') ? 'success' : 'idle')
  const [error, setError] = useState(null)

  useEffect(() => {
    let aborted = false
    const cached = peek('overview')
    if (cached) {
      setOverview(mapOverview(cached))
      setStatus('success')
    }

    ;(async () => {
      try {
        setStatus(cached ? 'refresh' : 'loading')
        const payload = await fetchResource('overview', api.fetchOverview)
        if (aborted) return
        setOverview(mapOverview(payload))
        setStatus('success')
        setError(null)
      } catch (err) {
        if (aborted) return
        setStatus(cached ? 'success' : 'error')
        setError(err.message)
        if (!cached) {
          setOverview(mapOverview(fallbackOverview))
        }
      }
    })()

    return () => {
      aborted = true
    }
  }, [fetchResource, peek])

  return (
    <div className="mx-auto max-w-6xl space-y-16 px-6 pb-20 pt-16">
      {status === 'loading' || status === 'refresh' ? (
        <div className="rounded-xl border border-primary/40 bg-primary/10 px-4 py-2 text-sm text-primary">
          Syncing latest overview insights...
        </div>
      ) : null}
      {status === 'error' ? (
        <div className="rounded-xl border border-red-500/50 bg-red-600/10 px-4 py-2 text-sm text-red-300">
          Unable to reach the API. Showing fallback data. {error}
        </div>
      ) : null}

      <section className="flex flex-col gap-10 lg:flex-row lg:items-start lg:justify-between">
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
            <div key={step.title} className="rounded-2xl border border-slate-800 bg-card-bg/50 p-5 text-slate-200">
              <h3 className="text-lg font-semibold text-white">{step.title}</h3>
              <p className="mt-3 text-sm text-slate-300">{step.body}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function mapOverview(payload) {
  if (!payload) return fallbackOverview
  return {
    hero: payload.hero,
    dataSources: payload.data_sources ?? payload.dataSources ?? fallbackOverview.dataSources,
    features: payload.features ?? fallbackOverview.features,
    metrics: payload.metrics ?? fallbackOverview.metrics,
    workflow: payload.workflow ?? fallbackOverview.workflow,
  }
}