import { useLocation } from 'react-router-dom';
import { Menu } from 'lucide-react';
import { findNavItem, ROLE_LABELS } from '@/config/navigation';
import { useSession } from '@/context/SessionContext';
import { Badge } from '@/components/ui/Badge';
import { ThemeToggle } from '@/components/ThemeToggle';

export function Topbar({ onMenu }: { onMenu: () => void }) {
  const { pathname } = useLocation();
  const { user } = useSession();
  const current = findNavItem(pathname);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b bg-background/75 px-4 backdrop-blur-xl sm:px-6">
      <button
        type="button"
        onClick={onMenu}
        aria-label="Abrir menú"
        className="grid size-9 cursor-pointer place-items-center rounded-lg text-muted-foreground hover:bg-muted lg:hidden [&_svg]:size-5"
      >
        <Menu />
      </button>

      <nav aria-label="Ruta" className="flex min-w-0 items-center gap-2 text-sm">
        <span className="hidden text-muted-foreground sm:inline">Gestión Académica 360</span>
        <span className="hidden text-border sm:inline">/</span>
        <span className="truncate font-semibold">{current?.label ?? 'Inicio'}</span>
      </nav>

      <div className="ml-auto flex items-center gap-2">
        {user?.roles.slice(0, 2).map((r) => (
          <Badge key={r} tone="brand" className="hidden md:inline-flex">
            {ROLE_LABELS[r] ?? r}
          </Badge>
        ))}
        <span className="hidden items-center gap-1.5 rounded-full bg-success-soft px-2.5 py-1 text-xs font-medium text-success sm:inline-flex">
          <span className="animate-pulse-ring size-1.5 rounded-full bg-success" />
          En línea
        </span>
        <ThemeToggle />
      </div>
    </header>
  );
}
