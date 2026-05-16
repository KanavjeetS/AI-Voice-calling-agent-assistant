import { Radio, Volume2 } from "lucide-react";
import { IntentBadge } from "@/components/IntentBadge";
import { PageHeader } from "@/components/PageHeader";
import { getCalls } from "@/lib/api";

export default async function MonitorPage() {
  const calls = await getCalls();
  const active = calls[0];
  return (
    <div>
      <PageHeader title="Live Monitor" description="Realtime transcript lane for supervisors watching active calls and interruption-safe AI turns." />
      <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
        <section className="min-h-[560px] rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <div className="mb-4 flex items-center gap-2">
            <Radio className="h-5 w-5 text-[#22C55E]" aria-hidden="true" />
            <h2 className="font-heading text-lg font-bold">{active ? active.call_sid : "No active stream"}</h2>
          </div>
          <div className="space-y-3">
            {active?.transcript.length ? (
              active.transcript.map((turn) => (
                <div key={`${turn.timestamp}-${turn.speaker}`} className="rounded-md border border-white/10 bg-black/20 p-3">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-xs uppercase text-slate-500">{turn.speaker}</span>
                    {turn.intent ? <IntentBadge intent={turn.intent} /> : null}
                  </div>
                  <p className="text-sm text-slate-200">{turn.text}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400">No live transcripts yet. The Twilio media WebSocket is ready at /api/v1/ws/twilio.</p>
            )}
          </div>
        </section>
        <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <div className="mb-4 flex items-center gap-2">
            <Volume2 className="h-5 w-5 text-indigo-300" aria-hidden="true" />
            <h2 className="font-heading text-lg font-bold">Playback</h2>
          </div>
          <div className="grid aspect-video place-items-center rounded-md border border-white/10 bg-black/30 text-sm text-slate-500">
            Recording appears after Twilio call completion
          </div>
          <div className="mt-4 space-y-2 text-sm text-slate-400">
            <p>Interruptions: {active?.follow_up_action === "escalate_agent" ? "Escalation pending" : "Ready"}</p>
            <p>Sentiment: {active ? active.sentiment_score.toFixed(2) : "0.00"}</p>
          </div>
        </section>
      </div>
    </div>
  );
}
