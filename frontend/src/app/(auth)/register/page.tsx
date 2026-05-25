'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/auth';

export default function RegisterPage() {
  const router = useRouter();
  const setAuth = useAuthStore(s => s.setAuth);
  const [form, setForm] = useState({ firm_name: '', email: '', password: '', first_name: '', last_name: '' });
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await authApi.register(form);
      setAuth(
        { id: data.user_id, email: data.email, first_name: form.first_name, last_name: form.last_name, role: data.role, firm_id: data.firm_id },
        data.access_token,
      );
      toast.success('Firm registered successfully!');
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  }

  const f = (key: string) => (e: React.ChangeEvent<HTMLInputElement>) => setForm(p => ({ ...p, [key]: e.target.value }));

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold text-ink-900">Register your firm</h2>
        <p className="text-sm text-ink-500 mt-1">Start preparing IFRS statements in minutes</p>
      </div>
      <div>
        <label className="label">Firm name</label>
        <input className="input" placeholder="Acme Accounting Ltd" value={form.firm_name} onChange={f('firm_name')} required />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div><label className="label">First name</label><input className="input" value={form.first_name} onChange={f('first_name')} required /></div>
        <div><label className="label">Last name</label><input className="input" value={form.last_name} onChange={f('last_name')} required /></div>
      </div>
      <div>
        <label className="label">Email address</label>
        <input type="email" className="input" placeholder="you@firm.com" value={form.email} onChange={f('email')} required />
      </div>
      <div>
        <label className="label">Password</label>
        <input type="password" className="input" minLength={8} value={form.password} onChange={f('password')} required />
      </div>
      <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
        {loading ? 'Creating account...' : 'Create firm account'}
      </button>
      <p className="text-sm text-center text-ink-500">
        Already registered? <Link href="/login" className="text-brand-600 hover:underline">Sign in</Link>
      </p>
    </form>
  );
}
