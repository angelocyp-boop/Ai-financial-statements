'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { clientApi } from '@/lib/api';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';

export default function NewClientPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: '', legal_name: '', registration_number: '', vat_number: '',
    industry: '', currency: 'EUR', year_end_month: 12, year_end_day: 31,
    contact_name: '', contact_email: '', address: '',
  });

  const f = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(p => ({ ...p, [key]: e.target.value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const client = await clientApi.create(form);
      toast.success('Client created successfully');
      router.push(`/clients/${client.id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to create client');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <TopBar title="New Client" />
      <div className="p-6 max-w-2xl">
        <PageHeader title="Add Client" subtitle="Create a new client in your firm" />
        <form onSubmit={handleSubmit} className="card p-6 space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="label">Client name *</label>
              <input className="input" value={form.name} onChange={f('name')} required placeholder="Acme Ltd" />
            </div>
            <div>
              <label className="label">Legal name</label>
              <input className="input" value={form.legal_name} onChange={f('legal_name')} />
            </div>
            <div>
              <label className="label">Registration number</label>
              <input className="input" value={form.registration_number} onChange={f('registration_number')} />
            </div>
            <div>
              <label className="label">VAT number</label>
              <input className="input" value={form.vat_number} onChange={f('vat_number')} />
            </div>
            <div>
              <label className="label">Industry</label>
              <input className="input" value={form.industry} onChange={f('industry')} placeholder="e.g. Manufacturing" />
            </div>
            <div>
              <label className="label">Currency</label>
              <select className="input" value={form.currency} onChange={f('currency')}>
                <option>EUR</option><option>USD</option><option>GBP</option><option>AED</option><option>CHF</option>
              </select>
            </div>
            <div>
              <label className="label">Year-end month</label>
              <select className="input" value={form.year_end_month} onChange={f('year_end_month')}>
                {Array.from({length: 12}, (_, i) => (
                  <option key={i+1} value={i+1}>{new Date(0,i).toLocaleString('en',{month:'long'})}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Contact name</label>
              <input className="input" value={form.contact_name} onChange={f('contact_name')} />
            </div>
            <div>
              <label className="label">Contact email</label>
              <input type="email" className="input" value={form.contact_email} onChange={f('contact_email')} />
            </div>
            <div className="col-span-2">
              <label className="label">Address</label>
              <textarea className="input" rows={2} value={form.address} onChange={f('address')} />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create client'}
            </button>
            <Link href="/clients" className="btn-secondary">Cancel</Link>
          </div>
        </form>
      </div>
    </>
  );
}
