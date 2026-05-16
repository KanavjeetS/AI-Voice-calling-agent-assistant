import { CheckCircle2, Server, TriangleAlert } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { getProviders } from "@/lib/api";

const tierCopy = {
  free: "Groq API - zero cost, ~800 tok/sec, 1,600 calls/day",
  balanced: "Groq LLM + local Whisper - unlimited STT, free LLM",
  full: "100% self-hosted - Mistral 24B + Whisper + Chatterbox"
};

export default async function SettingsPage() {
  const status = await getProviders();
  return (
    <div>
      <PageHeader title="Settings" description="Model tier, provider readiness, voice stack, and restart-safe configuration state." />
      <div className="grid gap-4 xl:grid-cols-[1fr_420px]">
        <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <h2 className="font-heading text-lg font-bold">Model tier</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {(["free", "balanced", "full"] as const).map((tier) => (
              <div key={tier} className={`rounded-md border p-4 ${status.tier === tier ? "border-[#4F46E5] bg-[#4F46E5]/10" : "border-white/10 bg-black/20"}`}>
                <div className="flex items-center justify-between">
                  <p className="font-bold capitalize">{tier}</p>
                  {status.tier === tier ? <CheckCircle2 className="h-5 w-5 text-[#22C55E]" aria-hidden="true" /> : null}
                </div>
                <p className="mt-3 text-sm text-slate-400">{tierCopy[tier]}</p>
              </div>
            ))}
          </div>
          <p className="mt-4 rounded-md border border-amber-400/20 bg-amber-400/10 p-3 text-sm text-amber-100">
            Changing tier calls PUT /api/v1/settings/tier and requires an API container restart.
          </p>
        </section>
        <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <div className="mb-4 flex items-center gap-2">
            <Server className="h-5 w-5 text-indigo-300" aria-hidden="true" />
            <h2 className="font-heading text-lg font-bold">Provider status</h2>
          </div>
          <div className="space-y-3">
            {Object.entries(status.providers).map(([name, value]) => (
              <div key={name} className="flex items-center justify-between rounded-md border border-white/10 bg-black/20 p-3">
                <span className="text-sm text-slate-300">{name.replaceAll("_", " ")}</span>
                <span className="flex items-center gap-2 text-sm">
                  {value.includes("Not") || value.includes("Offline") ? <TriangleAlert className="h-4 w-4 text-[#F59E0B]" aria-hidden="true" /> : <CheckCircle2 className="h-4 w-4 text-[#22C55E]" aria-hidden="true" />}
                  {value}
                </span>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-md border border-white/10 bg-black/20 p-3">
            {Object.entries(status.models).map(([name, value]) => (
              <p key={name} className="mb-2 text-sm text-slate-400"><span className="text-slate-200">{name}:</span> {value}</p>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
