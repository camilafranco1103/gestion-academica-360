import type { NameType, ValueType } from 'recharts/types/component/DefaultTooltipContent';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, type TooltipContentProps } from 'recharts';
import { Wallet } from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import type { PeriodoTotal } from './types';

const money = new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 });
const compact = new Intl.NumberFormat('es-AR', { notation: 'compact', maximumFractionDigits: 1 });

function periodoLabel(p: string): string {
  const [y, m] = p.split('-').map(Number);
  if (!y || !m) return p;
  return new Date(y, m - 1, 1).toLocaleDateString('es-AR', { month: 'short', year: '2-digit' });
}

function ChartTooltip({ active, payload, label }: TooltipContentProps<ValueType, NameType>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border bg-card px-3 py-2 text-xs shadow-[var(--shadow-lift)]">
      <p className="text-muted-foreground">{periodoLabel(String(label))}</p>
      <p className="tabular mt-0.5 text-sm font-semibold text-foreground">{money.format(Number(payload[0].value))}</p>
    </div>
  );
}

/** One series, one hue: total liquidado per period. */
export function LiquidadoChart({ data }: { data: PeriodoTotal[] }) {
  const total = data.reduce((n, d) => n + d.total, 0);
  return (
    <Card>
      <CardHeader icon={<Wallet />} title="Total liquidado por período" description={`${money.format(total)} acumulado`} />
      <CardBody>
        {data.length === 0 ? (
          <EmptyState title="Sin liquidaciones" description="Calculá una liquidación para verla acá." />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ left: -8, right: 8 }}>
                <CartesianGrid vertical={false} stroke="var(--color-border)" strokeDasharray="3 3" />
                <XAxis dataKey="periodo" tickFormatter={periodoLabel} tickLine={false} axisLine={false} tick={{ fill: 'var(--color-muted-foreground)', fontSize: 11 }} />
                <YAxis tickFormatter={(v: number) => compact.format(v)} tickLine={false} axisLine={false} tick={{ fill: 'var(--color-muted-foreground)', fontSize: 11 }} />
                <Tooltip content={ChartTooltip} cursor={{ fill: 'var(--color-muted)', opacity: 0.6 }} />
                <Bar dataKey="total" fill="var(--color-chart-1)" radius={[4, 4, 0, 0]} maxBarSize={36} animationDuration={900} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
