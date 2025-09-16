import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="mx-auto flex min-h-[60vh] max-w-3xl flex-col items-center justify-center space-y-6 px-6 text-center">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">404</p>
      <h1 className="text-3xl font-semibold text-white">We could not find that page</h1>
      <p className="max-w-md text-sm text-slate-300">
        The link you followed might be broken or the page may have been removed. Return to the overview or
        explore the dashboard for live policy intelligence.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-3 text-sm">
        <Link
          to="/"
          className="rounded-full border border-primary/60 bg-primary/10 px-4 py-2 text-primary transition hover:bg-primary/20"
        >
          Back to overview
        </Link>
        <Link
          to="/dashboard"
          className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-slate-200 transition hover:border-primary"
        >
          Go to dashboard
        </Link>
      </div>
    </div>
  )
}