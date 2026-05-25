'use client';
import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useDropzone } from 'react-dropzone';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { Upload, FileSpreadsheet, CheckCircle, XCircle, Loader2, ChevronRight, RefreshCw, ArrowRight } from 'lucide-react';
import { tbApi } from '@/lib/api';
import { cn, statusBadgeClass, formatNumber, confidenceColor } from '@/lib/utils';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';
import type { TrialBalance } from '@/types';

function TBStatusIcon({ status }: { status: string }) {
  if (status === 'PROCESSED') return <CheckCircle className="w-4 h-4 text-success-600" />;
  if (status === 'ERROR') return <XCircle className="w-4 h-4 text-danger-600" />;
  if (status === 'PROCESSING' || status === 'PENDING') return <Loader2 className="w-4 h-4 text-brand-500 animate-spin" />;
  return null;
}

export default function TrialBalancePage({ params }: { params: { id: string; engId: string } }) {
  const clientId = parseInt(params.id);
  const engId = parseInt(params.engId);
  const qc = useQueryClient();
  const [isComparative, setIsComparative] = useState(false);
  const [selectedTb, setSelectedTb] = useState<TrialBalance | null>(null);

  const { data: tbs = [], isLoading, refetch } = useQuery({
    queryKey: ['tbs', engId],
    queryFn: () => tbApi.listForEngagement(engId),
    refetchInterval: (data) => data?.some(t => t.status === 'PROCESSING' || t.status === 'PENDING') ? 3000 : false,
  });

  const upload = useMutation({
    mutationFn: (file: File) => tbApi.upload(engId, file, isComparative),
    onSuccess: () => { toast.success('Trial balance uploaded - processing...'); qc.invalidateQueries({ queryKey: ['tbs', engId] }); },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'Upload failed'),
  });

  const onDrop = useCallback((files: File[]) => {
    if (files[0]) upload.mutate(files[0]);
  }, [upload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'], 'text/csv': ['.csv'] },
    multiple: false,
  });

  const selectedFull = useQuery({
    queryKey: ['tb', selectedTb?.id],
    queryFn: () => tbApi.get(selectedTb!.id),
    enabled: !!selectedTb,
  });

  return (
    <>
      <TopBar title="Trial Balance" />
      <div className="p-6 max-w-6xl">
        <div className="flex items-center gap-2 text-sm text-ink-500 mb-4">
          <Link href={`/clients/${clientId}/engagements/${engId}`} className="hover:text-ink-900">Engagement</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-ink-900">Trial Balance</span>
        </div>

        <PageHeader
          title="Trial Balance"
          subtitle="Upload your trial balance to begin IFRS mapping"
          actions={
            <button onClick={() => refetch()} className="btn-secondary"><RefreshCw className="w-4 h-4" /></button>
          }
        />

        {/* Upload zone */}
        <div className="mb-6">
          <div className="flex items-center gap-4 mb-3">
            <label className="flex items-center gap-2 text-sm text-ink-700 cursor-pointer">
              <input type="checkbox" className="rounded" checked={isComparative} onChange={e => setIsComparative(e.target.checked)} />
              This is a comparative (prior year) trial balance
            </label>
          </div>
          <div
            {...getRootProps()}
            className={cn(
              'border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors',
              isDragActive ? 'border-brand-500 bg-brand-50' : 'border-surface-200 hover:border-brand-300 hover:bg-surface-50',
              upload.isPending && 'opacity-50 pointer-events-none',
            )}
          >
            <input {...getInputProps()} />
            <FileSpreadsheet className="w-10 h-10 text-ink-300 mx-auto mb-3" />
            {upload.isPending ? (
              <p className="text-ink-500">Uploading...</p>
            ) : isDragActive ? (
              <p className="text-brand-600 font-medium">Drop your trial balance here</p>
            ) : (
              <>
                <p className="font-medium text-ink-700">Drag & drop your trial balance</p>
                <p className="text-sm text-ink-400 mt-1">or <span className="text-brand-600">browse files</span> · .xlsx, .xls, .csv supported</p>
              </>
            )}
          </div>
        </div>

        {/* Uploaded TBs */}
        {tbs.length > 0 && (
          <div className="card overflow-hidden mb-6">
            <div className="px-5 py-3 bg-surface-50 border-b border-surface-100">
              <p className="text-sm font-semibold text-ink-700">Uploaded Trial Balances</p>
            </div>
            {tbs.map(tb => (
              <div key={tb.id} className="px-5 py-4 border-b border-surface-100 last:border-0 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <TBStatusIcon status={tb.status} />
                  <div>
                    <p className="font-medium text-ink-900 text-sm">{tb.filename}</p>
                    <p className="text-xs text-ink-500">{tb.row_count} accounts · {tb.mapped_count} mapped{tb.is_comparative ? ' · Comparative' : ''}</p>
                    {tb.error_message && <p className="text-xs text-danger-600 mt-0.5">{tb.error_message}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={statusBadgeClass(tb.status)}>{tb.status}</span>
                  {tb.status === 'PROCESSED' && (
                    <button onClick={() => setSelectedTb(selectedTb?.id === tb.id ? null : tb)} className="btn-ghost text-xs">
                      {selectedTb?.id === tb.id ? 'Hide' : 'View lines'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* TB Lines table */}
        {selectedTb && selectedFull.data && (
          <div className="card overflow-hidden">
            <div className="px-5 py-3 bg-surface-50 border-b border-surface-100 flex items-center justify-between">
              <p className="text-sm font-semibold text-ink-700">
                Lines — {selectedFull.data.lines.filter(l => !l.is_excluded).length} accounts
              </p>
              <Link href={`/clients/${clientId}/engagements/${engId}/mapping`} className="btn-primary text-xs">
                Proceed to AI Mapping <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="bg-surface-50 border-b border-surface-100">
                  <tr>
                    <th className="text-left px-4 py-2.5 font-semibold text-ink-500 uppercase tracking-wide">Code</th>
                    <th className="text-left px-4 py-2.5 font-semibold text-ink-500 uppercase tracking-wide">Account Name</th>
                    <th className="text-right px-4 py-2.5 font-semibold text-ink-500 uppercase tracking-wide">Balance</th>
                    <th className="text-left px-4 py-2.5 font-semibold text-ink-500 uppercase tracking-wide">IFRS Category</th>
                    <th className="text-center px-4 py-2.5 font-semibold text-ink-500 uppercase tracking-wide">Confidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-100">
                  {selectedFull.data.lines.filter(l => !l.is_excluded).map(line => (
                    <tr key={line.id} className="hover:bg-surface-50">
                      <td className="px-4 py-2.5 text-ink-500 font-mono">{line.account_code || '-'}</td>
                      <td className="px-4 py-2.5 text-ink-900 font-medium max-w-xs truncate">{line.account_name}</td>
                      <td className="px-4 py-2.5 text-right font-mono">{formatNumber(line.balance)}</td>
                      <td className="px-4 py-2.5">
                        {line.ifrs_category ? (
                          <span className="badge-blue">{line.ifrs_category.replace(/_/g, ' ')}</span>
                        ) : (
                          <span className="badge-danger">Unmapped</span>
                        )}
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        {line.mapping_confidence ? (
                          <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium', confidenceColor(line.mapping_confidence))}>
                            {(parseFloat(line.mapping_confidence) * 100).toFixed(0)}%
                          </span>
                        ) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
