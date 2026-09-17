#!/usr/bin/env python3
"""
Script utilitas untuk mengatur Chat Menu Button Telegram Bot menjadi ringkas (App / Commands).
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from core.bot import bot, setup_menu_button

if __name__ == "__main__":
    print("🔄 Mengatur Chat Menu Button Telegram...")
    try:
        setup_menu_button()
        print("✅ Berhasil! Chat Menu Button telah disetel ulang menjadi ringkas.")
        print("👉 Silakan buka kembali aplikasi Telegram Anda untuk melihat perubahannya.")
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
