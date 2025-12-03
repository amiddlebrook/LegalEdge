import { Hono } from 'hono'
import { sign, verify } from 'hono/jwt'
import { compare, hash } from 'bcryptjs'

const app = new Hono<{ Bindings: { DB: D1Database } }>()
const JWT_SECRET = 'your-secret-key-change-this-in-prod' // TODO: Move to env vars

app.post('/register', async (c) => {
    const { email, password, username, full_name } = await c.req.json()

    if (!email || !password || !username) {
        return c.json({ error: 'Missing required fields' }, 400)
    }

    const hashedPassword = await hash(password, 10)

    try {
        const { success } = await c.env.DB.prepare(
            `INSERT INTO users (email, username, hashed_password, full_name) VALUES (?, ?, ?, ?)`
        )
            .bind(email, username, hashedPassword, full_name || username)
            .run()

        if (!success) {
            return c.json({ error: 'Failed to create user' }, 500)
        }

        return c.json({ message: 'User created successfully' }, 201)
    } catch (e: any) {
        if (e.message.includes('UNIQUE constraint failed')) {
            return c.json({ error: 'Email or username already exists' }, 409)
        }
        return c.json({ error: e.message }, 500)
    }
})

app.post('/login', async (c) => {
    const { email, password } = await c.req.json()

    if (!email || !password) {
        return c.json({ error: 'Missing email or password' }, 400)
    }

    const user = await c.env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(email).first()

    if (!user) {
        return c.json({ error: 'Invalid credentials' }, 401)
    }

    const validPassword = await compare(password, user.hashed_password as string)

    if (!validPassword) {
        return c.json({ error: 'Invalid credentials' }, 401)
    }

    const token = await sign({ id: user.id, email: user.email, role: 'user' }, JWT_SECRET)

    return c.json({ token, user: { id: user.id, email: user.email, username: user.username, full_name: user.full_name } })
})

app.get('/me', async (c) => {
    const authHeader = c.req.header('Authorization')
    if (!authHeader) {
        return c.json({ error: 'Unauthorized' }, 401)
    }

    const token = authHeader.split(' ')[1]
    try {
        const payload = await verify(token, JWT_SECRET)
        const user = await c.env.DB.prepare('SELECT id, email, username, full_name, preferences FROM users WHERE id = ?').bind(payload.id).first()
        return c.json({ user })
    } catch (e) {
        return c.json({ error: 'Invalid token' }, 401)
    }
})

export default app
