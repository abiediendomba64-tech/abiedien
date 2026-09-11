import React, { useState } from 'react';
import { PanelAccount, User } from '../types';
import { KeyRound, Plus, Send, RefreshCw, Trash2, Copy, Globe, User as UserIcon } from 'lucide-react';

interface PanelManagerProps {
  panels: PanelAccount[];
  users: User[];
  onRefresh: () => void;
}

export const PanelManager: React.FC<PanelManagerProps> = ({ panels, users, onRefresh }) => {
  const [showCreate, setShowCreate] = useState(false);
  const [selectedUser, setSelectedUser] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [saving, setSaving] = useState(false);

  const handleCreate = async () => {
    if (!selectedUser) return;
    setSaving(true);
    try {
      const res = await fetch('/api/panel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: parseInt(selectedUser), username: username || null, password: password || null }),
      });
      if (res.ok) { setShowCreate(false); setSelectedUser(''); setUsername(''); setPassword(''); onRefresh(); }
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const handleSendPassword = async (id: number) => {
    if (!window.confirm('Kirim password ke member?')) return;
    try { await fetch(`/api/panel/${id}/send`, { method: 'POST' }); alert('Password terkirim!'); }
    catch (e) { console.error(e); }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Hapus akun panel?')) return;
    try { await fetch(`/api/panel/${id}`, { method: 'DELETE' }); onRefresh(); }
    catch (e) { console.error(e); }
  };

  const handleResetPassword = async (id: number) => {
    if (!window.confirm('Reset password?')) return;
    try { await fetch(`/api/panel/${id}/reset`, { method: 'POST' }); onRefresh(); }
    catch (e) { console.error(e); }
  };


  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <KeyRound className="w-5 h-5 text-amber-400" />
          Manajemen Panel Backoffice
        </h3>
        <div className="flex gap-2">
          <button onClick={onRefresh} className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={() => setShowCreate(!showCreate)} className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium transition">
            <Plus className="w-4 h-4" />Buat Akun
          </button>
        </div>
      </div>
      {showCreate && (
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-5 space-y-4">
          <h4 className="text-sm font-semibold text-slate-200">Buat Akun Panel Baru</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Member</label>
              <select value={selectedUser} onChange={(e) => setSelectedUser(e.target.value)} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-amber-500 focus:outline-none">
                <option value="">Pilih member...</option>
                {users.filter(u => u.domain_verified).map((u) => (
                  <option key={u.telegram_id} value={u.telegram_id}>{u.full_name} | {u.domain_name || 'No domain'}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Username</label>
              <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-amber-500 focus:outline-none" placeholder="auto jika kosong" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Password</label>
              <input type="text" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-amber-500 focus:outline-none" placeholder="auto jika kosong" />
            </div>
          </div>
          <div className="flex gap-2 pt-2">
            <button onClick={handleCreate} disabled={saving || !selectedUser} className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white text-sm font-medium transition">
              <Plus className="w-4 h-4" />{saving ? 'Membuat...' : 'Buat & Kirim'}
            </button>
            <button onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm transition">Batal</button>
          </div>
        </div>
      )}
      <div className="space-y-3">
        {panels.length === 0 ? (
          <div className="text-center py-8 text-slate-500"><KeyRound className="w-12 h-12 mx-auto mb-3 opacity-40" /><p>Belum ada akun panel.</p></div>
        ) : panels.map((p) => (
          <div key={p.id} className="bg-slate-900 border border-slate-700 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-sky-400" />
                  <span className="font-medium text-slate-200 font-mono">{p.domain}</span>
                  <span className="text-slate-500">/</span>
                  <span className="text-slate-400 text-sm">{p.panel_url}</span>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1"><UserIcon className="w-3 h-3" />{p.full_name || `User#${p.user_id}`}</span>
                  <span>User: <span className="text-slate-300 font-mono">{p.panel_username}</span></span>
                  <span className="flex items-center gap-1">Pass: <span className="text-slate-300 font-mono">{p.panel_password}</span>
                    <button onClick={() => copyToClipboard(p.panel_password)} className="p-0.5 hover:bg-slate-700 rounded"><Copy className="w-3 h-3 text-slate-500" /></button>
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${p.status === 'active' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'}`}>{p.status}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => handleSendPassword(p.id)} className="p-1.5 rounded-lg bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 transition" title="Kirim password"><Send className="w-3.5 h-3.5" /></button>
                <button onClick={() => handleResetPassword(p.id)} className="p-1.5 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 text-amber-400 transition" title="Reset password"><RefreshCw className="w-3.5 h-3.5" /></button>
                <button onClick={() => handleDelete(p.id)} className="p-1.5 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-400 transition" title="Hapus"><Trash2 className="w-3.5 h-3.5" /></button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
  const copyToClipboard = (text: string) => { navigator.clipboard.writeText(text); };