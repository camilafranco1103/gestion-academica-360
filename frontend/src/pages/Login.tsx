import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { Logo } from '@/components/layout/Logo';
import { ThemeToggle } from '@/components/ThemeToggle';
import { AuthHero } from '@/features/auth/AuthHero';
import { LoginForm } from '@/features/auth/LoginForm';
import { RegisterForm } from '@/features/auth/RegisterForm';
import { getAuthConfig, tokenStore } from '@/services/api';

export default function AuthPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [registerEnabled, setRegisterEnabled] = useState(false);
  const [registered, setRegistered] = useState(false);

  useEffect(() => {
    getAuthConfig()
      .then((c) => setRegisterEnabled(c.public_register))
      .catch(() => setRegisterEnabled(false));
  }, []);

  if (tokenStore.access) return <Navigate to="/" replace />;

  return (
    <div className="grid min-h-screen bg-background lg:grid-cols-[1.1fr_1fr]">
      <AuthHero />

      <div className="relative flex flex-col px-6 py-8 sm:px-12">
        <div className="flex items-center justify-between">
          <span className="lg:invisible">
            <Logo withText />
          </span>
          <ThemeToggle />
        </div>

        <div className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center py-10">
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}>
            <h2 className="text-3xl font-bold tracking-tight">
              {mode === 'login' ? 'Bienvenido de vuelta' : 'Crear cuenta'}
            </h2>
            <p className="mt-2 mb-8 text-sm text-muted-foreground">
              {mode === 'login' ? 'Ingresá con tu cuenta institucional para continuar.' : 'Completá tus datos para registrarte como alumno.'}
            </p>

            {registered && mode === 'login' && (
              <p className="mb-4 rounded-xl border border-success/25 bg-success-soft px-4 py-3 text-sm text-success">
                Cuenta creada. Ya podés ingresar.
              </p>
            )}

            {mode === 'login' ? (
              <LoginForm />
            ) : (
              <RegisterForm onDone={() => { setRegistered(true); setMode('login'); }} />
            )}

            {registerEnabled && (
              <p className="mt-6 text-center text-sm text-muted-foreground">
                {mode === 'login' ? '¿No tenés cuenta? ' : '¿Ya tenés cuenta? '}
                <button
                  type="button"
                  onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
                  className="cursor-pointer font-semibold text-primary hover:underline"
                >
                  {mode === 'login' ? 'Registrate' : 'Ingresá'}
                </button>
              </p>
            )}
          </motion.div>
        </div>

        <p className="text-center text-xs text-muted-foreground">Sesiones con rotación de tokens · 2FA disponible · Auditoría completa</p>
      </div>
    </div>
  );
}
