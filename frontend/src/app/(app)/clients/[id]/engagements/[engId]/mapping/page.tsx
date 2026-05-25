'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { ChevronRight, Cpu, RefreshCw, CheckCircle, ArrowRight, AlertCircle } from 'lucide-react';
import { tbApi } from '@/lib/api';
import { cn, formatNumber, confidenceColor } from '@/lib/utils';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';
import type { TBLine } from '@/types';

const IFRS_CATEGORIES = [
  'PPE', 'RIGHT_OF_USE', 'INTANGIBLES', 'GOODWILL', 'INVESTMENTS_ASSOCIATES',
  'FINANCIAL_ASSETS_NC', 'DEFERRED_TAX_ASSET', 'OTHER_NC_ASSETS',
  'INVENTORIES', 'TRADE_RECEIVABLES', 'PREPAYMENTS', 'FINANCIAL_ASSETS_C', 'CASH', 'OTHER_C_ASSETS',
  'BORROWINGS_NC', 'LEASE_LIABILITIES_NC', 'DEFERRED_TAX_LIABILITY', 'EMPLOYEE_OBLIGATIONS', 'OTHER_NC_LIABILITIES',
  'TRADE_PAYABLES', 'BORROWINGS_C', 'LEASE_LIABILITIES_C', 'TAX_PAYABLE', 'ACCRUALS', 'OTHER_C_LIABILITIES',
  'SHARE_CAPITAL', 'SHARE_PREMIUM', 'RETAINED_EARNINGS', 'OTHER_RESERVES',
  'REVENUE', 'COST_OF_SALES', 'OTHER_INCOME', 'DISTRIBUTION_COSTS', 'ADMIN_EXPENSES',
  'OTHER_OP_EXPENSES', 'FINANCE_INCOME', 'FINANCE_COSTS', 'INCOME_TAX', 'OCI',
];

function ConfidenceBadge({ confidence }: { confidence: string | null }) {
  if (!confidence) return <span className="badge-danger">Unmapped</span>;
  const val = parseFloat(confidence);
  return (
    <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', confidenceColor(val))}>
      {(val * 100).toFixed(0)}% {val >= 0.85 ? '✓' : val >= 0.6 ? '~' : '?'}
    </span>
  );
}

