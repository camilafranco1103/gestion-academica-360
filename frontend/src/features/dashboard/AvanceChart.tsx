import { useState } from 'react';
import type { NameType, ValueType } from 'recharts/types/component/DefaultTooltipContent';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, type TooltipContentProps } from 'recharts';
import { CheckCircle2, CircleDashed, Table2, XCircle, BarChart3 } from 'lucide-react';
import { Card, CardBody, CardHeader } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import type { AvanceMateria } from './types';

// Status palette (validated, see index.css). Order keeps green and red apart.
const SERIES = [
  { key: 'aprobadas', label: 'Aprobadas', color: 'var(--color-status-good)', Icon: CheckCircle2 },
  { key: 'faltantes', label: 'Sin entregar', color: 'var(--color-status-warning)', Icon: CircleDashed },
  { key: 'no_aprobadas', label: 'No aprobadas', color: 'var(--color-status-critical)', Icon: XCircle },
] as const;

function ChartTooltip({ active, payload, label }: TooltipContentProps<ValueType, NameType>) {
  if (!active || !payload?.length) return null;
  const total = payload.reduce((n, p) => n + Number(p.value ?? 0), 0);
  return (
    <div className="min-w-48 rounded-xl border bg-card px-3 py-2.5 text-xs shadow-[var(--shadow-lift)]">
      <p className="mb-2 font-semibold text-foreground">{label}</p>
      {SERIES.map((s) => {
        const value = Number(payload.find((p) => p.dataKey === s.key)?.value ?? 0);
        return (
          <div key={s.key} className="flex items-center justify-between gap-4 py-0.5">
            <span className="flex items-center gap-2 text-muted-foreground">
              <span className="size-2.5 rounded-sm" style={{ background: s.color }} />
              {s.label}
            </span>
            <span className="tabular font-medium text-foreground">
              {value} <span className="text-muted-foreground">({total ? Math.round((value / total) * 100) : 0}%)</span>
            </span>
          </div>
        );
      })}
    </div>
  );
}

export function AvanceChart({ data }: { data: AvanceMateria[] }) {
  const [asTable, setAsTable] = useState(false);

  return (
    <Card>
      <CardHeader
        icon={<BarChart3 />}
        title="Avance académico por materia"
        description="Actividades de todos los alumnos, materias con más actividad"
        action={
          <button
            type="button"
            onClick={() => setAsTable((v) => !v)}
            aria-pressed={asTable}
            className="inline-flex cursor-pointer items-center gap-1.5 rounded-lg px-2 py-1 text-xs text-muted-foreground hover:bg-muted hover:text-foreground"
          >
            {asTable ? <BarChart3 className="size-3.5" /> : <Table2 className="size-3.5" />}
            {asTable ? 'Ver gráfico' : 'Ver tabla'}
          </button>
        }
      />
      <CardBody>
        {data.length === 0 ? (
          <EmptyState title="Sin calificaciones importadas" description="Importá calificaciones desde Moodle para ver el avance." />
        ) : asTable ? (
          <table>
            <thead>
              <tr>
                <th>Materia</th>
                {SERIES.map((s) => <th key={s.key} className="text-right">{s.label}</th>)}
              </tr>
            </thead>
            <tbody>
              {data.map((r) => (
                <tr key={r.materia}>
                  <td>{r.materia}</td>
                  {SERIES.map((s) => <td key={s.key} className="tabular text-right">{r[s.key]}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <>
            <ul className="mb-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground" aria-label="Leyenda">
              {SERIES.map(({ key, label, color, Icon }) => (
                <li key={key} className="flex items-center gap-1.5">
                  <Icon className="size-3.5" style={{ color }} />
                  {label}
                </li>
              ))}
            </ul>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }} barCategoryGap={10}>
                  <CartesianGrid horizontal={false} stroke="var(--color-border)" strokeDasharray="3 3" />
                  <XAxis type="number" tickLine={false} axisLine={false} tick={{ fill: 'var(--color-muted-foreground)', fontSize: 11 }} allowDecimals={false} />
                  <YAxis type="category" dataKey="materia" width={150} tickLine={false} axisLine={false} tick={{ fill: 'var(--color-muted-foreground)', fontSize: 11 }} tickFormatter={(v: string) => (v.length > 22 ? `${v.slice(0, 21)}…` : v)} />
                  <Tooltip content={ChartTooltip} cursor={{ fill: 'var(--color-muted)', opacity: 0.6 }} />
                  {SERIES.map((s, i) => (
                    <Bar
                      key={s.key}
                      dataKey={s.key}
                      name={s.label}
                      stackId="avance"
                      fill={s.color}
                      stroke="var(--color-card)"
                      strokeWidth={2}
                      radius={i === SERIES.length - 1 ? [0, 4, 4, 0] : 0}
                      maxBarSize={22}
                      animationDuration={900}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
      </CardBody>
    </Card>
  );
}
