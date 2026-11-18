import { Navigate, Outlet } from 'react-router-dom';
import { useSession } from '@/context/SessionContext';
import { tokenStore } from '@/services/api';
import { FullPageLoader } from '@/components/layout/FullPageLoader';

export default function ProtectedRoute() {
  const { user, loading } = useSession();
  if (!tokenStore.access) return <Navigate to="/login" replace />;
  if (loading) return <FullPageLoader />;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}
