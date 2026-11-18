interface LogoProps {
  size?: number;
  withText?: boolean;
}

export function Logo({ size = 32, withText = false }: LogoProps) {
  return (
    <span className="inline-flex items-center gap-2.5">
      <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden className="shrink-0 drop-shadow-[0_6px_14px_oklch(51%_0.23_277/0.35)]">
        <defs>
          <linearGradient id="logo-g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#4f46e5" />
            <stop offset="1" stopColor="#7c3aed" />
          </linearGradient>
        </defs>
        <rect width="32" height="32" rx="8" fill="url(#logo-g)" />
        <path d="M7 20.5 12.5 13l4 5 4.5-7.5L25 16" fill="none" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
        <circle cx="25" cy="16" r="2.2" fill="#fff" />
      </svg>
      {withText && (
        <span className="flex flex-col leading-none">
          <span className="text-[0.95rem] font-bold tracking-tight">Gestión Académica</span>
          <span className="text-brand mt-1 text-[0.7rem] font-extrabold tracking-[0.22em]">360 · TRAZABILIDAD</span>
        </span>
      )}
    </span>
  );
}
