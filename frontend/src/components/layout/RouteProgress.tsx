import { useLocation } from 'react-router-dom';
import { motion } from 'motion/react';

/** Hairline that sweeps across the top bar on every navigation. */
export function RouteProgress() {
  const { pathname } = useLocation();
  return (
    <motion.span
      key={pathname}
      aria-hidden
      className="pointer-events-none absolute inset-x-0 bottom-0 h-0.5 origin-left bg-gradient-to-r from-accent via-primary to-transparent"
      initial={{ scaleX: 0, opacity: 1 }}
      animate={{ scaleX: 1, opacity: [1, 1, 0] }}
      transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
    />
  );
}
