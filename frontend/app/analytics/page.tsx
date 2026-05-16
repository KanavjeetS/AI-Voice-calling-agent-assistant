import { PageHeader } from "@/components/PageHeader";
import { getStats } from "@/lib/api";

export default async function AnalyticsPage() {
  const stats = await getStats();
  const intents = Object.entries(stats.intent_counts);
  return (
    <div>
      <PageHeader title="Analytics" description="Conversion, sentiment, intent distribution, and AI performance metrics for the loan calling program." />
      <div className="grid gap-4 lg:grid-cols-3">
        <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <p className="text-sm text-slate-400">Sentiment average</p>
          <p className="mt-2 font-mono text-4xl font-bold">{stats.average_sentiment.toFixed(2)}</p>
        </section>
        <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <p className="text-sm text-slate-400">AI latency average</p>
          <p className="mt-2 font-mono text-4xl font-bold">{stats.average_latency_ms}ms</p>
        </section>
        <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
          <p className="text-sm text-slate-400">Intent false-positive rate</p>
          <p className="mt-2 font-mono text-4xl font-bold">{(stats.false_positive_rate * 100).toFixed(1)}%</p>
        </section>
      </div>
      <section className="mt-4 rounded-lg border border-white/10 bg-white/[0.025] p-4">
        <h2 className="font-heading text-lg font-bold">Intent analytics</h2>
        <div className="mt-4 space-y-3">
          {intents.length ? intents.map(([intent, count]) => (
            <div key={intent} className="grid grid-cols-[140px_1fr_48px] items-center gap-3">
              <span className="text-sm text-slate-300">{intent.replace("_", " ")}</span>
              <div className="h-3 rounded-full bg-white/10">
                <div className="h-full w-1/3 rounded-full bg-[#4F46E5]" />
              </div>
              <span className="text-right font-mono text-sm">{count}</span>
            </div>
          )) : <p className="text-sm text-slate-400">No intent data yet.</p>}
        </div>
      </section>
    </div>
  );
}
