import { Hono } from 'hono'

const app = new Hono<{ Bindings: { DB: D1Database } }>()

app.get('/', async (c) => {
    const { results } = await c.env.DB.prepare('SELECT * FROM legislative_bills ORDER BY last_updated DESC LIMIT 50').all()
    return c.json({ results })
})

app.get('/:id', async (c) => {
    const id = c.req.param('id')
    const bill = await c.env.DB.prepare('SELECT * FROM legislative_bills WHERE bill_id = ?').bind(id).first()

    if (!bill) {
        return c.json({ error: 'Bill not found' }, 404)
    }

    return c.json({ bill })
})

export default app
