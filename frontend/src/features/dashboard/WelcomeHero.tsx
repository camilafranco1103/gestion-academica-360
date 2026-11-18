import { motion } from 'motion/react';
import { Sparkles } from 'lucide-react';
import { TraceLines } from '@/components/ui/TraceLines';
import { ROLE_LABELS } from '@/config/navigation';
import type { User } from '@/services/api';

function greeting(date: Date): string {
  const h = date.getHours();
  if (h < 12) return 'Buen día';
  if (h < 20) return 'Buenas tardes';
  return 'Buenas noches';
}

export function WelcomeHero({ user }: { user: User }) {
  const now = new Date();
  const firstName = user.nombre.split(' ')[0];
  const roles = user.roles.map((r) => ROLE_LABELS[r] ?? r).join(' · ');

  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="relative mb-8 overflow-hidden rounded-2xl p-6 text-white shadow-[var(--shadow-glow)] sm:p-8"
    >
      <div aria-hidden className="bg-hero animate-gradient absolute inset-0" />
      <div aria-hidden className="bg-grid absolute inset-0 opacity-30 [mask-image:linear-gradient(to_left,black,transparent)]" />
      <div aria-hidden className="animate-aurora absolute -top-16 right-10 size-56 rounded-full bg-accent/25 blur-3xl" />
      <TraceLines className="opacity-90 [mask-image:linear-gradient(to_right,transparent_28%,black_62%)] max-sm:opacity-20" />
      <div aria-hidden className="bg-grain absolute inset-0 opacity-[0.12] mix-blend-overlay" />

      <div className="relative flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="flex items-center gap-1.5 text-sm font-medium text-white/80">
            <Sparkles className="size-4 text-accent" />
            {now.toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long' })}
          </p>
          <h1 className="mt-3 text-3xl text-white sm:text-4xl">
            {greeting(now)}, <span className="text-accent">{firstName}</span>
          </h1>
          <p className="mt-2 text-sm text-white/75">Este es el resumen de tu actividad en la plataforma.</p>
        </div>
        <span className="rounded-full border border-white/25 bg-white/15 px-3 py-1 text-xs font-medium backdrop-blur">{roles}</span>
      </div>
    </motion.section>
  );
}
