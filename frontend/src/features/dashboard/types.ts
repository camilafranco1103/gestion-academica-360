export interface Aviso {
  id: string;
  titulo: string;
  cuerpo: string;
  severidad: 'Info' | 'Advertencia' | 'Crítico' | string;
  alcance: string;
  inicio_en: string;
  requiere_ack: boolean;
}

export interface AvanceMateria {
  materia: string;
  aprobadas: number;
  faltantes: number;
  no_aprobadas: number;
}

export interface EstadoCount {
  estado: string;
  cantidad: number;
}

export interface PeriodoTotal {
  periodo: string;
  total: number;
}

/** `null` = the user's roles can't see that source (the widget is hidden). */
export interface DashboardData {
  materias: number | null;
  alumnos: number | null;
  avisos: Aviso[];
  avance: AvanceMateria[] | null;
  comunicaciones: EstadoCount[] | null;
  tareasAbiertas: number | null;
  liquidado: PeriodoTotal[] | null;
  liquidacionesAbiertas: number | null;
}
