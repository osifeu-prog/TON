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
app.use(cors()); // לפרודקשן אפשר לצמצם ל-origin ספציפי
app.use(rateLimit({ windowMs: 60_000, max: 120 }));

// ===== Helpers =====
function buildSupportLink() {
  const direct = (process.env.SUPPORT_TG_LINK || '').trim();
  if (direct) return direct;
  const user = (process.env.SUPPORT_TG_USERNAME || '').trim().replace(/^@/, '');
  return user ? `https://t.me/${user}` : '';
}

// ===== CFG from ENV =====
const cfg = {
  sellerTonAddress      : process.env.SELLER_TON_ADDRESS || '',
  minDonationTon        : Number(process.env.MIN_DONATION_TON || '1'),
  frontendUrl           : process.env.FRONTEND_URL || 'https://slhisrael.com',
  communityLink         : process.env.TELEGRAM_COMMUNITY_LINK || '',
  verifiedCommunityLink : process.env.VERIFIED_TELEGRAM_COMMUNITY_LINK || '',
  botLink               : process.env.TELEGRAM_BOT_LINK || '',
  walletRedirectUrl     : process.env.WALLET_REDIRECT_URL || '',
  supportLink           : buildSupportLink(),
};

// ===== Health / Config =====
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'api', time: new Date().toISOString() });
});

app.get('/config', (_req, res) => {
  res.json({ ok: true, ...cfg });
});

// דיבוג: אילו ENV קיימים (בלי לחשוף ערכים)
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
      SUPPORT_TG_LINK: !!process.env.SUPPORT_TG_LINK,
      SUPPORT_TG_USERNAME: !!process.env.SUPPORT_TG_USERNAME,
      TONAPI_KEY: !!process.env.TONAPI_KEY,
      TONCENTER_API_KEY: !!process.env.TONCENTER_API_KEY,
      DATABASE_URL: !!process.env.DATABASE_URL
    },
    effective: {
      communityLink: !!cfg.communityLink,
      botLink: !!cfg.botLink,
      walletRedirectUrl: !!cfg.walletRedirectUrl,
      supportLink: !!cfg.supportLink
    }
  });
});

// ===== Logging to file + optional Postgres (לא מחקתי) =====
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const LOG_FILE = path.join(__dirname, 'donations.log');

function appendLog(line) {
  try { fs.appendFileSync(LOG_FILE, line + '\n', { encoding: 'utf8' }); }
  catch (e) { console.error('[log] append error', e); }
}

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

// ===== Optional: hard verify via TonAPI/Toncenter (לא מחקתי) =====
const TONAPI_KEY = process.env.TONAPI_KEY || '';
const TONCENTER_KEY = process.env.TONCENTER_API_KEY || '';

async function verifyWithTonAPI({ seller, from, minAmountTon, sinceTs }) {
  if (!TONAPI_KEY) return { supported: false };
  const url = `https://tonapi.io/v2/blockchain/transactions?account=${encodeURIComponent(seller)}&limit=50`;
  const r = await fetch(url, { headers: { Authorization: `Bearer ${TONAPI_KEY}` } });
  if (!r.ok) return { ok: false, status: r.status };
  const data = await r.json();

  const minNano = BigInt(Math.round(Number(minAmountTon) * 1e9));
  const since = sinceTs ? Number(sinceTs) : Date.now() - 15 * 60 * 1000;

  const hit = (data?.transactions || []).find(tx => {
    const utime = (tx?.utime ?? 0) * 1000;
    const inMsg = tx?.in_msg || {};
    const value = BigInt(inMsg?.value || 0);
    const toSeller = tx?.account_addr === seller || inMsg?.destination === seller;
    const okFrom = !from || inMsg?.source === from;
    return toSeller && okFrom && value >= minNano && utime >= since;
  });

  return { ok: true, found: !!hit };
}

async function verifyWithToncenter({ seller, from, minAmountTon, sinceTs }) {
  const u = new URL('https://toncenter.com/api/v2/getTransactions');
  u.searchParams.set('address', seller);
  u.searchParams.set('limit', '50');
  if (TONCENTER_KEY) u.searchParams.set('api_key', TONCENTER_KEY);
  const r = await fetch(u.toString());
  if (!r.ok) return { ok: false, status: r.status };
  const data = await r.json();

  const minNano = BigInt(Math.round(Number(minAmountTon) * 1e9));
  const since = sinceTs ? Number(sinceTs) : Date.now() - 15 * 60 * 1000;

  const txs = data?.result || [];
  const hit = txs.find(tx => {
    const utime = (tx?.utime ?? 0) * 1000;
    const inMsg = tx?.in_msg || {};
    const val = BigInt(typeof inMsg?.value === 'string' ? inMsg.value : (inMsg?.value || 0));
    const okFrom = !from || inMsg?.source === from;
    return okFrom && val >= minNano && utime >= since;
  });

  return { ok: true, found: !!hit };
}

// GET /verify-donation?amountTon=1&from=EQ...&since=unix_ms
app.get('/verify-donation', async (req, res) => {
  try {
    const seller = cfg.sellerTonAddress;
    if (!seller) return res.status(400).json({ ok: false, error: 'SELLER_TON_ADDRESS not set' });

    const amountTon = Number(req.query.amountTon || cfg.minDonationTon || 1);
    const from = req.query.from || '';
    const sinceTs = req.query.since ? Number(req.query.since) : undefined;

    if (TONAPI_KEY) {
      const v = await verifyWithTonAPI({ seller, from, minAmountTon: amountTon, sinceTs });
      if (v.supported !== false) return res.json({ ok: true, verified: !!v.found, via: 'tonapi' });
    }
    const v2 = await verifyWithToncenter({ seller, from, minAmountTon: amountTon, sinceTs });
    return res.json({ ok: true, verified: !!v2.found, via: 'toncenter' });
  } catch (e) {
    console.error('[verify]', e);
    res.status(500).json({ ok: false, error: 'verify_failed' });
  }
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
    SUPPORT_TG_USERNAME: !!process.env.SUPPORT_TG_USERNAME
  });
});
