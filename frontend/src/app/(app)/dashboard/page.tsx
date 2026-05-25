'use client';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { Users, FileText, CheckCircle, AlertTriangle, ArrowRight, Sparkles } from 'lucide-react';
import { clientApi, engagementApi } from '@/lib/api';
import { statusBadgeClass, formatDate } from '@/lib/utils';
import PageHeader from '@/components/layout/PageHeader';
import TopBar from '@/components/layout/TopBar';

function StatCard({ icon: Icon, label, value, color }: { icon: any; label: string; value: number | string; color: string }) {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-2xl font-bold text-ink-900">{value}</p>
        <p className="text-sm text-ink-500">{label}</p>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { data: clients = [] } = useQuery({ queryKey: ['clients'], queryFn: clientApi.list });
  const { data: engagements = [] } = useQuery({ queryKey: ['engagements'], queryFn: () => engagementApi.list() });

  const inProgress = engagements.filter(e => e.status === 'IN_PROGRESS').length;
  const complete = engagements.filter(e => e.status === 'COMPLETE').length;

  return (
    <>
      <TopBar title="Dashboard" />
      <div className="p-6 max-w-6xl">
        <PageHeader
          title="Welcome back"
          subtitle="Here's an overview of your firm's engagements"
          actions={
            <Link href="/clients/new" className="btn-primary">
              <Sparkles className="w-4 h-4" /> New Engagement
            </Link>
          }
        />

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard icon={Users} label="Active Clients" value={clients.length} color="bg-brand-50 text-brand-600" />
          <StatCard icon={FileText} label="Total Engagements" value={engagements.length} color="bg-surface-100 text-ink-600" />
          <StatCard icon={AlertTriangle} label="In Progress" value={inProgress} color="bg-warning-50 text-warning-700" />
          <StatCard icon={CheckCircle} label="Complete" value={complete} color="bg-success-50 text-success-700" />
        </div>

        {/* Recent engagements */}
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-surface-100 flex items-center justify-between">
            <h3 className="font-semibold text-ink-900">Recent Engagements</h3>
            <Link href="/clients" className="text-sm text-brand-600 hover:underline flex items-center gap-1">
              View all clients <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          {engagements.length === 0 ? (
            <div className="py-16 text-center">
              <FileText className="w-10 h-10 text-ink-300 mx-auto mb-3" />
              <p className="text-ink-500 font-medium">No engagements yet</p>
              <p className="text-sm text-ink-400 mt-1">Add a client to get started</p>
              <Link href="/clients/new" className="btn-primary mt-4">Add first client</Link>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-surface-50 border-b border-surface-100">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide">Client</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide">Year</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide">Standard</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide">Status</th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide">Updated</th>
                  <th className="px-5 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {engagements.slice(0, 10).map(eng => (
                  <tr key={eng.id} className="hover:bg-surface-50 transition-colors">
                    <td className="px-5 py-3 font-medium text-ink-900">{eng.client_name || `Client #${eng.client_id}`}</td>
                    <td className="px-5 py-3 text-ink-600">{eng.year}</td>
                    <td className="px-5 py-3"><span className="badge-blue">{eng.reporting_standard}</span></td>
                    <td className="px-5 py-3"><span className={statusBadgeClass(eng.status)}>{eng.status}</span></td>
                    <td className="px-5 py-3 text-ink-500">{formatDate(eng.updated_at)}</td>
                    <td className="px-5 py-3">
                      <Link href={`/clients/${eng.client_id}/engagements/${eng.id}`} className="btn-ghost text-xs">
                        Open <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
