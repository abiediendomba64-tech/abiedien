# Telegram Bot Enterprise

Bot Telegram modular untuk verifikasi domain, tiket, forum, pembayaran,
administrasi member, broadcast, dan pemeriksaan berkala.

## Quick start

Prasyarat: Python 3.9+ dan koneksi internet. Untuk verifikasi DNS TXT dan
WHOIS, gunakan server yang mengizinkan koneksi DNS/WHOIS keluar.

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` dan isi:

```dotenv
BOT_TOKEN=token_asli_dari_BotFather
SUPER_ADMIN_IDS=telegram_id_1,telegram_id_2
DB_NAME=data_member.db
VERIFICATION_EXPIRY_DAYS=30
```

Jalankan satu-satunya entry point:

```bash
python main.py
```

`config.py` akan menghentikan startup jika `BOT_TOKEN` belum diisi. Jangan
menjalankan file handler secara langsung dan jangan membuat instance `TeleBot`
kedua.

## Struktur

- `main.py` — entry point, inisialisasi database, polling, dan scheduler
- `config.py` — konfigurasi dari environment
- `core/` — instance bot, database, RBAC, dan utilitas
- `models/` — operasi data
- `handlers/` — menu, verifikasi, tiket, forum, pembayaran, dan admin
- `middlewares/` — autentikasi dan rate limit
- `deploy/` — contoh service systemd dan backup SQLite
- `PERBAIKAN_DAN_CARA_DEPLOY.md` — catatan perbaikan dan deployment
- `sop.md` — SOP operasional lengkap

## Keamanan deployment

- `.env` tidak disertakan dalam paket bersih dan sudah di-ignore Git.
- Simpan token hanya di environment variable atau secret manager.
- Batasi `SUPER_ADMIN_IDS` ke akun yang benar-benar diperlukan.
- Backup `data_member.db` secara berkala; contoh backup SQLite tersedia di
  `deploy/backup.sh`.
- Verifikasi bukti pembayaran tetap memerlukan pemeriksaan manual admin.

## Keterbatasan platform

PythonAnywhere gratis dapat membatasi koneksi raw socket dan proses yang
berjalan terus-menerus. VPS atau platform dengan outbound DNS/WHOIS dan worker
jangka panjang lebih sesuai untuk deployment produksi. Detailnya ada di
`PERBAIKAN_DAN_CARA_DEPLOY.md`.