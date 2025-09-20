import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

// Create a client with optimized defaults
export const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 5, // 5 minutes
        gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
        retry: (failureCount, error) => {
          // Don't retry on 4xx errors
          if (error?.status >= 400 && error?.status < 500) {
            return false
          }
          return failureCount < 3
        },
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: 1,
      },
    },
  })

export function QueryProvider({ children }) {
  const [queryClient] = useState(createQueryClient)

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

// Custom hooks for common data fetching patterns
export function useApiCache() {
  return {
    // This will be replaced with actual React Query hooks
    // For now, return placeholder functions
    fetchResource: async (key, fetcher) => {
      try {
        return await fetcher()
      } catch (error) {
        console.error(`Failed to fetch ${key}:`, error)
        throw error
      }
    },
    peek: (key) => {
      // Placeholder for cache peeking
      return null
    },
    invalidate: (key) => {
      // Placeholder for cache invalidation
      console.log(`Invalidating cache for ${key}`)
    },
  }
}

// Error boundary for React Query
export class QueryErrorBoundary extends Error {
  constructor(message, query) {
    super(message)
    this.name = 'QueryError'
    this.query = query
  }
}
