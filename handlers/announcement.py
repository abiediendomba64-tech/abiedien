from telebot import types  # type: ignore
from core.bot import bot
from core.rbac import require_role
from core.database import safe_execute
from models.announcement import Announcement
from models.user import User

# ================== STATES ==================
from telebot.handler_backends import State, StatesGroup  # type: ignore

class AnnouncementStates(StatesGroup):
    waiting_title = State()
    waiting_content = State()
    waiting_target = State()

# ================== ADMIN ANNOUNCEMENT MANAGEMENT ==================
@bot.message_handler(commands=['announce'])
@require_role('admin')
def announce_cmd(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Buat Pengumuman", callback_data="ann_create"),
        types.InlineKeyboardButton("Lihat Pengumuman", callback_data="ann_list"),
        types.InlineKeyboardButton("Kembali", callback_data="menu_admin")
    )
    bot.reply_to(
        message,
        "*Manajemen Pengumuman & Aturan*\n\nKirim informasi, aturan, atau update ke member.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "ann_list")
@require_role('admin')
def ann_list_callback(call):
    anns = Announcement.get_all()
    if not anns:
        return bot.answer_callback_query(call.id, "Belum ada pengumuman.", show_alert=True)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for a in anns:
        target = a[4] or "Semua"
        markup.add(types.InlineKeyboardButton(
            f"{a[2]} | {target}",
            callback_data=f"ann_detail_{a[0]}"
        ))
    markup.add(types.InlineKeyboardButton("Kembali", callback_data="announce"))
    bot.edit_message_text(
        "Daftar Pengumuman\nKlik untuk detail/hapus.",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("ann_detail_"))
@require_role('admin')
def ann_detail_callback(call):
    aid = int(call.data.split("_")[2])
    ann = Announcement.get_by_id(aid)
    if not ann:
        return bot.answer_callback_query(call.id, "Pengumuman tidak ditemukan.", show_alert=True)
    text = f"*Detail Pengumuman*\n\n"
    text += f"Judul: `{ann[2]}`\n"
    text += f"Target: `{ann[4] or 'Semua'}`\n"
    text += f"Dibuat: `{ann[5]}`\n\n"
    text += f"Konten:\n{ann[3]}\n"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Kirim ke Member", callback_data=f"ann_send_{aid}"),
        types.InlineKeyboardButton("Hapus", callback_data=f"ann_delete_{aid}"),
        types.InlineKeyboardButton("Kembali", callback_data="ann_list")
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("ann_send_"))
@require_role('admin')
def ann_send_callback(call):
    aid = int(call.data.split("_")[2])
    ann = Announcement.get_by_id(aid)
    if not ann:
        return bot.answer_callback_query(call.id, "Pengumuman tidak ditemukan.", show_alert=True)
    target_role = ann[4]
    msg = f"*PENGUMUMAN*\n\n*{ann[2]}*\n\n{ann[3]}"
    if target_role:
        users = safe_execute(
            "SELECT telegram_id FROM users WHERE role = ? OR role = 'admin' OR role = 'super_admin'",
            (target_role,), fetch=True
        )
    else:
        users = safe_execute("SELECT telegram_id FROM users", fetch=True)
    cnt = 0
    if users:
        for (uid,) in users:
            try:
                bot.send_message(uid, msg, parse_mode="Markdown")
                cnt += 1
            except Exception:
                pass
    bot.answer_callback_query(call.id, f"Pengumuman dikirim ke {cnt} member!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ann_delete_"))
@require_role('admin')
def ann_delete_callback(call):
    aid = int(call.data.split("_")[2])
    Announcement.delete(aid)
    bot.answer_callback_query(call.id, "Pengumuman dihapus.")
    ann_list_callback(call)

@bot.callback_query_handler(func=lambda call: call.data == "ann_create")
@require_role('admin')
def ann_create_callback(call):
    bot.send_message(call.message.chat.id, "*Buat Pengumuman Baru*\n\nMasukkan judul:", parse_mode="Markdown")
    bot.set_state(call.from_user.id, AnnouncementStates.waiting_title, call.message.chat.id)

@bot.message_handler(state=AnnouncementStates.waiting_title)
def ann_title_handler(message):
    title = message.text.strip()
    if len(title) < 3:
        return bot.reply_to(message, "Judul minimal 3 karakter.")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['ann_title'] = title
    bot.reply_to(message, "Masukkan konten pengumuman:")
    bot.set_state(message.from_user.id, AnnouncementStates.waiting_content, message.chat.id)

@bot.message_handler(state=AnnouncementStates.waiting_content)

@bot.message_handler(state=AnnouncementStates.waiting_target)
def ann_target_text_handler(message):
    """Fallback if user types target instead of clicking button."""
    target_map = {'all': None, 'member': 'member', 'admin': 'admin', 'dev': 'dev'}
    target = target_map.get(message.text.strip().lower())
    if target is None and message.text.strip().lower() != 'all':
        return bot.reply_to(message, "Target: all, member, admin, atau dev")
    _save_announcement(message.from_user.id, message.chat.id, target)
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ann_target_"))
@require_role('admin')
def ann_target_callback(call):
    target_map = {
        'ann_target_all': None,
        'ann_target_member': 'member',
        'ann_target_admin': 'admin',
        'ann_target_dev': 'dev'
    }
    target = target_map.get(call.data)
    _save_announcement(call.from_user.id, call.message.chat.id, target)
    bot.delete_state(call.from_user.id, call.message.chat.id)

def _save_announcement(user_id, chat_id, target_role):
    """Helper to save announcement from state data."""
    with bot.retrieve_data(user_id, chat_id) as data:
        title = data.get('ann_title')
        content = data.get('ann_content')
    if not title or not content:
        bot.send_message(chat_id, "Error: data hilang. Ulangi /announce")
        return
    Announcement.create(user_id, title, content, target_role)
    bot.send_message(
        chat_id,
        f"Pengumuman '{title}' dibuat!\nTarget: {target_role or 'Semua'}",
        parse_mode="Markdown"
    )

# ================== MEMBER VIEW ANNOUNCEMENTS ==================
@bot.message_handler(commands=['info'])
def info_cmd(message):
    """Member can view announcements targeted to them."""
    uid = message.from_user.id
    role = User.get_role(uid)
    anns = Announcement.get_for_role(role)
    if not anns:
        return bot.reply_to(message, "Tidak ada pengumuman saat ini.")
    text = "*PENGUMUMAN & INFO*\n\n"
    for a in anns[:10]:
        text += f"*{a[2]}*\n{a[3]}\n\n"
    bot.reply_to(message, text, parse_mode="Markdown")
def ann_content_handler(message):
    content = message.text.strip()
    if len(content) < 5:
        return bot.reply_to(message, "Konten minimal 5 karakter.")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['ann_content'] = content
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Semua", callback_data="ann_target_all"),
        types.InlineKeyboardButton("Member", callback_data="ann_target_member"),
        types.InlineKeyboardButton("Admin", callback_data="ann_target_admin"),
        types.InlineKeyboardButton("Dev", callback_data="ann_target_dev")
    )
    bot.reply_to(message, "Pilih target pengumuman:", reply_markup=markup)
    bot.set_state(message.from_user.id, AnnouncementStates.waiting_target, message.chat.id)