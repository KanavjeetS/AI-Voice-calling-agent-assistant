"use client";

import { useCallback, useState } from "react";
import { Loader2, Play } from "lucide-react";
import { IntentBadge } from "@/components/IntentBadge";
import { LatencyBars } from "@/components/LatencyBars";
import type { SimulatorResponse } from "@/types/api";

export function SimulatorClient() {
  const [scenario, setScenario] = useState("interested");
  const [language, setLanguage] = useState("english");
  const [result, setResult] = useState<SimulatorResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/backend/simulator/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario, language, turns: 6 })
      });
      if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
      }
      setResult((await response.json()) as SimulatorResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Simulation failed");
    } finally {
      setLoading(false);
    }
  }, [scenario, language]);

  return (
    <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
      <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
        <h2 className="font-heading text-lg font-bold">Scenario</h2>
        <label className="mt-4 block text-sm text-slate-400" htmlFor="scenario">Intent path</label>
        <select id="scenario" value={scenario} onChange={(event) => setScenario(event.target.value)} className="mt-2 h-11 w-full rounded-md border border-white/10 bg-black/30 px-3 text-sm text-white">
          <option value="interested">Interested</option>
          <option value="hindi">Hindi callback</option>
          <option value="confused">Confused</option>
          <option value="angry">Angry escalation</option>
        </select>
        <label className="mt-4 block text-sm text-slate-400" htmlFor="language">Language</label>
        <select id="language" value={language} onChange={(event) => setLanguage(event.target.value)} className="mt-2 h-11 w-full rounded-md border border-white/10 bg-black/30 px-3 text-sm text-white">
          <option value="english">English</option>
          <option value="hindi">Hindi</option>
          <option value="hinglish">Hinglish</option>
        </select>
        <button type="button" onClick={run} disabled={loading} className="mt-5 flex h-11 w-full items-center justify-center gap-2 rounded-md bg-[#4F46E5] px-4 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-60">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Play className="h-4 w-4" aria-hidden="true" />}
          Run simulation
        </button>
        {error ? <p className="mt-3 rounded border border-[#EF4444]/30 bg-[#EF4444]/10 p-3 text-sm text-red-100">{error}</p> : null}
      </section>
      <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
        <h2 className="font-heading text-lg font-bold">Transcript</h2>
        <div className="mt-4 space-y-3">
          {result ? result.turns.map((turn, index) => (
            <div key={`${turn.customer}-${index}`} className="rounded-md border border-white/10 bg-black/20 p-3">
              <p className="text-sm text-slate-400">Customer</p>
              <p className="mt-1 text-sm text-white">{turn.customer}</p>
              <div className="mt-3 border-t border-white/10 pt-3">
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-sm text-slate-400">Agent</p>
                  <IntentBadge intent={turn.agent.intent_label} />
                </div>
                <p className="text-sm text-slate-100">{turn.agent.text}</p>
                <div className="mt-3">
                  <LatencyBars latency={turn.agent.latency} />
                </div>
              </div>
            </div>
          )) : <p className="text-sm text-slate-400">Run a scenario to generate an English or Hindi demo call transcript.</p>}
        </div>
      </section>
    </div>
  );
}
