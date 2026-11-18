import type { ReactNode } from 'react';
import { motion } from 'motion/react';

interface RevealProps {
  children: ReactNode;
  /** Seconds to wait before animating; use index * 0.07 to stagger siblings. */
  delay?: number;
  className?: string;
}

/** Fades and lifts its content the first time it scrolls into view. */
export function Reveal({ children, delay = 0, className }: RevealProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}
