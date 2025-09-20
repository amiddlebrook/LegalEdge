import axios from 'axios'
import { toast } from 'react-hot-toast'

// Create axios instance
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  timeout: 10000,
})

// Request interceptor for auth
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }

    const message = error.response?.data?.detail || error.message || 'An error occurred'
    toast.error(message)
    return Promise.reject(error)
  }
)

export const apiClient = {
  // Authentication
  async login(credentials) {
    const formData = new URLSearchParams()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)

    const response = await axiosInstance.post('/auth/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return response.data
  },

  async register(userData) {
    const response = await axiosInstance.post('/auth/register', userData)
    return response.data
  },

  async getCurrentUser() {
    const response = await axiosInstance.get('/auth/me')
    return response.data
  },

  // Dashboard
  async fetchDashboardSnapshot() {
    const response = await axiosInstance.get('/dashboard/snapshot')
    return response.data
  },

  // Alerts
  async fetchAlerts(params = {}) {
    const response = await axiosInstance.get('/alerts', { params })
    return response.data
  },

  async createAlertSubscription(subscription) {
    const response = await axiosInstance.post('/alerts/subscriptions', subscription)
    return response.data
  },

  async updateAlertSubscription(id, updates) {
    const response = await axiosInstance.put(`/alerts/subscriptions/${id}`, updates)
    return response.data
  },

  async deleteAlertSubscription(id) {
    await axiosInstance.delete(`/alerts/subscriptions/${id}`)
  },

  // Opportunities
  async fetchOpportunities(params = {}) {
    const response = await axiosInstance.get('/opportunities', { params })
    return response.data
  },

  // Legislation
  async fetchLegislation(params = {}) {
    const response = await axiosInstance.get('/legislation/upcoming', { params })
    return response.data
  },

  // Forecasting
  async fetchForecast(params) {
    const response = await axiosInstance.get('/forecasts', { params })
    return response.data
  },

  // Portfolio
  async fetchPortfolioConflicts(params = {}) {
    const response = await axiosInstance.get('/portfolios/conflicts', { params })
    return response.data
  },

  // Task Management
  async getTaskStatus() {
    const response = await axiosInstance.get('/tasks/status')
    return response.data
  },

  async triggerIngestion() {
    const response = await axiosInstance.post('/tasks/ingestion/run')
    return response.data
  },
}

// Legacy API object for backward compatibility
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

