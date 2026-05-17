import { Activity, Clock3, IndianRupee, Phone, Target, TrendingUp } from "lucide-react";
import { IntentBadge } from "@/components/IntentBadge";
import { MetricCard } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { getAgents, getCalls, getLeads, getProviders, getStats } from "@/lib/api";
import { totalLatency } from "@/lib/format";
import { DialConsole } from "./DialConsole";

export default async function DashboardPage() {
  const [stats, calls, leads, agents, providers] = await Promise.all([
    getStats(),
    getCalls(),
    getLeads(),
    getAgents(),
    getProviders()
  ]);
  return (
    <div>
      <PageHeader title="Homeboard" description="Direct dial console for live AI loan follow-up, plus realtime operating metrics." />
      <DialConsole agents={agents} leads={leads} providerStatus={providers} />
      <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total calls" value={String(stats.total_calls)} detail={`${stats.live_calls} live conversations`} icon={Phone} />
        <MetricCard label="Conversion rate" value={`${stats.conversion_rate}%`} detail={`${stats.conversions} interested or high-ticket leads`} icon={TrendingUp} />
        <MetricCard label="Avg latency" value={`${stats.average_latency_ms}ms`} detail="Target is under 2500ms" icon={Clock3} />
        <MetricCard label="False positives" value={`${(stats.false_positive_rate * 100).toFixed(1)}%`} detail="Intent misclassification monitor" icon={Target} />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.5fr_1fr]">
        <section className="rounded-xl glass-card p-6 shadow-xl">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-heading text-lg font-extrabold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">Recent calls</h2>
            <Activity className="h-5 w-5 text-indigo-400 animate-pulse" aria-hidden="true" />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="text-xs uppercase text-slate-500 font-bold tracking-wider">
                <tr>
                  <th className="py-3 border-b border-white/5">Call</th>
                  <th className="border-b border-white/5">Lead</th>
                  <th className="border-b border-white/5">Intent</th>
                  <th className="border-b border-white/5">Action</th>
                  <th className="text-right border-b border-white/5">Latency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {calls.length === 0 ? (
                  <tr>
                    <td className="py-8 text-slate-400" colSpan={5}>No calls yet. Start one from the Calls page or run the simulator.</td>
                  </tr>
                ) : (
                  calls.map((call) => (
                    <tr key={call.call_sid} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3 font-mono text-xs text-indigo-300">{call.call_sid}</td>
                      <td className="font-semibold text-slate-200">{call.lead_id}</td>
                      <td><IntentBadge intent={call.intent_label} /></td>
                      <td className="text-slate-300 font-medium capitalize">{call.follow_up_action.replace("_", " ")}</td>
                      <td className="text-right font-mono text-slate-300">{totalLatency(call.latency)}ms</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rounded-xl glass-card p-6 shadow-xl flex flex-col justify-between">
          <div>
            <div className="mb-4 flex items-center gap-2">
              <IndianRupee className="h-5 w-5 text-[#22C55E]" aria-hidden="true" />
              <h2 className="font-heading text-lg font-extrabold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">Cost tracking</h2>
            </div>
            <p className="font-mono text-4xl font-extrabold text-[#22C55E] filter drop-shadow-[0_0_10px_rgba(34,197,94,0.2)]">${stats.cost_estimate.estimated_cost_usd.toFixed(2)}</p>
            <p className="mt-2 text-sm text-slate-400 font-medium">{stats.cost_estimate.message}</p>
          </div>
          <div className="mt-5 rounded-lg border border-white/10 bg-black/40 p-4">
            <div className="flex justify-between text-sm font-semibold">
              <span className="text-slate-400">Groq daily usage</span>
              <span className="font-mono text-[#22C55E]">{stats.cost_estimate.groq_pct_used}%</span>
            </div>
            <div className="mt-3 h-2 w-full rounded-full bg-white/10 overflow-hidden">
              <div 
                className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-green-500" 
                style={{ width: `${Math.min(stats.cost_estimate.groq_pct_used, 100)}%` }}
              />
            </div>
            <p className="mt-3 font-mono text-xs text-slate-500">{stats.cost_estimate.groq_tokens_used} / {stats.cost_estimate.groq_daily_limit} tokens</p>
          </div>
        </section>
      </div>
    </div>
  );
}
