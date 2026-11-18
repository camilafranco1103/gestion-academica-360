import { useState, type FormEvent } from 'react';
import { Lock, Mail, UserPlus } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import api, { apiErrorDetail } from '@/services/api';
import { TextField } from './TextField';

/** Only rendered when the backend reports public registration as enabled. */
export function RegisterForm({ onDone }: { onDone: () => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    if (password.length < 8) return setError('La contraseña debe tener al menos 8 caracteres.');
    if (password !== confirm) return setError('Las contraseñas no coinciden.');
    setLoading(true);
    try {
      await api.post('/api/auth/register', { email: email.trim(), password });
      onDone();
    } catch (err) {
      const { status, detail } = apiErrorDetail(err);
      setError(status === 409 ? 'Ese email ya está registrado.' : detail ?? 'No se pudo crear la cuenta.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      {error && <p role="alert" className="rounded-xl border border-danger/25 bg-danger-soft px-4 py-3 text-sm text-danger">{error}</p>}
      <TextField label="Email" type="email" autoComplete="email" icon={<Mail />} value={email} onChange={(e) => setEmail(e.target.value)} />
      <TextField label="Contraseña" type="password" autoComplete="new-password" icon={<Lock />} value={password} onChange={(e) => setPassword(e.target.value)} />
      <TextField label="Repetir contraseña" type="password" autoComplete="new-password" icon={<Lock />} value={confirm} onChange={(e) => setConfirm(e.target.value)} />
      <Button type="submit" size="lg" className="w-full" disabled={loading}>
        <UserPlus /> Crear cuenta
      </Button>
    </form>
  );
}
