import { motion } from 'motion/react';
import { cn } from '@/lib/cn';

/** Decorative "trace" lines: a signal drawn across the banner, with checkpoints
 *  that light up in sequence and a pulsing coral endpoint. Echoes the product's
 *  promise (everything leaves a trace). Purely visual, hidden from screen readers. */

const TRACES = [
  { d: 'M0,172 C70,172 92,112 162,122 S262,196 334,142 S452,58 524,84 S574,116 604,92', opacity: 0.45, width: 1.7, delay: 0.2 },
  { d: 'M0,196 C90,190 120,150 200,158 S330,206 410,170 S520,120 640,140', opacity: 0.2, width: 1.2, delay: 0.7 },
];
const NODES = [
  { x: 162, y: 122, delay: 1.0 },
  { x: 334, y: 142, delay: 1.5 },
  { x: 524, y: 84, delay: 2.0 },
];
const END = { x: 604, y: 92 };

interface TraceLinesProps {
  className?: string;
  /** cover = fill the box (wide banners); contain = keep the whole drawing visible. */
  fit?: 'cover' | 'contain';
}

export function TraceLines({ className, fit = 'cover' }: TraceLinesProps) {
  return (
    <svg
      aria-hidden
      viewBox="0 0 640 240"
      preserveAspectRatio={fit === 'contain' ? 'xMidYMid meet' : 'xMidYMid slice'}
      className={cn('pointer-events-none absolute inset-0 size-full', className)}
    >
      {TRACES.map((t) => (
        <motion.path
          key={t.d}
          d={t.d}
          fill="none"
          stroke="white"
          strokeOpacity={t.opacity}
          strokeWidth={t.width}
          strokeLinecap="round"
          vectorEffect="non-scaling-stroke"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2.4, delay: t.delay, ease: [0.65, 0, 0.35, 1] }}
        />
      ))}
      {NODES.map((n) => (
        <motion.g
          key={n.x}
          initial={{ opacity: 0, scale: 0.4 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: n.delay, type: 'spring', stiffness: 260, damping: 18 }}
          style={{ transformBox: 'fill-box', transformOrigin: 'center' }}
        >
          <circle cx={n.x} cy={n.y} r={9} fill="white" fillOpacity={0.12} />
          <circle cx={n.x} cy={n.y} r={3.6} fill="white" fillOpacity={0.85} />
        </motion.g>
      ))}
      <motion.circle
        cx={END.x}
        cy={END.y}
        fill="none"
        strokeWidth={1.5}
        style={{ stroke: 'var(--color-accent)' }}
        initial={{ r: 4, opacity: 0.8 }}
        animate={{ r: [4, 18], opacity: [0.8, 0] }}
        transition={{ duration: 2.2, repeat: Infinity, delay: 2.6, ease: 'easeOut' }}
      />
      <motion.circle
        cx={END.x}
        cy={END.y}
        r={5}
        style={{ fill: 'var(--color-accent)' }}
        initial={{ opacity: 0, scale: 0 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 2.5, type: 'spring', stiffness: 300, damping: 16 }}
      />
    </svg>
  );
}
