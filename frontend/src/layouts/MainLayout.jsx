import { useCallback, useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'

import { useApiCache } from '../context/ApiCacheContext.jsx'
import { api } from '../lib/api.js'

const navItems = [
  { to: '/', label: 'Overview', key: 'overview' },
  { to: '/dashboard', label: 'Dashboard', key: 'dashboard' },
  { to: '/coverage', label: 'Coverage', key: 'coverage' },
]

export function MainLayout() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { fetchResource } = useApiCache()

  const prefetchOverview = useCallback(() => {
    fetchResource('overview', api.fetchOverview).catch(() => {})
  }, [fetchResource])

  const prefetchDashboard = useCallback(() => {
    fetchResource('dashboard-snapshot', api.fetchDashboardSnapshot).catch(() => {})
    fetchResource('alerts-6', () => api.fetchAlerts({ limit: 6 })).catch(() => {})
    fetchResource('opportunities-6', () => api.fetchOpportunities({ limit: 6 })).catch(() => {})
    fetchResource('legislation-6', () => api.fetchLegislation({ limit: 6 })).catch(() => {})
    fetchResource('forecast-Technology-30', () =>
      api.fetchForecast({ sector: 'Technology', horizon_days: 30 }),
    ).catch(() => {})
    fetchResource('portfolio-conflicts-6', () => api.fetchPortfolioConflicts({ limit: 6 })).catch(() => {})
  }, [fetchResource])
  const prefetchCoverage = useCallback(() => {
    fetchResource('coverage', api.fetchCoverage).catch(() => {})
  }, [fetchResource])

  const prefetchHandlers = {
    overview: prefetchOverview,
    dashboard: prefetchDashboard,
    coverage: prefetchCoverage,
  }

  const handlePrefetch = useCallback(
    (key) => {
      prefetchHandlers[key]?.()
    },
    [prefetchHandlers],
  )

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="text-lg font-semibold tracking-tight text-white" onMouseEnter={prefetchOverview}>
            LegalEdge
          </Link>
          <nav className="hidden items-center gap-6 text-sm font-medium text-slate-300 md:flex">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onMouseEnter={() => handlePrefetch(item.key)}
                onFocus={() => handlePrefetch(item.key)}
                onTouchStart={() => handlePrefetch(item.key)}
                className={({ isActive }) =>
                  `transition hover:text-white ${isActive ? 'text-primary' : ''}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-200 shadow-sm shadow-black/30 transition hover:border-primary md:hidden"
            onClick={() => setIsMenuOpen((prev) => !prev)}
            aria-expanded={isMenuOpen}
          >
            Menu
          </button>
        </div>
        {isMenuOpen ? (
          <nav className="space-y-2 border-t border-slate-800/80 px-6 py-4 text-sm font-medium text-slate-200 md:hidden">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `block rounded-lg px-3 py-2 transition hover:bg-slate-800/60 ${
                    isActive ? 'bg-primary/10 text-primary' : 'text-slate-200'
                  }`
                }
                onClick={() => setIsMenuOpen(false)}
                onFocus={() => handlePrefetch(item.key)}
                onMouseEnter={() => handlePrefetch(item.key)}
                onTouchStart={() => handlePrefetch(item.key)}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        ) : null}
      </header>

      <main>
        <Outlet />
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
