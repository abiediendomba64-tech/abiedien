from telebot import types  # type: ignore
from core.bot import bot
from core.rbac import require_role
from models.theme import Theme

# ================== STATES ==================
from telebot.handler_backends import State, StatesGroup  # type: ignore

class ThemeStates(StatesGroup):
    waiting_name = State()
    waiting_primary_color = State()
    waiting_secondary_color = State()
    waiting_accent_color = State()
    waiting_bg_color = State()
    waiting_text_color = State()
    waiting_landing_title = State()
    waiting_landing_subtitle = State()
    waiting_landing_template = State()

# ================== ADMIN THEME MANAGEMENT ==================
@bot.message_handler(commands=['theme'])
@require_role('admin')
def theme_cmd(message):
    """Show theme management menu."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🎨 Lihat Tema", callback_data="theme_list"),
        types.InlineKeyboardButton("➕ Buat Tema", callback_data="theme_create"),
        types.InlineKeyboardButton("🌐 Landing Sync", callback_data="theme_landing"),
        types.InlineKeyboardButton("🔙 Kembali", callback_data="menu_admin")
    )
    active = Theme.get_active()
    active_name = active[1] if active else "Tidak ada"
    bot.reply_to(
        message,
        f"🎨 *Manajemen Tema*\n\nTema Aktif: `{active_name}`\n\nPilih aksi:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "theme_list")
@require_role('admin')
def theme_list_callback(call):
    themes = Theme.get_all()
    if not themes:
        return bot.answer_callback_query(call.id, "Belum ada tema.", show_alert=True)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for t in themes:
        status = "✅" if t[12] else "⬜"
        markup.add(types.InlineKeyboardButton(
            f"{status} {t[1]} | {t[8]}",
            callback_data=f"theme_detail_{t[0]}"
        ))
    markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="theme"))
    bot.edit_message_text(
        "🎨 *Daftar Tema*\nKlik untuk mengaktifkan/detail.",
        call.message.chat.id, call.message.message_id,
        reply_markup=markup, parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("theme_detail_"))
@require_role('admin')
def theme_detail_callback(call):
    tid = int(call.data.split("_")[2])
    theme = Theme.get_by_id(tid)
    if not theme:
        return bot.answer_callback_query(call.id, "Tema tidak ditemukan.", show_alert=True)
    text = f"🎨 *Detail Tema: {theme[1]}*\n\n"
    text += f"Warna Primer: `{theme[2]}`\n"
    text += f"Warna Sekunder: `{theme[3]}`\n"
    text += f"Warna Aksen: `{theme[4]}`\n"
    text += f"Background: `{theme[5]}`\n"
    text += f"Teks: `{theme[6]}`\n"
    text += f"Template Landing: `{theme[8]}`\n"
    text += f"Judul Landing: `{theme[9]}`\n"
    text += f"Status: {'Aktif' if theme[12] else 'Nonaktif'}\n"
    markup = types.InlineKeyboardMarkup(row_width=2)
    if not theme[12]:
        markup.add(types.InlineKeyboardButton("Aktifkan", callback_data=f"theme_activate_{tid}"))
    markup.add(
        types.InlineKeyboardButton("Hapus", callback_data=f"theme_delete_{tid}"),
        types.InlineKeyboardButton("Kembali", callback_data="theme_list")

@bot.callback_query_handler(func=lambda call: call.data == "theme_create")
@require_role('admin')
def theme_create_callback(call):
    bot.send_message(call.message.chat.id, "Membuat tema baru.\nMasukkan nama tema:")
    bot.set_state(call.from_user.id, ThemeStates.waiting_name, call.message.chat.id)

@bot.message_handler(state=ThemeStates.waiting_name)
def theme_name_handler(message):
    name = message.text.strip()
    if Theme.get_by_name(name):
        return bot.reply_to(message, "Nama tema sudah ada. Coba nama lain:")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['theme_name'] = name
    bot.reply_to(message, "Masukkan warna primer (hex, contoh: #1e40af):")
    bot.set_state(message.from_user.id, ThemeStates.waiting_primary_color, message.chat.id)

@bot.message_handler(state=ThemeStates.waiting_primary_color)
def theme_primary_color_handler(message):
    color = message.text.strip()
    if not color.startswith('#') or len(color) != 7:
        return bot.reply_to(message, "Format hex salah. Contoh: #1e40af")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['primary_color'] = color
    bot.reply_to(message, "Masukkan warna sekunder (hex, contoh: #3b82f6):")
    bot.set_state(message.from_user.id, ThemeStates.waiting_secondary_color, message.chat.id)

@bot.message_handler(state=ThemeStates.waiting_secondary_color)
def theme_secondary_color_handler(message):
    color = message.text.strip()
    if not color.startswith('#') or len(color) != 7:
        return bot.reply_to(message, "Format hex salah. Contoh: #3b82f6")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['secondary_color'] = color
    bot.reply_to(message, "Masukkan warna aksen (hex, contoh: #60a5fa):")
    bot.set_state(message.from_user.id, ThemeStates.waiting_accent_color, message.chat.id)

@bot.message_handler(state=ThemeStates.waiting_accent_color)
def theme_accent_color_handler(message):
    color = message.text.strip()
    if not color.startswith('#') or len(color) != 7:
        return bot.reply_to(message, "Format hex salah. Contoh: #60a5fa")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['accent_color'] = color
    bot.reply_to(message, "Masukkan warna background (hex, contoh: #0f172a):")
    bot.set_state(message.from_user.id, ThemeStates.waiting_bg_color, message.chat.id)
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(state=ThemeStates.waiting_bg_color)
def theme_bg_color_handler(message):
    color = message.text.strip()
    if not color.startswith('#') or len(color) != 7:
        return bot.reply_to(message, "Format hex salah. Contoh: #0f172a")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['bg_color'] = color
    bot.reply_to(message, "Masukkan warna teks (hex, contoh: #f1f5f9):")
    bot.set_state(message.from_user.id, ThemeStates.waiting_text_color, message.chat.id)

@bot.message_handler(state=ThemeStates.waiting_text_color)
def theme_text_color_handler(message):
    color = message.text.strip()
    if not color.startswith('#') or len(color) != 7:
        return bot.reply_to(message, "Format hex salah. Contoh: #f1f5f9")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['text_color'] = color
    bot.reply_to(message, "Masukkan judul landing page:")
    bot.set_state(message.from_user.id, ThemeStates.waiting_landing_title, message.chat.id)

@bot.message_handler(state=ThemeStates.waiting_landing_title)
def theme_landing_title_handler(message):
    title = message.text.strip()
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['landing_title'] = title
    bot.reply_to(message, "Masukkan subtitle landing (atau ketik '-' untuk kosong):")
    bot.set_state(message.from_user.id, ThemeStates.waiting_landing_subtitle, message.chat.id)

@bot.message_handler(state=ThemeStates.waiting_landing_subtitle)
def theme_landing_subtitle_handler(message):
    subtitle = message.text.strip()
    if subtitle == '-':
        subtitle = ''
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['landing_subtitle'] = subtitle
    bot.reply_to(message, "Masukkan template landing (default/minimal/hero):")
    bot.set_state(message.from_user.id, ThemeStates.waiting_landing_template, message.chat.id)

@bot.message_handler(state=ThemeStates.waiting_landing_template)
def theme_landing_template_handler(message):
    template = message.text.strip().lower()
    if template not in ['default', 'minimal', 'hero']:
        return bot.reply_to(message, "Template harus: default, minimal, atau hero")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        name = data['theme_name']
        primary = data['primary_color']
        secondary = data['secondary_color']
        accent = data['accent_color']
        bg = data['bg_color']
        text_c = data['text_color']
        title = data['landing_title']
        subtitle = data['landing_subtitle']
    Theme.create(name, primary, secondary, accent, bg, text_c,
                 template, title, subtitle)
    bot.reply_to(message, f"Tema '{name}' berhasil dibuat! Gunakan /theme untuk mengaktifkan.")
    bot.delete_state(message.from_user.id, message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "theme_landing")
@require_role('admin')
def theme_landing_callback(call):
    config = Theme.get_landing_config()
    if not config:
        return bot.answer_callback_query(call.id, "Tidak ada tema aktif.", show_alert=True)
    text = "Landing Page (Aktif)\n\n"
    text += f"Template: {config['template']}\n"
    text += f"Judul: {config['title']}\n"
    text += f"Subtitle: {config['subtitle']}\n"
    text += f"Status: {'Aktif' if config['enabled'] else 'Nonaktif'}\n"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Kembali", callback_data="theme"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markup, parse_mode="Markdown")
@bot.callback_query_handler(func=lambda call: call.data.startswith("theme_activate_"))
@require_role('admin')
def theme_activate_callback(call):
    tid = int(call.data.split("_")[2])
    Theme.set_active(tid)
    theme = Theme.get_by_id(tid)
    bot.answer_callback_query(call.id, f"Tema '{theme[1]}' diaktifkan!")
    theme_detail_callback(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("theme_delete_"))
@require_role('admin')
def theme_delete_callback(call):
    tid = int(call.data.split("_")[2])
    theme = Theme.get_by_id(tid)
    if theme and theme[12]:
        return bot.answer_callback_query(call.id, "Tidak bisa hapus tema aktif!", show_alert=True)
    Theme.delete(tid)
    bot.answer_callback_query(call.id, "Tema dihapus.")
    theme_list_callback(call)