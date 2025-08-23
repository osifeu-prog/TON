// bot/index.js
import express from 'express';
import dotenv from 'dotenv';

dotenv.config();
const app = express();
app.use(express.json());

// === ENV ===
const TOKEN   = process.env.TELEGRAM_BOT_TOKEN || '';
const SELLER  = process.env.SELLER_TON_ADDRESS || '';
// אתר ברירת מחדל: אם לא הוגדר FRONTEND_URL — נשלח ל-slhisrael.com
const FRONTEND_URL = (process.env.FRONTEND_URL || 'https://slhisrael.com').replace(/\/+$/, '');
const COMMUNITY    = process.env.TELEGRAM_COMMUNITY_LINK || 'https://t.me/+HIzvM8sEgh1kNWY0';
const BOT_LINK     = process.env.TELEGRAM_BOT_LINK || 'https://t.me/hbdcommunity_bot';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
// תמיכה
const SUPPORT_TG_USERNAME = (process.env.SUPPORT_TG_USERNAME || 'OsifFintech').replace(/^@/, '');
const SUPPORT_PHONE       = process.env.SUPPORT_PHONE || ''; // למשל: +972501234567

if (!TOKEN) console.warn('[bot] TELEGRAM_BOT_TOKEN missing');
if (!OPENAI_API_KEY) console.warn('[bot] OPENAI_API_KEY missing (AI replies disabled)');

const TG_API = `https://api.telegram.org/bot${TOKEN}`;

// === Telegram helpers ===
async function tg(method, payload) {
  const r = await fetch(`${TG_API}/${method}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  return r.json().catch(()=> ({}));
}

// --- תפריט ראשי: לחצנים כפי שביקשת ---
function mainMenuKeyboard() {
  const rows = [
    [{ text: 'חזרה לאתר', url: FRONTEND_URL }],
    [{ text: 'לקבוצה שלנו', url: COMMUNITY }],
    [{ text: 'סטייקינג — בקרוב', callback_data: 'staking_soon' }],
    [{ text: 'תמיכה ב-Telegram', url: `https://t.me/${SUPPORT_TG_USERNAME}` }],
  ];
  if (SUPPORT_PHONE) {
    rows.push([{ text: 'תמיכה (טלפון)', url: `tel:${SUPPORT_PHONE}` }]);
  }
  // תשלום מיידי בש״ח
  rows.push([{ text: 'תשלום מיידי (₪)', callback_data: 'pay_ils' }]);
  return { inline_keyboard: rows };
}

// --- הודעת תשלום/תרומה בסיסית ---
function donationText(amtTon) {
  const amount = Number(amtTon) || 1;
  const nano = Math.round(amount * 1e9);
  const tonDeep = SELLER
    ? `ton://transfer/${SELLER}?amount=${nano}&text=${encodeURIComponent('Thanks for your work!')}`
    : null;
  const siteUrl = `${FRONTEND_URL}?donate=${encodeURIComponent(amount)}`;
  const lines = [];
  if (tonDeep) lines.push(`ארנק TON (deeplink): ${tonDeep}`);
  lines.push(`מעולה! סכום מוצע: ${amount} TON.`);
  lines.push(`1) פתחו את הארנק ובצעו תשלום.`);
  lines.push(`2) חזרו לאתר לקבלת ההטבה: ${siteUrl}`);
  lines.push(`\nTelegram Wallet: https://t.me/wallet`);
  return lines.join('\n');
}

// --- תשובת AI (אופציונלי) ---
async function aiAnswer(userText) {
  if (!OPENAI_API_KEY) return null;
  const { default: OpenAI } = await import('openai');
  const client = new OpenAI({ apiKey: OPENAI_API_KEY });
  const system = [
    'אתה עוזר חכם עבור קהילת TON.',
    'הנחיה: הפנה משתמשים לתשלום/תרומה דרך האתר או הארנק; אל תבקש פרטים אישיים.',
    `קישור אתר: ${FRONTEND_URL}.`,
    COMMUNITY ? `קהילה: ${COMMUNITY}.` : '',
    BOT_LINK ? `בוט: ${BOT_LINK}.` : ''
  ].filter(Boolean).join(' ');

  const resp = await client.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: system },
      { role: 'user',   content: userText }
    ],
    temperature: 0.3,
    max_tokens: 350
  });
  const content = resp.choices?.[0]?.message?.content?.trim();
  return content || null;
}

// --- המרת ₪ → TON (CoinGecko) עם קאש 60 שניות ---
let priceCache = { ils: 0, ts: 0 };
async function fetchTonPriceILS() {
  const now = Date.now();
  if (now - priceCache.ts < 60_000 && priceCache.ils > 0) return priceCache.ils;
  const url = 'https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=ils';
  const r = await fetch(url);
  if (!r.ok) throw new Error('price_http_' + r.status);
  const j = await r.json();
  const ils = Number(j?.['the-open-network']?.ils);
  if (!isFinite(ils) || ils <= 0) throw new Error('price_bad');
  priceCache = { ils, ts: now };
  return ils;
}

