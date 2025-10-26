import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'

const skeletonProps = {
  baseColor: '#374151',
  highlightColor: '#4b5563',
  borderRadius: '0.5rem',
  duration: 1.5,
}

const StyledSkeleton = (props) => <Skeleton {...skeletonProps} {...props} />

export function SkeletonCard() {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <StyledSkeleton circle width={40} height={40} />
          <div className="flex-1 space-y-2">
            <StyledSkeleton width="60%" />
            <StyledSkeleton width="40%" />
          </div>
        </div>
        <div className="space-y-2">
          <StyledSkeleton width="100%" />
          <StyledSkeleton width="80%" />
          <StyledSkeleton width="60%" />
        </div>
      </div>
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
            <div className="space-y-3">
              <StyledSkeleton width="60%" />
              <StyledSkeleton width="40%" />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="bg-slate-800/50 rounded-xl border border-slate-700 p-6">
            <div className="space-y-4">
              <StyledSkeleton width="50%" />
              <StyledSkeleton width="100%" height={300} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function AlertSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, index) => (
        <div key={index} className="bg-slate-800/50 rounded-xl border border-slate-700 p-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <StyledSkeleton width={80} height={24} />
              <StyledSkeleton width={100} height={24} />
              <StyledSkeleton width={60} height={16} />
            </div>
            <StyledSkeleton width="100%" />
            <StyledSkeleton width="80%" />
            <div className="flex gap-2">
              <StyledSkeleton width={60} height={20} />
              <StyledSkeleton width={80} height={20} />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
