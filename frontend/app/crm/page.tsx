import { Users } from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { getLeads } from "@/lib/api";
import { formatCurrency } from "@/lib/format";

export default async function CRMPage() {
  const leads = await getLeads();
  return (
    <div>
      <PageHeader title="CRM" description="Lead status, missing information, and follow-up readiness saved after every call." />
      <section className="rounded-lg border border-white/10 bg-white/[0.025] p-4">
        <div className="mb-4 flex items-center gap-2">
          <Users className="h-5 w-5 text-indigo-300" aria-hidden="true" />
          <h2 className="font-heading text-lg font-bold">Lead pipeline</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="text-xs uppercase text-slate-500">
              <tr>
                <th className="py-3">Name</th>
                <th>Phone</th>
                <th>Loan amount</th>
                <th>Status</th>
                <th>Missing info</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {leads.map((lead) => (
                <tr key={lead.id}>
                  <td className="py-3 font-bold">{lead.name}</td>
                  <td className="font-mono text-xs text-slate-400">{lead.phone_number}</td>
                  <td>{formatCurrency(lead.loan_amount)}</td>
                  <td>{lead.status.replace("_", " ")}</td>
                  <td className="text-slate-400">{lead.missing_fields.length ? lead.missing_fields.join(", ") : "Complete"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
