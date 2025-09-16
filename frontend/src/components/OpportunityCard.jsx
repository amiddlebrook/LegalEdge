const percent = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—'
  }
  return `${value.toFixed(1)}%`
}

export function OpportunityCard({ ticker, thesis, expectedReturnPct, conviction, horizonDays, catalysts, riskRating }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-card-bg/60 p-5">
      <div className="flex items-center justify-between text-sm text-slate-300">
        <span className="text-lg font-semibold text-white">{ticker}</span>
        <span className="rounded-full border border-primary/40 bg-primary/10 px-2 py-0.5 text-xs text-primary">
          {percent(expectedReturnPct)} target
        </span>
      </div>
      <p className="mt-3 text-sm text-slate-300">{thesis}</p>
      <div className="mt-4 flex flex-wrap gap-3 text-xs text-slate-400">
        <span className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200">
          Conviction {Math.round((conviction ?? 0) * 100)}%
        </span>
        <span className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200">
          Horizon {horizonDays}d
        </span>
        <span className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200">
          Risk {riskRating}
        </span>
      </div>
      {catalysts?.length ? (
        <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
          {catalysts.map((item) => (
            <span key={item} className="rounded-full border border-slate-700/60 px-2 py-0.5">
              {item}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  )
}