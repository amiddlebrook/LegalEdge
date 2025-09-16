const formatPercent = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—'
  }
  return `${value.toFixed(1)}% exp. return`
}

export function ForecastSignalCard({ ticker, thesis, expectedReturnPct, confidence, catalysts }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-card-bg/60 p-5">
      <div className="flex items-center justify-between text-sm text-slate-300">
        <span className="text-lg font-semibold text-white">{ticker}</span>
        <span className="rounded-full border border-primary/40 bg-primary/10 px-2 py-0.5 text-xs text-primary">
          {formatPercent(expectedReturnPct)}
        </span>
      </div>
      <p className="mt-3 text-sm text-slate-300">{thesis}</p>
      <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
        <span className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200">
          Confidence {Math.round((confidence ?? 0) * 100)}%
        </span>
        {catalysts?.map((catalyst) => (
          <span key={catalyst} className="rounded-full border border-slate-700/60 px-2 py-0.5">
            {catalyst}
          </span>
        ))}
      </div>
    </div>
  )
}