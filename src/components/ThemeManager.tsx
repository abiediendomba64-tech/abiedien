import React, { useState } from 'react';
import { Theme } from '../types';
import { Palette, Plus, Check, Trash2, Globe, Save, RefreshCw } from 'lucide-react';

interface ThemeManagerProps {
  themes: Theme[];
  onRefresh: () => void;
}

export const ThemeManager: React.FC<ThemeManagerProps> = ({ themes, onRefresh }) => {
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    name: '',
    primary_color: '#1e40af',
    secondary_color: '#3b82f6',
    accent_color: '#60a5fa',
    bg_color: '#0f172a',
    text_color: '#f1f5f9',
    landing_template: 'default',
    landing_title: 'Selamat Datang',
    landing_subtitle: '',
  });
  const [saving, setSaving] = useState(false);

  const handleCreate = async () => {
    if (!form.name) return;
    setSaving(true);
    try {
      const res = await fetch('/api/themes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (res.ok) { setShowCreate(false); onRefresh(); }
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const handleActivate = async (id: number) => {
    try { await fetch(`/api/themes/${id}/activate`, { method: 'POST' }); onRefresh(); }
    catch (e) { console.error(e); }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Hapus tema ini?')) return;
    try { await fetch(`/api/themes/${id}`, { method: 'DELETE' }); onRefresh(); }
    catch (e) { console.error(e); }
  };

  const ColorInput = ({ label, value, field }: { label: string; value: string; field: string }) => (
    <div>
      <label className="text-xs text-slate-400 mb-1 block">{label}</label>
      <div className="flex gap-2 items-center">
        <input type="color" value={value} onChange={(e) => setForm({ ...form, [field]: e.target.value })} className="w-10 h-10 rounded border border-slate-700 cursor-pointer" />
        <input type="text" value={value} onChange={(e) => setForm({ ...form, [field]: e.target.value })} className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 font-mono focus:border-purple-500 focus:outline-none" />
      </div>
    </div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Palette className="w-5 h-5 text-purple-400" />
          Manajemen Tema & Landing Sync
        </h3>
        <div className="flex gap-2">
          <button onClick={onRefresh} className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition">
            <RefreshCw className="w-4 h-4" />
          </button>
          <button onClick={() => setShowCreate(!showCreate)} className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium transition">
            <Plus className="w-4 h-4" />Buat Tema
          </button>
        </div>
      </div>
      {showCreate && (
        <div className="bg-slate-900 border border-slate-700 rounded-xl p-5 space-y-4">
          <h4 className="text-sm font-semibold text-slate-200">Buat Tema Baru</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Nama Tema</label>
              <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-purple-500 focus:outline-none" placeholder="tema-merah" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Template Landing</label>
              <select value={form.landing_template} onChange={(e) => setForm({ ...form, landing_template: e.target.value })} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-purple-500 focus:outline-none">
                <option value="default">Default</option>
                <option value="minimal">Minimal</option>
                <option value="hero">Hero</option>
              </select>
            </div>
            <ColorInput label="Warna Primer" value={form.primary_color} field="primary_color" />
            <ColorInput label="Warna Sekunder" value={form.secondary_color} field="secondary_color" />
            <ColorInput label="Warna Background" value={form.bg_color} field="bg_color" />
            <ColorInput label="Warna Teks" value={form.text_color} field="text_color" />
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Judul Landing</label>
              <input type="text" value={form.landing_title} onChange={(e) => setForm({ ...form, landing_title: e.target.value })} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-purple-500 focus:outline-none" />
            </div>
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Subtitle Landing</label>
              <input type="text" value={form.landing_subtitle} onChange={(e) => setForm({ ...form, landing_subtitle: e.target.value })} className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 focus:border-purple-500 focus:outline-none" />
            </div>
          </div>
          <div className="flex gap-2 pt-2">
            <button onClick={handleCreate} disabled={saving || !form.name} className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-medium transition">
              <Save className="w-4 h-4" />{saving ? 'Menyimpan...' : 'Simpan'}
            </button>
            <button onClick={() => setShowCreate(false)} className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm transition">Batal</button>
          </div>
        </div>
      )}
      <div className="space-y-3">
        {themes.length === 0 ? (
          <div className="text-center py-8 text-slate-500"><Palette className="w-12 h-12 mx-auto mb-3 opacity-40" /><p>Belum ada tema.</p></div>
        ) : themes.map((t) => (
          <div key={t.id} className={`bg-slate-900 border rounded-xl p-4 ${t.is_active ? 'border-purple-500/50 ring-1 ring-purple-500/20' : 'border-slate-700'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex gap-1">
                  <div className="w-5 h-5 rounded-full border border-slate-600" style={{ backgroundColor: t.primary_color }} />
                  <div className="w-5 h-5 rounded-full border border-slate-600" style={{ backgroundColor: t.secondary_color }} />
                  <div className="w-5 h-5 rounded-full border border-slate-600" style={{ backgroundColor: t.accent_color }} />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-slate-200">{t.name}</span>
                    {t.is_active && <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">AKTIF</span>}
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5 flex items-center gap-1">
                    <Globe className="w-3 h-3" />{t.landing_template}: {t.landing_title || 'Tanpa judul'}
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                {!t.is_active && <button onClick={() => handleActivate(t.id)} className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 text-xs font-medium transition"><Check className="w-3.5 h-3.5" />Aktifkan</button>}
                {!t.is_active && <button onClick={() => handleDelete(t.id)} className="p-1.5 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-400 transition"><Trash2 className="w-3.5 h-3.5" /></button>}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
            <ColorInput label="Warna Aksen" value={form.accent_color} field="accent_color" />
  );