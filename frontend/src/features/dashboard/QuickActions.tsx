import { Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { ArrowUpRight } from 'lucide-react';
import { allNavItems } from '@/config/navigation';
import { useSession } from '@/context/SessionContext';

const DESCRIPTIONS: Record<string, string> = {
  '/calificaciones': 'Importar y finalizar notas',
  '/atrasados': 'Alumnos con actividades pendientes',
  '/comunicaciones': 'Envíos masivos con aprobación',
  '/encuentros': 'Clases y guardias programadas',
  '/coloquios': 'Convocatorias y turnos',
  '/tareas': 'Trabajo interno del equipo',
  '/equipos': 'Asignaciones y vigencias',
  '/estructura': 'Carreras, cohortes y materias',
  '/usuarios': 'Altas, roles y accesos',
  '/auditoria': 'Quién hizo qué y cuándo',
  '/liquidaciones': 'Cálculo y cierre de honorarios',
  '/facturas': 'Comprobantes de docentes',
  '/salarios': 'Montos base y plus',
  '/avisos': 'Tablón institucional',
};

export function QuickActions() {
  const { hasRole } = useSession();
  const items = allNavItems.filter((i) => i.path !== '/' && hasRole(...i.roles)).slice(0, 6);

  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      {items.map((item, i) => (
        <motion.div
          key={item.path}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 + i * 0.05, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        >
          <Link
            to={item.path}
            className="group relative flex items-center gap-3 overflow-hidden rounded-xl border bg-card p-4 transition-all hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-[var(--shadow-lift)]"
          >
            <span className="grid size-10 shrink-0 place-items-center rounded-xl bg-primary-soft text-primary transition-colors group-hover:bg-brand group-hover:text-white">
              <item.icon className="size-5" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-sm font-semibold">{item.label}</span>
              <span className="block truncate text-xs text-muted-foreground">{DESCRIPTIONS[item.path]}</span>
            </span>
            <ArrowUpRight className="size-4 text-muted-foreground transition-all group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-primary" />
          </Link>
        </motion.div>
      ))}
    </div>
  );
}
