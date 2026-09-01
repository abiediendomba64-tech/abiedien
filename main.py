#!/usr/bin/env python3
"""
Telegram Bot Enterprise - Entry Point
"""
import threading
import time
import schedule
from core.bot import bot
from core.database import init_db
from core.utils import check_domain_ownership
from models.user import User

# Import semua handler agar terdaftar
from handlers import menu, verification, tickets, forum, payment, admin

# ================== SCHEDULER ==================
def monthly_check():
    """Cek keaktifan domain member setiap bulan."""
    print("🔄 Running monthly verification check...")
    from core.database import safe_execute
    users = safe_execute(
        "SELECT telegram_id, domain_name, verification_token FROM users WHERE domain_verified=1",
        fetch=True
    )
    for uid, domain, token in users or []:
        if not domain or not token:
            continue
        result = check_domain_ownership(domain, token)
        if result != True:
            User.update_domain_verified(uid, 0)
            try:
                bot.send_message(
                    uid,
                    f"⚠️ Verifikasi domain `{domain}` kadaluarsa. /start untuk perbarui.",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print(f"Error notifying user {uid}: {e}")
    print("✅ Monthly check done.")

def run_scheduler():
    """Jalankan scheduler di background thread."""
    schedule.every().day.at("00:00").do(monthly_check)
    while True:
        schedule.run_pending()
        time.sleep(60)

# ================== MAIN ==================
if __name__ == "__main__":
    init_db()
    threading.Thread(target=run_scheduler, daemon=True).start()
    print("\n" + "=" * 60)
    print("🚀 BOT ENTERPRISE (Multi-File) READY TO DEPLOY")
    print("✅ Status: Production Ready")
    print("=" * 60 + "\n")
    bot.infinity_polling()