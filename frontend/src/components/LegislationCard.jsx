const formatter = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

const safeFormatDate = (value) => {
  if (!value) return 'TBD'
  const date = new Date(value)
  if (Number.isNaN(date.valueOf())) {
    return 'TBD'
  }
  return formatter.format(date)
}

const percentOrNA = (value) => {
  if (value === null || value === undefined) return 'N/A'
  return `${Math.round(value * 100)}%`
}

export function LegislationCard({ billId, title, stage, jurisdiction, summary, nextActionDate, sentimentScore, probabilityOfEnactment }) {
  return (
    <article className="rounded-2xl border border-slate-800 bg-card-bg/50 p-5 text-left text-slate-200">
      <div className="flex items-center justify-between text-xs uppercase tracking-wide text-slate-400">
        <span>{billId}</span>
        <span>{jurisdiction}</span>
      </div>
      <h3 className="mt-2 text-lg font-semibold text-white">{title}</h3>
      <p className="mt-3 text-sm text-slate-300">{summary}</p>
      <dl className="mt-4 grid grid-cols-2 gap-4 text-xs text-slate-400 sm:grid-cols-4">
        <div>
          <dt className="font-semibold text-slate-300">Stage</dt>
          <dd className="mt-1 text-slate-200">{stage}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-300">Next action</dt>
          <dd className="mt-1 text-slate-200">{safeFormatDate(nextActionDate)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-300">Sentiment</dt>
          <dd className="mt-1 text-slate-200">{percentOrNA(sentimentScore)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-300">Pass probability</dt>
          <dd className="mt-1 text-slate-200">{percentOrNA(probabilityOfEnactment)}</dd>
        </div>
      </dl>
    </article>
  )
}