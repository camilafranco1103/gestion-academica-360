import type { ComponentType } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './components/AppLayout';
import ProtectedRoute from './components/ProtectedRoute';
import RoleRoute from './components/RoleRoute';
import { allNavItems } from './config/navigation';
import { SessionProvider } from './context/SessionContext';
import AuthPage from './pages/Login';
import Dashboard from './pages/Dashboard';
import Calificaciones from './pages/Calificaciones';
import Atrasados from './pages/Atrasados';
import Comunicaciones from './pages/Comunicaciones';
import EquiposDocentes from './pages/EquiposDocentes';
import Avisos from './pages/Avisos';
import Tareas from './pages/Tareas';
import Encuentros from './pages/Encuentros';
import Coloquios from './pages/Coloquios';
import Liquidaciones from './pages/Liquidaciones';
import Facturas from './pages/Facturas';
import Salarios from './pages/Salarios';
import EstructuraAcademica from './pages/EstructuraAcademica';
import Auditoria from './pages/Auditoria';
import Usuarios from './pages/Usuarios';

const pages: Record<string, ComponentType> = {
  '/': Dashboard,
  '/avisos': Avisos,
  '/calificaciones': Calificaciones,
  '/atrasados': Atrasados,
  '/comunicaciones': Comunicaciones,
  '/encuentros': Encuentros,
  '/coloquios': Coloquios,
  '/tareas': Tareas,
  '/equipos': EquiposDocentes,
  '/estructura': EstructuraAcademica,
  '/usuarios': Usuarios,
  '/auditoria': Auditoria,
  '/liquidaciones': Liquidaciones,
  '/facturas': Facturas,
  '/salarios': Salarios,
};

export default function App() {
  return (
    <SessionProvider>
      <Routes>
        <Route path="/login" element={<AuthPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            {/* Roles per route come from config/navigation.ts (same source as the sidebar). */}
            {allNavItems.map(({ path, roles }) => {
              const Page = pages[path];
              return (
                <Route key={path} element={<RoleRoute roles={roles} />}>
                  <Route path={path} element={<Page />} />
                </Route>
              );
            })}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Route>
      </Routes>
    </SessionProvider>
  );
}
