import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { getCurrentUser, logout as apiLogout, tokenStore, type User } from '@/services/api';

interface SessionValue {
  user: User | null;
  loading: boolean;
  hasRole: (...roles: string[]) => boolean;
  logout: () => Promise<void>;
}

const SessionContext = createContext<SessionValue | null>(null);

/** Loads the signed-in user once and shares it with the whole app shell. */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(() => Boolean(tokenStore.access));

  useEffect(() => {
    if (!tokenStore.access) return;
    let alive = true;
    getCurrentUser()
      .then((u) => alive && setUser(u))
      .catch(() => alive && setUser(null))
      .finally(() => alive && setLoading(false));
    return () => {
      alive = false;
    };
  }, []);

  const hasRole = useCallback(
    (...roles: string[]) => roles.length === 0 || roles.some((r) => user?.roles.includes(r)),
    [user],
  );

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  return <SessionContext.Provider value={{ user, loading, hasRole, logout }}>{children}</SessionContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useSession(): SessionValue {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession must be used inside <SessionProvider>');
  return ctx;
}
