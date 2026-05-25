'use client';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { ChevronRight, Upload, Cpu, FileText, BookOpen, ShieldCheck, Download, CheckCircle } from 'lucide-react';
import { engagementApi, tbApi, statementApi, validationApi } from '@/lib/api';
import { statusBadgeClass, formatDate } from '@/lib/utils';
import TopBar from '@/components/layout/TopBar';

const STEPS = [
  { key: 'trial-balance', label: 'Trial Balance', icon: Upload, desc: 'Import and review trial balance data' },
  { key: 'mapping', label: 'AI Mapping', icon: Cpu, desc: 'Auto-classify accounts to IFRS categories' },
  { key: 'statements', label: 'Statements', icon: FileText, desc: 'Generate IFRS financial statements' },
  { key: 'disclosures', label: 'Disclosures', icon: BookOpen, desc: 'Review and edit disclosure notes' },
  { key: 'export', label: 'Export', icon: Download, desc: 'Export to Word and PDF' },
];

export default function EngagementPage({ params }: { params: { id: string; engId: string } }) {
  const clientId = parseInt(params.id);
  const engId = parseInt(params.engId);
  const { data: eng } = useQuery({ queryKey: ['engagement', engId], queryFn: () => engagementApi.get(engId) });
  const { data: tbs = [] } = useQuery({ queryKey: ['tbs', engId], queryFn: () => tbApi.listForEngagement(engId) });
  const { data: stmts = [] } = useQuery({ queryKey: ['statements', engId], queryFn: () => statementApi.list(engId) });
  const { data: validation } = useQuery({ queryKey: ['validation', engId], queryFn: () => validationApi.get(engId) });

  if (!eng) return <div className="p-8 text-center text-ink-500">Loading...</div>;

  const hasTB = tbs.length > 0 && tbs.some(t => t.status === 'PROCESSED');
  const hasStmts = stmts.length > 0;
  const stepStatus = {
    'trial-balance': hasTB ? 'complete' : 'pending',
    'mapping': hasTB ? 'complete' : 'pending',
    'statements': hasStmts ? 'complete' : 'pending',
    'disclosures': 'pending',
    'export': 'pending',
  } as Record<string, string>;

  return (
    <>
      <TopBar title={`Engagement ${eng.year}`} />
      <div className="p-6 max-w-4xl">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-ink-500 mb-4">
          <Link href="/clients" className="hover:text-ink-900">Clients</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <Link href={`/clients/${clientId}`} className="hover:text-ink-900">{eng.client_name || `Client ${clientId}`}</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-ink-900">Year {eng.year}</span>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-ink-900">Financial Year {eng.year}</h2>
            <p className="text-sm text-ink-500 mt-0.5">{eng.period_start} → {eng.period_end} · {eng.reporting_standard} · {eng.currency}</p>
          </div>
          <span className={`${statusBadgeClass(eng.status)} text-sm px-3 py-1`}>{eng.status.replace('_', ' ')}</span>
        </div>

        {/* Validation alerts */}
        {validation && validation.errors > 0 && (
          <div className="mb-4 p-4 bg-danger-50 border border-danger-200 rounded-lg">
            <p className="text-danger-700 font-medium text-sm">⚠️ {validation.errors} validation error{validation.errors !== 1 ? 's' : ''} found</p>
            <Link href={`/clients/${clientId}/engagements/${engId}/export`} className="text-sm text-danger-600 underline mt-1 inline-block">View details</Link>
          </div>
        )}

        {/* Workflow steps */}
        <div className="grid grid-cols-1 gap-3">
          {STEPS.map((step, idx) => {
            const status = stepStatus[step.key];
            return (
              <Link
                key={step.key}
                href={`/clients/${clientId}/engagements/${engId}/${step.key}`}
                className="card px-5 py-4 flex items-center gap-4 hover:shadow-md transition-shadow group"
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  status === 'complete' ? 'bg-success-50' : 'bg-surface-100'
                }`}>
                  {status === 'complete'
                    ? <CheckCircle className="w-5 h-5 text-success-600" />
                    : <step.icon className="w-5 h-5 text-ink-500" />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-ink-900">{idx + 1}. {step.label}</span>
                    {status === 'complete' && <span className="badge-success">Done</span>}
                  </div>
                  <p className="text-sm text-ink-500 mt-0.5">{step.desc}</p>
                </div>
                <ChevronRight className="w-4 h-4 text-ink-400 group-hover:translate-x-0.5 transition-transform" />
              </Link>
            );
          })}
        </div>
      </div>
    </>
  );
}
