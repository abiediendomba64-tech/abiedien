from telebot import types  # type: ignore
from core.bot import bot
from core.rbac import has_access, require_role
from models.user import User
from models.ticket import Ticket
from handlers.menu import show_ticket_menu
from config import SUPER_ADMIN_IDS

# ================== STATES ==================
from telebot.handler_backends import State, StatesGroup  # type: ignore

class TicketStates(StatesGroup):
    waiting_message = State()

class SeoAuditStates(StatesGroup):
    waiting_domain = State()
    waiting_keywords = State()

class AdminStates(StatesGroup):
    waiting_admin_reply = State()

# ================== FUNGSI BANTU MENAMPILKAN DAFTAR PENDING ==================
def show_pending_list(cid, uid):
    tickets = Ticket.get_all_pending()
    if not tickets:
        bot.send_message(cid, "📊 Tidak ada tiket pending.")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for t in tickets:
        btn_text = f"📩 {t[1]} - {t[3]} (dari {t[2]})"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"ticket_detail_{t[0]}"))
    markup.add(types.InlineKeyboardButton("🔙 Kembali ke Menu Tiket", callback_data="ticket_back"))
    bot.send_message(
        cid,
        "📊 **Daftar Tiket Pending**\nKlik salah satu untuk melihat detail.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ================== CALLBACK KHUSUS ==================
@bot.callback_query_handler(func=lambda call: call.data.startswith("ticket_detail_"))
@require_role('member')  # Member ke atas bisa lihat detail
def ticket_detail_callback(call):
    tid = int(call.data.split("_")[2])
    uid = call.from_user.id
    cid = call.message.chat.id
    
    ticket = Ticket.get_detail(tid)
    if not ticket:
        return bot.edit_message_text("❌ Tiket tidak ditemukan.", cid, call.message.message_id)
    
    text = f"📩 **Detail Tiket**\n"
    text += f"Nomor: `{ticket[1]}`\nKategori: {ticket[3]}\nDari: `{ticket[2]}`\nStatus: {ticket[5]}\n\n📝 Pesan:\n{ticket[4]}"
    if ticket[8]:
        text += f"\n\n💬 Balasan Admin:\n{ticket[8]}"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    role = User.get_role(uid)
    if has_access(role, 'member'):
        if ticket[5] == 'pending':
            markup.add(types.InlineKeyboardButton("📌 Ambil Tiket", callback_data=f"ticket_assign_{tid}"))
        if ticket[5] in ['pending', 'assigned']:
            markup.add(types.InlineKeyboardButton("✅ Selesaikan", callback_data=f"ticket_resolve_{tid}"))
        markup.add(types.InlineKeyboardButton("💬 Balas", callback_data=f"ticket_reply_{tid}"))
    markup.add(types.InlineKeyboardButton("🔙 Kembali ke Daftar", callback_data="ticket_manage_back"))
    
    bot.edit_message_text(text, cid, call.message.message_id, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("ticket_assign_"))
@require_role('member')
def ticket_assign_callback(call):
    tid = int(call.data.split("_")[2])
    uid = call.from_user.id
    Ticket.update_status(tid, "assigned", assigned_to=uid)
    bot.answer_callback_query(call.id, "✅ Tiket diambil.")
    bot.edit_message_text("📌 Tiket telah di-assign ke Anda.", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ticket_resolve_"))
@require_role('member')
def ticket_resolve_callback(call):
    tid = int(call.data.split("_")[2])
    Ticket.update_status(tid, "resolved")
    bot.answer_callback_query(call.id, "✅ Tiket selesai.")
    bot.edit_message_text("✅ Tiket resolved.", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ticket_reply_"))
@require_role('member')
def ticket_reply_callback(call):
    tid = int(call.data.split("_")[2])
    bot.send_message(call.message.chat.id, "✍️ Ketik balasan Anda (akan dikirim ke user dan tiket ditutup):")
    bot.set_state(call.from_user.id, AdminStates.waiting_admin_reply, call.message.chat.id)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['reply_tid'] = tid

@bot.message_handler(state=AdminStates.waiting_admin_reply)
@require_role('member')
def handle_admin_reply(message):
    reply_text = message.text.strip()
    if not reply_text:
        return bot.reply_to(message, "❌ Balasan tidak boleh kosong.")
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        tid = data.get('reply_tid')
    if not tid:
        return bot.reply_to(message, "❌ Sesi error. Kembali ke menu tiket.")
    
    ticket = Ticket.get_detail(tid)
    if ticket:
        try:
            bot.send_message(
                ticket[2],
                f"💬 **Balasan Admin untuk Tiket `{ticket[1]}`:**\n\n{reply_text}\n\nStatus: ✅ Selesai",
                parse_mode="Markdown"
            )
        except:
            pass
        Ticket.update_status(tid, "resolved", admin_reply=reply_text)
        bot.reply_to(message, "✅ Balasan terkirim dan tiket ditutup.")
    
    bot.delete_state(message.from_user.id, message.chat.id)

# ================== CALLBACK UMUM ==================
@bot.callback_query_handler(func=lambda call: call.data.startswith("ticket_"))
def ticket_callback(call):
    action = call.data.split("_")[1]
    cid = call.message.chat.id
    uid = call.from_user.id

    if action == "new":
        bot.delete_message(cid, call.message.message_id)
        show_category_buttons(cid)
        bot.set_state(uid, TicketStates.waiting_message, cid)
    
    elif action == "my":
        tickets = Ticket.get_user_tickets(uid)
        if not tickets:
            text = "Belum ada tiket."
        else:
            text = "📜 Tiket Saya:\n" + "\n".join([f"{t[0]} | {t[1]} | {t[3]} | {t[4][:10]}" for t in tickets])
        bot.edit_message_text(text, cid, call.message.message_id, parse_mode="Markdown")
    
    elif action == "manage":
        role = User.get_role(uid)
        if not has_access(role, 'member'):
            return bot.answer_callback_query(call.id, "Akses ditolak! Minimum role: Member", show_alert=True)
        bot.delete_message(cid, call.message.message_id)
        show_pending_list(cid, uid)
    
    elif action == "manage_back":
        bot.delete_message(cid, call.message.message_id)
        show_pending_list(cid, uid)
    
    elif action == "cancel":
        bot.delete_state(uid, cid)
        bot.delete_message(cid, call.message.message_id)
        show_ticket_menu(cid, uid)
    
    elif action == "back":
        bot.delete_message(cid, call.message.message_id)
        show_ticket_menu(cid, uid)

# ================== KATEGORI ==================
def show_category_buttons(cid):
    markup = types.InlineKeyboardMarkup(row_width=2)
    cats = [
        ("🌐 Domain", "cat_domain"), ("🔍 Audit SEO / Index", "cat_seoaudit"),
        ("⚙️ Masalah", "cat_problem"), ("💳 Payment", "cat_payment"),
        ("🔄 Push", "cat_push"), ("🚀 Migrasi", "cat_migration"),
        ("💰 Pendapatan", "cat_revenue"), ("👥 Member", "cat_member"),
        ("🛒 Akuisisi", "cat_acquire"), ("🖥️ Kendala Web", "cat_webissue"),
        ("📝 Claim", "cat_claim"), ("🔄 Web Update", "cat_webupdate")
    ]
    for label, data in cats:
        markup.add(types.InlineKeyboardButton(label, callback_data=data))
    markup.add(types.InlineKeyboardButton("🔙 Batal", callback_data="ticket_cancel"))
    bot.send_message(cid, "📌 Pilih Kategori:", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def category_callback(call):
    cat = call.data.split("_")[1]
    cid = call.message.chat.id
    uid = call.from_user.id
    
    if cat == "seoaudit":
        bot.delete_message(cid, call.message.message_id)
        bot.set_state(uid, SeoAuditStates.waiting_domain, cid)
        return bot.send_message(
            cid,
            "🔍 *Layanan Audit Indexing & SEO*\n\n"
            "Masukkan domain target (contoh: `jaya26.site`).\n"
            "Data akan dikumpulkan untuk ditinjau oleh Admin.",
            parse_mode="Markdown"
        )
    
    cat_map = {
        "domain":"🌐 Domain", "problem":"⚙️ Masalah", "payment":"💳 Payment",
        "push":"🔄 Push", "migration":"🚀 Migrasi", "revenue":"💰 Pendapatan",
        "member":"👥 Member", "acquire":"🛒 Akuisisi", "webissue":"🖥️ Kendala Web",
        "claim":"📝 Claim", "webupdate":"🔄 Web Update"
    }
    label = cat_map.get(cat, cat)
    with bot.retrieve_data(uid, cid) as data:
        data['category'] = label
    bot.delete_message(cid, call.message.message_id)
    bot.send_message(cid, f"✍️ Kategori: {label}\nTulis detail pesan (min 10 karakter):")
    bot.set_state(uid, TicketStates.waiting_message, cid)

# ================== INTENT CLASSIFIER: SEO & INDEXING AUDIT ==================
SEO_INTENT_KEYWORDS = [
    'deteksi indexing', 'cek index google', 'audit indexing', 'audit seo', 
    'permintaan backlink', 'migrasi seo domain', 'cek index', 'deteksi index'
]

@bot.message_handler(func=lambda msg: any(k in (msg.text or '').lower() for k in SEO_INTENT_KEYWORDS) and not (msg.text or '').startswith('/'))
def handle_seo_audit_intent(message):
    uid = message.from_user.id
    cid = message.chat.id
    bot.set_state(uid, SeoAuditStates.waiting_domain, cid)
    bot.reply_to(
        message,
        "🔍 *Layanan Audit Indexing & Permintaan SEO*\n\n"
        "Masukkan domain target (contoh: `jaya26.site`).\n"
        "Data akan dicatat sebagai permintaan audit untuk ditinjau Admin.",
        parse_mode="Markdown"
    )

@bot.message_handler(state=SeoAuditStates.waiting_domain)
def get_seo_domain(message):
    domain = message.text.strip().lower()
    uid = message.from_user.id
    cid = message.chat.id
    
    # Cek kepemilikan domain
    user = User.get(uid)
    user_domain = (user[3] or '').lower() if user else ''
    is_verified = (user[8] == 1) if user else False
    is_owned = (domain == user_domain) and is_verified

    with bot.retrieve_data(uid, cid) as data:
        data['domain'] = domain
        data['is_owned'] = is_owned

    warning_text = ""
    if not is_owned:
        warning_text = "\n⚠️ _Catatan: Domain belum terverifikasi atas akun Anda. Pengajuan ini diproses sebagai Audit Indexing & Laporan Terbatas._\n"

    bot.reply_to(
        message,
        f"✅ Domain `{domain}` dicatat.{warning_text}\n"
        "Masukkan *target keywords* yang ingin dianalisis (pisahkan dengan koma).\n"
        "Contoh: `judi online, slot gacor, maxwin`",
        parse_mode="Markdown"
    )
    bot.set_state(uid, SeoAuditStates.waiting_keywords, cid)

@bot.message_handler(state=SeoAuditStates.waiting_keywords)
def get_seo_keywords(message):
    keywords_raw = message.text.strip()
    keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]
    if not keywords:
        return bot.reply_to(message, "❌ Masukkan minimal 1 keyword.")

    uid = message.from_user.id
    cid = message.chat.id
    with bot.retrieve_data(uid, cid) as data:
        domain = data.get('domain', 'target.site')
        is_owned = data.get('is_owned', False)

    description = f"Audit Indexing & SEO untuk {domain} | Keywords: {', '.join(keywords)} | Status: {'Owner Verified' if is_owned else 'Unverified Domain (Audit Only)'}"
    ticket_num = Ticket.create(uid, "seo_audit", description)

    bot.reply_to(
        message,
        f"✅ *Tiket #{ticket_num} - Permintaan Audit Indexing Diterima*\n\n"
        f"📌 Domain: `{domain}`\n"
        f"🔑 Keywords: `{', '.join(keywords)}`\n"
        f"🛡️ Status Kepemilikan: `{'Terverifikasi' if is_owned else 'Audit Only (Belum Terverifikasi)'}`\n\n"
        "Admin akan meninjau status indexing dan menyampaikan laporan ke akun Anda.",
        parse_mode="Markdown"
    )
    bot.delete_state(uid, cid)

    for admin in SUPER_ADMIN_IDS:
        try:
            bot.send_message(admin, f"🔍 *Tiket Baru #{ticket_num} (seo_audit)* dari user `{uid}` untuk domain `{domain}`.")
        except:
            pass

@bot.message_handler(state=TicketStates.waiting_message)
def ticket_message_handler(message):
    text = message.text.strip()
    if len(text) < 10:
        return bot.reply_to(message, "❌ Minimal 10 karakter.")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        cat = data.get('category', 'Umum')
    ticket_num = Ticket.create(message.from_user.id, cat, text)
    bot.reply_to(message, f"✅ Tiket {ticket_num} dibuat.")
    bot.delete_state(message.from_user.id, message.chat.id)
    for admin in SUPER_ADMIN_IDS:
        try:
            bot.send_message(admin, f"🔔 Tiket baru {ticket_num} dari {message.from_user.id}")
        except:
            pass