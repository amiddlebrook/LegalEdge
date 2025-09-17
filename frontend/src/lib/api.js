const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

const buildQuery = (params = {}) => {
  const searchParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === '') continue
    if (Array.isArray(value)) {
      value.forEach((entry) => searchParams.append(key, entry))
    } else {
      searchParams.append(key, value)
    }
  }
  const query = searchParams.toString()
  return query ? `?${query}` : ''
}

async function apiFetch(path, options) {
  const url = `${API_BASE_URL}${path}`
  const response = await fetch(url, {
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    ...options,
  })

  if (!response.ok) {
    const error = new Error(`Request failed with status ${response.status}`)
    error.status = response.status
    error.url = url
    throw error
  }

  return response.json()
}

export const api = {
  fetchOverview() {
    return apiFetch('/overview')
  },
  fetchDashboardSnapshot() {
    return apiFetch('/dashboard/snapshot')
  },
  fetchAlerts(params = {}) {
    return apiFetch(`/alerts${buildQuery(params)}`)
  },
  fetchOpportunities(params = {}) {
    return apiFetch(`/opportunities${buildQuery(params)}`)
  },
  fetchLegislation(params = {}) {
    return apiFetch(`/legislation/upcoming${buildQuery(params)}`)
  },
  fetchForecast(params = {}) {
    return apiFetch(`/forecasts/sector${buildQuery(params)}`)
  },
  fetchPortfolioSignals(params = {}) {
    return apiFetch(`/portfolios/signals${buildQuery(params)}`)
  },
  fetchPortfolioConflicts(params = {}) {
    return apiFetch(`/portfolios/conflicts${buildQuery(params)}`)
  },
  fetchCoverage() {
    return apiFetch('/coverage')
  },
}

