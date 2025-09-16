export function MetricCard({ label, value, helper }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-card-bg/60 p-6 text-center">
      <div className="text-2xl font-bold text-white">{value}</div>
      <div className="mt-1 text-sm uppercase tracking-wide text-slate-400">{label}</div>
      {helper ? <p className="mt-2 text-xs text-slate-400">{helper}</p> : null}
    </div>
  )
}