import { createContext, useCallback, useContext, useMemo, useRef } from 'react'

const ApiCacheContext = createContext(null)

export function ApiCacheProvider({ children, ttlMs = 60_000 }) {
  const cacheRef = useRef(new Map())

  const fetchResource = useCallback(
    async (key, fetcher) => {
      const cache = cacheRef.current
      const existing = cache.get(key)
      const now = Date.now()

      if (existing?.data && now - (existing.timestamp ?? 0) < ttlMs) {
        return existing.data
      }

      if (existing?.promise) {
        return existing.promise
      }

      const promise = Promise.resolve()
        .then(fetcher)
        .then((data) => {
          cache.set(key, { data, timestamp: Date.now() })
          return data
        })
        .catch((error) => {
          if (existing?.data) {
            cache.set(key, { ...existing, error, timestamp: Date.now() })
          } else {
            cache.delete(key)
          }
          throw error
        })

      cache.set(key, { ...existing, promise })
      try {
        return await promise
      } finally {
        const current = cache.get(key)
        if (current && current.promise) {
          cache.set(key, { ...current, promise: undefined })
        }
      }
    },
    [ttlMs],
  )

  const peek = useCallback(
    (key) => {
      const record = cacheRef.current.get(key)
      if (!record?.data) return undefined
      if (!record.timestamp) return record.data
      if (Date.now() - record.timestamp < ttlMs) {
        return record.data
      }
      return record.data
    },
    [ttlMs],
  )

  const value = useMemo(
    () => ({ fetchResource, peek }),
    [fetchResource, peek],
  )

  return <ApiCacheContext.Provider value={value}>{children}</ApiCacheContext.Provider>
}

export function useApiCache() {
  const context = useContext(ApiCacheContext)
  if (!context) {
    throw new Error('useApiCache must be used within an ApiCacheProvider')
  }
  return context
}