// bot/index.js
import express from 'express';
import dotenv from 'dotenv';

dotenv.config();
const app = express();
app.use(express.json());

const TOKEN   = process.env.TELEGRAM_BOT_TOKEN || '';
const SELLER  = process.env.SELLER_TON_ADDRESS || '';
const FRONTEND_URL = (process.env.FRONTEND_URL || 'https://tonfront.onrender.com').replace(/\/+$/,'');
const COMMUNITY = process.env.TELEGRAM_COMMUNITY_LINK || '';
const BOT_LINK  = process.env.TELEGRAM_BOT_LINK || '';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';

if (!TOKEN) console.warn('[bot] TELEGRAM_BOT_TOKEN missing');
if (!OPENAI_API_KEY) console.warn('[bot] OPENAI_API_KEY missing (AI replies disabled)');

const API = `https://api.telegram.org/bot${TOKEN}`;

async function tg(method, payload) {
  const r = await fetch(`${API}/${method}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  return r.json().catch(()=> ({}));
}

function donationText(amt) {
  const nano = Math.round((Number(amt) || 1) * 1e9);
  const tonDeep = SELLER ? `ton://transfer/${SELLER}?amount=${nano}&text=${encodeURIComponent('Thanks for your work!')}` : null;
  const siteUrl = `${FRONTEND_URL}?donate=${encodeURIComponent(Number(amt)||1)}`;
  let lines = [
    `סכום מוצע: ${amt} TON`,
    `אתר: ${siteUrl}`,
    `Telegram Wallet: https://t.me/wallet`
  ];
  if (tonDeep) lines.unshift(`ארנק TON (deeplink): ${tonDeep}`);
  return lines.join('\n');
}

async function aiAnswer(userText) {
  if (!OPENAI_API_KEY) return null;
  const { default: OpenAI } = await import('openai');
  const client = new OpenAI({ apiKey: OPENAI_API_KEY });

  const system = [
    'אתה עוזר חכם עבור קהילת TON.',
    'הנחיה: לכוון משתמשים לתרומה/תשלום דרך האתר או הארנק—לא לבקש פרטים אישיים.',
    `קישור אתר: ${FRONTEND_URL}.
