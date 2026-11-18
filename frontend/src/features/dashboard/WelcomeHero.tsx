import { motion } from 'motion/react';
import { Sparkles } from 'lucide-react';
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
      className="relative mb-6 overflow-hidden rounded-2xl p-6 text-white shadow-[var(--shadow-glow)] sm:p-8"
    >
      <div aria-hidden className="bg-brand animate-gradient absolute inset-0 bg-[length:200%_200%]" />
      <div aria-hidden className="bg-grid absolute inset-0 opacity-30 [mask-image:linear-gradient(to_left,black,transparent)]" />
      <div aria-hidden className="animate-float absolute -top-16 right-10 size-56 rounded-full bg-white/15 blur-2xl" />
      <div aria-hidden className="absolute -bottom-24 left-1/3 size-64 rounded-full bg-fuchsia-300/20 blur-3xl" />

      <div className="relative flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="flex items-center gap-1.5 text-sm font-medium text-white/80">
            <Sparkles className="size-4" />
            {now.toLocaleDateString('es-AR', { weekday: 'long', day: 'numeric', month: 'long' })}
          </p>
          <h1 className="mt-2 text-2xl font-bold text-white sm:text-3xl">
            {greeting(now)}, {firstName}
          </h1>
          <p className="mt-1 text-sm text-white/75">Este es el resumen de tu actividad en la plataforma.</p>
        </div>
        <span className="rounded-full border border-white/25 bg-white/15 px-3 py-1 text-xs font-medium backdrop-blur">{roles}</span>
      </div>
    </motion.section>
  );
}