export default function MappingPage({ params }: { params: { id: string; engId: string } }) {
  const clientId = parseInt(params.id);
  const engId = parseInt(params.engId);
  const qc = useQueryClient();
  const [editingLine, setEditingLine] = useState<number | null>(null);
  const [filter, setFilter] = useState<'all' | 'low' | 'unmapped'>('all');

  const { data: tbs = [] } = useQuery({ queryKey: ['tbs', engId], queryFn: () => tbApi.listForEngagement(engId) });
  const processedTb = tbs.find(t => t.status === 'PROCESSED' && !t.is_comparative);

  const { data: tbDetail, isLoading } = useQuery({
    queryKey: ['tb', processedTb?.id],
    queryFn: () => tbApi.get(processedTb!.id),
    enabled: !!processedTb,
  });

  const updateLine = useMutation({
    mutationFn: ({ lineId, data }: { lineId: number; data: Partial<TBLine> }) => tbApi.updateLine(lineId, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['tb', processedTb?.id] }); toast.success('Mapping updated'); setEditingLine(null); },
    onError: () => toast.error('Failed to update'),
  });

  const rerunMapping = useMutation({
    mutationFn: () => tbApi.runMapping(processedTb!.id),
    onSuccess: () => { toast.success('AI mapping started'); setTimeout(() => qc.invalidateQueries({ queryKey: ['tb', processedTb?.id] }), 3000); },
  });

  const lines = tbDetail?.lines.filter(l => !l.is_excluded) || [];
  const filtered = lines.filter(l => {
    if (filter === 'unmapped') return !l.ifrs_category;
    if (filter === 'low') return l.mapping_confidence && parseFloat(l.mapping_confidence) < 0.7;
    return true;
  });

  const unmappedCount = lines.filter(l => !l.ifrs_category).length;
  const lowConfCount = lines.filter(l => l.mapping_confidence && parseFloat(l.mapping_confidence) < 0.7).length;

  if (!processedTb) return (
    <div className="p-6">
      <div className="card p-12 text-center">
        <AlertCircle className="w-10 h-10 text-warning-500 mx-auto mb-3" />
        <p className="font-medium text-ink-700">No processed trial balance found</p>
        <Link href={`/clients/${clientId}/engagements/${engId}/trial-balance`} className="btn-primary mt-4">Upload Trial Balance</Link>
      </div>
    </div>
  );

  return (
    <>
      <TopBar title="AI Account Mapping" />
      <div className="p-6 max-w-7xl">
        <div className="flex items-center gap-2 text-sm text-ink-500 mb-4">
          <Link href={`/clients/${clientId}/engagements/${engId}`} className="hover:text-ink-900">Engagement</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-ink-900">AI Mapping</span>
        </div>

        <PageHeader
          title="AI Account Mapping"
          subtitle={`${lines.length} accounts · ${unmappedCount} unmapped · ${lowConfCount} low confidence`}
          actions={
            <div className="flex gap-2">
              <button onClick={() => rerunMapping.mutate()} className="btn-secondary" disabled={rerunMapping.isPending}>
                <Cpu className="w-4 h-4" /> {rerunMapping.isPending ? 'Running AI...' : 'Re-run AI'}
              </button>
              <Link href={`/clients/${clientId}/engagements/${engId}/statements`} className="btn-primary">
                Generate Statements <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          }
        />

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-5">
          <button onClick={() => setFilter('all')} className={cn('card p-4 text-left hover:shadow-sm transition-shadow', filter === 'all' && 'ring-2 ring-brand-500')}>
            <p className="text-2xl font-bold text-ink-900">{lines.length}</p>
            <p className="text-sm text-ink-500">Total accounts</p>
          </button>
          <button onClick={() => setFilter('low')} className={cn('card p-4 text-left hover:shadow-sm transition-shadow', filter === 'low' && 'ring-2 ring-warning-500')}>
            <p className="text-2xl font-bold text-warning-700">{lowConfCount}</p>
            <p className="text-sm text-ink-500">Low confidence</p>
          </button>
          <button onClick={() => setFilter('unmapped')} className={cn('card p-4 text-left hover:shadow-sm transition-shadow', filter === 'unmapped' && 'ring-2 ring-danger-500')}>
            <p className="text-2xl font-bold text-danger-700">{unmappedCount}</p>
            <p className="text-sm text-ink-500">Unmapped</p>
          </button>
        </div>

        {/* Mapping table */}
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-surface-50 border-b border-surface-100">
                <tr>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide w-24">Code</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide">Account Name</th>
                  <th className="text-right px-4 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide w-32">Balance</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide w-56">IFRS Category</th>
                  <th className="text-center px-4 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide w-28">Confidence</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-ink-500 uppercase tracking-wide">AI Explanation</th>
                  <th className="w-20"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {isLoading ? (
                  <tr><td colSpan={7} className="py-10 text-center text-ink-400">Loading mappings...</td></tr>
                ) : filtered.map(line => (
                  <tr key={line.id} className={cn('hover:bg-surface-50', line.is_manually_mapped && 'bg-brand-50/30')}>
                    <td className="px-4 py-2.5 font-mono text-xs text-ink-500">{line.account_code || '-'}</td>
                    <td className="px-4 py-2.5 font-medium text-ink-900 max-w-xs">
                      <span className="truncate block">{line.account_name}</span>
                      {line.is_manually_mapped && <span className="text-xs text-brand-500">manually mapped</span>}
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-ink-700">{formatNumber(line.balance)}</td>
                    <td className="px-4 py-2.5">
                      {editingLine === line.id ? (
                        <select
                          className="input text-xs py-1"
                          defaultValue={line.ifrs_category || ''}
                          autoFocus
                          onChange={e => updateLine.mutate({ lineId: line.id, data: { ifrs_category: e.target.value, is_manually_mapped: true } })}
                          onBlur={() => setEditingLine(null)}
                        >
                          <option value="">-- Select category --</option>
                          {IFRS_CATEGORIES.map(c => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
                        </select>
                      ) : (
                        <button onClick={() => setEditingLine(line.id)} className="text-left">
                          {line.ifrs_category ? (
                            <span className="badge-blue">{line.ifrs_category.replace(/_/g, ' ')}</span>
                          ) : (
                            <span className="badge-danger">Click to map</span>
                          )}
                        </button>
                      )}
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      <ConfidenceBadge confidence={line.mapping_confidence} />
                    </td>
                    <td className="px-4 py-2.5 text-xs text-ink-500 max-w-xs">
                      <span className="truncate block">{line.mapping_explanation || '-'}</span>
                    </td>
                    <td className="px-4 py-2.5">
                      {line.ifrs_category && <CheckCircle className="w-4 h-4 text-success-500" />}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
