import React, { useState, useEffect } from 'react';
import { Bot, LayoutDashboard, Users, ShieldCheck, Crown, Terminal, UserCheck, RefreshCw, ExternalLink } from 'lucide-react';
import { BotSimulator } from './components/BotSimulator';
import { NewUserWorkspace } from './components/workspaces/NewUserWorkspace';
import { MemberWorkspace } from './components/workspaces/MemberWorkspace';
import { AdminWorkspace } from './components/workspaces/AdminWorkspace';
import { DevWorkspace } from './components/workspaces/DevWorkspace';
import { SuperAdminWorkspace } from './components/workspaces/SuperAdminWorkspace';
import { User, Ticket, DashboardStats, UserRole } from './types';

const API_BASE_URL = (import.meta.env.VITE_DASHBOARD_API_URL ?? '').replace(/\/$/, '');
const ADVANCED_TOOL_URL = import.meta.env.VITE_ADVANCED_TOOL_URL ?? '';

function apiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export default function App() {
  const [activeView, setActiveView] = useState<'workspace' | 'simulator'>('workspace');
  const [stats, setStats] = useState<DashboardStats>({ totalUsers: 0, verifiedMembers: 0, pendingTickets: 0, totalTopics: 0, pendingPayments: 0, totalWebsites: 0, superAdminCount: 1 });
  const [users, setUsers] = useState<User[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedRole, setSelectedRole] = useState<UserRole>('admin');

  const personas: Record<UserRole, User> = {
    new_user: { id: 99, telegram_id: 112233445, telegram_username: 'calon_member', full_name: 'Budi Hartono (Calon)', whatsapp_number: '081299887766', domain_name: '', role: 'new_user', is_verified: false, domain_verified: false, onboarding_status: 'PENDING_REVIEW', join_reason: 'Butuh manajemen website dan konsultasi DNS', created_at: new Date().toISOString() },
    member: { id: 10, telegram_id: 987654321, telegram_username: 'johndoe', full_name: 'John Doe', whatsapp_number: '081234567890', domain_name: 'tokoanda.com', role: 'member', is_verified: true, domain_verified: true, onboarding_status: 'VERIFIED', join_reason: 'Kelola e-commerce domain tokoanda.com', created_at: new Date().toISOString() },
    admin: { id: 2, telegram_id: 889900112, telegram_username: 'admin_ops', full_name: 'Siti Aminah (Admin Ops)', whatsapp_number: '081399881122', domain_name: 'admin.internal', role: 'admin', is_verified: true, domain_verified: true, onboarding_status: 'VERIFIED', created_at: new Date().toISOString() },
    dev: { id: 3, telegram_id: 778899001, telegram_username: 'dev_lead', full_name: 'Rian DevOps', whatsapp_number: '081566778899', domain_name: 'dev.internal', role: 'dev', is_verified: true, domain_verified: true, onboarding_status: 'VERIFIED', created_at: new Date().toISOString() },
    super_admin: { id: 1, telegram_id: 123456789, telegram_username: 'super_boss', full_name: 'Super Administrator', whatsapp_number: '081122334455', domain_name: 'super.internal', role: 'super_admin', is_verified: true, domain_verified: true, onboarding_status: 'VERIFIED', created_at: new Date().toISOString() },
    root: { id: 999, telegram_id: 999888777, telegram_username: 'system_root', full_name: 'Root / System Owner', whatsapp_number: '081100009999', domain_name: 'root.system', role: 'root', is_verified: true, domain_verified: true, onboarding_status: 'VERIFIED', created_at: new Date().toISOString() }
  };

  const currentUser = personas[selectedRole];

  const fetchAllData = async () => {
    if (!API_BASE_URL) return;
    setRefreshing(true);
    try {
      const [statsRes, usersRes, ticketsRes] = await Promise.all([fetch(apiUrl('/api/stats')), fetch(apiUrl('/api/users')), fetch(apiUrl('/api/tickets'))]);
      if (statsRes.ok) setStats(await statsRes.json());
      if (usersRes.ok) setUsers(await usersRes.json());
      if (ticketsRes.ok) setTickets(await ticketsRes.json());
    } catch (error) {
      console.error('Dashboard API unavailable:', error);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => { void fetchAllData(); }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-sky-500 selection:text-white">
      <header className="sticky top-0 z-40 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          <div className="flex items-center space-x-3"><div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 via-indigo-600 to-purple-600 flex items-center justify-center text-white"><Bot className="w-6 h-6" /></div><div><h1 className="font-bold text-base tracking-tight text-white">Telegram Enterprise Engine</h1><p className="text-xs text-slate-400 hidden sm:block">Bot Gatekeeper • Role-Aware Workspaces • Supabase Repository Layer</p></div></div>
          <div className="flex items-center space-x-2 sm:space-x-3">
            {ADVANCED_TOOL_URL && <a href={ADVANCED_TOOL_URL} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs"><ExternalLink className="w-3.5 h-3.5" /><span className="hidden md:inline">Lanjutan Alat</span></a>}
            <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800"><button onClick={() => setActiveView('workspace')} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${activeView === 'workspace' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}><LayoutDashboard className="w-3.5 h-3.5" />Role Workspace</button><button onClick={() => setActiveView('simulator')} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${activeView === 'simulator' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}><Bot className="w-3.5 h-3.5" />Bot Simulator</button></div>
            <button onClick={fetchAllData} title="Refresh Data" className="p-2 rounded-xl bg-slate-800 border border-slate-700"><RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} /></button>
          </div>
        </div>
        <div className="bg-slate-950/90 border-t border-slate-800/80 px-4 sm:px-6 lg:px-8 py-2"><div className="max-w-7xl mx-auto flex items-center justify-between flex-wrap gap-2 text-xs"><span className="font-semibold text-slate-300">Dashboard Preview Role</span><div className="flex items-center gap-1.5 overflow-x-auto"><button onClick={() => setSelectedRole('new_user')} className="px-3 py-1.5 rounded-lg bg-slate-900 text-slate-300"><Users className="w-3 h-3 inline mr-1" />Tier 0</button><button onClick={() => setSelectedRole('member')} className="px-3 py-1.5 rounded-lg bg-slate-900 text-slate-300"><ShieldCheck className="w-3 h-3 inline mr-1" />Tier 1</button><button onClick={() => setSelectedRole('admin')} className="px-3 py-1.5 rounded-lg bg-slate-900 text-slate-300"><UserCheck className="w-3 h-3 inline mr-1" />Tier 2</button><button onClick={() => setSelectedRole('dev')} className="px-3 py-1.5 rounded-lg bg-slate-900 text-slate-300"><Terminal className="w-3 h-3 inline mr-1" />Tier 3</button><button onClick={() => setSelectedRole('super_admin')} className="px-3 py-1.5 rounded-lg bg-slate-900 text-slate-300"><Crown className="w-3 h-3 inline mr-1" />Tier 4</button><button onClick={() => setSelectedRole('root')} className="px-3 py-1.5 rounded-lg bg-slate-900 text-slate-300"><Crown className="w-3 h-3 inline mr-1" />Tier 5</button></div></div></div>
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeView === 'simulator' ? <BotSimulator onRefreshData={fetchAllData} /> : <div>{selectedRole === 'new_user' && <NewUserWorkspace currentUser={currentUser} onRefreshData={fetchAllData} />}{selectedRole === 'member' && <MemberWorkspace currentUser={currentUser} tickets={tickets} onRefreshData={fetchAllData} />}{selectedRole === 'admin' && <AdminWorkspace currentUser={currentUser} users={users} tickets={tickets} stats={stats} onRefreshData={fetchAllData} />}{selectedRole === 'dev' && <DevWorkspace currentUser={currentUser} tickets={tickets} onRefreshData={fetchAllData} />}{selectedRole === 'super_admin' && <SuperAdminWorkspace currentUser={currentUser} users={users} tickets={tickets} stats={stats} onRefreshData={fetchAllData} />}{selectedRole === 'root' && <div className="p-6 rounded-2xl bg-slate-900 border border-rose-500/30"><h2 className="text-lg font-bold text-rose-300">Tier 5 — Root / System Owner</h2><p className="text-sm text-slate-400 mt-2">Emergency/system recovery surface is intentionally isolated from routine workspaces.</p></div>}</div>}
      </main>
    </div>
  );
}
