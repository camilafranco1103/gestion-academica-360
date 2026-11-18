import { useEffect, useRef } from 'react';
import { animate, useInView, useReducedMotion } from 'motion/react';

interface AnimatedNumberProps {
  value: number;
  format?: (n: number) => string;
  duration?: number;
}

const defaultFormat = (n: number) => Math.round(n).toLocaleString('es-AR');

/** Counts up from 0 to `value` the first time it scrolls into view. */
export function AnimatedNumber({ value, format = defaultFormat, duration = 1.1 }: AnimatedNumberProps) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const reduce = useReducedMotion();

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    if (!inView || reduce) {
      node.textContent = format(value);
      return;
    }
    const controls = animate(0, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => {
        node.textContent = format(v);
      },
    });
    return () => controls.stop();
  }, [inView, reduce, value, format, duration]);

  return <span ref={ref} className="tabular">{format(0)}</span>;
}
