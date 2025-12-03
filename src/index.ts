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

// Queue consumer handler
async function queue(batch: MessageBatch, env: Bindings): Promise<void> {
    for (const message of batch.messages) {
        try {
            const payload = message.body as { type: string; data: any }

            console.log(`Processing queue message: ${payload.type}`)

            // Handle different job types
            switch (payload.type) {
                case 'ingest_legislation':
                    console.log('Ingesting legislation:', payload.data)
                    // TODO: Implement actual ingestion logic
                    break
                case 'update_forecasts':
                    console.log('Updating forecasts:', payload.data)
                    // TODO: Implement forecast update logic
                    break
                default:
                    console.warn(`Unknown job type: ${payload.type}`)
            }

            message.ack()
        } catch (error) {
            console.error('Error processing message:', error)
            message.retry()
        }
    }
}

export default { fetch: app.fetch, queue }
