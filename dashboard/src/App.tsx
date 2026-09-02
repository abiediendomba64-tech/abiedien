import React, { useEffect, useState } from 'react';
import { AlertTriangle, Bot, LayoutDashboard, RefreshCw, ShieldCheck, UserCheck } from 'lucide-react';
import { BotSimulator } from './components/BotSimulator';
import { AdminWorkspace } from './components/workspaces/AdminWorkspace';
import { DevWorkspace } from './components/workspaces/DevWorkspace';
import { SuperAdminWorkspace } from './components/workspaces/SuperAdminWorkspace';
import { User, Ticket, DashboardStats, UserRole } from './types';

const API_BASE_URL = (import.meta.env.VITE_DASHBOARD_API_URL ?? '').replace(/\/$/, '');
// Fake personas are development-only. Production builds cannot enable this mode.
const LOCAL_PREVIEW_MODE = import.meta.env.DEV && import.meta.env.VITE_DASHBOARD_PREVIEW_MODE === 'true';
const ALLOWED_DASHBOARD_ROLES: UserRole[] = ['admin', 'dev', 'super_admin'];

type SessionResponse = { authenticated: boolean; user?: User };

function apiUrl(path: string): string { return `${API_BASE_URL}${path}`; }

function AccessLocked({ reason, onRetry }: { reason: string; onRetry?: () => void }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-6">
      <div className="w-full max-w-xl rounded-3xl bg-slate-900 border border-rose-500/30 shadow-2xl p-8">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center"><ShieldCheck className="w-6 h-6 text-rose-300" /></div>
          <div><h1 className="text-lg font-bold">Dashboard Operasional Terkunci</h1><p className="text-xs text-slate-400">Hanya Admin, Dev, dan Super Admin yang berwenang.</p></div>
        </div>
        <div className="rounded-2xl bg-slate-950 border border-slate-800 p-4">
          <div className="flex items-start gap-2"><AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 shrink-0" /><div><p className="font-semibold text-slate-100">Akses belum diberikan</p><p className="text-xs text-slate-500 mt-1">{reason}</p></div></div>
        </div>
        {onRetry && <button onClick={onRetry} className="mt-5 inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold"><RefreshCw className="w-3.5 h-3.5" /> Coba Lagi</button>}
      </div>
    </div>
  );
}

