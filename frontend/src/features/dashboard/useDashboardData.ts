import { useEffect, useState } from 'react';
import api from '@/services/api';
import type { User } from '@/services/api';
import type { AvanceMateria, Aviso, DashboardData, EstadoCount, PeriodoTotal } from './types';

interface MonitorResponse {
  total: number;
  alumnos: { materias: { materia_nombre: string; aprobadas: number; no_aprobadas: number; faltantes: number }[] }[];
}
interface ComunicacionesResponse {
  items: { pendientes: number; enviando: number; enviados: number; errores: number; cancelados: number }[];
}
interface Liquidacion {
  periodo: string;
  total: string;
  estado: string;
}
interface Tarea {
  estado: string;
}

const has = (user: User, ...roles: string[]) => roles.some((r) => user.roles.includes(r));

function avancePorMateria(monitor: MonitorResponse): AvanceMateria[] {
  const acc = new Map<string, AvanceMateria>();
  for (const alumno of monitor.alumnos) {
    for (const m of alumno.materias) {
      const row = acc.get(m.materia_nombre) ?? { materia: m.materia_nombre, aprobadas: 0, faltantes: 0, no_aprobadas: 0 };
      row.aprobadas += m.aprobadas;
      row.faltantes += m.faltantes;
      row.no_aprobadas += m.no_aprobadas;
      acc.set(m.materia_nombre, row);
    }
  }
  const total = (r: AvanceMateria) => r.aprobadas + r.faltantes + r.no_aprobadas;
  return [...acc.values()].sort((a, b) => total(b) - total(a)).slice(0, 6);
}

function estadosComunicaciones(res: ComunicacionesResponse): EstadoCount[] {
  const sum = (k: keyof ComunicacionesResponse['items'][number]) => res.items.reduce((n, i) => n + i[k], 0);
  return [
    { estado: 'Enviados', cantidad: sum('enviados') },
    { estado: 'Pendientes', cantidad: sum('pendientes') + sum('enviando') },
    { estado: 'Con error', cantidad: sum('errores') },
    { estado: 'Cancelados', cantidad: sum('cancelados') },
  ].sort((a, b) => b.cantidad - a.cantidad);
}

function totalesPorPeriodo(liqs: Liquidacion[]): PeriodoTotal[] {
  const acc = new Map<string, number>();
  for (const l of liqs) acc.set(l.periodo, (acc.get(l.periodo) ?? 0) + Number(l.total));
  return [...acc.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([periodo, total]) => ({ periodo, total }));
}

async function optional<T>(enabled: boolean, url: string): Promise<T | null> {
  if (!enabled) return null;
  try {
    return (await api.get<T>(url)).data;
  } catch {
    return null; // a failing widget must not take the whole dashboard down
  }
}

/** Loads only what the user's roles may see; every source is optional. */
export function useDashboardData(user: User | null) {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    if (!user) return;
    let alive = true;
    const coord = has(user, 'COORDINADOR', 'ADMIN');
    const docente = has(user, 'PROFESOR', 'TUTOR', 'COORDINADOR', 'ADMIN');
    const finanzas = has(user, 'FINANZAS', 'ADMIN');

    Promise.all([
      optional<unknown[]>(true, '/api/materias'),
      optional<Aviso[]>(true, '/api/v1/avisos/mis-avisos'),
      optional<MonitorResponse>(coord, '/api/v1/analisis/monitor/general?limit=500'),
      optional<ComunicacionesResponse>(has(user, 'PROFESOR', 'COORDINADOR', 'ADMIN'), '/api/v1/comunicaciones/estados'),
      optional<Tarea[]>(coord, '/api/v1/tareas/admin?limit=500'),
      optional<Tarea[]>(docente && !coord, '/api/v1/tareas/mis-tareas?limit=500'),
      optional<Liquidacion[]>(finanzas, '/api/v1/liquidaciones'),
    ]).then(([materias, avisos, monitor, comunicaciones, tareasAdmin, misTareas, liquidaciones]) => {
      if (!alive) return;
      const tareas = tareasAdmin ?? misTareas;
      setData({
        materias: materias?.length ?? null,
        alumnos: monitor?.total ?? null,
        avisos: avisos ?? [],
        avance: monitor ? avancePorMateria(monitor) : null,
        comunicaciones: comunicaciones ? estadosComunicaciones(comunicaciones) : null,
        tareasAbiertas: tareas ? tareas.filter((t) => t.estado === 'Pendiente' || t.estado === 'En progreso').length : null,
        liquidado: liquidaciones ? totalesPorPeriodo(liquidaciones) : null,
        liquidacionesAbiertas: liquidaciones ? liquidaciones.filter((l) => l.estado === 'Abierta').length : null,
      });
    });
    return () => {
      alive = false;
    };
  }, [user]);

  return data;
}
