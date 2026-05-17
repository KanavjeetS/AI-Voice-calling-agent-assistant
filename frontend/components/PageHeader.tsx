interface PageHeaderProps {
  title: string;
  description: string;
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-6">
      <h1 className="font-heading text-4xl font-extrabold tracking-tight bg-gradient-to-r from-amber-200 via-yellow-400 to-amber-500 bg-clip-text text-transparent filter drop-shadow-[0_0_15px_rgba(245,158,11,0.15)]">{title}</h1>
      <p className="mt-2 max-w-3xl text-sm text-slate-400 font-medium">{description}</p>
    </div>
  );
}
