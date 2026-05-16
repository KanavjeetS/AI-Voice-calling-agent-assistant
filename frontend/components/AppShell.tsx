import Link from "next/link";
import { BarChart3, Bot, Gauge, Headphones, LayoutDashboard, PhoneCall, Settings, Users } from "lucide-react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/monitor", label: "Monitor", icon: Headphones },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/calls", label: "Calls", icon: PhoneCall },
  { href: "/crm", label: "CRM", icon: Users },
  { href: "/studio", label: "Studio", icon: Bot },
  { href: "/simulator", label: "Simulator", icon: Gauge },
  { href: "/settings/keys", label: "Settings", icon: Settings }
];

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[#050810] text-slate-100">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-white/10 bg-[#0a0f1e] p-5 lg:block">
        <Link href="/dashboard" className="block">
          <p className="font-heading text-xl font-bold text-white">VahanAI Studio</p>
          <p className="mt-1 text-sm text-slate-500">Loan voice operations</p>
        </Link>
        <nav className="mt-8 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex h-11 items-center gap-3 rounded-md px-3 text-sm font-medium text-slate-300 transition hover:bg-white/5 hover:text-white"
            >
              <item.icon className="h-4 w-4" aria-hidden="true" />
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <header className="sticky top-0 z-10 border-b border-white/10 bg-[#050810]/90 px-5 py-4 backdrop-blur">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="font-heading text-lg font-bold lg:hidden">
              VahanAI Studio
            </Link>
            <div className="hidden text-sm text-slate-400 lg:block">Realtime loan follow-up command center</div>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <span className="h-2 w-2 rounded-full bg-[#22C55E]" />
              Free tier ready
            </div>
          </div>
        </header>
        <div className="mx-auto max-w-7xl p-5">{children}</div>
      </main>
    </div>
  );
}
