'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Link from 'next/link';
import toast from 'react-hot-toast';
import { ChevronRight, Sparkles, BookOpen, Check, Pencil, Save, Trash2, ArrowRight } from 'lucide-react';
import { disclosureApi } from '@/lib/api';
import { cn } from '@/lib/utils';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';
import type { DisclosureNote } from '@/types';

function DisclosureEditor({ note, onSave }: { note: DisclosureNote; onSave: (id: number, content: string) => void }) {
  const [editing, setEditing] = useState(false);
  const [content, setContent] = useState(note.content || '');

  function handleSave() {
    onSave(note.id, content);
    setEditing(false);
  }

  return (
    <div className="card overflow-hidden">
      <div className="px-5 py-3 bg-surface-50 border-b border-surface-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center">
            {note.note_number}
          </span>
          <h4 className="font-semibold text-ink-900 text-sm">{note.title}</h4>
          {note.is_ai_generated && <span className="badge-blue text-xs">AI</span>}
          {note.is_approved && <span className="badge-success text-xs">Approved</span>}
        </div>
        <div className="flex items-center gap-2">
          {editing ? (
            <button onClick={handleSave} className="btn-primary text-xs"><Save className="w-3.5 h-3.5" /> Save</button>
          ) : (
            <button onClick={() => setEditing(true)} className="btn-ghost text-xs"><Pencil className="w-3.5 h-3.5" /> Edit</button>
          )}
        </div>
      </div>
      <div className="p-5">
        {editing ? (
          <textarea
            className="input font-mono text-xs"
            rows={12}
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="Enter disclosure content (HTML supported)..."
          />
        ) : (
          <div
            className="prose prose-sm max-w-none text-ink-700"
            dangerouslySetInnerHTML={{ __html: note.content || '<p class="text-ink-400">No content yet. Click Edit to add content.</p>' }}
          />
        )}
      </div>
    </div>
  );
}

export default function DisclosuresPage({ params }: { params: { id: string; engId: string } }) {
  const clientId = parseInt(params.id);
  const engId = parseInt(params.engId);
  const qc = useQueryClient();

  const { data: notes = [], isLoading } = useQuery({
    queryKey: ['disclosures', engId],
    queryFn: () => disclosureApi.list(engId),
  });

  const generate = useMutation({
    mutationFn: () => disclosureApi.generate(engId),
    onSuccess: (data) => { qc.setQueryData(['disclosures', engId], data); toast.success(`${data.length} disclosure notes generated`); },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'Generation failed'),
  });

  const updateNote = useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) => disclosureApi.update(id, { content }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['disclosures', engId] }); toast.success('Disclosure saved'); },
  });

  const approveNote = useMutation({
    mutationFn: (id: number) => disclosureApi.update(id, { is_approved: true }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['disclosures', engId] }),
  });

  return (
    <>
      <TopBar title="Disclosure Notes" />
      <div className="p-6 max-w-4xl">
        <div className="flex items-center gap-2 text-sm text-ink-500 mb-4">
          <Link href={`/clients/${clientId}/engagements/${engId}`} className="hover:text-ink-900">Engagement</Link>
          <ChevronRight className="w-3.5 h-3.5" />
          <span className="text-ink-900">Disclosures</span>
        </div>

        <PageHeader
          title="Disclosure Notes"
          subtitle={notes.length > 0 ? `${notes.length} notes · ${notes.filter(n => n.is_approved).length} approved` : 'Generate AI-drafted notes based on your mappings'}
          actions={
            <div className="flex gap-2">
              <button onClick={() => generate.mutate()} className="btn-primary" disabled={generate.isPending}>
                <Sparkles className="w-4 h-4" />
                {generate.isPending ? 'Generating...' : notes.length > 0 ? 'Regenerate' : 'Generate Notes'}
              </button>
              {notes.length > 0 && (
                <Link href={`/clients/${clientId}/engagements/${engId}/export`} className="btn-secondary">
                  Export <ArrowRight className="w-4 h-4" />
                </Link>
              )}
            </div>
          }
        />

        {isLoading ? (
          <div className="card p-12 text-center"><div className="animate-spin w-6 h-6 border-2 border-brand-500 border-t-transparent rounded-full mx-auto" /></div>
        ) : notes.length === 0 ? (
          <div className="card p-16 text-center">
            <BookOpen className="w-12 h-12 text-ink-300 mx-auto mb-3" />
            <p className="font-medium text-ink-700">No disclosure notes yet</p>
            <p className="text-sm text-ink-400 mt-1">AI will automatically draft notes based on your account mappings</p>
            <button onClick={() => generate.mutate()} className="btn-primary mt-4" disabled={generate.isPending}>
              <Sparkles className="w-4 h-4" /> Generate Disclosure Notes
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {notes.sort((a, b) => a.order - b.order).map(note => (
              <div key={note.id}>
                <DisclosureEditor
                  note={note}
                  onSave={(id, content) => updateNote.mutate({ id, content })}
                />
                {!note.is_approved && (
                  <div className="mt-2 flex justify-end">
                    <button onClick={() => approveNote.mutate(note.id)} className="btn-ghost text-xs text-success-700">
                      <Check className="w-3.5 h-3.5" /> Approve note
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
