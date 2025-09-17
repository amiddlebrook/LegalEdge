import { fireEvent, render } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { ApiCacheProvider } from '../context/ApiCacheContext.jsx'
import { MainLayout } from '../layouts/MainLayout.jsx'
import { api } from '../lib/api.js'

vi.mock('../lib/api.js', () => ({
  api: {
    fetchOverview: vi.fn().mockResolvedValue({
      hero: {
        kicker: 'Prefetch',
        headline: 'Prefetch overview',
        subheadline: 'Test',
        callouts: [],
      },
      data_sources: [],
      features: [],
      metrics: [],
      workflow: [],
    }),
    fetchDashboardSnapshot: vi.fn().mockResolvedValue({
      upcoming_legislation: [],
      portfolio_signals: [],
      sector_forecast: {
        sector: 'Technology',
        horizon_days: 30,
        generated_on: new Date().toISOString(),
        signals: [],
      },
    }),
    fetchAlerts: vi.fn().mockResolvedValue({ alerts: [] }),
    fetchOpportunities: vi.fn().mockResolvedValue({ opportunities: [] }),
    fetchLegislation: vi.fn().mockResolvedValue([]),
    fetchForecast: vi.fn().mockResolvedValue({
      sector: 'Technology',
      horizon_days: 30,
      generated_on: new Date().toISOString(),
      signals: [],
    }),
    fetchCoverage: vi.fn().mockResolvedValue({
      jurisdictions: [],
      state_programs: [],
      processing_health: {
        ingestion_latency_minutes: 3,
        processing_sla_minutes: 5,
        pipelines_active: 10,
        last_ingestion_run: new Date().toISOString(),
        detection_backlog: 2,
      },
      trade_surveillance: {
        active_watchlist_members: 0,
        disclosures_last_7_days: 0,
        conflicts_flagged_last_30_days: 0,
        high_priority_alerts: 0,
      },
      data_sources: [],
    }),
  },
}))

const renderWithProviders = () =>
  render(
    <ApiCacheProvider ttlMs={5000}>
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route element={<MainLayout />}>
            <Route index element={<div />} />
            <Route path="dashboard" element={<div />} />
            <Route path="coverage" element={<div />} />
          </Route>
        </Routes>
      </MemoryRouter>
    </ApiCacheProvider>,
  )

describe('MainLayout prefetch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('prefetches overview data on hover', async () => {
    const { getByText } = renderWithProviders()
    fireEvent.mouseEnter(getByText('Overview'))

    await vi.waitFor(() => expect(api.fetchOverview).toHaveBeenCalledTimes(1))
  })

  test('prefetches dashboard data on hover', async () => {
    const { getByText } = renderWithProviders()
    fireEvent.mouseEnter(getByText('Dashboard'))

    await vi.waitFor(() => {
      expect(api.fetchDashboardSnapshot).toHaveBeenCalledTimes(1)
      expect(api.fetchAlerts).toHaveBeenCalledTimes(1)
      expect(api.fetchOpportunities).toHaveBeenCalledTimes(1)
      expect(api.fetchLegislation).toHaveBeenCalledTimes(1)
      expect(api.fetchForecast).toHaveBeenCalledTimes(1)
    })
  })

  test('prefetches coverage data on hover', async () => {
    const { getByText } = renderWithProviders()
    fireEvent.mouseEnter(getByText('Coverage'))

    await vi.waitFor(() => {
      expect(api.fetchCoverage).toHaveBeenCalledTimes(1)
    })
  })
})
