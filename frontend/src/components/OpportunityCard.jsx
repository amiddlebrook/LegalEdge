const percent = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '-'
  }
  return `${value.toFixed(1)}%`
}

const ratioPercent = (value, digits = 0) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return null
  }
  return `${(value * 100).toFixed(digits)}%`
}

const conflictBadgeClass = (score) => {
  if (typeof score !== 'number') {
    return 'border-slate-700/60 text-slate-200'
  }
  if (score >= 0.5) {
    return 'border-rose-500/40 bg-rose-500/10 text-rose-300'
  }
  if (score >= 0.25) {
    return 'border-amber-500/40 bg-amber-500/10 text-amber-300'
  }
  return 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
}

export function OpportunityCard({
  ticker,
  thesis,
  expectedReturnPct,
  conviction,
  horizonDays,
  catalysts,
  riskRating,
  compositeScore,
  policyAlignment,
  conflictScore,
  policyAlpha,
  drivers = [],
  explanation,
  methodology,
}) {
  const compositeDisplay = ratioPercent(compositeScore)
  const alignmentDisplay = ratioPercent(policyAlignment)
  const conflictDisplay = ratioPercent(conflictScore)
  const alphaDisplay = typeof policyAlpha === 'number' && !Number.isNaN(policyAlpha) ? percent(policyAlpha) : null
  const convictionDisplay = Math.round((conviction ?? 0) * 100)

  return (
    <div className="rounded-2xl border border-slate-800 bg-card-bg/60 p-5 shadow-lg shadow-black/30">
      <div className="flex items-start justify-between gap-3 text-sm text-slate-300">
        <div>
          <span className="text-lg font-semibold text-white">{ticker}</span>
          <p className="mt-2 text-sm text-slate-300">{thesis}</p>
        </div>
        {compositeDisplay ? (
          <div className="text-right">
            <span className="text-[10px] uppercase tracking-wide text-slate-500">Composite</span>
            <div className="text-xl font-semibold text-primary">{compositeDisplay}</div>
          </div>
        ) : null}
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-200">
        {alignmentDisplay ? (
          <span className="rounded-full border border-slate-700/60 bg-slate-800/60 px-2 py-0.5">
            Policy alignment {alignmentDisplay}
          </span>
        ) : null}
        {alphaDisplay ? (
          <span className="rounded-full border border-slate-700/60 bg-slate-800/60 px-2 py-0.5">
            Policy alpha {alphaDisplay}
          </span>
        ) : null}
        {conflictDisplay ? (
          <span className={`rounded-full px-2 py-0.5 ${conflictBadgeClass(conflictScore)}`}>
            Conflict dampener {conflictDisplay}
          </span>
        ) : null}
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-400">
        <span className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200">
          Conviction {convictionDisplay}%
        </span>
        <span className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200">
          Horizon {horizonDays}d
        </span>
        <span className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200">
          Risk {riskRating}
        </span>
        <span className="rounded-full border border-primary/40 bg-primary/10 px-2 py-0.5 text-primary">
          {percent(expectedReturnPct)} target
        </span>
      </div>

      {drivers?.length ? (
        <div className="mt-4">
          <p className="text-[11px] uppercase tracking-wide text-slate-500">Key drivers</p>
          <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-200">
            {drivers.map((driver) => (
              <span key={driver} className="rounded-full border border-slate-700/60 px-2 py-0.5">
                {driver}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {catalysts?.length ? (
        <div className="mt-4">
          <p className="text-[11px] uppercase tracking-wide text-slate-500">Catalysts</p>
          <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
            {catalysts.map((item) => (
              <span key={item} className="rounded-full border border-slate-700/60 px-2 py-0.5">
                {item}
              </span>
            ))}
          </div>
        </div>
      ) : null}

      {explanation ? (
        <p className="mt-4 text-xs text-slate-400">{explanation}</p>
      ) : null}

      {methodology ? (
        <p className="mt-3 text-[11px] text-slate-500">Methodology: {methodology}</p>
      ) : null}
    </div>
  )
}
