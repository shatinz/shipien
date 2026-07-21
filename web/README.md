# Shipien Web Platform

A full-stack Next.js 14 website for Shipien — selling Network, AI, Dev, Machine Learning, Automation, and VPN services.

## Features

- **6 Service Pages**: Network, AI, Dev, ML, Automation, and VPN
- **Auth**: Phone + username signup, JWT sessions (HttpOnly cookies)
- **VPN Gate**: Plans page only visible to logged-in users
- **VPN Purchase Flow**: Select plan → upload receipt → admin approves via Telegram
- **Telegram Bot Integration**: Admin receives inline approve/reject buttons
- **Dashboard**: View VPN subscription status, configs, expiry
- **Marzban API Integration**: Auto-create VPN users on approval

---

## Quick Start (Local Dev)

```bash
# 1. Install dependencies
npm install

# 2. Set up environment
cp .env.example .env.local
# Edit .env.local with your values

# 3. Push database schema
npm run db:push

# 4. Seed VPN plans
npm run db:seed

# 5. Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## Deploy to Vercel

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USER/shipien-web.git
git push -u origin main
```

### 2. Import to Vercel
- Go to [vercel.com/new](https://vercel.com/new)
- Import your GitHub repo
- Add the environment variables (see below)

### 3. Database
Use **Vercel Postgres** (Neon) or any PostgreSQL provider:
- Vercel Dashboard → Storage → Create Database → Postgres
- Copy the `DATABASE_URL` to your environment variables

### 4. Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Random 32+ char secret |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_ADMIN_ID` | Your Telegram user ID |
| `VPN_SERVER_URL` | Marzban panel URL (e.g. `https://panel.example.com`) |
| `VPN_SERVER_TOKEN` | Marzban admin token |
| `NEXT_PUBLIC_TELEGRAM_USERNAME` | `shipien` |
| `CARD_NUMBER` | Payment card number to show users |

### 5. Set Telegram Webhook
After deploying, register the webhook:
```
https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://YOUR_DOMAIN.vercel.app/api/telegram/webhook
```

### 6. Seed the Database (run once)
```bash
# After setting DATABASE_URL
npm run db:seed
```

---

## Project Structure

```
src/
├── app/
│   ├── page.tsx              # Landing page
│   ├── services/page.tsx     # Services listing
│   ├── auth/
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── vpn/
│   │   ├── page.tsx          # Protected - plan selector
│   │   └── VpnPageClient.tsx # Checkout + receipt upload
│   ├── dashboard/
│   │   ├── page.tsx          # Protected - user dashboard
│   │   └── DashboardClient.tsx
│   └── api/
│       ├── auth/{login,signup,logout,me}/
│       ├── vpn/{plans,subscribe}/
│       ├── payment/upload/
│       ├── user/subscriptions/
│       └── telegram/webhook/
├── components/
│   └── Navbar.tsx
└── lib/
    ├── auth.ts       # JWT helpers
    ├── prisma.ts     # DB client
    ├── telegram.ts   # Bot API
    └── vpn.ts        # Marzban API
```

---

## Telegram Bot Flow

1. User uploads payment receipt on the website
2. Bot sends the receipt to admin (you) with **✅ Approve / ❌ Reject** buttons
3. Admin clicks Approve → VPN user created on Marzban, subscription activated
4. Admin clicks Reject → subscription marked rejected
5. User sees updated status on their Dashboard

## Contact & Support
- Telegram: [@shipien](https://t.me/shipien)
