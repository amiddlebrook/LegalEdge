export function FeatureCard({ title, description, items }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-card-bg/70 p-6 shadow-lg shadow-black/20">
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="mt-2 text-sm text-slate-300">{description}</p>
      {items?.length ? (
        <ul className="mt-4 space-y-2 text-sm text-slate-200">
          {items.map((item) => (
            <li key={item} className="flex items-start gap-3">
              <span className="mt-0.5 h-2 w-2 rounded-full bg-primary" aria-hidden="true" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}