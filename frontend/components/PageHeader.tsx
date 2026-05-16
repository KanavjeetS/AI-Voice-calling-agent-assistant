interface PageHeaderProps {
  title: string;
  description: string;
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-6">
      <h1 className="font-heading text-3xl font-bold text-white">{title}</h1>
      <p className="mt-2 max-w-3xl text-sm text-slate-400">{description}</p>
    </div>
  );
}
