'use client';
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { ChevronRight, Download, FileText, AlertTriangle, CheckCircle, XCircle, Info, ShieldCheck } from 'lucide-react';
import { validationApi, exportApi } from '@/lib/api';
import { cn } from '@/lib/utils';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';
import type { ValidationResult } from '@/types';

function SeverityIcon({ severity }: { severity: string }) {
  if (severity === 'ERROR') return <XCircle className="w-4 h-4 text-danger-500" />;
  if (severity === 'WARNING') return <AlertTriangle className="w-4 h-4 text-warning-500" />;
  return <Info className="w-4 h-4 text-brand-500" />;
}

export default function ExportPage({ params }: { params: { id: string; engId: string } }) {
  const clientId = parseInt(params.id);
  const engId = parseInt(params.engId);
  const [downloading, setDownloading] = useState<string | null>(null);

  const { data: validation, isLoading, refetch } = useQuery({
    queryKey: ['validation', engId],
    queryFn: () => validationApi.get(engId),
  });

  const runValidation = useMutation({
    mutationFn: () => validationApi.run(engId),
    onSuccess: (data) => { toast.success(`Validation complete: ${data.errors} errors, ${data.warnings} warnings`); refetch(); },
  });

  const resolve = useMutation({
    mutationFn: (id: number) => validationApi.resolve(id),
    onSuccess: () => refetch(),
  });

  async function downloadFile(type: 'word' | 'pdf') {
    setDownloading(type);
    try {
      const blob = type === 'word' ? await exportApi.word(engId) : await exportApi.pdf(engId);
      const url = URL.createObjectURL(new Blob([blob]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `financial_statements_${engId}.${type === 'word' ? 'docx' : 'pdf'}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`${type.toUpperCase()} downloaded`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || `Failed to generate ${type}`);
    } finally {
      setDownloading(null);
    }
  }

  const hasErrors = (validation?.errors || 0) > 0;

  return (
    <>
      <TopBar title="Validate & Export" />
      <div className="p-6 max-w-4xl">
        <div className="flex items-center gap-2 text-sm text-ink-500 mb-4">
          <Link href={`/clients/${clientId}/engagements/${engId}`} className="hover:text-ink-900">Engagement</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-ink-900">Export</span>
        </div>

        <PageHeader
          title="Validate & Export"
          subtitle="Run final checks and export your financial statements"
        />

        {/* Validation panel */}
        <div className="card mb-6">
          <div className="px-5 py-4 border-b border-surface-100 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-brand-600" />
              <h3 className="font-semibold text-ink-900">Validation Checks</h3>
            </div>
            <button onClick={() => runValidation.mutate()} className="btn-primary text-xs" disabled={runValidation.isPending}>
              {runValidation.isPending ? 'Running...' : 'Run Validation'}
            </button>
          </div>

          {validation ? (
            <>
              <div className="grid grid-cols-4 gap-0 border-b border-surface-100">
                {[
                  { label: 'Errors', value: validation.errors, cls: 'text-danger-700' },
                  { label: 'Warnings', value: validation.warnings, cls: 'text-warning-700' },
                  { label: 'Info', value: validation.info, cls: 'text-brand-700' },
                  { label: 'Unresolved', value: validation.unresolved, cls: 'text-ink-700' },
                ].map((item, i) => (
                  <div key={item.label} className={cn('p-4 text-center', i < 3 && 'border-r border-surface-100')}>
                    <p className={cn('text-2xl font-bold', item.cls)}>{item.value}</p>
                    <p className="text-xs text-ink-500 mt-0.5">{item.label}</p>
                  </div>
                ))}
              </div>
              <div className="divide-y divide-surface-100">
                {validation.results.filter(r => !r.is_resolved).map(result => (
                  <div key={result.id} className="px-5 py-3 flex items-start gap-3">
                    <SeverityIcon severity={result.severity} />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-ink-900">{result.message}</p>
                      {result.details && <p className="text-xs text-ink-500 mt-0.5 whitespace-pre-line">{result.details}</p>}
                    </div>
                    {result.severity !== 'ERROR' && (
                      <button onClick={() => resolve.mutate(result.id)} className="btn-ghost text-xs flex-shrink-0">
                        <CheckCircle className="w-3.5 h-3.5" /> Resolve
                      </button>
                    )}
                  </div>
                ))}
                {validation.results.filter(r => !r.is_resolved).length === 0 && (
                  <div className="py-8 text-center">
                    <CheckCircle className="w-8 h-8 text-success-500 mx-auto mb-2" />
                    <p className="text-ink-500 font-medium">All checks passed</p>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="py-10 text-center text-ink-400">
              <p>Run validation to check your financial statements before export</p>
            </div>
          )}
        </div>

        {/* Export options */}
        <div className="grid grid-cols-2 gap-4">
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-brand-50 flex items-center justify-center">
                <FileText className="w-5 h-5 text-brand-600" />
              </div>
              <div>
                <h4 className="font-semibold text-ink-900">Word Document</h4>
                <p className="text-xs text-ink-500">.docx · Editable format</p>
              </div>
            </div>
            <p className="text-sm text-ink-600 mb-4">Professional Word document with statements, notes, and firm branding. Fully editable after export.</p>
            {hasErrors && <p className="text-xs text-warning-600 mb-3">⚠ {validation?.errors} validation error{validation?.errors !== 1 ? 's' : ''} found</p>}
            <button onClick={() => downloadFile('word')} className="btn-primary w-full justify-center" disabled={downloading === 'word'}>
              <Download className="w-4 h-4" />
              {downloading === 'word' ? 'Generating...' : 'Export to Word'}
            </button>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-danger-50 flex items-center justify-center">
                <FileText className="w-5 h-5 text-danger-600" />
              </div>
              <div>
                <h4 className="font-semibold text-ink-900">PDF Document</h4>
                <p className="text-xs text-ink-500">.pdf · Print-ready format</p>
              </div>
            </div>
            <p className="text-sm text-ink-600 mb-4">Print-ready PDF with professional formatting. Ideal for client delivery and archiving.</p>
            {hasErrors && <p className="text-xs text-warning-600 mb-3">⚠ {validation?.errors} validation error{validation?.errors !== 1 ? 's' : ''} found</p>}
            <button onClick={() => downloadFile('pdf')} className="btn-secondary w-full justify-center" disabled={downloading === 'pdf'}>
              <Download className="w-4 h-4" />
              {downloading === 'pdf' ? 'Generating...' : 'Export to PDF'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
