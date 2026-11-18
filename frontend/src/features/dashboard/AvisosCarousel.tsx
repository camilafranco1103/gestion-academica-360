import { Link } from 'react-router-dom';
import { AlertOctagon, AlertTriangle, ArrowUpRight, Info, Megaphone } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { Carousel } from '@/components/ui/Carousel';
import { EmptyState } from '@/components/ui/EmptyState';
import type { Aviso } from './types';

const severity = {
  Info: { tone: 'info', Icon: Info, label: 'Info' },
  Advertencia: { tone: 'warning', Icon: AlertTriangle, label: 'Advertencia' },
  Crítico: { tone: 'danger', Icon: AlertOctagon, label: 'Crítico' },
} as const;

function severityOf(s: string) {
  return severity[s as keyof typeof severity] ?? severity.Info;
}

export function AvisosCarousel({ avisos }: { avisos: Aviso[] }) {
  return (
    <Card>
      <CardHeader
        icon={<Megaphone />}
        title="Tablón de avisos"
        description={avisos.length ? `${avisos.length} avisos vigentes` : 'Sin avisos vigentes'}
        action={
          <Link to="/avisos" className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline">
            Ver todos <ArrowUpRight className="size-3.5" />
          </Link>
        }
      />
      <CardBody>
        {avisos.length === 0 ? (
          <EmptyState title="Todo tranquilo" description="No hay avisos publicados para tu perfil." />
        ) : (
          <Carousel label="Avisos vigentes" slideClassName="basis-full md:basis-1/2 xl:basis-1/3">
            {avisos.map((a) => {
              const { tone, Icon, label } = severityOf(a.severidad);
              return (
                <article key={a.id} className="flex h-full flex-col rounded-xl border bg-gradient-to-br from-card to-muted/60 p-4 transition-shadow hover:shadow-[var(--shadow-lift)]">
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <Badge tone={tone}>
                      <Icon className="size-3" /> {label}
                    </Badge>
                    <time className="text-xs text-muted-foreground" dateTime={a.inicio_en}>
                      {new Date(a.inicio_en).toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })}
                    </time>
                  </div>
                  <h4 className="line-clamp-2 text-sm font-semibold">{a.titulo}</h4>
                  <p className="mt-1.5 line-clamp-3 text-xs text-muted-foreground">{a.cuerpo}</p>
                  {a.requiere_ack && <p className="mt-auto pt-3 text-xs font-medium text-primary">Requiere confirmación de lectura</p>}
                </article>
              );
            })}
          </Carousel>
        )}
      </CardBody>
    </Card>
  );
}
