# האתר הזה יכול להיות שלך — Project Handbook

## TL;DR
פלטפורמת תרומות/תשלומים על TON: אתר סטטי + API + בוט טלגרם. ברירת מחדל תשלום: Telegram Wallet. אימות תשלום קשיח (On-chain) + מסלול צילום מסך כגיבוי. הטבה = הצטרפות לקבוצת טלגרם סגורה למאומתים.

## Services
- Frontend (`frontend/`): `index.html`, `tonconnect-manifest.json`, `frontendassets/*`
- API (`api/`): `index.js` — `/config`, `/verify-donation`, `/log-donation`, `/record-proof`, `/admin/approve`
- Bot (`bot/`): `index.js` — תפריט, סכומים, תשלום, צילום הוכחה, אימות קשיח, Admin approve

## ENV
API: `SELLER_TON_ADDRESS`, `FRONTEND_URL`, `TELEGRAM_COMMUNITY_LINK`, `VERIFIED_COMMUNITY_LINK`, `TELEGRAM_BOT_LINK`, `WALLET_REDIRECT_URL`, `DATABASE_URL`, (`TONAPI_KEY`/`TONCENTER_API_KEY`), `HARD_VERIFY_ONLY`, `ALLOW_SCREENSHOT_FALLBACK`  
Bot: `TELEGRAM_BOT_TOKEN`, `SELLER_TON_ADDRESS`, `FRONTEND_URL`, `TELEGRAM_COMMUNITY_LINK`, `VERIFIED_COMMUNITY_LINK`, `API_BASE`, `HERO_IMAGE_URL`, `SUPPORT_TG_USERNAME`, (`SUPPORT_PHONE`), `ADMIN_FORWARD_CHAT_ID`, `ADMIN_IDS`

## DB
Postgres tables:
- `donations(id, ts, amount_ton, to_addr, from_addr, source, comment, meta)`
- `verifications(id, ts, chat_id, amount_ton, from_addr, via, verified, proof_file_id, admin_id, note)`

## Deploy (Render)
- Frontend: Static Site → Root `frontend`
- API: Web Service (Node) → Root `api` → Build `npm i --production` → Start `node index.js`
- Bot: Web Service (Node) → Root `bot` → Build `npm i --production` → Start `node index.js` → webhook to `/webhook`

## QA Checklist
- `/config` מחזיר לינקים מלאים (כולל `verifiedCommunityLink`, `walletRedirectUrl`)
- Frontend: התחברות ארנק → “שלם עכשיו” → fallback תקין → חזרה
- Bot: `/start` עם תמונת HERO, “📋 כתובת שליחה” מחזיר רק כתובת, “⬆️ העלאת אישור” + “✅ אמת תשלום” עובדים
- אימות קשיח מצליח (TonAPI/Toncenter) או Admin approve שולח לינק הטבה

## Principles
לא שוברים עיצוב/טקסט; Fallback ברור; שקיפות; קהילתיות; Feature Flags.
