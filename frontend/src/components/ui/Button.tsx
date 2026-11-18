import type { ButtonHTMLAttributes, Ref } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/cn';

// eslint-disable-next-line react-refresh/only-export-components
export const buttonVariants = cva(
  'relative inline-flex cursor-pointer items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-150 active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        primary: 'bg-brand shine overflow-hidden text-white shadow-[var(--shadow-glow)] hover:brightness-110',
        accent: 'bg-accent text-accent-foreground shadow-[0_8px_24px_-8px_var(--color-accent)] hover:brightness-105',
        secondary: 'border bg-card text-foreground hover:bg-muted',
        ghost: 'text-muted-foreground hover:bg-muted hover:text-foreground',
        danger: 'bg-danger text-white hover:brightness-110',
        soft: 'bg-primary-soft text-primary hover:brightness-95',
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-9 px-4',
        lg: 'h-11 px-6 text-base',
        icon: 'size-9',
      },
    },
    defaultVariants: { variant: 'primary', size: 'md' },
  },
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  ref?: Ref<HTMLButtonElement>;
}

export function Button({ className, variant, size, ref, ...props }: ButtonProps) {
  return <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />;
}
