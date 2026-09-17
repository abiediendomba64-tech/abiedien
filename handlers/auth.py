from telebot import types
from core.bot import bot
from core.rbac import has_access
from models.user import User
from config import SUPER_ADMIN_IDS

ADMIN_LOGIN_URL = "https://abiedienbackoffice.pages.dev/admin/login"
MEMBER_LOGIN_URL = "https://abiedienbackoffice.pages.dev/member/login"

@bot.message_handler(commands=['login', 'masuk'])
def login_command(message):
    """Memberikan tautan langsung dan tombol WebApp untuk login ke Backoffice."""
    uid = message.from_user.id
    user = User.get(uid)
    role = User.get_role(uid) if user else ('super_admin' if uid in SUPER_ADMIN_IDS else 'new_user')

    markup = types.InlineKeyboardMarkup(row_width=1)

    if uid in SUPER_ADMIN_IDS or has_access(role, 'admin') or role in ['super_admin', 'dev', 'admin']:
        markup.add(
            types.InlineKeyboardButton("👑 Buka Portal Super Admin", url=ADMIN_LOGIN_URL),
            types.InlineKeyboardButton("📱 Buka WebApp Admin", web_app=types.WebAppInfo(url=ADMIN_LOGIN_URL))
        )
        text = (
            f"👑 *Akses Login Super Admin / Staf*\n\n"
            f"Halo, *{message.from_user.first_name}*!\n"
            f"Akun Telegram Anda (`{uid}`) terdaftar dengan role *{role.upper()}*.\n\n"
            f"Klik salah satu tombol di bawah untuk membuka halaman login Dashboard Backoffice:"
        )
    else:
        markup.add(
            types.InlineKeyboardButton("🌐 Buka Portal Member", url=MEMBER_LOGIN_URL),
            types.InlineKeyboardButton("📱 Buka WebApp Member", web_app=types.WebAppInfo(url=MEMBER_LOGIN_URL))
        )
        text = (
            f"👤 *Akses Login Portal Member*\n\n"
            f"Halo, *{message.from_user.first_name}*!\n"
            f"Klik salah satu tombol di bawah untuk masuk ke Portal Member Backoffice:"
        )

    bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")
