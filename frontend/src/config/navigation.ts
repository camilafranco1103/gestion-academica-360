import {
  BarChart3, Bell, BookOpenCheck, Building2, CalendarClock, ClipboardList,
  GraduationCap, LayoutDashboard, MessageSquareShare, Receipt, ShieldCheck, TriangleAlert,
  Users, UsersRound, Wallet, type LucideIcon,
} from 'lucide-react';

export interface NavItem {
  path: string;
  label: string;
  icon: LucideIcon;
  /** Roles allowed; empty = every authenticated user. Also drives the route guard. */
  roles: string[];
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

const DOCENTES = ['PROFESOR', 'TUTOR', 'COORDINADOR', 'ADMIN'];

/** Single source of truth for the sidebar AND the route guards in App.tsx. */
export const navigation: NavGroup[] = [
  {
    label: 'General',
    items: [
      { path: '/', label: 'Inicio', icon: LayoutDashboard, roles: [] },
      { path: '/avisos', label: 'Avisos', icon: Bell, roles: [] },
    ],
  },
  {
    label: 'Académico',
    items: [
      { path: '/calificaciones', label: 'Calificaciones', icon: BookOpenCheck, roles: DOCENTES },
      { path: '/atrasados', label: 'Atrasados', icon: TriangleAlert, roles: DOCENTES },
      { path: '/comunicaciones', label: 'Comunicaciones', icon: MessageSquareShare, roles: ['PROFESOR', 'COORDINADOR', 'ADMIN'] },
      { path: '/encuentros', label: 'Encuentros', icon: CalendarClock, roles: DOCENTES },
      { path: '/coloquios', label: 'Coloquios', icon: GraduationCap, roles: ['ALUMNO', 'PROFESOR', 'COORDINADOR', 'ADMIN'] },
      { path: '/tareas', label: 'Tareas', icon: ClipboardList, roles: DOCENTES },
    ],
  },
  {
    label: 'Gestión',
    items: [
      { path: '/equipos', label: 'Equipos docentes', icon: UsersRound, roles: ['COORDINADOR', 'ADMIN'] },
      { path: '/estructura', label: 'Estructura', icon: Building2, roles: ['ADMIN'] },
      { path: '/usuarios', label: 'Usuarios', icon: Users, roles: ['ADMIN'] },
      { path: '/auditoria', label: 'Auditoría', icon: ShieldCheck, roles: ['COORDINADOR', 'ADMIN', 'FINANZAS'] },
    ],
  },
  {
    label: 'Finanzas',
    items: [
      { path: '/liquidaciones', label: 'Liquidaciones', icon: Wallet, roles: ['FINANZAS', 'ADMIN'] },
      { path: '/facturas', label: 'Facturas', icon: Receipt, roles: ['FINANZAS', 'ADMIN'] },
      { path: '/salarios', label: 'Grilla salarial', icon: BarChart3, roles: ['FINANZAS', 'ADMIN'] },
    ],
  },
];

export const allNavItems: NavItem[] = navigation.flatMap((g) => g.items);

export function findNavItem(pathname: string): NavItem | undefined {
  return allNavItems.find((i) => i.path === pathname);
}

export const ROLE_LABELS: Record<string, string> = {
  ADMIN: 'Administración',
  COORDINADOR: 'Coordinación',
  PROFESOR: 'Docente',
  TUTOR: 'Tutoría',
  ALUMNO: 'Alumno',
  FINANZAS: 'Finanzas',
  NEXO: 'Nexo',
};

