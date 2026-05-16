# API Flow

## Outbound Call

1. Admin or scheduler calls `POST /api/v1/calls/initiate`.
2. Backend resolves the lead and creates a call record.
3. Twilio connects media to `/api/v1/ws/twilio`.
4. Media chunks are decoded from G.711 mulaw.
5. STT stream buffers speech with VAD and emits final utterances.
6. Live intent detection runs during the conversation turn.
7. Agent branch logic chooses greeting, eligibility, EMI, document reminder,
   objection handling, or callback booking.
8. LLM creates the concise voice response.
9. TTS returns 8kHz mulaw chunks to Twilio.
10. CRM persistence stores transcript, intent, sentiment, action, duration, and
    updated lead status.
11. Hot leads, angry customers, and high-ticket cases trigger Slack alerts.

## Dashboard

The frontend reads:

- `GET /api/v1/dashboard/stats`
- `GET /api/v1/calls`
- `GET /api/v1/crm/leads`
- `GET /api/v1/settings/providers`
- `POST /api/v1/simulator/run`

## Intent Actions

| Intent | Action |
| --- | --- |
| interested | Continue AI conversation |
| confused | Continue AI conversation |
| angry | Escalate to human agent |
| spam_invalid | Polite termination |
| high_ticket | Escalate to human agent |
| callback | Schedule human callback |
