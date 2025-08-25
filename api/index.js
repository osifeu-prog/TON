// api/index.js
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import rateLimit from 'express-rate-limit';

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors()); // לפרודקשן אפשר לצמצם ל-origin ספציפי
app.use(rateLimit({ windowMs: 60_000, max: 120 }));

// === ENV → CFG ===
function buildSupportLink() {
  // עדיפות 1: SUPPORT_TG_LINK מלא, עדיפות 2: @username
  const direct = (process.env.SUPPORT_TG_LINK || '').trim();
  if (direct) return direct;
  const user = (process.env.SUPPORT_TG_USERNAME || '').trim().replace(/^@/, '');
  return user ? `https://t.me/${user}` : '';
}

const cfg = {
  sellerTonAddress   : process.env.SELLER_TON_ADDRESS || '',
  minDonationTon     : Number(process.env.MIN_DONATION_TON || '1'),
  frontendUrl        : process.env.FRONTEND_URL || 'https://slhisrael.com',
  communityLink      : process.env.TELEGRAM_COMMUNITY_LINK || '',
  verifiedCommunityLink: process.env.VERIFIED_TELEGRAM_COMMUNITY_LINK || '', // אופציונלי להמשך
  botLink            : process.env.TELEGRAM_BOT_LINK || '',
  walletRedirectUrl  : process.env.WALLET_REDIRECT_URL || '',
  supportLink        : buildSupportLink(), // חדש: קישור למנהל
};

app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'api', time: new Date().toISOString() });
});

app.get('/config', (_req, res) => {
  res.json({ ok: true, ...cfg });
});

// דיבוג נוחות: מראה אילו ENV קיימים (לא את הערכים)
app.get('/config/debug', (_req, res) => {
  res.json({
    ok: true,
    present: {
      SELLER_TON_ADDRESS: !!process.env.SELLER_TON_ADDRESS,
      MIN_DONATION_TON: !!process.env.MIN_DONATION_TON,
      FRONTEND_URL: !!process.env.FRONTEND_URL,
      TELEGRAM_COMMUNITY_LINK: !!process.env.TELEGRAM_COMMUNITY_LINK,
      VERIFIED_TELEGRAM_COMMUNITY_LINK: !!process.env.VERIFIED_TELEGRAM_COMMUNITY_LINK,
      TELEGRAM_BOT_LINK: !!process.env.TELEGRAM_BOT_LINK,
      WALLET_REDIRECT_URL: !!process.env.WALLET_REDIRECT_URL,
      SUPPORT_TG_LINK: !!(process.env.SUPPORT_TG_LINK),
      SUPPORT_TG_USERNAME: !!(process.env.SUPPORT_TG_USERNAME),
    },
    effective: {
      communityLink: !!cfg.communityLink,
      botLink: !!cfg.botLink,
      walletRedirectUrl: !!cfg.walletRedirectUrl,
      supportLink: !!cfg.supportLink,
    }
  });
});

const port = Number(process.env.PORT || 4000);
app.listen(port, () => {
  console.log(`[api] listening on http://0.0.0.0:${port}`);
  console.log('[api] env present:', {
    SELLER_TON_ADDRESS: !!process.env.SELLER_TON_ADDRESS,
    TELEGRAM_COMMUNITY_LINK: !!process.env.TELEGRAM_COMMUNITY_LINK,
    TELEGRAM_BOT_LINK: !!process.env.TELEGRAM_BOT_LINK,
    WALLET_REDIRECT_URL: !!process.env.WALLET_REDIRECT_URL,
    SUPPORT_TG_LINK: !!process.env.SUPPORT_TG_LINK,
    SUPPORT_TG_USERNAME: !!process.env.SUPPORT_TG_USERNAME,
  });
});
