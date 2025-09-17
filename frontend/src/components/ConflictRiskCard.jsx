const formatDate = (value) => {
  if (!value) return 'TBD'
  const date = new Date(value)
  if (Number.isNaN(date.valueOf())) return 'TBD'
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const formatPercent = (value) => {
  if (value === null || value === undefined) return '-'
  const numeric = Number(value)
  if (Number.isNaN(numeric)) return '-'
  return `${Math.round(numeric * 100)}%`
}

const riskBadgeTone = (percent) => {
  if (percent >= 75) return 'bg-red-500/15 text-red-200 border-red-500/40'
  if (percent >= 60) return 'bg-amber-500/15 text-amber-200 border-amber-500/40'
  return 'bg-emerald-500/15 text-emerald-200 border-emerald-500/40'
}

export function ConflictRiskCard({
  ticker,
  member,
  chamber,
  transactionType,
  transactionDate,
  amountRange,
  billTitle,
  billStage,
  jurisdiction,
  nextActionDate,
  riskScore,
  confidence,
  rationale,
}) {
  const riskPercent = Math.round((riskScore ?? 0) * 100)

  return (
    <article className="rounded-2xl border border-slate-800 bg-card-bg/60 p-5 shadow-lg shadow-black/20">
      <header className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">{jurisdiction ?? 'Federal'}</p>
          <h3 className="text-xl font-semibold text-white">{ticker}</h3>
        </div>
        <span
          className={`rounded-full border px-3 py-1 text-xs font-semibold ${riskBadgeTone(riskPercent)}`}
        >
          Risk {formatPercent(riskScore)}
        </span>
      </header>

      <p className="mt-4 text-sm text-slate-300">{rationale}</p>

      <dl className="mt-5 space-y-2 text-sm text-slate-300">
        <div className="flex items-center justify-between">
          <dt className="text-slate-400">Confidence</dt>
          <dd className="text-white">{formatPercent(confidence)}</dd>
        </div>
        <div className="flex items-center justify-between">
          <dt className="text-slate-400">Trade disclosed</dt>
          <dd className="text-white">{transactionType} | {formatDate(transactionDate)}</dd>
        </div>
        <div className="flex items-center justify-between">
          <dt className="text-slate-400">Member</dt>
          <dd className="text-white">{member} ({chamber})</dd>
        </div>
        <div className="flex items-center justify-between">
          <dt className="text-slate-400">Amount</dt>
          <dd className="text-white">{amountRange}</dd>
        </div>
      </dl>

      <div className="mt-5 rounded-xl border border-slate-800/80 bg-slate-900/60 p-4 text-sm">
        <p className="text-xs uppercase tracking-wide text-slate-500">Legislation linkage</p>
        <h4 className="mt-2 text-sm font-semibold text-white">{billTitle ?? 'Associated legislation pending'}</h4>
        <p className="mt-1 text-xs text-slate-400">
          {(billStage ?? 'Pending')} | Next action {formatDate(nextActionDate)}
        </p>
      </div>
    </article>
  )
}
