'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import { Plus, Search, Building2, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import { clientApi } from '@/lib/api';
import { formatDate, statusBadgeClass } from '@/lib/utils';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';

export default function ClientsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState('');
  const { data: clients = [], isLoading } = useQuery({ queryKey: ['clients'], queryFn: clientApi.list });

  const filtered = clients.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    (c.registration_number || '').toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <>
      <TopBar title="Clients" />
      <div className="p-6 max-w-5xl">
        <PageHeader
          title="Clients"
          subtitle={`${clients.length} client${clients.length !== 1 ? 's' : ''} in your firm`}
          actions={<Link href="/clients/new" className="btn-primary"><Plus className="w-4 h-4" /> Add client</Link>}
        />

        <div className="mb-4">
          <div className="relative">
            <Search className="w-4 h-4 text-ink-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input className="input pl-9 max-w-sm" placeholder="Search clients..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
        </div>

        {isLoading ? (
          <div className="card p-12 flex items-center justify-center">
            <div className="animate-spin w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="card p-16 text-center">
            <Building2 className="w-10 h-10 text-ink-300 mx-auto mb-3" />
            <p className="font-medium text-ink-700">No clients found</p>
            <p className="text-sm text-ink-400 mt-1">Add your first client to start preparing financial statements</p>
            <Link href="/clients/new" className="btn-primary mt-4"><Plus className="w-4 h-4" /> Add client</Link>
          </div>
        ) : (
          <div className="card divide-y divide-surface-100 overflow-hidden">
            {filtered.map(client => (
              <Link key={client.id} href={`/clients/${client.id}`}
                className="flex items-center justify-between px-5 py-4 hover:bg-surface-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-brand-50 flex items-center justify-center">
                    <Building2 className="w-4 h-4 text-brand-600" />
                  </div>
                  <div>
                    <p className="font-medium text-ink-900">{client.name}</p>
                    <p className="text-xs text-ink-500">{client.registration_number || 'No reg. number'} · {client.industry || 'Unspecified industry'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-ink-500">{client.engagement_count} engagement{client.engagement_count !== 1 ? 's' : ''}</span>
                  <span className="text-sm text-ink-500">{client.currency}</span>
                  <ChevronRight className="w-4 h-4 text-ink-400" />
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
