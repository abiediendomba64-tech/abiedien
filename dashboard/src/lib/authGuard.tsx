import React from 'react';
import { ShieldAlert, Lock } from 'lucide-react';
import { UserRole } from '../types';
export const ROLE_LEVELS: Record<string, number> = { new_user: 0, member: 1, admin: 2, dev: 3, super_admin: 4, root: 5 };
export function getRoleLevel(role: string): number { return ROLE_LEVELS[role?.toLowerCase()] ?? 0; }
export function hasAccess(userRole: string, requiredRole: string): boolean { return getRoleLevel(userRole) >= getRoleLevel(requiredRole); }
export const TIER_NAMES: Record<string, { label: string; tier: number; desc: string }> = {
 new_user:{label:'New User (Tier 0)',tier:0,desc:'Onboarding & Pending Review'}, member:{label:'Member (Tier 1)',tier:1,desc:'Requester, Tickets & Forum'}, admin:{label:'Admin Operasional (Tier 2)',tier:2,desc:'Operational & Ticket Decisions'}, dev:{label:'Dev Tech (Tier 3)',tier:3,desc:'Technical, DNS & Infrastructure'}, super_admin:{label:'Super Admin (Tier 4)',tier:4,desc:'High-Risk & Financial Security'}, root:{label:'Root / System Owner (Tier 5)',tier:5,desc:'Emergency & System Recovery'}
};
interface RoleGuardProps { minRole: UserRole|string; currentRole: UserRole|string; fallback?: React.ReactNode; children: React.ReactNode; }
export const RoleGuard: React.FC<RoleGuardProps> = ({minRole,currentRole,fallback,children}) => {
 if(hasAccess(currentRole,minRole)) return <>{children}</>;
 if(fallback) return <>{fallback}</>;
 const required=TIER_NAMES[minRole]?.label||minRole; const current=TIER_NAMES[currentRole]?.label||currentRole;
 return <div className="p-4 rounded-xl bg-slate-950/90 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between gap-3"><div className="flex items-center gap-2.5"><ShieldAlert className="w-4 h-4 text-rose-400"/><div><span className="font-bold text-rose-200">Akses Dibatasi oleh RBAC 5-Tier</span><p className="text-[11px] text-slate-400 mt-0.5">Memerlukan <strong className="text-slate-200">{required}</strong>. Role saat ini: <strong className="text-amber-300">{current}</strong>.</p></div></div><span className="px-2.5 py-1 rounded bg-rose-500/10 border border-rose-500/20 text-[10px] font-mono"><Lock className="w-3 h-3 inline"/> Locked</span></div>;
};
export function requireRole<P extends object>(WrappedComponent: React.ComponentType<P>, minRole: UserRole|string) { return function WithRoleComponent(props:P&{currentUserRole?:string;currentRole?:string}) { const role=props.currentUserRole||props.currentRole||'new_user'; if(!hasAccess(role,minRole)) return <RoleGuard minRole={minRole} currentRole={role}/>; return <WrappedComponent {...props}/>; }; }
export function assertActionPermission(currentRole:string,minRole:string,actionName:string):boolean { if(!hasAccess(currentRole,minRole)) throw new Error(`⛔ Aksi ditolak (${actionName}): Memerlukan otorisasi ${TIER_NAMES[minRole]?.label||minRole}.`); return true; }
