import { useState, type FormEvent } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { ArrowRight, KeyRound, Lock, Mail, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { apiErrorDetail, login } from '@/services/api';
import { TextField } from './TextField';

function messageFor(status: number, detail?: string): string {
  if (status === 401) return detail === 'Código de verificación inválido' ? detail : 'Email o contraseña incorrectos.';
  if (status === 429) return 'Demasiados intentos fallidos. Esperá unos minutos y volvé a probar.';
  if (status === 0) return 'No se pudo conectar con el servidor.';
  return detail ?? 'Ocurrió un error. Intentá de nuevo.';
}

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [totp, setTotp] = useState('');
  const [needsTotp, setNeedsTotp] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (!email.trim() || !password) {
      setError('Completá email y contraseña.');
      return;
    }
    setLoading(true);
    try {
      await login({ email: email.trim(), password, ...(needsTotp ? { totp_code: totp } : {}) });
      // Full navigation so the session context loads the new user.
      window.location.assign('/');
    } catch (err) {
      const { status, detail } = apiErrorDetail(err);
      if (status === 403 && detail === 'totp_required') {
        setNeedsTotp(true);
      } else {
        setError(messageFor(status, detail));
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      <AnimatePresence>
        {error && (
          <motion.div
            role="alert"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <p className="rounded-xl border border-danger/25 bg-danger-soft px-4 py-3 text-sm text-danger">{error}</p>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait" initial={false}>
        {!needsTotp ? (
          <motion.div key="creds" initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -12 }} className="space-y-4">
            <TextField label="Email" type="email" autoComplete="username" placeholder="nombre@institucion.edu" icon={<Mail />} value={email} onChange={(e) => setEmail(e.target.value)} autoFocus />
            <TextField label="Contraseña" type="password" autoComplete="current-password" placeholder="Tu contraseña" icon={<Lock />} value={password} onChange={(e) => setPassword(e.target.value)} />
          </motion.div>
        ) : (
          <motion.div key="totp" initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 12 }} className="space-y-4">
            <div className="flex items-start gap-3 rounded-xl bg-primary-soft p-4 text-sm">
              <ShieldCheck className="mt-0.5 size-5 shrink-0 text-primary" />
              <p>Tu cuenta tiene verificación en dos pasos. Ingresá el código de 6 dígitos de tu app autenticadora.</p>
            </div>
            <TextField
              label="Código de verificación"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              placeholder="000000"
              icon={<KeyRound />}
              value={totp}
              onChange={(e) => setTotp(e.target.value.replace(/\D/g, ''))}
              autoFocus
              className="[&_input]:font-mono [&_input]:tracking-[0.4em]"
            />
            <button type="button" onClick={() => { setNeedsTotp(false); setTotp(''); }} className="cursor-pointer text-xs text-muted-foreground hover:text-foreground">
              ← Volver
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <Button type="submit" size="lg" className="group w-full" disabled={loading || (needsTotp && totp.length < 6)}>
        {loading ? (
          <span className="size-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        ) : (
          <>
            {needsTotp ? 'Verificar' : 'Ingresar'}
            <ArrowRight className="transition-transform group-hover:translate-x-0.5" />
          </>
        )}
      </Button>
    </form>
  );
}
