'use client';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ArrowLeft, Plus, FileText, ChevronRight } from 'lucide-react';
import { clientApi, engagementApi } from '@/lib/api';
import { statusBadgeClass, formatDate } from '@/lib/utils';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';

export default function ClientDetailPage({ params }: { params: { id: string } }) {
  const clientId = parseInt(params.id);
  const { data: client, isLoading } = useQuery({ queryKey: ['client', clientId], queryFn: () => clientApi.get(clientId) });
  const { data: engagements = [] } = useQuery({ queryKey: ['engagements', clientId], queryFn: () => engagementApi.list(clientId) });

  if (isLoading) return <div className="p-8 text-center text-ink-500">Loading...</div>;
  if (!client) return <div className="p-8 text-center text-ink-500">Client not found</div>;

  return (
    <>
      <TopBar title={client.name} />
      <div className="p-6 max-w-4xl">
        <div className="flex items-center gap-2 text-sm text-ink-500 mb-4">
          <Link href="/clients" className="hover:text-ink-900">Clients</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-ink-900">{client.name}</span>
        </div>

        <PageHeader
          title={client.name}
          subtitle={`${client.legal_name || ''} · ${client.registration_number || 'No reg. no.'}`}
          actions={
            <Link href={`/clients/${clientId}/engagements/new`} className="btn-primary">
              <Plus className="w-4 h-4" /> New Engagement
            </Link>
          }
        />

        {/* Client info */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: 'Currency', value: client.currency },
            { label: 'VAT Number', value: client.vat_number || '-' },
            { label: 'Industry', value: client.industry || '-' },
            { label: 'Year End', value: `${client.year_end_day}/${client.year_end_month}` },
            { label: 'Contact', value: client.contact_name || '-' },
            { label: 'Email', value: client.contact_email || '-' },
          ].map(item => (
            <div key={item.label} className="card p-4">
              <p className="text-xs text-ink-500 uppercase tracking-wide">{item.label}</p>
              <p className="font-medium text-ink-900 mt-1 text-sm">{item.value}</p>
            </div>
          ))}
        </div>

        {/* Engagements */}
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-surface-100 flex items-center justify-between">
            <h3 className="font-semibold text-ink-900">Engagements ({engagements.length})</h3>
            <Link href={`/clients/${clientId}/engagements/new`} className="btn-ghost text-xs">
              <Plus className="w-3.5 h-3.5" /> Add
            </Link>
          </div>
          {engagements.length === 0 ? (
            <div className="py-12 text-center">
              <FileText className="w-8 h-8 text-ink-300 mx-auto mb-2" />
              <p className="text-ink-500">No engagements yet</p>
              <Link href={`/clients/${clientId}/engagements/new`} className="btn-primary mt-3">
                <Plus className="w-4 h-4" /> Create first engagement
              </Link>
            </div>
          ) : (
            <div className="divide-y divide-surface-100">
              {engagements.map(eng => (
                <Link key={eng.id} href={`/clients/${clientId}/engagements/${eng.id}`}
                  className="flex items-center justify-between px-5 py-4 hover:bg-surface-50 transition-colors">
                  <div>
                    <p className="font-medium text-ink-900">Year {eng.year}</p>
                    <p className="text-xs text-ink-500">{eng.period_start} → {eng.period_end} · {eng.reporting_standard}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={statusBadgeClass(eng.status)}>{eng.status.replace('_', ' ')}</span>
                    <ChevronRight className="w-4 h-4 text-ink-400" />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
