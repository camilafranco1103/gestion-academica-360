import { cn } from '@/lib/cn';

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return ((parts[0]?.[0] ?? '') + (parts[1]?.[0] ?? '')).toUpperCase() || '?';
}

export function UserAvatar({ name, className }: { name: string; className?: string }) {
  return (
    <span
      aria-hidden
      className={cn(
        'bg-brand grid size-9 shrink-0 place-items-center rounded-full text-xs font-bold text-white ring-2 ring-card',
        className,
      )}
    >
      {initials(name)}
    </span>
  );
}
