import type { AgentConfig, CallRecord, DashboardStats, Lead, ProviderStatus, SimulatorResponse } from "@/types/api";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

export async function getStats(): Promise<DashboardStats> {
  return apiFetch<DashboardStats>("/api/v1/dashboard/stats");
}

export async function getLeads(): Promise<Lead[]> {
  return apiFetch<Lead[]>("/api/v1/crm/leads");
}

export async function getCalls(): Promise<CallRecord[]> {
  return apiFetch<CallRecord[]>("/api/v1/calls");
}

export async function getProviders(): Promise<ProviderStatus> {
  return apiFetch<ProviderStatus>("/api/v1/settings/providers");
}

export async function getAgents(): Promise<AgentConfig[]> {
  return apiFetch<AgentConfig[]>("/api/v1/settings/agents");
}

export async function runSimulation(scenario: string, language: string): Promise<SimulatorResponse> {
  return apiFetch<SimulatorResponse>("/api/v1/simulator/run", {
    method: "POST",
    body: JSON.stringify({ scenario, language, turns: 6 })
  });
}

export async function createCall(phoneNumber: string, leadId?: string, agentId = "vahan_loan_assistant"): Promise<CallRecord> {
  return apiFetch<CallRecord>("/api/v1/calls/initiate", {
    method: "POST",
    body: JSON.stringify({ phone_number: phoneNumber, lead_id: leadId, agent_id: agentId })
  });
}
