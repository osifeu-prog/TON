import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import rateLimit from 'express-rate-limit';
import fs from 'fs';
import path from 'path';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';

dotenv.config();
const app = express();
app.use(express.json());
app.use(cors());

// === CONFIG ===
const cfg = {
  sellerTonAddress: process.env.SELLER_TON_ADDRESS || '',
  minDonationTon: Number(process.env.MIN_DONATION_TON || '1'),
  frontendUrl: process.env.FRONTEND_URL || 'https://tonfront.onrender.com',
  communityLink: process.env.TELEGRAM_COMMUNITY_LINK || '',
  botLink: process.env.TELEGRAM_BOT_LINK || ''
};

// === Rate Limit בסיסי (מומלץ לפרודקשן) ===
const limiter = rateLimit({ windowMs: 60_000, max: 60 });
app.use(limiter);

// === בריאות/קונפיג ===
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'api', time: new Date().toISOString() });
});
app.get('/config', (_req, res) => {
  res.json({ ok: true, ...cfg });
});

// === לוגים: לקובץ גלגול פשוט (fallback אם אין DB) ===
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const LOG_FILE = path.join(__dirname, 'donations.log');

function appendLog(line) {
  try {
    fs.appendFileSync(LOG_FILE, line + '\n', { encoding: 'utf8' });
  } catch (e) {
    console.error('[log] append error', e);
  }
}

// === POST /log-donation  (MVP "רך") ===
app.post('/log-donation', (req, res) => {
  const body = req.body || {};
  console.log('[donation]', body);
  appendLog(JSON.stringify({ t: Date.now(), ...body }));
  res.json({ ok: true });
});

// === אימות קשיח על-שרשרת (Hard Verify) ===
// אפשר לעבוד מול TonAPI או Toncenter. ננסה לפי המפתח שקיים בסביבה.
const TONAPI_KEY = process.env.TONAPI_KEY || '';
const TONCENTER_KEY = process.env.TONCENTER_API_KEY || ''; // optional

// helper: בודק דרך TonAPI אם יש טרנזקציה נכנסת ל-seller מאז זמן נתון
async function verifyWithTonAPI({ seller, from, minAmountTon, sinceTs }) {
  if (!TONAPI_KEY) return { supported: false };
  // TonAPI מספקת endpoints לעבודה עם טרנזקציות; נשתמש ב-search לפי כתובת היעד ומגבלת זמן.
  // הערה: בפועל כדאי להשתמש ב-/v2/blockchain/transactions של TonAPI עם פילטרים מתאימים.
  const url = `https://tonapi.io/v2/blockchain/transactions?account=${encodeURIComponent(seller)}&limit=50`;
  const r = await fetch(url, { headers: { Authorization: `Bearer ${TONAPI_KEY}` }});
  if (!r.ok) return { ok: false, status: r.status };
  const data = await r.json();

  const minNano = BigInt(Math.round(Number(minAmountTon) * 1e9));
  const since = sinceTs ? Number(sinceTs) : Date.now() - 15 * 60 * 1000;

  const hit = (data?.transactions || []).find(tx => {
    // בדיקה גסה: התקבלו כספים מאת כתובת מסוימת לתוך seller, בסכום מתאים, מאז 'since'
    const utime = (tx?.utime ?? 0) * 1000;
    const inMsgs = (tx?.in_msgs || []).concat(tx?.in_msg ? [tx.in_msg] : []);
    const anyFrom = inMsgs.some(m => !from || (m?.source === from));
    const value = BigInt(tx?.in_msg?.value || 0n);
    const toSeller = tx?.account_addr === seller || (tx?.in_msg?.destination === seller);
    return toSeller && anyFrom && value >= minNano && utime >= since;
  });

  return { ok: true, found: !!hit };
}

// helper: Toncenter getTransactions (REST)  https://toncenter.com/api/v2/getTransactions
async function verifyWithToncenter({ seller, from, minAmountTon, sinceTs }) {
  const url = new URL('https://toncenter.com/api/v2/getTransactions');
  url.searchParams.set('address', seller);
  url.searchParams.set('limit', '50');
  if (TONCENTER_KEY) url.searchParams.set('api_key', TONCENTER_KEY);
  const r = await fetch(url.toString());
  if (!r.ok) return { ok: false, status: r.status };
  const data = await r.json();

  const minNano = BigInt(Math.round(Number(minAmountTon) * 1e9));
  const since = sinceTs ? Number(sinceTs) : Date.now() - 15 * 60 * 1000;

  const txs = data?.result || [];
  const hit = txs.find(tx => {
    const utime = (tx?.utime ?? 0) * 1000;
    const inMsg = tx?.in_msg || {};
    const anyFrom = !from || (inMsg?.source === from);
    const value = BigInt(inMsg?.value || 0n);
    // חלק מהחזרים מחזירים in_msg.value כמחרוזת – נתמוך גם בזה:
    const val = typeof inMsg?.value === 'string' ? BigInt(inMsg.value) : value;
    return anyFrom && val >= minNano && utime >= since;
  });

  return { ok: true, found: !!hit };
}

// GET /verify-donation?amountTon=1&from=EQ...&since=unix_ms
app.get('/verify-donation', async (req, res) => {
  const seller = cfg.sellerTonAddress;
  const from = req.query.from || '';
  const amountTon = Number(req.query.amountTon || cfg.minDonationTon || 1);
  const sinceTs = req.query.since ? Number(req.query.since) : undefined;

  try {
    if (!seller) return res.status(400).json({ ok: false, error: 'SELLER_TON_ADDRESS not set' });

    if (TONAPI_KEY) {
      const v = await verifyWithTonAPI({ seller, from, minAmountTon: amountTon, sinceTs });
      if (v.supported === false) { /* fallthrough */ }
      else return res.json({ ok: !!v.ok, verified: !!v.found, via: 'tonapi' });
    }
    // fallback Toncenter
    const v2 = await verifyWithToncenter({ seller, from, minAmountTon: amountTon, sinceTs });
    return res.json({ ok: !!v2.ok, verified: !!v2.found, via: 'toncenter' });
  } catch (e) {
    console.error('[verify]', e);
    res.status(500).json({ ok: false, error: 'verify_failed' });
  }
});

const port = Number(process.env.PORT || 4000);
app.listen(port, () => {
  console.log(`[api] listening on http://0.0.0.0:${port}`);
});
