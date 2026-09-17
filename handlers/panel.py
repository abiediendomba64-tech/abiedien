from telebot import types  # type: ignore
from core.bot import bot
from core.rbac import require_role
from models.panel import PanelAccount
from models.user import User

# ================== STATES ==================
from telebot.handler_backends import State, StatesGroup  # type: ignore

class PanelStates(StatesGroup):
    waiting_user_id = State()
    waiting_username = State()
    waiting_password = State()

# ================== ADMIN PANEL MANAGEMENT ==================
@bot.message_handler(commands=['panel'])
@require_role('admin')
def panel_cmd(message):
    """Show panel backoffice management menu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("List Panel", callback_data="panel_list"),
        types.InlineKeyboardButton("Buat Akun", callback_data="panel_create"),
        types.InlineKeyboardButton("Kembali", callback_data="menu_admin")
    )
    bot.reply_to(
        message,
        "*Manajemen Panel Backoffice*\n\nKelola akses panel untuk member terverifikasi.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "panel")
@require_role('admin')
def panel_menu_callback(call):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("List Panel", callback_data="panel_list"),
        types.InlineKeyboardButton("Buat Akun", callback_data="panel_create"),
        types.InlineKeyboardButton("Kembali", callback_data="menu_admin")
    )
    bot.edit_message_text(
        "*Manajemen Panel Backoffice*\n\nKelola akses panel untuk member terverifikasi.",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "panel_list")
@require_role('admin')
def panel_list_callback(call):
    panels = PanelAccount.get_all()
    if not panels:
        return bot.answer_callback_query(call.id, "Belum ada akun panel.", show_alert=True)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for p in panels:
        btn_text = f"{p[2]} | @{p[3]} | {p[7]}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"panel_detail_{p[0]}"))
    markup.add(types.InlineKeyboardButton("Kembali", callback_data="panel"))
    bot.edit_message_text(
        "Daftar Akun Panel\nKlik untuk detail/kirim password.",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("panel_detail_"))
@require_role('admin')
def panel_detail_callback(call):
    pid = int(call.data.split("_")[2])
    panel = PanelAccount.get_by_id(pid)
    if not panel:
        return bot.answer_callback_query(call.id, "Akun tidak ditemukan.", show_alert=True)
    text = f"*Detail Akun Panel*\n\n"
    text += f"User: `{panel[10]}` (ID: `{panel[1]}`)\n"
    text += f"Domain: `{panel[2]}`\n"
    text += f"Username: `{panel[3]}`\n"
    text += f"Password: `{panel[4]}`\n"
    text += f"URL: `{panel[2]}/backoffice`\n"
    text += f"Status: `{panel[7]}`\n"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Kirim Password", callback_data=f"panel_sendpass_{pid}"),
        types.InlineKeyboardButton("Reset Password", callback_data=f"panel_resetpass_{pid}"),
        types.InlineKeyboardButton("Hapus", callback_data=f"panel_delete_{pid}"),
        types.InlineKeyboardButton("Kembali", callback_data="panel_list")
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("panel_sendpass_"))
@require_role('admin')
def panel_sendpass_callback(call):
    pid = int(call.data.split("_")[2])
    panel = PanelAccount.get_by_id(pid)
    if not panel:
        return bot.answer_callback_query(call.id, "Akun tidak ditemukan.", show_alert=True)
    user_id = panel[1]
    domain = panel[2]
    username = panel[3]
    password = panel[4]
    try:
        bot.send_message(
            user_id,
            f"*Akses Panel Backoffice*\n\n"
            f"Domain: `{domain}`\n"
            f"URL: `{domain}/backoffice`\n"
            f"Username: `{username}`\n"
            f"Password: `{password}`\n\n"
            f"Simpan informasi ini dengan aman!",
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id, "Password terkirim ke member!", show_alert=True)
    except Exception:
        bot.answer_callback_query(call.id, "Gagal kirim. Mungkin user memblokir bot.", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("panel_resetpass_"))
@require_role('admin')
def panel_resetpass_callback(call):
    pid = int(call.data.split("_")[2])
    import secrets
    new_pass = secrets.token_urlsafe(12)
    PanelAccount.update(pid, panel_password=new_pass)
    bot.answer_callback_query(call.id, f"Password direset: {new_pass}", show_alert=True)
    panel_detail_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("panel_delete_"))
@require_role('admin')
def panel_delete_callback(call):
    pid = int(call.data.split("_")[2])
    PanelAccount.delete(pid)
    bot.answer_callback_query(call.id, "Akun panel dihapus.")
    panel_list_callback(call)

@bot.callback_query_handler(func=lambda call: call.data == "panel_create")
@require_role('admin')
def panel_create_callback(call):
    bot.send_message(
        call.message.chat.id,
        "*Buat Akun Panel*\n\nMasukkan Telegram ID member (harus sudah terverifikasi domain):"
    )
    bot.set_state(call.from_user.id, PanelStates.waiting_user_id, call.message.chat.id)

@bot.message_handler(state=PanelStates.waiting_user_id)
def panel_user_id_handler(message):
    try:
        user_id = int(message.text.strip())
    except ValueError:
        return bot.reply_to(message, "Masukkan Telegram ID (angka):")
    user = User.get(user_id)
    if not user:
        return bot.reply_to(message, "User tidak ditemukan.")
    if user[9] != 1:
        return bot.reply_to(message, "Domain user belum terverifikasi!")
    domain = user[3]
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['panel_user_id'] = user_id
        data['panel_domain'] = domain
    bot.reply_to(
        message,
        f"Domain: `{domain}`\nMasukkan username panel (atau ketik '-' untuk auto-generate):",
        parse_mode="Markdown"
    )
    bot.set_state(message.from_user.id, PanelStates.waiting_username, message.chat.id)

@bot.message_handler(state=PanelStates.waiting_username)
def panel_username_handler(message):
    username = message.text.strip()
    if username == '-':
        username = None
    elif len(username) < 3:
        return bot.reply_to(message, "Username minimal 3 karakter.")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['panel_username'] = username
    bot.reply_to(message, "Masukkan password panel (atau ketik '-' untuk auto-generate):")
    bot.set_state(message.from_user.id, PanelStates.waiting_password, message.chat.id)

@bot.message_handler(state=PanelStates.waiting_password)
def panel_password_handler(message):
    password = message.text.strip()
    if password == '-':
        password = None
    elif len(password) < 6:
        return bot.reply_to(message, "Password minimal 6 karakter.")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        user_id = data['panel_user_id']
        domain = data['panel_domain']
        username = data.get('panel_username')
    PanelAccount.create(user_id, domain, username, password)
    panel = PanelAccount.get_by_user(user_id)
    try:
        bot.send_message(
            user_id,
            f"*Akun Panel Backoffice Dibuat!*\n\n"
            f"Domain: `{domain}`\n"
            f"URL: `{domain}/backoffice`\n"
            f"Username: `{panel[3]}`\n"
            f"Password: `{panel[4]}`\n\n"
            f"Simpan informasi ini dengan aman!",
            parse_mode="Markdown"
        )
    except Exception:
        pass
    bot.reply_to(
        message,
        f"Akun panel dibuat!\nUser: `{user_id}`\nDomain: `{domain}`\nUsername: `{panel[3]}`\nPassword: `{panel[4]}`\n\nPassword sudah dikirim ke member.",
        parse_mode="Markdown"
    )
    bot.delete_state(message.from_user.id, message.chat.id)

# ================== MEMBER ACCESS PANEL INFO ==================
@bot.message_handler(commands=['mypanel'])
def mypanel_cmd(message):
    """Member can request their panel credentials."""
    uid = message.from_user.id
    panel = PanelAccount.get_by_user(uid)
    if not panel:
        return bot.reply_to(
            message,
            "Anda belum memiliki akun panel.\nHubungi admin untuk membuat akses panel."
        )
    bot.reply_to(
        message,
        f"*Akses Panel Anda*\n\n"
        f"Domain: `{panel[2]}`\n"
        f"URL: `{panel[2]}/backoffice`\n"
        f"Username: `{panel[3]}`\n"
        f"Password: `{panel[4]}`\n"
        f"Status: `{panel[7]}`\n\n"
        f"Simpan informasi ini dengan aman!",
        parse_mode="Markdown"
    )