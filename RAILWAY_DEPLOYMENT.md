"""
Quick Start & Deployment Guide - Railway Free Tier
Panduan lengkap dalam 15 menit
"""

# =============== STEP 1: LOCAL TESTING (5 MENIT) ===============

echo "=== STEP 1: SETUP LOKAL ==="

# 1. Clone repo (sudah ada)
cd abiedien

# 2. Copy .env
cp .env.example .env

# 3. Edit .env dengan token asli
# BOT_TOKEN=123456:ABC-DEF-GHI
# SUPER_ADMIN_IDS=YOUR_TELEGRAM_ID

# 4. Install dependencies
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 5. Run bot lokal
python main.py

# Expected output:
# ============================================================
# 🚀 TELEGRAM BOT ENTERPRISE - STARTING
# ✅ Database initialized
# ✅ Scheduler thread started
# ✅ All handlers registered
# ✅ Status: Production Ready
# ============================================================
# 🔄 Polling messages (Ctrl+C to stop)...

# 6. Test bot
# - Buka Telegram, cari bot Anda
# - Kirim: /start
# - Kirim: "Pak buat domain jayapro"
# - Bot harus respons dalam < 1 detik

# =============== STEP 2: DEPLOY KE RAILWAY (10 MENIT) ===============

echo "=== STEP 2: RAILWAY DEPLOYMENT ==="

# 1. Buka https://railway.app
# 2. Login dengan GitHub

# 3. New Project → Deploy from GitHub
#    - Pilih abiediendomba64-tech/abiedien
#    - Railway auto-detect Python

# 4. Tunggu build selesai (2-3 menit)
#    - "Building..."
#    - "Build successfully"
#    - Container ready

# 5. Set Environment Variables
#    Di Railway Dashboard:
#    Klik project → Variables → Add:
#    
#    BOT_TOKEN = isi_token_dari_botfather
#    SUPER_ADMIN_IDS = telegram_id_anda
#    DB_NAME = data_member.db
#    VERIFICATION_EXPIRY_DAYS = 30
#    LOG_LEVEL = INFO

# 6. Mount Volume (untuk persist SQLite)
#    Di Railway → project → Storage → New:
#    Mount path: /app/data_member.db
#    Size: 1 GB (cukup untuk 10K users)

# 7. Klik Deploy
#    - Railway akan restart container dengan env vars
#    - Bot mulai polling

# 8. Verifikasi
#    - Buka Logs (tail -f di Railway UI)
#    - Cari: "🔄 Polling messages..."
#    - Jika ada ERROR, cek 10 baris terakhir

# =============== STEP 3: SMOKE TEST (2 MENIT) ===============

echo "=== STEP 3: TEST BOT LIVE ==="

# 1. Open Telegram app
# 2. Cari bot Anda

# 3. Test 1: Greeting
#    Kirim: /start
#    Expected: Welcome menu + buttons

# 4. Test 2: Conversation State
#    Kirim: "Pak buat domain jayapro"
#    Bot: "Untuk apa domain jayapro?"
#    Kirim: "Untuk toko online"
#    Bot: "✅ Request #TKT-0001 dibuat"

# 5. Test 3: Duplicate Prevention
#    Kirim: "Pak"
#    Bot: "Request sebelumnya masih diproses..."
#    Kirim: "Pak"
#    Bot: "(sama, tidak buat tiket baru)"

# 6. Test 4: Status Check
#    Kirim: "Gimana pak?"
#    Bot: "Request #TKT-0001 Status: ⏳ Menunggu admin"

# 7. Test 5: Admin Command
#    Kirim: /pending
#    Bot: (Admin only, jika Anda di SUPER_ADMIN_IDS)
#    Respons: "📋 PENDING TICKETS\n#TKT-0001 | DOMAIN_REQUEST..."

# =============== TROUBLESHOOTING ===============

ISSUES = {
    "Bot tidak respons": {
        "Cek 1": "BOT_TOKEN di Railway === Token dari BotFather?",
        "Cek 2": "Bot di Railway Logs, ada error? (tail -f)",
        "Cek 3": "Telegram API bisa diakses dari Railway? (check network)",
        "Fix": "Redeploy: Railway → Deployments → kebab menu → Redeploy"
    },
    
    "Message delay > 5 detik": {
        "Cek": "Bot dengan banyak users? (concurrent)",
        "Cek": "SQLite query slow? (Buka Logs, lihat query time)",
        "Fix": "Migrate to Supabase (cloud DB, lebih cepat)"
    },
    
    "Bot crash setiap hari": {
        "Cek": "Memory limit? (Railway free: ~200MB)",
        "Cek": "Database lock? (SQLite issue saat write besar)",
        "Fix": "Enable WAL mode di core/database.py (sudah default)"
    },
    
    "Data hilang setelah restart": {
        "Cek": "Volume mounted? (Railway Storage)",
        "Fix": "Setup Volume atau migrate ke Supabase"
    }
}

# =============== MONITORING & MAINTENANCE ===============

MONITORING = {
    
    "Daily": {
        "Check Logs": "Setiap pagi, lihat Telegram notifications dari admin alerts",
        "User count": "SELECT COUNT(*) FROM users (check growth)",
        "Error rate": "Cari 'ERROR' di logs (harus < 1%)"
    },
    
    "Weekly": {
        "Backup": "Download data_member.db (manual) atau configure Supabase auto-backup",
        "Ticket SLA": "Admin response time < 1 jam (check LOGIC_UPDATE.md)",
        "Performance": "Average message latency < 500ms"
    },
    
    "Monthly": {
        "Database cleanup": "Archive resolved tickets > 90 hari",
        "User segmentation": "Analyze domain_verified ratio (target > 80%)",
        "Cost review": "Railway free vs. scale to paid?"
    }
}

# =============== SCALING (IF NEEDED) ===============

SCALING = {
    
    "If 100-1000 users": {
        "Status": "Railway free tier OK (< 500MB)",
        "Action": "Maintain current setup"
    },
    
    "If 1000-10K users": {
        "Bottleneck": "SQLite locking pada write-heavy (100+ msg/s)",
        "Solution": "Migrate to Supabase PostgreSQL (1 click, Railway auto-connect)",
        "Cost": "Supabase free tier: 500K row writes/month (enough)"
    },
    
    "If 10K+ users": {
        "Solution": "Add message queue (Redis/Bull)",
        "Setup": "Railway + Redis add-on",
        "Cost": "Railway paid tier ($5+) + Supabase paid tier"
    }
}

# =============== ROLLBACK / EMERGENCY ===============

EMERGENCY = {
    
    "Bot tidak respons (timeout > 30s)": {
        "Step 1": "Railway → Deployments → Latest → Redeploy",
        "Step 2": "Jika masih tidak OK: Rollback ke deployment sebelumnya"
    },
    
    "Data corruption / tiket hilang": {
        "Step 1": "Restore dari backup (Supabase atau manual backup)",
        "Step 2": "Restart bot",
        "Step 3": "Notify members yang affected"
    },
    
    "Token exposed": {
        "Step 1": "IMMEDIATELY: Go to BotFather /settoken dengan token baru",
        "Step 2": "Update BOT_TOKEN di Railway Variables",
        "Step 3": "Redeploy bot"
    }
}

print("=" * 70)
print("QUICK START: READY FOR RAILWAY")
print("=" * 70)
print("\n✅ All setup guides prepared")
print("✅ Expected deployment time: 15 menit")
print("✅ No downtime required")
print("\nNext: Follow STEP 1 lokal, then STEP 2 ke Railway")
