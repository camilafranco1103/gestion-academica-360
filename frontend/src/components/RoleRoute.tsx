import { Navigate, Outlet } from 'react-router-dom';
import { useSession } from '@/context/SessionContext';

/** UX guard only: the backend enforces permissions on every endpoint. */
export default function RoleRoute({ roles }: { roles: string[] }) {
  const { hasRole } = useSession();
  return hasRole(...roles) ? <Outlet /> : <Navigate to="/" replace />;
}
