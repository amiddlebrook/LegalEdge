import { Hono } from 'hono'
import { cors } from 'hono/cors'

type Bindings = {
    DB: D1Database
    KV: KVNamespace
    STORAGE: R2Bucket
    INGESTION_QUEUE: Queue
}

import auth from './routes/auth'
import legislation from './routes/legislation'
import portfolio from './routes/portfolio'

const app = new Hono<{ Bindings: Bindings }>()

app.use('/*', cors())
app.route('/auth', auth)
app.route('/legislation', legislation)
app.route('/portfolios', portfolio)

app.get('/', (c) => {
    return c.json({ message: 'Welcome to LegalEdge API (Cloudflare Native)' })
})

app.get('/health', (c) => {
    return c.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// Queue management endpoint
app.post('/queue/ingest', async (c) => {
    await c.env.INGESTION_QUEUE.send({
        type: 'ingest_legislation',
        data: { source: 'congress.gov' }
    })
    return c.json({ message: 'Ingestion job queued' })
})

export default app
