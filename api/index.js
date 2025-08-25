// api/index.js
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import rateLimit from 'express-rate-limit';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pkg from 'pg';

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors()); // בפרודקשן אפשר לצמצם ל-origin ספציפי

const cfg = {
  sellerTonAddress: process.env.SELLER_TON_ADDRESS || '',
  minDonationTon: Number(process.env.MIN_DONATION_TON || '1'),
  frontendUrl: process.env.FRONTEND_URL || 'https://slhisrael.com',
  communityLink: process.env.TELEGRAM_COMMUNITY_LINK || '',
  botLink: process.env.TELEGRAM_BOT_LINK || '',
  walletRedirectUrl: process.env.WALLET_REDIRECT_URL || ''
};

// Rate Limit בסיסי
const limiter = rateLimit({ windowMs: 60_000, max: 60 });
app.use(limiter);

// בריאות/קונפיג
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'api', time: new Date().toISOString() });
});
app.get('/config', (_req, res) => {
  res.json({ ok: true, ...cfg });
});

// דיבוג: מראה רק האם הערכים קיימים (לא את הערך עצמו)
app.get('/config/debug', (_req, res) => {
  res.json({
    ok: true,
    has: {
      SELLER_TON_ADDRESS: !!process.env.SELLER_TON_ADDRESS,
      MIN_DONATION_TON: !!process.env.MIN_DONATION_TON,
      FRONTEND_URL: !!process.env.FRONTEND_URL,
      TELEGRAM_COMMUNITY_LINK: !!process.env.TELEGRAM_COMMUNITY_LINK,
      TELEGRAM_BOT_LINK: !!process.env.TELEGRAM_BOT_LINK,
      WALLET_REDIRECT_URL: !!process.env.WALLET_REDIRECT_URL
    },
    effective: {
      communityLink: !!cfg.communityLink,
      botLink: !!cfg.botLink,
      walletRedirectUrl: !!cfg.walletRedirectUrl
    }
  });
});

// לוגים: קובץ + Postgres (אופציונלי)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const LOG_FILE = path.join(__dirname, 'donations.log');
function appendLog(line) {
  try { fs.appendFileSync(LOG_FILE, line + '\n', { encoding: 'utf8' }); }
  catch (e) { console.error('[log] append error', e); }
}

// Postgres (אופציונלי)
const { Pool } = pkg;
const DATABASE_URL = process.env.DATABASE_URL || '';
const pool = DATABASE_URL
  ? new Pool({ connectionString: DATABASE_URL, ssl: { rejectUnauthorized: false } })
  : null;

async function ensureSchema() {
  if (!pool) return;
  await pool.query(`
    create table if not exists donations (
      id serial primary key,
      ts timestamptz default now(),
      amount_ton numeric,
      to_addr text,
      from_addr text,
      source text,
      comment text,
      meta jsonb
    );
  `);
}
ensureSchema().catch(console.error);

// MVP "רך"
app.post('/log-donation', async (req, res) => {
  const body = req.body || {};
  console.log('[donation]', body);
  appendLog(JSON.stringify({ t: Date.now(), ...body }));
  if (pool) {
    const { amountTon, to, from, source, comment, meta } = body;
    try {
      await pool.query(
        'insert into donations(amount_ton,to_addr,from_addr,source,comment,meta) values ($1,$2,$3,$4,$5,$6)',
        [amountTon ?? null, to ?? null, from ?? null, source ?? null, comment ?? null, meta ?? null]
      );
    } catch (e) {
      console.error('[db insert]', e);
    }
  }
  res.json({ ok: true });
});

// (אופציונלי) אימות קשיח עם TonAPI/Toncenter — נשאר כמו קודם (קיצרתי כאן)
const port = Number(process.env.PORT || 4000);
app.listen(port, () => {
  console.log(`[api] listening on http://0.0.0.0:${port}]`);
  console.log(`[api] env present:`, {
    SELLER_TON_ADDRESS: !!process.env.SELLER_TON_ADDRESS,
    TELEGRAM_COMMUNITY_LINK: !!process.env.TELEGRAM_COMMUNITY_LINK,
    TELEGRAM_BOT_LINK: !!process.env.TELEGRAM_BOT_LINK,
    WALLET_REDIRECT_URL: !!process.env.WALLET_REDIRECT_URL
  });
});
