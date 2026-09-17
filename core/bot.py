from telebot import TeleBot, apihelper
from telebot.storage import StateMemoryStorage
from config import BOT_TOKEN

# WAJIB: tanpa baris ini, semua @bot.middleware_handler (auth & ratelimit)
# TIDAK PERNAH dijalankan oleh pyTelegramBotAPI (silent no-op).
apihelper.ENABLE_MIDDLEWARE = True

# Inisialisasi state storage
state_storage = StateMemoryStorage()

# Inisialisasi bot instance (SATU-SATUNYA instance bot di seluruh proyek —
# jangan buat instance TeleBot lain di file manapun, atau handler yang
# didaftarkan di instance lain tidak akan pernah terpanggil oleh polling).
bot = TeleBot(BOT_TOKEN, state_storage=state_storage)

# Register semua middleware (di-import di sini agar circular import aman)
def register_middlewares():
    from middlewares.auth import register_auth_middleware
    from middlewares.ratelimit import register_ratelimit_middleware
    
    register_auth_middleware(bot)
    register_ratelimit_middleware(bot)

register_middlewares()

def setup_menu_button():
    """Konfigurasi Telegram Chat Menu Button agar ringkas dan tidak memakan lebar kolom chat di mobile."""
    try:
        from telebot.types import MenuButtonWebApp, WebAppInfo, MenuButtonCommands
        from config import WEBAPP_URL, MENU_BUTTON_TITLE
        
        if WEBAPP_URL:
            bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    type="web_app",
                    text=(MENU_BUTTON_TITLE or "App")[:10],
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            )
        else:
            bot.set_chat_menu_button(
                menu_button=MenuButtonCommands(type="commands")
            )
    except Exception as e:
        print(f"Warning: gagal mengatur chat menu button: {e}")