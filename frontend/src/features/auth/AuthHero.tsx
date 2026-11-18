import { motion } from 'motion/react';
import { Activity, BellRing, ShieldCheck, TrendingUp, Users, Wallet } from 'lucide-react';
import { Carousel } from '@/components/ui/Carousel';
import { Logo } from '@/components/layout/Logo';

const features = [
  {
    icon: TrendingUp,
    title: 'Seguimiento académico en tiempo real',
    text: 'Calificaciones consolidadas desde Moodle y detección automática de alumnos atrasados.',
  },
  {
    icon: BellRing,
    title: 'Comunicación con aprobación',
    text: 'Envíos masivos personalizados con vista previa obligatoria y cola asíncrona.',
  },
  {
    icon: Wallet,
    title: 'Liquidaciones sin planillas',
    text: 'Grilla salarial, cálculo por docente y cierre inmutable del período.',
  },
  {
    icon: ShieldCheck,
    title: 'Todo queda trazado',
    text: 'Auditoría append-only: quién hizo qué, cuándo y sobre qué dato.',
  },
];

const floating = [
  { icon: Users, label: 'Roles y permisos', value: '7 perfiles', className: 'top-[18%] right-[8%]', delay: 0 },
  { icon: Activity, label: 'Integración', value: 'Moodle WS', className: 'bottom-[12%] right-[10%]', delay: 1.5 },
];

export function AuthHero() {
  return (
    <div className="relative hidden overflow-hidden lg:flex lg:flex-col lg:justify-between lg:p-12">
      {/* animated gradient mesh */}
      <div
        aria-hidden
        className="animate-gradient absolute inset-0 bg-[length:200%_200%]"
        style={{
          backgroundImage:
            'linear-gradient(125deg, oklch(42% 0.22 277), oklch(48% 0.25 293), oklch(40% 0.2 265), oklch(50% 0.24 300))',
        }}
      />
      <div aria-hidden className="bg-grid absolute inset-0 opacity-40 [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]" />
      <div aria-hidden className="absolute -top-24 -left-24 size-96 rounded-full bg-white/10 blur-3xl" />
      <div aria-hidden className="absolute -right-20 -bottom-32 size-[28rem] rounded-full bg-fuchsia-400/20 blur-3xl" />

      {floating.map(({ icon: Icon, label, value, className, delay }) => (
        <motion.div
          key={label}
          aria-hidden
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1, y: [0, -12, 0] }}
          transition={{ opacity: { delay: 0.4 + delay / 3 }, y: { duration: 7, repeat: Infinity, delay } }}
          className={`absolute ${className} flex items-center gap-3 rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-white shadow-2xl backdrop-blur-md`}
        >
          <span className="grid size-9 place-items-center rounded-xl bg-white/20">
            <Icon className="size-4.5" />
          </span>
          <span>
            <span className="block text-xs text-white/70">{label}</span>
            <span className="block text-lg font-bold tabular-nums">{value}</span>
          </span>
        </motion.div>
      ))}

      <div className="relative text-white">
        <Logo size={40} />
      </div>

      <div className="relative max-w-md text-white">
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="text-4xl leading-tight font-bold text-white"
        >
          La capa de inteligencia sobre tu campus virtual.
        </motion.h1>
        <p className="mt-4 text-white/75">
          Consolidá Moodle, coordiná equipos docentes y automatizá la gestión administrativa en un solo lugar.
        </p>

        <div className="mt-10">
          <Carousel label="Funcionalidades" autoplayMs={4500}>
            {features.map(({ icon: Icon, title, text }) => (
              <div key={title} className="rounded-2xl border border-white/15 bg-white/10 p-5 backdrop-blur-md">
                <Icon className="size-6 text-white" />
                <p className="mt-3 font-semibold">{title}</p>
                <p className="mt-1 text-sm text-white/70">{text}</p>
              </div>
            ))}
          </Carousel>
        </div>
      </div>

      <p className="relative text-xs text-white/60">© {new Date().getFullYear()} Gestión Académica 360 · Multi-institución · Datos aislados por tenant</p>
    </div>
  );
}
