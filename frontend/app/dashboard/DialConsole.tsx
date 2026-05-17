"use client";

import { useCallback, useMemo, useState } from "react";
import { Loader2, PhoneCall, RadioTower, ShieldAlert } from "lucide-react";
import type { AgentConfig, CallRecord, Lead, ProviderStatus } from "@/types/api";

interface DialConsoleProps {
  agents: AgentConfig[];
  leads: Lead[];
  providerStatus: ProviderStatus;
}

export function DialConsole({ agents, leads, providerStatus }: DialConsoleProps) {
  const [phoneNumber, setPhoneNumber] = useState(leads[0]?.phone_number ?? "");
  const [leadId, setLeadId] = useState(leads[0]?.id ?? "");
  const [agentId, setAgentId] = useState(agents[0]?.id ?? "vahan_loan_assistant");
  const [dialing, setDialing] = useState(false);
  const [result, setResult] = useState<CallRecord | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedAgent = useMemo(
    () => agents.find((agent) => agent.id === agentId) ?? agents[0],
    [agentId, agents]
  );

  const twilioReady = providerStatus.providers.twilio === "Ready";

  const dial = useCallback(async () => {
    setDialing(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch("/api/backend/calls/initiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone_number: phoneNumber,
          lead_id: leadId || undefined,
          agent_id: agentId
        })
      });
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      setResult((await response.json()) as CallRecord);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to initiate call");
    } finally {
      setDialing(false);
    }
  }, [agentId, leadId, phoneNumber]);

  return (
    <section className="rounded-xl glass-card p-6 shadow-2xl">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="font-heading text-2xl font-bold bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">Direct Dial</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Select an agent, enter a customer number, and start an outbound AI loan follow-up call.
          </p>
        </div>
        <div className={`flex items-center gap-2 rounded-md border px-3 py-2 text-sm ${twilioReady ? "border-[#22C55E]/30 bg-[#22C55E]/10 text-[#BBF7D0]" : "border-[#F59E0B]/30 bg-[#F59E0B]/10 text-amber-100"}`}>
          {twilioReady ? <RadioTower className="h-4 w-4 animate-pulse text-[#22C55E]" aria-hidden="true" /> : <ShieldAlert className="h-4 w-4" aria-hidden="true" />}
          {twilioReady ? "Twilio live dialing ready" : "Needs public webhook for live Twilio dialing"}
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_1fr_1fr_auto]">
        <label className="block">
          <span className="text-sm font-semibold text-slate-400">Customer number</span>
          <input
            value={phoneNumber}
            onChange={(event) => setPhoneNumber(event.target.value)}
            placeholder="+919876543210"
            className="mt-2 h-12 w-full rounded-md border border-white/10 bg-black/40 px-3 font-mono text-sm text-white outline-none focus:border-[#6366f1]"
          />
        </label>
        <label className="block">
          <span className="text-sm font-semibold text-slate-400">Lead</span>
          <select
            value={leadId}
            onChange={(event) => {
              const nextLeadId = event.target.value;
              setLeadId(nextLeadId);
              const lead = leads.find((item) => item.id === nextLeadId);
              if (lead) {
                setPhoneNumber(lead.phone_number);
              }
            }}
            className="mt-2 h-12 w-full rounded-md border border-white/10 bg-black/40 px-3 text-sm text-white outline-none focus:border-[#6366f1]"
          >
            <option value="">New number</option>
            {leads.map((lead) => (
              <option key={lead.id} value={lead.id}>{lead.name}</option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-sm font-semibold text-slate-400">AI agent</span>
          <select
            value={agentId}
            onChange={(event) => setAgentId(event.target.value)}
            className="mt-2 h-12 w-full rounded-md border border-white/10 bg-black/40 px-3 text-sm text-white outline-none focus:border-[#6366f1]"
          >
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>{agent.name}</option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={dial}
          disabled={dialing || !phoneNumber.trim()}
          className="mt-6 flex h-12 min-w-36 items-center justify-center gap-2 rounded-md bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 shadow-[0_0_15px_rgba(99,102,241,0.4)] hover:shadow-[0_0_25px_rgba(99,102,241,0.6)] px-5 text-sm font-bold text-white transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-60 lg:mt-[26px]"
        >
          {dialing ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <PhoneCall className="h-4 w-4" aria-hidden="true" />}
          Dial
        </button>
      </div>

      {selectedAgent ? (
        <div className="mt-4 rounded-md border border-white/10 bg-black/20 p-3">
          <p className="text-sm font-bold text-slate-100">{selectedAgent.name}</p>
          <p className="mt-1 text-sm text-slate-400">{selectedAgent.description}</p>
          <p className="mt-2 font-mono text-xs text-slate-500">{selectedAgent.language} | {selectedAgent.voice}</p>
        </div>
      ) : null}

      {result ? (
        <div className="mt-4 rounded-md border border-[#22C55E]/25 bg-[#22C55E]/10 p-3 text-sm text-green-100">
          Call queued: <span className="font-mono">{result.call_sid}</span> | mode: {result.call_mode} | status: {result.status}
        </div>
      ) : null}
      {error ? (
        <div className="mt-4 rounded-md border border-[#EF4444]/25 bg-[#EF4444]/10 p-3 text-sm text-red-100">{error}</div>
      ) : null}
    </section>
  );
}
