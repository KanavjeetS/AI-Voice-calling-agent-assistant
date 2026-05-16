import { PhoneCall } from "lucide-react";
import { IntentBadge } from "@/components/IntentBadge";
import { LatencyBars } from "@/components/LatencyBars";
import { PageHeader } from "@/components/PageHeader";
import { getCalls, getLeads } from "@/lib/api";

export default async function CallsPage() {
  const [calls, leads] = await Promise.all([getCalls(), getLeads()]);
  return (
    <div>
      <PageHeader title="Calls" description="Call records with transcript viewing, intent labels, follow-up actions, and recording slots." />
      <section className="mb-4 rounded-lg border border-white/10 bg-white/[0.025] p-4">
        <div className="flex items-center gap-2">
          <PhoneCall className="h-5 w-5 text-indigo-300" aria-hidden="true" />
          <h2 className="font-heading text-lg font-bold">Ready leads</h2>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {leads.map((lead) => (
            <div key={lead.id} className="rounded-md border border-white/10 bg-black/20 p-3">
              <p className="font-bold">{lead.name}</p>
              <p className="mt-1 font-mono text-xs text-slate-400">{lead.phone_number}</p>
              <p className="mt-2 text-sm text-slate-400">{lead.status.replace("_", " ")}</p>
            </div>
          ))}
        </div>
      </section>
      <div className="space-y-4">
        {calls.length ? calls.map((call) => (
          <section key={call.call_sid} className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-mono text-sm text-slate-400">{call.call_sid}</p>
                <p className="mt-1 font-heading text-xl font-bold">{call.customer_phone}</p>
              </div>
              <IntentBadge intent={call.intent_label} />
            </div>
            <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_360px]">
              <div className="space-y-2">
                {call.transcript.length ? call.transcript.map((turn) => (
                  <div key={`${turn.timestamp}-${turn.speaker}`} className="rounded-md border border-white/10 bg-black/20 p-3">
                    <span className="text-xs uppercase text-slate-500">{turn.speaker}</span>
                    <p className="mt-1 text-sm text-slate-200">{turn.text}</p>
                  </div>
                )) : <p className="text-sm text-slate-400">Transcript will appear after the first customer turn.</p>}
              </div>
              <div className="rounded-md border border-white/10 bg-black/20 p-3">
                <p className="mb-3 text-sm font-bold">Latency breakdown</p>
                <LatencyBars latency={call.latency} />
                <div className="mt-4 grid aspect-video place-items-center rounded border border-white/10 text-xs text-slate-500">
                  Recording playback placeholder
                </div>
              </div>
            </div>
          </section>
        )) : (
          <section className="rounded-lg border border-white/10 bg-white/[0.025] p-8 text-sm text-slate-400">
            No call records yet. Use the simulator to create realistic demo interactions.
          </section>
        )}
      </div>
    </div>
  );
}
