'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { engagementApi } from '@/lib/api';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';

export default function NewEngagementPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const clientId = parseInt(params.id);
  const currentYear = new Date().getFullYear();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    year: currentYear,
    period_start: `${currentYear}-01-01`,
    period_end: `${currentYear}-12-31`,
    comparative_year: currentYear - 1,
    reporting_standard: 'IFRS',
    currency: 'EUR',
    notes: '',
  });

  const f = (key: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm(p => ({ ...p, [key]: e.target.value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const eng = await engagementApi.create({ ...form, client_id: clientId });
      toast.success('Engagement created');
      router.push(`/clients/${clientId}/engagements/${eng.id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to create engagement');
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <TopBar title="New Engagement" />
      <div className="p-6 max-w-2xl">
        <PageHeader title="New Engagement" subtitle="Start a new financial year engagement" />
        <form onSubmit={handleSubmit} className="card p-6 space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Financial year *</label>
              <input type="number" className="input" value={form.year} onChange={f('year')} required min={2000} max={2100} />
            </div>
            <div>
              <label className="label">Comparative year</label>
              <input type="number" className="input" value={form.comparative_year} onChange={f('comparative_year')} min={2000} max={2100} />
            </div>
            <div>
              <label className="label">Period start *</label>
              <input type="date" className="input" value={form.period_start} onChange={f('period_start')} required />
            </div>
            <div>
              <label className="label">Period end *</label>
              <input type="date" className="input" value={form.period_end} onChange={f('period_end')} required />
            </div>
            <div>
              <label className="label">Reporting standard</label>
              <select className="input" value={form.reporting_standard} onChange={f('reporting_standard')}>
                <option value="IFRS">Full IFRS</option>
                <option value="IFRS_SME">IFRS for SMEs</option>
              </select>
            </div>
            <div>
              <label className="label">Currency</label>
              <select className="input" value={form.currency} onChange={f('currency')}>
                <option>EUR</option><option>USD</option><option>GBP</option><option>AED</option>
              </select>
            </div>
            <div className="col-span-2">
              <label className="label">Notes</label>
              <textarea className="input" rows={3} value={form.notes} onChange={f('notes')} placeholder="Any notes about this engagement..." />
            </div>
          </div>
          <div className="flex gap-3">
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create engagement'}
            </button>
            <Link href={`/clients/${clientId}`} className="btn-secondary">Cancel</Link>
          </div>
        </form>
      </div>
    </>
  );
}
