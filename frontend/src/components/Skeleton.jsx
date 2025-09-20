import { createSkeletonProvider } from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'

export const SkeletonProvider = createSkeletonProvider({
  baseColor: '#374151',
  highlightColor: '#4b5563',
  borderRadius: '0.5rem',
  duration: 1.5,
})

export function SkeletonCard() {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <SkeletonProvider>
            <skeleton.circle width={40} height={40} />
            <div className="flex-1 space-y-2">
              <skeleton.text width="60%" />
              <skeleton.text width="40%" />
            </div>
          </SkeletonProvider>
        </div>
        <SkeletonProvider>
          <skeleton.text width="100%" />
          <skeleton.text width="80%" />
          <skeleton.text width="60%" />
        </SkeletonProvider>
      </div>
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      {/* Metrics skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
            <SkeletonProvider>
              <div className="space-y-3">
                <skeleton.text width="60%" />
                <skeleton.text width="40%" />
              </div>
            </SkeletonProvider>
          </div>
        ))}
      </div>

      {/* Charts skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
            <SkeletonProvider>
              <skeleton.text width="50%" />
              <skeleton.rect width="100%" height={300} />
            </SkeletonProvider>
          </div>
        ))}
      </div>
    </div>
  )
}

export function AlertSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="bg-slate-800/50 rounded-xl border border-slate-700 p-4">
          <SkeletonProvider>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <skeleton.rect width={80} height={24} />
                <skeleton.rect width={100} height={24} />
                <skeleton.rect width={60} height={16} />
              </div>
              <skeleton.text width="100%" />
              <skeleton.text width="80%" />
              <div className="flex gap-2">
                <skeleton.rect width={60} height={20} />
                <skeleton.rect width={80} height={20} />
              </div>
            </div>
          </SkeletonProvider>
        </div>
      ))}
    </div>
  )
}
