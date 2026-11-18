import type { ReactNode } from 'react';

/** Small-caps section label with a hairline rule: quiet, but gives the page rhythm. */
export function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <div className="mb-3 flex items-center gap-3">
      <h2 className="text-xs font-semibold tracking-[0.18em] whitespace-nowrap text-muted-foreground uppercase">
        {children}
      </h2>
      <span aria-hidden className="h-px flex-1 bg-gradient-to-r from-border to-transparent" />
    </div>
  );
}