export default function App() {
  const [activeView, setActiveView] = useState<'workspace' | 'simulator'>('workspace');
  const [stats, setStats] = useState<DashboardStats>({ totalUsers: 0, verifiedMembers: 0, pendingTickets: 0, totalTopics: 0, pendingPayments: 0, totalWebsites: 0, superAdminCount: 0 });
  const [users, setUsers] = useState<User[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [sessionUser, setSessionUser] = useState<User | null>(null);
  const [sessionState, setSessionState] = useState<'checking' | 'authenticated' | 'unauthenticated' | 'unconfigured' | 'forbidden'>('checking');
  const [selectedPreviewRole, setSelectedPreviewRole] = useState<UserRole>('admin');

  const previewPersonas: Partial<Record<UserRole, User>> = {
    admin: { id: 2, telegram_id: 889900112, telegram_username: 'preview_admin', full_name: 'Preview Admin', whatsapp_number: '', domain_name: '', role: 'admin', is_verified: true, domain_verified: true, onboarding_status: 'VERIFIED', created_at: new Date().toISOString() },
    dev: { id: 3, telegram_id: 778899001, telegram_username: 'preview_dev', full_name: 'Preview Dev', whatsapp_number: '', domain_name: '', role: 'dev', is_verified: true, domain_verified: true, onboarding_status: 'VERIFIED', created_at: new Date().toISOString() },
    super_admin: { id: 1, telegram_id: 123456789, telegram_username: 'preview_super_admin', full_name: 'Preview Super Admin', whatsapp_number: '', domain_name: '', role: 'super_admin', is_verified: true, domain_verified: true, onboarding_status: 'VERIFIED', created_at: new Date().toISOString() },
  };

  const currentUser = LOCAL_PREVIEW_MODE ? previewPersonas[selectedPreviewRole] ?? null : sessionUser;

  const authenticateSession = async () => {
    if (LOCAL_PREVIEW_MODE) { setSessionState('authenticated'); return; }
    if (!API_BASE_URL) { setSessionState('unconfigured'); return; }
    setSessionState('checking');
    try {
      const response = await fetch(apiUrl('/api/session'), { method: 'GET', credentials: 'include', headers: { Accept: 'application/json' } });
      if (!response.ok) { setSessionUser(null); setSessionState(response.status === 401 ? 'unauthenticated' : 'forbidden'); return; }
      const data = (await response.json()) as SessionResponse;
      if (!data.authenticated || !data.user) { setSessionUser(null); setSessionState('unauthenticated'); return; }
      if (!ALLOWED_DASHBOARD_ROLES.includes(data.user.role)) { setSessionUser(data.user); setSessionState('forbidden'); return; }
      setSessionUser(data.user); setSessionState('authenticated');
    } catch (error) {
      console.error('Dashboard authentication check failed:', error);
      setSessionUser(null); setSessionState('unauthenticated');
    }
  };

  const fetchAllData = async () => {
    if (LOCAL_PREVIEW_MODE || !API_BASE_URL || !sessionUser) return;
    setRefreshing(true);
    try {
      const init: RequestInit = { credentials: 'include', headers: { Accept: 'application/json' } };
      const [statsRes, usersRes, ticketsRes] = await Promise.all([fetch(apiUrl('/api/stats'), init), fetch(apiUrl('/api/users'), init), fetch(apiUrl('/api/tickets'), init)]);
      if (statsRes.ok) setStats(await statsRes.json());
      if (usersRes.ok) setUsers(await usersRes.json());
      if (ticketsRes.ok) setTickets(await ticketsRes.json());
    } catch (error) { console.error('Dashboard API unavailable:', error); }
    finally { setRefreshing(false); }
  };

  useEffect(() => { void authenticateSession(); }, []);
  useEffect(() => { if (sessionState === 'authenticated' && sessionUser) void fetchAllData(); }, [sessionState, sessionUser]);

  if (sessionState === 'checking') return <AccessLocked reason="Memverifikasi sesi dashboard..." />;
  if (sessionState === 'unconfigured') return <AccessLocked reason="Backend autentikasi belum dikonfigurasi. Workspace operasional tetap tertutup." />;
  if (sessionState === 'unauthenticated') return <AccessLocked reason="Sesi tidak valid atau belum login. Tidak ada data operasional yang ditampilkan." onRetry={() => void authenticateSession()} />;
  if (sessionState === 'forbidden' || !currentUser || !ALLOWED_DASHBOARD_ROLES.includes(currentUser.role)) return <AccessLocked reason="Akun terautentikasi, tetapi role tidak memiliki akses dashboard operasional." />;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-sky-500 selection:text-white">
      <header className="sticky top-0 z-40 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center space-x-3"><div className="w-10 h-10 rounded-xl bg-sky-600 flex items-center justify-center text-white"><Bot className="w-6 h-6" /></div><div><h1 className="font-bold text-base tracking-tight text-white">Telegram Enterprise Engine</h1><p className="text-xs text-slate-400 hidden sm:block">Restricted Operational Dashboard</p></div></div>
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300"><UserCheck className="w-3.5 h-3.5 inline mr-1.5" />{currentUser.role}</div>
            <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800"><button onClick={() => setActiveView('workspace')} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${activeView === 'workspace' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}><LayoutDashboard className="w-3.5 h-3.5" />Workspace</button>{LOCAL_PREVIEW_MODE && <button onClick={() => setActiveView('simulator')} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${activeView === 'simulator' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}><Bot className="w-3.5 h-3.5" />Simulator</button>}</div>
            <button onClick={fetchAllData} title="Refresh Data" className="p-2 rounded-xl bg-slate-800 border border-slate-700"><RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} /></button>
          </div>
        </div>
        {LOCAL_PREVIEW_MODE && <div className="bg-amber-950/30 border-t border-amber-500/20 px-4 sm:px-6 lg:px-8 py-2 text-xs"><div className="max-w-7xl mx-auto flex items-center gap-2 flex-wrap"><span className="font-semibold text-amber-300">LOCAL PREVIEW ONLY</span>{(Object.keys(previewPersonas) as UserRole[]).map((role) => <button key={role} onClick={() => setSelectedPreviewRole(role)} className="px-2.5 py-1 rounded-lg bg-slate-900 text-slate-300 border border-slate-800">{role}</button>)}</div></div>}
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeView === 'simulator' && LOCAL_PREVIEW_MODE ? <BotSimulator onRefreshData={fetchAllData} /> : <div>{currentUser.role === 'admin' && <AdminWorkspace currentUser={currentUser} users={users} tickets={tickets} stats={stats} onRefreshData={fetchAllData} />}{currentUser.role === 'dev' && <DevWorkspace currentUser={currentUser} tickets={tickets} onRefreshData={fetchAllData} />}{currentUser.role === 'super_admin' && <SuperAdminWorkspace currentUser={currentUser} users={users} tickets={tickets} stats={stats} onRefreshData={fetchAllData} />}</div>}
      </main>
    </div>
  );
}
