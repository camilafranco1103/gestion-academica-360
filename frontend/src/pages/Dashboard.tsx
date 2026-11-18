import { BookOpen, ClipboardList, GraduationCap, Receipt } from 'lucide-react';
import { Reveal } from '@/components/ui/Reveal';
import { SectionTitle } from '@/components/ui/SectionTitle';
import { Skeleton } from '@/components/ui/Skeleton';
import { StatCard } from '@/components/ui/StatCard';
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
        <div className="space-y-10">
          {kpis.length > 0 && (
            <section>
              <SectionTitle>Resumen</SectionTitle>
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {kpis.map((k, i) => (
                  <Reveal key={k.label} delay={i * 0.07}>
                    <StatCard {...k} />
                  </Reveal>
                ))}
              </div>
            </section>
          )}

          <section>
            <SectionTitle>Novedades</SectionTitle>
            <Reveal>
              <AvisosCarousel avisos={data.avisos} />
            </Reveal>
          </section>

          {(data.avance || data.comunicaciones) && (
            <section>
              <SectionTitle>Actividad académica</SectionTitle>
              <div className="grid gap-6 xl:grid-cols-3">
                {data.avance && (
                  <Reveal className="xl:col-span-2">
                    <AvanceChart data={data.avance} />
                  </Reveal>
                )}
                {data.comunicaciones && (
                  <Reveal delay={0.1}>
                    <ComunicacionesMeters data={data.comunicaciones} />
                  </Reveal>
                )}
              </div>
            </section>
          )}

          {data.liquidado && (
            <section>
              <SectionTitle>Finanzas</SectionTitle>
              <Reveal>
                <LiquidadoChart data={data.liquidado} />
              </Reveal>
            </section>
          )}

          <section>
            <SectionTitle>Accesos rápidos</SectionTitle>
            <QuickActions />
          </section>
        </div>
      )}
    </div>
  );
}
