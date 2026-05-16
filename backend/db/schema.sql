CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    loan_amount INTEGER DEFAULT 0,
    city TEXT DEFAULT 'Unknown',
    status TEXT NOT NULL DEFAULT 'new',
    language_hint TEXT DEFAULT 'hinglish',
    missing_fields JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS call_records (
    call_sid TEXT PRIMARY KEY,
    lead_id TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    agent_id TEXT DEFAULT 'vahan_loan_assistant',
    agent_name TEXT DEFAULT 'Vahan Loan Assistant',
    call_mode TEXT DEFAULT 'simulation',
    provider_call_sid TEXT,
    status TEXT DEFAULT 'queued',
    duration_seconds INTEGER DEFAULT 0,
    transcript JSONB NOT NULL DEFAULT '[]'::jsonb,
    intent_label TEXT NOT NULL DEFAULT 'unknown',
    sentiment_score REAL DEFAULT 0,
    follow_up_action TEXT NOT NULL DEFAULT 'continue_ai',
    updated_lead_status TEXT NOT NULL DEFAULT 'contacted',
    recording_url TEXT,
    latency JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS intent_evaluations (
    id BIGSERIAL PRIMARY KEY,
    call_sid TEXT NOT NULL,
    predicted_intent TEXT NOT NULL,
    actual_intent TEXT,
    is_false_positive BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);
