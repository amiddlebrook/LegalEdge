import { createContext, useContext, useReducer, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { apiClient } from '../lib/api'

// Action types for user preferences
const PREFERENCES_ACTIONS = {
  UPDATE_PREFERENCES: 'UPDATE_PREFERENCES',
  TOGGLE_THEME: 'TOGGLE_THEME',
  SET_NOTIFICATIONS: 'SET_NOTIFICATIONS',
  SET_PERSONA: 'SET_PERSONA'
}

// Initial state
const initialPreferences = {
  theme: 'dark',
  notifications: 'important',
  refreshInterval: 30,
  exportFormat: 'csv',
  timezone: 'UTC',
  language: 'en',
  persona: 'investor',
  compactView: false,
  autoRefresh: true
}

// Reducer for preferences
function preferencesReducer(state, action) {
  switch (action.type) {
    case PREFERENCES_ACTIONS.UPDATE_PREFERENCES:
      return { ...state, ...action.payload }
    case PREFERENCES_ACTIONS.TOGGLE_THEME:
      return { ...state, theme: state.theme === 'dark' ? 'light' : 'dark' }
    case PREFERENCES_ACTIONS.SET_NOTIFICATIONS:
      return { ...state, notifications: action.payload }
    case PREFERENCES_ACTIONS.SET_PERSONA:
      return { ...state, persona: action.payload }
    default:
      return state
  }
}

// Create contexts
const AuthContext = createContext()
const PreferencesContext = createContext()
const GlobalContext = createContext()

// Auth Provider
export function AuthProvider({ children }) {
  const queryClient = useQueryClient()

  const { data: user, isLoading, error } = useQuery({
    queryKey: ['auth', 'currentUser'],
    queryFn: apiClient.getCurrentUser,
    enabled: !!localStorage.getItem('auth_token'),
    retry: false,
  })

  const loginMutation = useMutation({
    mutationFn: apiClient.login,
    onSuccess: (data) => {
      localStorage.setItem('auth_token', data.access_token)
      queryClient.setQueryData(['auth', 'currentUser'], data.user)
      toast.success('Logged in successfully')
    },
    onError: (error) => {
      toast.error('Login failed')
    }
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      localStorage.removeItem('auth_token')
      return true
    },
    onSuccess: () => {
      queryClient.clear()
      toast.success('Logged out successfully')
    }
  })

  const value = {
    user,
    isLoading,
    error,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    isLoggedIn: !!user
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Preferences Provider
export function PreferencesProvider({ children }) {
  const [preferences, dispatch] = useReducer(preferencesReducer, initialPreferences)

  // Load preferences from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('legaledge_preferences')
    if (saved) {
      try {
        const parsedPreferences = JSON.parse(saved)
        dispatch({ type: PREFERENCES_ACTIONS.UPDATE_PREFERENCES, payload: parsedPreferences })
      } catch (error) {
        console.error('Failed to parse saved preferences:', error)
      }
    }
  }, [])

  // Save preferences to localStorage when they change
  useEffect(() => {
    localStorage.setItem('legaledge_preferences', JSON.stringify(preferences))
  }, [preferences])

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(preferences.theme)
  }, [preferences.theme])

  const updatePreferences = (updates) => {
    dispatch({ type: PREFERENCES_ACTIONS.UPDATE_PREFERENCES, payload: updates })
  }

  const toggleTheme = () => {
    dispatch({ type: PREFERENCES_ACTIONS.TOGGLE_THEME })
  }

  const setNotifications = (level) => {
    dispatch({ type: PREFERENCES_ACTIONS.SET_NOTIFICATIONS, payload: level })
  }

  const setPersona = (persona) => {
    dispatch({ type: PREFERENCES_ACTIONS.SET_PERSONA, payload: persona })
  }

  const value = {
    preferences,
    updatePreferences,
    toggleTheme,
    setNotifications,
    setPersona
  }

  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>
}

// Global Provider (combines everything)
export function GlobalProvider({ children }) {
  const value = {
    // This will be extended with global state as needed
    version: '1.0.0',
    environment: import.meta.env.MODE || 'development'
  }

  return <GlobalProvider.Provider value={value}>{children}</GlobalProvider.Provider>
}

// Main provider component
export function AppProviders({ children }) {
  return (
    <GlobalProvider>
      <PreferencesProvider>
        <AuthProvider>
          {children}
        </AuthProvider>
      </PreferencesProvider>
    </GlobalProvider>
  )
}

// Hooks for using contexts
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function usePreferences() {
  const context = useContext(PreferencesContext)
  if (!context) {
    throw new Error('usePreferences must be used within a PreferencesProvider')
  }
  return context
}

export function useGlobal() {
  const context = useContext(GlobalContext)
  if (!context) {
    throw new Error('useGlobal must be used within a GlobalProvider')
  }
  return context
}

// Enhanced API hooks with error handling and caching
export function useAlerts(filters = {}) {
  const queryClient = useQueryClient()

  return useQuery({
    queryKey: ['alerts', filters],
    queryFn: () => apiClient.fetchAlerts(filters),
    staleTime: 15000,
    refetchInterval: 30000,
    onError: (error) => {
      console.error('Failed to fetch alerts:', error)
    }
  })
}

export function useOpportunities(filters = {}) {
  return useQuery({
    queryKey: ['opportunities', filters],
    queryFn: () => apiClient.fetchOpportunities(filters),
    staleTime: 60000,
    onError: (error) => {
      console.error('Failed to fetch opportunities:', error)
    }
  })
}

export function useDashboardData(filters = {}) {
  return useQuery({
    queryKey: ['dashboard', filters],
    queryFn: () => apiClient.fetchDashboardSnapshot(),
    staleTime: 30000,
    onError: (error) => {
      console.error('Failed to fetch dashboard data:', error)
    }
  })
}

// Notification helpers
export function useNotifications() {
  const { preferences } = usePreferences()

  const showNotification = (type, message, options = {}) => {
    const notificationLevel = preferences.notifications

    // Check if notification should be shown based on user preferences
    if (notificationLevel === 'none') return
    if (notificationLevel === 'critical' && type !== 'error') return
    if (notificationLevel === 'important' && !['error', 'warning'].includes(type)) return

    switch (type) {
      case 'success':
        toast.success(message, options)
        break
      case 'error':
        toast.error(message, options)
        break
      case 'warning':
        toast(message, { ...options, icon: '⚠️' })
        break
      case 'info':
        toast(message, options)
        break
    }
  }

  return { showNotification }
}
