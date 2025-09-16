# LegalEdge Frontend

React + Vite single page experience styled with TailwindCSS for the LegalEdge policy intelligence platform.

## Available scripts

```bash
npm install          # install dependencies
npm run dev          # start local dev server on http://localhost:5173
npm run build        # produce production build
npm run lint         # run ESLint checks
```

## Implementation notes

- TailwindCSS is configured in `tailwind.config.js` with a gradient theme aligning to the product vision.
- Components live under `src/components` and consume data structures pulled from the product brief plus backend APIs.
- The landing view renders alerts, market opportunities, live policy radar, forecast spotlights, portfolio intelligence, and product overview sections fed by the API.

### Environment variables

Create a `.env.local` file if you need to point at a different backend origin:

```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```