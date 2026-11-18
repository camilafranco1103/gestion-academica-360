import { Logo } from './Logo';

export function FullPageLoader() {
  return (
    <div className="grid min-h-screen place-items-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-pulse">
          <Logo size={44} />
        </div>
        <div className="h-1 w-32 overflow-hidden rounded-full bg-muted">
          <div className="bg-brand h-full w-1/2 animate-[shimmer_1.2s_linear_infinite] rounded-full" style={{ backgroundSize: '200% 100%' }} />
        </div>
      </div>
    </div>
  );
}
