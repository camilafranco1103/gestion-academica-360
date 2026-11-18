import { motion } from 'motion/react';
import { Send } from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import type { EstadoCount } from './types';

/** Meter list (dataviz skill): name, one-hue bar and figure per row, largest first. */
export function ComunicacionesMeters({ data }: { data: EstadoCount[] }) {
  const total = data.reduce((n, d) => n + d.cantidad, 0);
  const max = Math.max(1, ...data.map((d) => d.cantidad));

  return (
    <Card>
      <CardHeader icon={<Send />} title="Comunicaciones" description={`${total} mensajes en la cola de envío`} />
      <CardBody>
        {total === 0 ? (
          <EmptyState title="Sin comunicaciones" description="Los envíos masivos aparecerán acá." />
        ) : (
          <ul className="space-y-4">
            {data.map((d, i) => (
              <li key={d.estado}>
                <div className="mb-1.5 flex items-baseline justify-between text-sm">
                  <span className="text-muted-foreground">{d.estado}</span>
                  <span className="tabular font-semibold">{d.cantidad}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-muted">
                  <motion.div
                    className="h-full rounded-full bg-[var(--color-chart-1)]"
                    initial={{ width: 0 }}
                    whileInView={{ width: `${(d.cantidad / max) * 100}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: i * 0.08, ease: [0.16, 1, 0.3, 1] }}
                  />
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardBody>
    </Card>
  );
}
