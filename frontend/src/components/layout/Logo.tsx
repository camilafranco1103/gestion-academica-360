import { cn } from '@/lib/cn';

interface LogoProps {
  size?: number;
  withText?: boolean;
  /** "light" = text for dark surfaces (the sidebar). */
  tone?: 'default' | 'light';
}

export function Logo({ size = 32, withText = false, tone = 'default' }: LogoProps) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <svg
        width={size}
        height={size}
        viewBox="0 0 32 32"
        aria-hidden
        className="shrink-0 drop-shadow-[0_6px_14px_oklch(48%_0.08_203/0.45)]"
      >
        <defs>
          <linearGradient id="logo-g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" style={{ stopColor: 'var(--color-brand-from)' }} />
            <stop offset="1" style={{ stopColor: 'var(--color-brand-to)' }} />
          </linearGradient>
        </defs>
        <rect width="32" height="32" rx="8" fill="url(#logo-g)" />
        <path d="M7 20.5 12.5 13l4 5 4.5-7.5L25 16" fill="none" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="25" cy="16" r="2.4" style={{ fill: 'var(--color-accent)' }} />
      </svg>
      {withText && (
        <span className="flex flex-col leading-none">
          <span className={cn('font-display text-[1.02rem] font-semibold tracking-tight', tone === 'light' && 'text-sidebar-foreground')}>
            Gestión Académica
          </span>
          <span className={cn('mt-1.5 text-[0.66rem] font-bold tracking-[0.24em]', tone === 'light' ? 'text-accent' : 'text-accent-ink')}>
            360 · TRAZABILIDAD
          </span>
        </span>
      )}
    </span>
  );
}
