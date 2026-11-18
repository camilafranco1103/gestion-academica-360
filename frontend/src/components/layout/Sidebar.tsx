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
    <aside className="flex h-full w-64 flex-col border-r bg-sidebar">
      <div className="flex h-16 items-center px-5">
        <Logo withText />
      </div>

      <nav aria-label="Principal" className="scrollbar-thin flex-1 overflow-y-auto px-3 pb-4">
        {groups.map((group) => (
          <div key={group.label} className="mt-4 first:mt-1">
            <p className="mb-1.5 px-3 text-[0.68rem] font-semibold tracking-wider text-muted-foreground/80 uppercase">
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
                        'relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                        isActive ? 'text-primary' : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                      )
                    }
                  >
                    {({ isActive }) => (
                      <>
                        {isActive && (
                          <motion.span
                            layoutId="sidebar-active"
                            className="absolute inset-0 rounded-lg bg-primary-soft"
                            transition={{ type: 'spring', stiffness: 420, damping: 34 }}
                          >
                            <span className="bg-brand absolute top-1.5 bottom-1.5 left-0 w-1 rounded-full" />
                          </motion.span>
                        )}
                        <item.icon className="relative size-4.5 shrink-0" />
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
        <div className="border-t p-3">
          <div className="flex items-center gap-3 rounded-lg p-2">
            <UserAvatar name={user.nombre} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold">{user.nombre}</p>
              <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            </div>
            <button
              type="button"
              onClick={onLogout}
              aria-label="Cerrar sesión"
              title="Cerrar sesión"
              className="grid size-8 cursor-pointer place-items-center rounded-lg text-muted-foreground transition-colors hover:bg-danger-soft hover:text-danger [&_svg]:size-4"
            >
              <LogOut />
            </button>
          </div>
        </div>
      )}
    </aside>
  );
}
