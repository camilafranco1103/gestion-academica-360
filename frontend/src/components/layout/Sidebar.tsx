import { NavLink } from 'react-router-dom';
import { motion } from 'motion/react';
import { LogOut } from 'lucide-react';
import { navigation } from '@/config/navigation';
import { useSession } from '@/context/SessionContext';
import { cn } from '@/lib/cn';
import { Logo } from './Logo';
import { UserAvatar } from './UserAvatar';

interface SidebarProps {
  onNavigate?: () => void;
  onLogout: () => void;
}

export function Sidebar({ onNavigate, onLogout }: SidebarProps) {
  const { user, hasRole } = useSession();
  const groups = navigation
    .map((g) => ({ ...g, items: g.items.filter((i) => hasRole(...i.roles)) }))
    .filter((g) => g.items.length > 0);

  return (
    <aside className="relative flex h-full w-64 flex-col overflow-hidden border-r border-sidebar-border bg-sidebar text-sidebar-foreground">
      {/* soft coral/teal glow + grain give the dark surface depth */}
      <div aria-hidden className="pointer-events-none absolute -top-24 -left-20 size-64 rounded-full bg-accent/15 blur-3xl" />
      <div aria-hidden className="bg-grain pointer-events-none absolute inset-0 opacity-[0.07] mix-blend-overlay" />

      <div className="relative flex h-16 items-center px-5">
        <Logo withText tone="light" />
      </div>

      <nav aria-label="Principal" className="scrollbar-thin relative flex-1 overflow-y-auto px-3 pb-4">
        {groups.map((group) => (
          <div key={group.label} className="mt-4 first:mt-1">
            <p className="mb-1.5 px-3 text-[0.66rem] font-semibold tracking-[0.16em] text-sidebar-muted/70 uppercase">
              {group.label}
            </p>
            <ul className="space-y-0.5">
              {group.items.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    end={item.path === '/'}
                    onClick={onNavigate}
                    className={({ isActive }) =>
                      cn(
                        'group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                        isActive ? 'text-white' : 'text-sidebar-muted hover:bg-white/5 hover:text-sidebar-foreground',
                      )
                    }
                  >
                    {({ isActive }) => (
                      <>
                        {isActive && (
                          <motion.span
                            layoutId="sidebar-active"
                            className="absolute inset-0 rounded-lg bg-sidebar-active"
                            transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                          >
                            <span className="absolute top-1.5 bottom-1.5 left-0 w-1 rounded-full bg-accent shadow-[0_0_12px_var(--color-accent)]" />
                          </motion.span>
                        )}
                        <item.icon
                          className={cn(
                            'relative size-4.5 shrink-0 transition-transform duration-200 group-hover:translate-x-0.5',
                            isActive && 'text-accent',
                          )}
                        />
                        <span className="relative">{item.label}</span>
                      </>
                    )}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      {user && (
        <div className="relative border-t border-sidebar-border p-3">
          <div className="flex items-center gap-3 rounded-lg p-2">
            <UserAvatar name={user.nombre} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold">{user.nombre}</p>
              <p className="truncate text-xs text-sidebar-muted">{user.email}</p>
            </div>
            <button
              type="button"
              onClick={onLogout}
              aria-label="Cerrar sesión"
              title="Cerrar sesión"
              className="grid size-8 cursor-pointer place-items-center rounded-lg text-sidebar-muted transition-colors hover:bg-white/10 hover:text-white [&_svg]:size-4"
            >
              <LogOut />
            </button>
          </div>
        </div>
      )}
    </aside>
  );
}
