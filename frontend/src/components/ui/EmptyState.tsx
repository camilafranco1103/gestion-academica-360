import type { ReactNode } from 'react';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
}

export function EmptyState({ title, description, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 px-6 py-10 text-center">
      <span className="animate-float relative grid size-12 place-items-center rounded-full bg-primary-soft text-primary ring-8 ring-primary-soft/50 [&_svg]:size-5">
        {icon ?? <Inbox />}
      </span>
      <p className="text-sm font-medium">{title}</p>
      {description && <p className="max-w-xs text-xs text-muted-foreground">{description}</p>}
    </div>
  );
}
