import { BookOpen, ClipboardList, GraduationCap, Receipt } from 'lucide-react';
import { StatCard } from '@/components/ui/StatCard';
import { Skeleton } from '@/components/ui/Skeleton';
import { useSession } from '@/context/SessionContext';
import { AvanceChart } from '@/features/dashboard/AvanceChart';
import { AvisosCarousel } from '@/features/dashboard/AvisosCarousel';
import { ComunicacionesMeters } from '@/features/dashboard/ComunicacionesMeters';
import { LiquidadoChart } from '@/features/dashboard/LiquidadoChart';
import { QuickActions } from '@/features/dashboard/QuickActions';
import { WelcomeHero } from '@/features/dashboard/WelcomeHero';
import { useDashboardData } from '@/features/dashboard/useDashboardData';

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
      </div>
      <Skeleton className="h-64 rounded-xl" />
    </div>
  );
}

export default function Dashboard() {
  const { user } = useSession();
  const data = useDashboardData(user);
  if (!user) return null;

  const kpis = data
    ? [
        data.materias !== null && { label: 'Materias', value: data.materias, icon: <BookOpen />, tone: 'brand' as const, hint: 'En el catálogo de la institución' },
        data.alumnos !== null && { label: 'Alumnos monitoreados', value: data.alumnos, icon: <GraduationCap />, tone: 'info' as const, hint: 'Con calificaciones importadas' },
        data.tareasAbiertas !== null && { label: 'Tareas abiertas', value: data.tareasAbiertas, icon: <ClipboardList />, tone: 'warning' as const, hint: 'Pendientes o en progreso' },
        data.liquidacionesAbiertas !== null && { label: 'Liquidaciones abiertas', value: data.liquidacionesAbiertas, icon: <Receipt />, tone: 'success' as const, hint: 'Listas para revisar y cerrar' },
      ].filter((k): k is Exclude<typeof k, false> => Boolean(k))
    : [];

  return (
    <div>
      <WelcomeHero user={user} />

      {!data ? (
        <DashboardSkeleton />
      ) : (
        <div className="space-y-6">
          {kpis.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {kpis.map((k) => <StatCard key={k.label} {...k} />)}
            </div>
          )}

          <AvisosCarousel avisos={data.avisos} />

          {(data.avance || data.comunicaciones) && (
            <div className="grid gap-6 xl:grid-cols-3">
              {data.avance && <div className="xl:col-span-2"><AvanceChart data={data.avance} /></div>}
              {data.comunicaciones && <ComunicacionesMeters data={data.comunicaciones} />}
            </div>
          )}

          {data.liquidado && <LiquidadoChart data={data.liquidado} />}

          <section>
            <h2 className="mb-3 text-sm font-semibold text-muted-foreground">Accesos rápidos</h2>
            <QuickActions />
          </section>
        </div>
      )}
    </div>
  );
}
