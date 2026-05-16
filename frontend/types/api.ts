export type LeadStatus =
  | "new"
  | "contacted"
  | "interested"
  | "callback_booked"
  | "escalated"
  | "not_interested"
  | "invalid";

export interface Lead {
  id: string;
  name: string;
  phone_number: string;
  loan_amount: number;
  city: string;
  status: LeadStatus;
  language_hint: string;
  missing_fields: string[];
  created_at: string;
}

export interface TranscriptTurn {
  speaker: string;
  text: string;
  timestamp: string;
  latency_ms?: number;
  intent?: string;
}

export interface LatencyBreakdown {
  twilio_ingress_ms: number;
  stt_ms: number;
  llm_ms: number;
  tts_ms: number;
  twilio_egress_ms: number;
}

export interface CallRecord {
  call_sid: string;
  lead_id: string;
  customer_phone: string;
  agent_id: string;
  agent_name: string;
  call_mode: string;
  provider_call_sid?: string;
  status: string;
  duration_seconds: number;
  transcript: TranscriptTurn[];
  intent_label: string;
  sentiment_score: number;
  follow_up_action: string;
  updated_lead_status: LeadStatus;
  recording_url?: string;
  latency: LatencyBreakdown;
  created_at: string;
}

export interface DashboardStats {
  total_calls: number;
  live_calls: number;
  conversions: number;
  conversion_rate: number;
  average_latency_ms: number;
  average_sentiment: number;
  false_positive_rate: number;
  intent_counts: Record<string, number>;
  cost_estimate: {
    tier: string;
    calls_today: number;
    groq_tokens_used: number;
    groq_daily_limit: number;
    groq_pct_used: number;
    estimated_cost_usd: number;
    message: string;
  };
}

export interface ProviderStatus {
  tier: string;
  providers: Record<string, string>;
  models: Record<string, string>;
}

export interface AgentConfig {
  id: string;
  name: string;
  language: string;
  voice: string;
  description: string;
  branches: string[];
  active: boolean;
}

export interface SimulatorResponse {
  scenario: string;
  language: string;
  final_status: LeadStatus;
  turns: Array<{
    customer: string;
    agent: {
      text: string;
      branch: string;
      intent_label: string;
      sentiment_score: number;
      follow_up_action: string;
      lead_status: LeadStatus;
      latency: LatencyBreakdown;
    };
  }>;
}
