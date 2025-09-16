const formatter = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" })

const renderTrade = (trade) => {
  if (!trade) return null
  const timestamp = trade.transactionDate ? formatter.format(new Date(trade.transactionDate)) : "Recent"
  return `${timestamp} - ${trade.transactionType} ${trade.amountRange}`
}

export function PortfolioSignalCard({ ticker, signal, conviction, rationale, supportingTrades = [] }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-card-bg/60 p-5">
      <div className="flex items-center justify-between text-sm text-slate-300">
        <span className="text-lg font-semibold text-white">{ticker}</span>
        <span className="rounded-full border border-primary/40 bg-primary/10 px-2 py-0.5 text-xs text-primary">
          {signal}
        </span>
      </div>
      <p className="mt-3 text-sm text-slate-300">{rationale}</p>
      <div className="mt-4 flex items-center gap-3 text-xs text-slate-400">
        <span className="rounded-full border border-slate-700/60 px-2 py-0.5 text-slate-200">
          Conviction {Math.round((conviction ?? 0) * 100)}%
        </span>
        <span>{supportingTrades.length ? `${supportingTrades.length} supporting trades` : "No recent trades logged"}</span>
      </div>
      {supportingTrades.length ? (
        <ul className="mt-3 space-y-2 text-xs text-slate-400">
          {supportingTrades.map((trade) => (
            <li key={`${trade.member}-${trade.transactionDate}-${trade.ticker}`} className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-3">
              <div className="font-semibold text-slate-200">{trade.member}</div>
              <div className="mt-1">{renderTrade(trade)}</div>
              {trade.relatedBill ? <div className="mt-1">Linked bill: {trade.relatedBill}</div> : null}
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}