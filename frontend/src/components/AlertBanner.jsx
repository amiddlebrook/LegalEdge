const severityStyles = {
  high: 'border-red-500/60 bg-red-500/10 text-red-200',
  medium: 'border-amber-400/60 bg-amber-400/10 text-amber-100',
  low: 'border-emerald-400/60 bg-emerald-400/10 text-emerald-100',
}

const formatTimestamp = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.valueOf())) return ''
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function AlertBanner({ category, title, description, severity, createdAt, relatedEntities }) {
  const style = severityStyles[severity?.toLowerCase()] ?? severityStyles.medium
  return (
    <article className={`rounded-2xl border px-4 py-3 ${style}`}>
      <header className="flex flex-wrap items-center justify-between gap-2 text-xs uppercase tracking-wide">
        <span>{category}</span>
        <span>{formatTimestamp(createdAt)}</span>
      </header>
      <h3 className="mt-2 text-base font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-slate-200/90">{description}</p>
      {relatedEntities?.length ? (
        <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-200">
          {relatedEntities.map((entity) => (
            <span key={entity} className="rounded-full border border-current px-2 py-0.5">
              {entity}
            </span>
          ))}
        </div>
      ) : null}
    </article>
  )
}