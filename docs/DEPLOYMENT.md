# Deployment Plan

## Frontend

Deploy `frontend/` to Vercel as the project root directory.

Required Vercel environment variable:

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com
```

The Vercel dashboard can host the Next.js operator console, dashboard, analytics,
CRM, settings, studio, and simulator pages.

## Backend

Deploy the FastAPI backend as a Docker service on Railway, Render, Fly.io,
DigitalOcean, AWS, GCP, or another container host with persistent HTTPS and
WebSocket support.

Required backend environment variables:

```bash
MODEL_TIER=free
GROQ_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...
TWILIO_WEBHOOK_BASE_URL=https://your-backend-domain.com
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
DATABASE_URL=...
REDIS_URL=...
```

Twilio live dialing will stay in simulation mode until `TWILIO_WEBHOOK_BASE_URL`
is a public HTTPS URL reachable by Twilio. Once set, `POST /api/v1/calls/initiate`
creates a real outbound Twilio call and Twilio loads `/api/v1/twilio/voice`,
which connects media streams to `/api/v1/ws/twilio`.

## Database

Use Supabase Postgres with `backend/db/schema.sql`. The schema includes leads,
call records, transcript JSON, latency JSON, knowledge chunks with `vector(768)`,
and intent evaluation rows for false-positive tracking.
