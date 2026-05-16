import { Bot, GitBranch, Mic, PhoneForwarded, Volume2, Workflow } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { getProviders } from "@/lib/api";

const nodes = [
  { title: "Greeting", detail: "Consent, identity, loan context", icon: Mic },
  { title: "Eligibility", detail: "Income, city, missing fields", icon: Workflow },
  { title: "EMI", detail: "Installment questions and quote handoff", icon: GitBranch },
  { title: "Documents", detail: "Salary slip, PAN, bank statement", icon: Bot },
  { title: "Callback", detail: "Human booking and escalation", icon: PhoneForwarded }
];

export default async function StudioPage() {
  const providers = await getProviders();
  const latencyCopy: Record<string, string> = {
    free: "~2.0-2.5s avg | Groq LLM + Kokoro TTS",
    balanced: "~1.8-2.2s avg | Groq LLM + Whisper local",
    full: "~1.5-2.0s avg | vLLM Mistral + Chatterbox"
  };
  return (
    <div>
      <PageHeader title="Agent Studio" description="Visual flow builder for the bilingual loan follow-up assistant and voice configuration." />
      <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
        <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <h2 className="font-heading text-lg font-bold">Conversation flow</h2>
          <div className="mt-5 grid gap-3 md:grid-cols-5">
            {nodes.map((node, index) => (
              <div key={node.title} className="rounded-md border border-white/10 bg-black/20 p-3">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-md bg-[#4F46E5]/15">
                  <node.icon className="h-5 w-5 text-indigo-200" aria-hidden="true" />
                </div>
                <p className="font-bold">{index + 1}. {node.title}</p>
                <p className="mt-2 text-xs text-slate-400">{node.detail}</p>
              </div>
            ))}
          </div>
          <div className="mt-5 rounded-md border border-white/10 bg-black/20 p-4">
            <p className="text-sm text-slate-300">Intent router actions</p>
            <div className="mt-3 grid gap-2 md:grid-cols-4">
              {["Escalate human", "Continue AI", "Terminate politely", "Book callback"].map((action) => (
                <span key={action} className="rounded border border-white/10 px-3 py-2 text-sm text-slate-300">{action}</span>
              ))}
            </div>
          </div>
        </section>
        <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <div className="mb-4 flex items-center gap-2">
            <Volume2 className="h-5 w-5 text-indigo-300" aria-hidden="true" />
            <h2 className="font-heading text-lg font-bold">Voice config</h2>
          </div>
          <div className="space-y-3">
            <div className="rounded-md border border-[#4F46E5]/30 bg-[#4F46E5]/10 p-3">
              <p className="text-xs uppercase text-indigo-200">Active tier</p>
              <p className="mt-1 font-heading text-2xl font-bold capitalize">{providers.tier}</p>
              <p className="mt-2 text-sm text-slate-300">{latencyCopy[providers.tier]}</p>
            </div>
            {Object.entries(providers.models).map(([name, value]) => (
              <div key={name} className="rounded-md border border-white/10 bg-black/20 p-3">
                <p className="text-xs uppercase text-slate-500">{name}</p>
                <p className="mt-1 text-sm text-slate-200">{value}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
