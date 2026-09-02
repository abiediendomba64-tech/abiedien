# Enterprise Support Dashboard

Standalone React/Vite dashboard. It is intentionally separated from the Telegram bot/backend so it can be deployed as a static site (for example, Cloudflare Pages).

## Local development

```bash
cd dashboard
npm install
npm run dev
```

## Production build

```bash
cd dashboard
npm run build
```

The generated static files are in `dashboard/dist`.

## Cloudflare Pages

- Root directory: `dashboard`
- Build command: `npm run build`
- Output directory: `dist`
- Configure `VITE_DASHBOARD_API_URL` only when a separately deployed backend API exists.
- `VITE_*` values are browser-visible. Never put Supabase service-role keys, Telegram bot tokens, or other secrets here.

## Architecture boundary

```text
Telegram -> backend/webhook -> Supabase

Browser -> Dashboard (static) -> authenticated backend API / Supabase public client
```

The frontend must never be treated as the authority for RBAC, payment approval, ticket ownership, escalation, or other security-sensitive decisions. Those controls belong to the backend/database policies.
