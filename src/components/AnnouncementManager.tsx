import React, { useState } from 'react';
import { Announcement } from '../types';
import { Megaphone, Plus, Send, Trash2, RefreshCw, FileText } from 'lucide-react';

interface AnnouncementManagerProps {
  announcements: Announcement[];
  onRefresh: () => void;
}

export const AnnouncementManager: React.FC<AnnouncementManagerProps> = ({ announcements, onRefresh }) => {
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [targetRole, setTargetRole] = useState<string>('all');
  const [saving, setSaving] = useState(false);

  const handleCreate = async () => {
    if (!title || !content) return;
    setSaving(true);
    try {
      const res = await fetch('/api/announcements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, target_role: targetRole }),
      });
      if (res.ok) { setShowCreate(false); setTitle(''); setContent(''); setTargetRole('all'); onRefresh(); }
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const handleSend = async (id: number) => {
    if (!window.confirm('Kirim ke member?')) return;
    try {
      const res = await fetch(`/api/announcements/${id}/send`, { method: 'POST' });
      if (res.ok) { const data = await res.json(); alert(`Terkirim ke ${data.count} member!`); }
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Hapus?')) return;
    try { await fetch(`/api/announcements/${id}`, { method: 'DELETE' }); onRefresh(); }
    catch (e) { console.error(e); }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Megaphone className="w-5 h-5 text-rose-400" />
          Pengumuman & Informasi ke Member
        </h3>
        <div className="flex gap-2">
          <button onClick={onRefresh} className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition"><RefreshCw className="w-4 h-4" /></button>
          <button onClick={() => setShowCreate(!showCreate)} className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-sm font-medium transition">
            <Plus className="w-4 h-4" />Buat Pengumuman
          </button>
        </div>
      </div>
      {showCreate && (
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-5 space-y-4">
          <h4 className="text-sm font-semibold text-slate-200">Buat Pengumuman Baru</h4>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Judul</label>
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-rose-500 focus:outline-none" placeholder="Judul pengumuman..." />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Konten</label>
              <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={4} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-rose-500 focus:outline-none resize-none" placeholder="Tulis informasi, aturan, atau update..." />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Target</label>
              <div className="flex gap-2">
                {['all', 'member', 'admin', 'dev'].map((role) => (
                  <button key={role} onClick={() => setTargetRole(role)} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${targetRole === role ? 'bg-rose-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}>
                    {role === 'all' ? 'Semua' : role.charAt(0).toUpperCase() + role.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="flex gap-2 pt-2">
            <button onClick={handleCreate} disabled={saving || !title || !content} className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white text-sm font-medium transition">
              <FileText className="w-4 h-4" />{saving ? 'Menyimpan...' : 'Simpan'}
            </button>
            <button onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm transition">Batal</button>
          </div>
        </div>
      )}
      <div className="space-y-3">
        {announcements.length === 0 ? (
          <div className="text-center py-8 text-slate-500"><Megaphone className="w-12 h-12 mx-auto mb-3 opacity-40" /><p>Belum ada pengumuman.</p></div>
        ) : announcements.map((a) => (
          <div key={a.id} className="bg-slate-900 border border-slate-700 rounded-xl p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-medium text-slate-200">{a.title}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-700 text-slate-300">{a.target_role || 'Semua'}</span>
                </div>
                <p className="text-sm text-slate-400 line-clamp-2">{a.content}</p>
                <p className="text-xs text-slate-500 mt-1">{a.created_at}</p>
              </div>
              <div className="flex gap-2 ml-4">
                <button onClick={() => handleSend(a.id)} className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 text-xs font-medium transition"><Send className="w-3.5 h-3.5" />Kirim</button>
                <button onClick={() => handleDelete(a.id)} className="p-1.5 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-400 transition"><Trash2 className="w-3.5 h-3.5" /></button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
  };