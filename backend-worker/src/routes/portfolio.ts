import { Hono } from 'hono'

const app = new Hono<{ Bindings: { DB: D1Database } }>()

app.get('/', async (c) => {
    const { results } = await c.env.DB.prepare('SELECT * FROM trade_disclosures ORDER BY transaction_date DESC LIMIT 50').all()
    return c.json({ results })
})

app.get('/conflicts', async (c) => {
    // Simple conflict detection: trades where the ticker matches a sector or bill related company
    // For now, just return recent trades as "potential conflicts" for demo
    const { results } = await c.env.DB.prepare('SELECT * FROM trade_disclosures ORDER BY transaction_date DESC LIMIT 10').all()
    return c.json({ conflicts: results })
})

export default app
