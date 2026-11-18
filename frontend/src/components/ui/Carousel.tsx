import { Children, useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import useEmblaCarousel from 'embla-carousel-react';
import Autoplay from 'embla-carousel-autoplay';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/cn';

interface CarouselProps {
  children: ReactNode;
  label: string;
  /** Tailwind basis classes for each slide, e.g. "basis-full md:basis-1/2". */
  slideClassName?: string;
  autoplayMs?: number;
}

/** Accessible carousel: autoplay that pauses on hover/focus, arrows, dots, swipe. */
export function Carousel({ children, label, slideClassName = 'basis-full', autoplayMs = 5000 }: CarouselProps) {
  const slides = Children.toArray(children);
  const loop = slides.length > 1;
  // Embla re-initialises whenever options/plugins change identity, and every
  // re-init fires 'reInit' → setState → render. Both MUST be memoised, or the
  // carousel loops forever ("Maximum update depth exceeded").
  const options = useMemo(() => ({ loop, align: 'start' as const }), [loop]);
  const plugins = useMemo(
    () => [Autoplay({ delay: autoplayMs, stopOnInteraction: false, stopOnMouseEnter: true, stopOnFocusIn: true })],
    [autoplayMs],
  );
  const [viewportRef, api] = useEmblaCarousel(options, plugins);
  const [selected, setSelected] = useState(0);
  const [snapCount, setSnapCount] = useState(0);

  const onSelect = useCallback(() => {
    if (!api) return;
    setSelected(api.selectedScrollSnap());
    setSnapCount(api.scrollSnapList().length); // a number: equal values don't re-render
  }, [api]);

  useEffect(() => {
    if (!api) return;
    // Sync the initial snap list outside the effect body, then follow Embla's events.
    const frame = requestAnimationFrame(onSelect);
    api.on('select', onSelect).on('reInit', onSelect);
    return () => {
      cancelAnimationFrame(frame);
      api.off('select', onSelect).off('reInit', onSelect);
    };
  }, [api, onSelect]);

  return (
    <section aria-roledescription="carousel" aria-label={label} className="relative">
      <div ref={viewportRef} className="overflow-hidden">
        <div className="-ml-4 flex touch-pan-y">
          {slides.map((slide, i) => (
            <div
              key={i}
              role="group"
              aria-roledescription="slide"
              aria-label={`${i + 1} de ${slides.length}`}
              className={cn('min-w-0 shrink-0 grow-0 pl-4', slideClassName)}
            >
              {slide}
            </div>
          ))}
        </div>
      </div>

      {snapCount > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <div className="flex gap-1.5">
            {Array.from({ length: snapCount }, (_, i) => (
              <button
                key={i}
                type="button"
                aria-label={`Ir a ${i + 1}`}
                aria-current={i === selected}
                onClick={() => api?.scrollTo(i)}
                className={cn(
                  'h-1.5 cursor-pointer rounded-full transition-all duration-300',
                  i === selected ? 'w-6 bg-accent' : 'w-1.5 bg-border hover:bg-muted-foreground/40',
                )}
              />
            ))}
          </div>
          <div className="flex gap-1">
            <ArrowButton label="Anterior" onClick={() => api?.scrollPrev()}>
              <ChevronLeft />
            </ArrowButton>
            <ArrowButton label="Siguiente" onClick={() => api?.scrollNext()}>
              <ChevronRight />
            </ArrowButton>
          </div>
        </div>
      )}
    </section>
  );
}

function ArrowButton({ label, onClick, children }: { label: string; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className="grid size-8 cursor-pointer place-items-center rounded-full border bg-card text-muted-foreground transition-colors hover:bg-muted hover:text-foreground [&_svg]:size-4"
    >
      {children}
    </button>
  );
}
