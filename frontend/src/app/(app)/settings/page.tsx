'use client';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { firmApi } from '@/lib/api';
import { useAuthStore } from '@/lib/auth';
import TopBar from '@/components/layout/TopBar';
import PageHeader from '@/components/layout/PageHeader';

export default function SettingsPage() {
  const qc = useQueryClient();
  const user = useAuthStore(s => s.user);
  const { data: firm } = useQuery({ queryKey: ['firm'], queryFn: firmApi.getMyFirm });
  const { data: users = [] } = useQuery({ queryKey: ['firm-users'], queryFn: firmApi.getUsers });
  const [firmForm, setFirmForm] = useState({ name: firm?.name || '', email: firm?.email || '' });
  const [inviteForm, setInviteForm] = useState({ email: '', first_name: '', last_name: '', role: 'ACCOUNTANT', password: '' });
  const [showInvite, setShowInvite] = useState(false);

  const updateFirm = useMutation({
    mutationFn: () => firmApi.updateFirm(firmForm),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['firm'] }); toast.success('Firm settings saved'); },
  });

  const inviteUser = useMutation({
    mutationFn: () => firmApi.inviteUser(inviteForm),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['firm-users'] }); toast.success('User invited'); setShowInvite(false); },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'Failed'),
  });

  return (
    <>
      <TopBar title="Settings" />
      <div className="p-6 max-w-3xl">
        <PageHeader title="Settings" subtitle="Manage your firm account and team" />

        {/* Firm settings */}
        <div className="card p-6 mb-6">
          <h3 className="font-semibold text-ink-900 mb-4">Firm Profile</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="label">Firm name</label>
              <input className="input" value={firmForm.name || firm?.name || ''} onChange={e => setFirmForm(f => ({ ...f, name: e.target.value }))} />
            </div>
            <div>
              <label className="label">Email</label>
              <input type="email" className="input" value={firmForm.email || firm?.email || ''} onChange={e => setFirmForm(f => ({ ...f, email: e.target.value }))} />
            </div>
          </div>
          <button onClick={() => updateFirm.mutate()} className="btn-primary mt-4" disabled={updateFirm.isPending}>
            {updateFirm.isPending ? 'Saving...' : 'Save changes'}
          </button>
        </div>

        {/* Team */}
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-surface-100 flex items-center justify-between">
            <h3 className="font-semibold text-ink-900">Team Members ({users.length})</h3>
            {user?.role === 'ADMIN' && (
              <button onClick={() => setShowInvite(s => !s)} className="btn-primary text-xs">Invite user</button>
            )}
          </div>

          {showInvite && (
            <div className="px-5 py-4 bg-surface-50 border-b border-surface-100">
              <div className="grid grid-cols-2 gap-3">
                <div><label className="label">First name</label><input className="input" value={inviteForm.first_name} onChange={e => setInviteForm(f => ({ ...f, first_name: e.target.value }))} /></div>
                <div><label className="label">Last name</label><input className="input" value={inviteForm.last_name} onChange={e => setInviteForm(f => ({ ...f, last_name: e.target.value }))} /></div>
                <div><label className="label">Email</label><input type="email" className="input" value={inviteForm.email} onChange={e => setInviteForm(f => ({ ...f, email: e.target.value }))} /></div>
                <div><label className="label">Password</label><input type="password" className="input" value={inviteForm.password} onChange={e => setInviteForm(f => ({ ...f, password: e.target.value }))} /></div>
                <div>
                  <label className="label">Role</label>
                  <select className="input" value={inviteForm.role} onChange={e => setInviteForm(f => ({ ...f, role: e.target.value }))}>
                    <option value="ACCOUNTANT">Accountant</option>
                    <option value="VIEWER">Viewer</option>
                    <option value="ADMIN">Admin</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-2 mt-3">
                <button onClick={() => inviteUser.mutate()} className="btn-primary text-xs" disabled={inviteUser.isPending}>
                  {inviteUser.isPending ? 'Inviting...' : 'Add user'}
                </button>
                <button onClick={() => setShowInvite(false)} className="btn-secondary text-xs">Cancel</button>
              </div>
            </div>
          )}

          <div className="divide-y divide-surface-100">
            {users.map((u: any) => (
              <div key={u.id} className="px-5 py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 text-xs font-bold">
                    {u.first_name?.[0]?.toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-ink-900 text-sm">{u.first_name} {u.last_name}</p>
                    <p className="text-xs text-ink-500">{u.email}</p>
                  </div>
                </div>
                <span className="badge-neutral">{u.role}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
