# LegalEdge — Cloudflare-native policy intelligence

A free, primary-source legislative and regulatory research workspace. This is the Cloudflare-native v2 restoration of the older LegalEdge monorepo.

## What works

- Live **U.S. congressional bill** updates from the [GovInfo RSS feed](https://www.govinfo.gov/feeds).
- **Federal regulations, proposed rules, and notices** from the [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1).
- Topic tagging with explicit keyword dictionaries (Energy, Technology, Healthcare, Financials, Defense, Infrastructure, Agriculture, Trade).
- Interactive search/filter, source links, responsive dashboard, export to CSV, and a browser-local watchlist.
- Real upstream failure and partial-coverage states; **no fabricated fallback data**.
- Zero mandatory paid services, external AI API keys, databases, scheduled jobs, queues, or persistent servers.

## Architecture

Cloudflare Worker: src/index.js (GET /api/health, /api/sources, /api/feed).
Public source normalizers: src/feeds.js.
UI: web/index.html + web/assets/*. 
Static assets are served by Workers Static Assets. API routes run in the same Worker. Watchlist uses only localStorage in the visitor's own browser. No account registration and no portfolio data is sent to the server.

**Legacy code:** the prior FastAPI, Postgres, Redis, AWS Terraform, Celery, React and experimental Worker code is retained in older folders for reference, but is not part of the v2 deploy or CI. The old root Worker code with its hardcoded authentication secret has been removed.

## Start locally

Install Node.js 22 or newer and run:

    npm run dev

Wrangler starts the Worker and serves the static assets. Use the provided local URL.

Run unit tests:

    npm test

Deploy manually (on the Cloudflare Workers Free plan):

    npx wrangler@4 login
    npm run deploy

The Cloudflare Worker name is **legaledge** (from wrangler.toml), so it updates the existing Worker of that name in the selected Cloudflare account.

## GitHub CI/CD

The workflow at .github/workflows/ci-cd.yml runs tests and source checks on PRs and main pushes, then deploys automatically on main **when both repository secrets are configured**:

- CLOUDFLARE_API_TOKEN: scoped to Workers Scripts edit in the target account.
- CLOUDFLARE_ACCOUNT_ID: the Cloudflare account identifier.

Repository -> Settings -> Secrets and variables -> Actions -> New repository secret. Never commit the token. Missing secrets skip the deployment with a GitHub Actions warning rather than reporting a false publish. Once configured, merge this restoration into main; subsequent pushes redeploy automatically.

## Source caveats and privacy

This tool shows a recent window of records returned by each publisher, not an exhaustive searchable legislative corpus. Source outages are visible. The sector association is **only keyword matching**, not legal analysis, securities pricing, investment advice, passage probability, or proof of congressional trade conflicts. No future market performance is predicted. Confirm records at the original government source before relying on them.

The watchlist is not synchronized across devices. Browser storage can be cleared by the user or browser; the app has no login or cloud backup. The two public government upstream services have their own availability and acceptable-use policies.

The v2 build uses only free-tier-compatible Workers Static Assets and short Worker HTTP requests. Cloudflare Workers Free imposes request and CPU limits; high traffic or changes in third-party source availability may require capacity decisions. No billing-dependent Cloudflare resources are provisioned.

## API

- GET /api/health: Worker liveness.
- GET /api/sources: official upstream URLs and supported topic categories.
- GET /api/feed: normalized recent documents, fetch timestamp, per-source availability and partial results.

The endpoint reports HTTP 503 if *both* publishers fail, and HTTP 200 with status=partial if one works.

## Security

The v2 Worker exposes only read-only, same-origin GET endpoints. No hardcoded login secret or open user-data API is deployed. All document titles, summaries and symbols are rendered as text nodes rather than injected HTML. Outbound links are restricted to official government hosts. CSV exports prefix potentially dangerous spreadsheet formulas. Local watchlist data stays in the browser.

License and authorship of original contents remain as stated in the legacy repository.
