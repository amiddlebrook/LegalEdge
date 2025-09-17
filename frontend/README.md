# LegalEdge Frontend

React + Vite single page experience styled with TailwindCSS for the LegalEdge policy intelligence platform.

## Available scripts

```bash
npm install          # install dependencies
npm run dev          # start local dev server on http://localhost:5173
npm run build        # produce production build
npm run lint         # run ESLint checks
npm run test -- --run  # execute the Vitest suite once
```

## Implementation notes

- TailwindCSS is configured in `tailwind.config.js` with a gradient theme aligning to the product vision.
- Components live under `src/components`; shared fallbacks and API helpers sit in `src/lib` for reuse across views.
- React Router powers three primary routes: the Overview (marketing narrative), the Dashboard (interactive alerts, opportunities, forecasts, and portfolio intelligence), and the Coverage command center (jurisdiction health + ingestion metrics). Navigation persists via `MainLayout`.
- Calls to the FastAPI backend are abstracted through `api.js`, which gracefully falls back to curated data when endpoints are unreachable.
- `ApiCacheProvider` caches responses for 60 seconds and the navigation prefetches both overview and dashboard data to keep transitions instant.

### Environment variables

Create a `.env.local` file if you need to point at a different backend origin:

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```
