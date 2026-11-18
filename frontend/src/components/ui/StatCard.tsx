import type { MouseEvent, ReactNode } from 'react';
import { motion, useMotionTemplate, useMotionValue, useSpring, useTransform } from 'motion/react';
import { cn } from '@/lib/cn';
import { AnimatedNumber } from './AnimatedNumber';

type Tone = 'brand' | 'success' | 'warning' | 'danger' | 'info';

const toneClasses: Record<Tone, string> = {
  brand: 'bg-primary-soft text-primary',
  success: 'bg-success-soft text-success',
  warning: 'bg-warning-soft text-warning',
  danger: 'bg-danger-soft text-danger',
  info: 'bg-info-soft text-info',
};

interface StatCardProps {
  label: string;
  value: number;
  icon: ReactNode;
  hint?: string;
  tone?: Tone;
  format?: (n: number) => string;
}

/** KPI tile: animated count-up, subtle 3D tilt and a light that follows the pointer. */
export function StatCard({ label, value, icon, hint, tone = 'brand', format }: StatCardProps) {
  const mx = useMotionValue(0.5);
  const my = useMotionValue(0.5);
  const rotateX = useSpring(useTransform(my, [0, 1], [4, -4]), { stiffness: 200, damping: 20 });
  const rotateY = useSpring(useTransform(mx, [0, 1], [-4, 4]), { stiffness: 200, damping: 20 });
  const spotlight = useMotionTemplate`radial-gradient(260px circle at ${useTransform(mx, (v) => `${v * 100}%`)} ${useTransform(my, (v) => `${v * 100}%`)}, oklch(from var(--color-primary) l c h / 0.12), transparent 70%)`;

  function onMove(e: MouseEvent<HTMLDivElement>) {
    const r = e.currentTarget.getBoundingClientRect();
    mx.set((e.clientX - r.left) / r.width);
    my.set((e.clientY - r.top) / r.height);
  }
  function onLeave() {
    mx.set(0.5);
    my.set(0.5);
  }

  return (
    <motion.div
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      style={{ rotateX, rotateY, transformPerspective: 800 }}
      whileHover={{ y: -3 }}
      className="group relative overflow-hidden rounded-xl border bg-card p-5 shadow-[var(--shadow-soft)] transition-shadow hover:shadow-[var(--shadow-lift)]"
    >
      <motion.div aria-hidden className="pointer-events-none absolute inset-0 opacity-0 transition-opacity group-hover:opacity-100" style={{ background: spotlight }} />
      <span aria-hidden className="bg-brand absolute inset-x-0 top-0 h-0.5 scale-x-0 transition-transform duration-500 group-hover:scale-x-100" />
      <div className="relative flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          <p className="font-display mt-2 text-4xl leading-none font-semibold tracking-tight [font-variant-numeric:lining-nums_tabular-nums]">
            <AnimatedNumber value={value} format={format} />
          </p>
          {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
        </div>
        <span className={cn('grid size-10 place-items-center rounded-xl [&_svg]:size-5', toneClasses[tone])}>{icon}</span>
      </div>
    </motion.div>
  );
}
