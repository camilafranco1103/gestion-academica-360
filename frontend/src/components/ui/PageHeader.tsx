import type { ReactNode } from 'react';
import { motion } from 'motion/react';

interface PageHeaderProps {
  title: string;
  description?: string;
  eyebrow?: string;
  actions?: ReactNode;
}

export function PageHeader({ title, description, eyebrow, actions }: PageHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      className="mb-6 flex flex-wrap items-end justify-between gap-4"
    >
      <div>
        {eyebrow && <p className="mb-2 text-xs font-semibold tracking-[0.2em] text-accent-ink uppercase">{eyebrow}</p>}
        <h1 className="text-3xl sm:text-4xl">{title}</h1>
        {description && <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </motion.div>
  );
}