// --- סטייט מינימלי לזיהוי בקשת ₪ ---
const state = new Map(); // chat_id -> { awaitingIls: true }

// בריאות
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'bot', time: new Date().toISOString() });
});

// Webhook
app.post('/webhook', async (req, res) => {
  try {
    const update = req.body;
    res.json({ ok: true }); // עונים מיידית לטלגרם

    // --- CALLBACK (לחיצה על כפתור) ---
    if (update.callback_query) {
      const cq = update.callback_query;
      const chat_id = cq.message?.chat?.id;
      const data = cq.data || '';

      if (!chat_id) {
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        return;
      }

      if (data === 'staking_soon') {
        await tg('answerCallbackQuery', {
          callback_query_id: cq.id,
          text: 'בקרוב! צוות הפיתוח עובד על זה 🚧',
          show_alert: false
        });
        await tg('sendMessage', {
          chat_id,
          text: 'סטייקינג — בקרוב 🔜\nנעדכן בקבוצה כשהפיצ׳ר יוכרז.',
          reply_markup: mainMenuKeyboard()
        });
        return;
      }

      if (data === 'pay_ils') {
        state.set(chat_id, { awaitingIls: true });
        await tg('answerCallbackQuery', {
          callback_query_id: cq.id,
          text: 'הקלד/י סכום בש״ח…',
          show_alert: false
        });
        await tg('sendMessage', {
          chat_id,
          text: 'הקלד/י בבקשה סכום בש״ח (לדוגמה: 50). אני אמיר ל-TON ואחזיר לך קישור תשלום 👇',
          reply_markup: mainMenuKeyboard()
        });
        return;
      }

      await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'בוצע', show_alert: false });
      return;
    }

    // --- MESSAGE ---
    const msg = update.message || update.edited_message;
    if (!msg) return;
    const chat_id = msg.chat.id;
    const text = (msg.text || '').trim();

    // אם מחכים לסכום בש״ח:
    const st = state.get(chat_id);
    if (st?.awaitingIls && text) {
      state.delete(chat_id);
      // חלץ מספר (תומך ב-"₪ 50", "50 ש\"ח", וכו')
      const ilsStr = (text.replace(/[^\d.,]/g, '') || '').replace(',', '.');
      const ils = Number(ilsStr);
      if (!isFinite(ils) || ils <= 0) {
        await tg('sendMessage', {
          chat_id,
          text: 'לא זיהיתי סכום תקין. נסה/י שוב עם מספר, לדוגמה: 50',
          reply_markup: mainMenuKeyboard()
        });
        return;
      }
      try {
        const priceIls = await fetchTonPriceILS();
        const ton = Math.max(0.001, +(ils / priceIls).toFixed(3));
        await tg('sendMessage', {
          chat_id,
          text: donationText(ton),
          disable_web_page_preview: true,
          reply_markup: mainMenuKeyboard()
        });
      } catch (e) {
        console.error('[price]', e?.message || e);
        await tg('sendMessage', {
          chat_id,
          text: 'לא הצלחתי להביא שער עדכני כרגע. אנא הקלד/י את הסכום ב-TON ישירות (למשל: 1).',
          reply_markup: mainMenuKeyboard()
        });
      }
      return;
    }

    // /start עם payload donate_X
    if (text.startsWith('/start')) {
      const payload = text.split(' ')[1] || '';
      if (payload.startsWith('donate_')) {
        const amt = payload.split('_')[1] || '1';
        await tg('sendMessage', {
          chat_id,
          text: donationText(amt),
          disable_web_page_preview: true,
          reply_markup: mainMenuKeyboard()
        });
        return;
      }
      // /start רגיל — הודעת ברוך הבא + תפריט + המלצה 1 TON
      await tg('sendMessage', {
        chat_id,
        text: 'ברוך הבא! השתמשו בתפריט/פקודות לקבלת עזרה או מעבר לפלטפורמה.',
        reply_markup: mainMenuKeyboard()
      });
      await tg('sendMessage', {
        chat_id,
        text: donationText(1),
        disable_web_page_preview: true,
        reply_markup: mainMenuKeyboard()
      });
      return;
    }

    // /menu — תפריט בכל רגע
    if (text === '/menu') {
      await tg('sendMessage', { chat_id, text: 'תפריט:', reply_markup: mainMenuKeyboard() });
      return;
    }

    // טקסט חופשי → AI (אם קיים), ואז מחזירים גם תפריט
    if (text) {
      const answer = await aiAnswer(text).catch(e => {
        console.error('[openai]', e?.status || e?.message || e);
        return null;
      });
      await tg('sendMessage', {
        chat_id,
        text: answer || `לתרומה/תשלום: ${FRONTEND_URL}`,
        reply_markup: mainMenuKeyboard()
      });
    }
  } catch (e) {
    console.error('[webhook handler]', e);
  }
});

const PORT = Number(process.env.PORT || 8080);
app.listen(PORT, () => {
  console.log(`[bot] listening on http://0.0.0.0:${PORT}`);
  console.log(`[bot] FRONTEND_URL=${FRONTEND_URL}`);
});
