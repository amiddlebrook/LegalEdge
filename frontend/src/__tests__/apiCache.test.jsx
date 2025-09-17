import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, test, vi } from 'vitest'

import { ApiCacheProvider, useApiCache } from '../context/ApiCacheContext.jsx'

const wrapper = ({ children }) => <ApiCacheProvider ttlMs={1000}>{children}</ApiCacheProvider>

describe('ApiCacheContext', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  test('fetchResource resolves once within TTL', async () => {
    const fetcher = vi.fn().mockResolvedValue({ value: 42 })
    const {
      result: {
        current: { fetchResource },
      },
    } = renderHook(() => useApiCache(), { wrapper })

    await act(async () => {
      const data = await fetchResource('key', fetcher)
      expect(data).toEqual({ value: 42 })
    })

    await act(async () => {
      const data = await fetchResource('key', fetcher)
      expect(data).toEqual({ value: 42 })
    })

    expect(fetcher).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(1001)

    await act(async () => {
      await fetchResource('key', fetcher)
    })

    expect(fetcher).toHaveBeenCalledTimes(2)
  })

  test('peek returns cached data if available', async () => {
    const fetcher = vi.fn().mockResolvedValue({ greeting: 'hi' })
    const {
      result: {
        current: { fetchResource, peek },
      },
    } = renderHook(() => useApiCache(), { wrapper })

    expect(peek('cached')).toBeUndefined()

    await act(async () => {
      await fetchResource('cached', fetcher)
    })

    expect(peek('cached')).toEqual({ greeting: 'hi' })
  })
})