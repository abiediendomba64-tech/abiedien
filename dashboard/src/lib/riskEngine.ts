// Deterministic UI classifier used for ticket drafting and preview only.
// Backend remains authoritative for priority, routing, RBAC, and business decisions.
export type TicketPriority = 'low' | 'medium' | 'high' | 'urgent';
export type RouteTarget = 'ADMIN' | 'DEV' | 'SUPER_ADMIN';
export type RiskScoreLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TicketIntent = 'ACCOUNT_TAKEOVER' | 'SECURITY_INCIDENT' | 'FRAUD' | 'FINANCIAL_DISPUTE' | 'PRIVILEGE_CHANGE' | 'MAINTENANCE' | 'SERVER_DOWN' | 'PAYMENT_VERIFICATION' | 'ACCOUNT_ACCESS' | 'DOMAIN_REQUEST' | 'WEB_UPDATE' | 'GENERAL_INQUIRY';
export interface ClassificationResult { intent: TicketIntent; category: string; priority: TicketPriority; route_target: RouteTarget; risk_score: RiskScoreLevel; signals: string[]; human_review_required: boolean; explanation: string; confidence: number; }
const SIGNALS: Array<[string[], TicketIntent, string, TicketPriority, RouteTarget, RiskScoreLevel, number]> = [
[['retas','diretas','hacked','hack','takeover','pembajakan','dibajak','breach','anomali token','token bocor','disusupi','malware','backdoor','phishing','exploit','ddos','serangan siber','injeksi','kebocoran data'],'SECURITY_INCIDENT','🔒 Keamanan & Akun','urgent','DEV','CRITICAL',0.98],
[['saldo hilang','rekening diganti','dana tidak bisa ditarik','penipuan','mutasi palsu','sengketa finansial','uang tidak masuk','double charge','fraud','scam','tipu','penggelapan','rekening siluman'],'FINANCIAL_DISPUTE','💳 Pembayaran','urgent','SUPER_ADMIN','CRITICAL',0.95],
[['ganti role','mutasi hak akses','super admin authority','naikkan role','promote admin','akses root','ganti superadmin','izin khusus'],'PRIVILEGE_CHANGE','🛡️ Otoritas Sistem','urgent','SUPER_ADMIN','HIGH',0.92],
[['tidak bisa dibuka','web down','server down','error 500','error 502','bad gateway','connection timeout','dns failed','server crash','website mati','rusak total','database error','crash','down parah'],'MAINTENANCE','🛠 Maintenance','high','DEV','HIGH',0.90],
[['pembayaran','invoice','transfer','bukti bayar','topup saldo','tagihan','bayar hosting','bukti transfer','struk','bca','mandiri','qris'],'PAYMENT_VERIFICATION','💳 Pembayaran','high','ADMIN','MEDIUM',0.88],
[['gagal login','lupa password','reset password','tidak bisa masuk','terkunci','otp tidak masuk','ganti nomor wa','verifikasi ulang'],'ACCOUNT_ACCESS','👤 Akses Akun','high','ADMIN','MEDIUM',0.85],
[['domain baru','buat domain','order domain','tambah domain','beli domain','migrasi dns','nameserver','txt token','cloudflare','cpanel','subdomain'],'DOMAIN_REQUEST','🌐 Domain','medium','ADMIN','LOW',0.86],
[['ganti nama web','update web','koreksi nama','ubah konten','ganti judul','edit halaman','tambah menu'],'WEB_UPDATE','🔄 Web Update','medium','ADMIN','LOW',0.84],
];
function normalize(text: string): string { return (text || '').toLowerCase().replace(/[\r\n\t]/g,' ').replace(/\s+/g,' ').trim(); }
export function classifyTicketOrMessage(rawText: string, categoryHint?: string, _userRole?: string): ClassificationResult {
 const text=normalize(rawText);
 for (const [terms,intent,category,priority,route_target,risk_score,confidence] of SIGNALS) {
  const matches=terms.filter(term=>text.includes(term));
  const hint=(categoryHint||'').toLowerCase();
  const hintMatch=(intent==='MAINTENANCE'&&hint.includes('maintenance'))||(intent==='PAYMENT_VERIFICATION'&&(['payment','pembayaran'].some(x=>hint.includes(x))))||(intent==='DOMAIN_REQUEST'&&hint.includes('domain'))||(intent==='WEB_UPDATE'&&(['update','koreksi'].some(x=>hint.includes(x))));
  if(matches.length>0||hintMatch) return {intent,category,priority,route_target,risk_score,signals:matches.length?matches:['category_hint'],human_review_required:true,explanation:'Klasifikasi ini hanya membantu drafting/routing UI; keputusan akhir tetap oleh manusia yang berwenang.',confidence};
 }
 return {intent:'GENERAL_INQUIRY',category:categoryHint||'❓ Bantuan',priority:'low',route_target:'ADMIN',risk_score:'LOW',signals:['inquiry_umum'],human_review_required:true,explanation:'Permintaan informasi standar diproses oleh Admin; keputusan akhir tetap manusia.',confidence:0.80};
}
export function getPriorityMeta(priority: TicketPriority) { switch(priority) { case 'urgent': return {label:'🚨 URGENT',colorClass:'bg-rose-500/20 text-rose-300 border-rose-500/40',dotColor:'bg-rose-500 animate-ping',bgGradient:'from-rose-950/40 to-rose-900/20'}; case 'high': return {label:'🔴 HIGH',colorClass:'bg-amber-500/20 text-amber-300 border-amber-500/40',dotColor:'bg-amber-500',bgGradient:'from-amber-950/40 to-amber-900/20'}; case 'medium': return {label:'🟡 MEDIUM',colorClass:'bg-sky-500/20 text-sky-300 border-sky-500/40',dotColor:'bg-sky-500',bgGradient:'from-sky-950/40 to-sky-900/20'}; default: return {label:'🟢 LOW',colorClass:'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',dotColor:'bg-emerald-500',bgGradient:'from-emerald-950/40 to-emerald-900/20'}; } }
export function getRouteMeta(route: RouteTarget) { switch(route) { case 'DEV': return {label:'👨‍💻 DEV (Tier 3)',badgeClass:'bg-indigo-500/20 text-indigo-300 border-indigo-500/40',description:'Eskalasi Teknis, DNS & Infrastruktur'}; case 'SUPER_ADMIN': return {label:'👑 SUPER ADMIN (Tier 4)',badgeClass:'bg-purple-500/20 text-purple-300 border-purple-500/40',description:'Otoritas Tinggi & Sengketa Finansial'}; default: return {label:'🛡️ ADMIN OPS',badgeClass:'bg-sky-500/20 text-sky-300 border-sky-500/40',description:'Gatekeeper & Operasional Harian'}; } }
