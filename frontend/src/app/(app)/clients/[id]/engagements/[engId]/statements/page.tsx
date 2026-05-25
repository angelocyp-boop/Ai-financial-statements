'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { ChevronRight, Sparkles, CheckCircle, FileText, ArrowRight } from 'lucide-react';
import { statementApi } from '@/lib/api';
import { cn, formatNumber } from '@/lib/utils';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';
import type { FinancialStatement, StatementLine } from '@/types';

const STMT_LABELS: Record<string, string> = {
  SFP: 'Statement of Financial Position',
  PL: 'Statement of Profit or Loss',
  CASH_FLOW: 'Statement of Cash Flows',
  EQUITY: 'Statement of Changes in Equity',
};

function StatementTable({ stmt, engYear, compYear }: { stmt: FinancialStatement; engYear?: number; compYear?: number }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b-2 border-ink-900">
            <th className="text-left py-2 font-semibold text-ink-900 pr-4"></th>
            <th className="text-right py-2 font-semibold text-ink-900 w-32">{engYear || 'Current'}</th>
            <th className="text-right py-2 font-semibold text-ink-900 w-32">{compYear || 'Prior'}</th>
            <th className="w-12 text-center py-2 text-xs text-ink-400">Note</th>
          </tr>
        </thead>
        <tbody>
          {stmt.lines.map(line => (
            <tr key={line.id} className={cn(
              'border-b border-surface-100',
              line.is_header && 'bg-surface-50',
              line.is_total && 'border-t-2 border-ink-900',
            )}>
              <td className={cn(
                'py-1.5 pr-4',
                line.indent_level > 0 && `pl-${line.indent_level * 4}`,
                line.is_header && 'font-bold text-ink-900 uppercase tracking-wide text-xs pt-3',
                line.is_total && 'font-bold text-ink-900',
                line.is_subtotal && 'font-semibold text-ink-800',
                !line.is_header && !line.is_total && !line.is_subtotal && 'text-ink-700',
                line.indent_level === 1 && 'pl-4',
                line.indent_level === 2 && 'pl-8',
              )}>
                {line.label}
              </td>
              <td className={cn(
                'text-right py-1.5 font-mono w-32 tabular-nums',
                line.is_header ? 'text-ink-400 text-xs' : 'text-ink-900',
                (line.is_total || line.is_subtotal) && 'font-bold',
              )}>
                {line.is_header ? (engYear || 'EUR') : formatNumber(line.current_amount)}
              </td>
              <td className={cn(
                'text-right py-1.5 font-mono w-32 tabular-nums text-ink-500',
                line.is_header ? 'text-ink-400 text-xs' : '',
                (line.is_total || line.is_subtotal) && 'font-semibold',
              )}>
                {line.is_header ? (compYear || 'EUR') : formatNumber(line.comparative_amount)}
              </td>
              <td className="text-center py-1.5 text-xs text-brand-600 w-12">
                {line.note_reference && `Note ${line.note_reference}`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function StatementsPage({ params }: { params: { id: string; engId: string } }) {
  const clientId = parseInt(params.id);
  const engId = parseInt(params.engId);
  const qc = useQueryClient();
  const [activeStmt, setActiveStmt] = useState<string>('SFP');

  const { data: stmts = [], isLoading } = useQuery({
    queryKey: ['statements', engId],
    queryFn: () => statementApi.list(engId),
  });

  const generate = useMutation({
    mutationFn: () => statementApi.generate(engId),
    onSuccess: (data) => {
      qc.setQueryData(['statements', engId], data);
      toast.success('Financial statements generated');
      if (data.length > 0) setActiveStmt(data[0].statement_type);
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'Generation failed'),
  });

  const approve = useMutation({
    mutationFn: (id: number) => statementApi.approve(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['statements', engId] }); toast.success('Statement approved'); },
  });

  const activeStatement = stmts.find(s => s.statement_type === activeStmt);

  return (
    <>
      <TopBar title="Financial Statements" />
      <div className="p-6 max-w-5xl">
        <div className="flex items-center gap-2 text-sm text-ink-500 mb-4">
          <Link href={`/clients/${clientId}/engagements/${engId}`} className="hover:text-ink-900">Engagement</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-ink-900">Financial Statements</span>
        </div>

        <PageHeader
          title="Financial Statements"
          subtitle="IFRS-compliant statements generated from your mapped trial balance"
          actions={
            <div className="flex gap-2">
              <button onClick={() => generate.mutate()} className="btn-primary" disabled={generate.isPending}>
                <Sparkles className="w-4 h-4" />
                {generate.isPending ? 'Generating...' : stmts.length > 0 ? 'Regenerate' : 'Generate Statements'}
              </button>
              {stmts.length > 0 && (
                <Link href={`/clients/${clientId}/engagements/${engId}/disclosures`} className="btn-secondary">
                  Next: Disclosures <ArrowRight className="w-4 h-4" />
                </Link>
              )}
            </div>
          }
        />

        {stmts.length === 0 && !isLoading ? (
          <div className="card p-16 text-center">
            <FileText className="w-12 h-12 text-ink-300 mx-auto mb-3" />
            <p className="font-medium text-ink-700">No statements generated yet</p>
            <p className="text-sm text-ink-400 mt-1">Complete AI mapping first, then generate IFRS statements</p>
            <button onClick={() => generate.mutate()} className="btn-primary mt-4" disabled={generate.isPending}>
              <Sparkles className="w-4 h-4" /> Generate Statements
            </button>
          </div>
        ) : (
          <>
            {/* Statement tabs */}
            <div className="flex gap-1 mb-4 p-1 bg-surface-100 rounded-lg w-fit">
              {['SFP', 'PL', 'CASH_FLOW', 'EQUITY'].map(type => {
                const exists = stmts.find(s => s.statement_type === type);
                return (
                  <button
                    key={type}
                    onClick={() => setActiveStmt(type)}
                    className={cn(
                      'px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                      activeStmt === type ? 'bg-white text-ink-900 shadow-sm' : 'text-ink-500 hover:text-ink-700',
                    )}
                  >
                    {type}
                    {exists?.is_approved && <CheckCircle className="w-3 h-3 inline ml-1 text-success-500" />}
                  </button>
                );
              })}
            </div>

            {activeStatement ? (
              <div className="card">
                <div className="px-6 py-4 border-b border-surface-100 flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-ink-900">{STMT_LABELS[activeStmt]}</h3>
                    <p className="text-xs text-ink-500 mt-0.5">v{activeStatement.version} · Generated {new Date(activeStatement.generated_at).toLocaleDateString()}</p>
                  </div>
                  {!activeStatement.is_approved ? (
                    <button onClick={() => approve.mutate(activeStatement.id)} className="btn-secondary text-xs">
                      <CheckCircle className="w-3.5 h-3.5" /> Approve
                    </button>
                  ) : (
                    <span className="badge-success"><CheckCircle className="w-3 h-3" /> Approved</span>
                  )}
                </div>
                <div className="p-6">
                  <StatementTable stmt={activeStatement} />
                </div>
              </div>
            ) : (
              <div className="card p-8 text-center text-ink-400">
                <p>This statement type has not been generated yet.</p>
                <button onClick={() => generate.mutate()} className="btn-primary mt-3">
                  <Sparkles className="w-4 h-4" /> Generate
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
}
