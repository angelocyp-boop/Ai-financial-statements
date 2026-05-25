'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { authApi } from '@/lib/api';
import { useAuthStore } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore(s => s.setAuth);
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await authApi.login(form.email, form.password);
      setAuth(
        { id: data.user_id, email: data.email, first_name: data.full_name.split(' ')[0], last_name: data.full_name.split(' ')[1] || '', role: data.role, firm_id: data.firm_id },
        data.access_token,
      );
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <h2 className="text-xl font-semibold text-ink-900">Sign in</h2>
        <p className="text-sm text-ink-500 mt-1">Welcome back to your firm portal</p>
      </div>
      <div>
        <label className="label">Email address</label>
        <input type="email" className="input" placeholder="name@firm.com" value={form.email}
          onChange={e => setForm(f => ({ ...f, email: e.target.value }))} required />
      </div>
      <div>
        <label className="label">Password</label>
        <input type="password" className="input" placeholder="••••••••" value={form.password}
          onChange={e => setForm(f => ({ ...f, password: e.target.value }))} required />
      </div>
      <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
        {loading ? 'Signing in...' : 'Sign in'}
      </button>
      <p className="text-sm text-center text-ink-500">
        No account? <Link href="/register" className="text-brand-600 hover:underline">Register your firm</Link>
      </p>
    </form>
  );
}
