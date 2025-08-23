// bot/index.js
import express from 'express';
import dotenv from 'dotenv';

dotenv.config();
const app = express();
app.use(express.json());

// === ENV ===
const TOKEN   = process.env.TELEGRAM_BOT_TOKEN || '';
const SELLER  = process.env.SELLER_TON_ADDRESS || '';
const FRONTEND_URL = (process.env.FRONTEND_URL || 'https://slhisrael.com').replace(/\/+$/, '');
const COMMUNITY    = process.env.TELEGRAM_COMMUNITY_LINK || 'https://t.me/+HIzvM8sEgh1kNWY0';
const BOT_LINK     = process.env.TELEGRAM_BOT_LINK || 'https://t.me/hbdcommunity_bot';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
const SUPPORT_TG_USERNAME = (process.env.SUPPORT_TG_USERNAME || 'OsifFintech').replace(/^@/, '');
const SUPPORT_PHONE       = process.env.SUPPORT_PHONE || '';
const HERO_IMAGE_URL = (process.env.HERO_IMAGE_URL || 'https://tonfront.onrender.com/frontendassets/536279550_10237941019841362_2777380265588054892_n.jpg').trim();

if (!TOKEN) console.warn('[bot] TELEGRAM_BOT_TOKEN missing');
const TG_API = `https://api.telegram.org/bot${TOKEN}`;

// === Telegram helper ===
async function tg(method, payload) {
  const r = await fetch(`${TG_API}/${method}`, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  const j = await r.json().catch(()=> ({}));
  if (!j.ok) console.error('[tg err]', method, j);
  return j;
}

// --- עזרי מחיר ---
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
function formatILS(n) {
  if (!isFinite(n)) return '₪?';
  const opts = (n < 1) ? { minimumFractionDigits: 2, maximumFractionDigits: 3 }
                       : { minimumFractionDigits: 0, maximumFractionDigits: 2 };
  return '₪' + n.toLocaleString('he-IL', opts);
}
function formatTON(x) {
  const v = Math.max(0.001, Number(x) || 0);
  return v.toLocaleString('en-US', { minimumFractionDigits: 3, maximumFractionDigits: 3 });
}

// --- זיהוי “₪” גם בלי state ---
function parseIlsLike(text) {
  if (!text) return null;
  const cleaned = text.replace(/[^\d.,]/g, '').replace(',', '.');
  const v = Number(cleaned);
  return isFinite(v) && v > 0 ? v : null;
}

// --- בנאי תפריט דינמי: כל הכפתורים עם ערכים חיים ---
async function buildMainMenu() {
  // ברירות מחדל:
  let minBtnLabel = 'תרומה מזערית 0.001 TON';
  let btn50 = '₪50';
  let btn100 = '₪100';
  let btn200 = '₪200';
  let payAny = 'תשלום מיידי (₪)';

  try {
    const rate = await fetchTonPriceILS(); // ₪ לכל 1 TON
    // 0.001 TON -> ₪
    const ilsForMin = 0.001 * rate;
    minBtnLabel += ` (~${formatILS(ilsForMin)})`;

    // ₪ -> TON
    const ton50  = 50  / rate;
    const ton100 = 100 / rate;
    const ton200 = 200 / rate;

    btn50  = `₪50 (~${formatTON(ton50)} TON)`;
    btn100 = `₪100 (~${formatTON(ton100)} TON)`;
    btn200 = `₪200 (~${formatTON(ton200)} TON)`;

    // להראות גם את השער על הכפתור של "תשלום מיידי"
    payAny = `תשלום מיידי (₪) • שער ${formatILS(rate)}/TON`;
  } catch {
    // תוויות fallback יישארו כפי שהוגדרו בתחילת הפונקציה
  }

  const rows = [
    [{ text: 'חזרה לאתר', url: FRONTEND_URL }],
    [{ text: 'לקבוצה שלנו', url: COMMUNITY }],
    [{ text: 'סטייקינג — בקרוב', callback_data: 'staking_soon' }],
    [{ text: 'תמיכה', url: `https://t.me/${SUPPORT_TG_USERNAME}` }],
    [{ text: '📋 כתובת שליחה', callback_data: 'copy_addr' }],
    [{ text: '📋 ‏חיבור ארנק אישי', callback_data: 'copy_wallet' }],
  ];
  if (SUPPORT_PHONE) rows.push([{ text: 'תמיכה (טלפון)', url: `tel:${SUPPORT_PHONE}` }]);

  // חדש: 0.001 TON עם ₪
  rows.push([{ text: minBtnLabel, callback_data: 'pay_min_ton' }]);

  // ₪ דינמי עם TON משוער
  rows.push([
    { text: btn50,  callback_data: 'pay_ils_50' },
    { text: btn100, callback_data: 'pay_ils_100' },
    { text: btn200, callback_data: 'pay_ils_200' }
  ]);
  rows.push([{ text: payAny, callback_data: 'pay_ils' }]);

  return { inline_keyboard: rows };
}

// --- כפתורי תשלום לאחר חישוב — רק Telegram Wallet + חזרה לתפריט ---
function paymentKeyboard() {
  return {
    inline_keyboard: [
      [{ text: 'פתיחה ב-Telegram Wallet', url: 'https://t.me/wallet' }],
      [{ text: '⬅️ חזרה לתפריט', callback_data: 'back_menu' }]
    ]
  };
}

// --- /start: הודעה אחת עם תמונה + טקסט שלך ---
function startCombinedCaption() {
  return [
    'ברוך הבא! השתמשו בתפריט/פקודות לקבלת עזרה או מעבר לפלטפורמה.',
    '',
    'לאחר אישור התשלום ההטבה תישלח כאן בבוט.'
  ].join('\n');
}

// --- הודעת תרומה אחרי חישוב ₪→TON ---
function donationText(amtTon) {
  const amount = Number(amtTon) || 1;
  const siteUrl = `${FRONTEND_URL}?donate=${encodeURIComponent(amount)}`;
  return [
    `סכום חישוב לדוגמה: ~${amount} TON.`,
    '1) פתחו את הארנק ובצעו תשלום.',
    `2) חזרו לאתר לקבלת ההטבה: ${siteUrl}`
  ].join('\n');
}

// --- AI (אופציונלי) ---
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

// === בריאות ===
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'bot', time: new Date().toISOString() });
});

// === Webhook ===
app.post('/webhook', async (req, res) => {
  try {
    const update = req.body;
    res.json({ ok: true });

    // CALLBACK
    if (update.callback_query) {
      const cq = update.callback_query;
      const chat_id = cq.message?.chat?.id;
      const data = cq.data || '';
      if (!chat_id) { await tg('answerCallbackQuery', { callback_query_id: cq.id }); return; }

      if (data === 'staking_soon') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'בקרוב! צוות הפיתוח עובד על זה 🚧', show_alert: false });
        await tg('sendMessage', { chat_id, text: 'סטייקינג — בקרוב 🔜\nנעדכן בקבוצה כשהפיצ׳ר יוכרז.', reply_markup: await buildMainMenu() });
        return;
      }

      if (data === 'copy_addr') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'שלחתי את הכתובת להעתקה', show_alert: false });
        await tg('sendMessage', { chat_id, text: SELLER || '—', reply_markup: await buildMainMenu() });
        return;
      }

      if (data === 'copy_wallet') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'שלחתי @wallet להעתקה', show_alert: false });
        await tg('sendMessage', { chat_id, text: '@wallet', reply_markup: await buildMainMenu() });
        return;
      }

      if (data === 'back_menu') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        await tg('sendMessage', { chat_id, text: 'תפריט:', reply_markup: await buildMainMenu() });
        return;
      }

      // 0.001 TON
      if (data === 'pay_min_ton') {
        const tonAmt = 0.001;
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        await tg('sendMessage', {
          chat_id,
          text: donationText(tonAmt),
          disable_web_page_preview: true,
          reply_markup: paymentKeyboard()
        });
        return;
      }

      // קיצורי ₪
      const quick = data.match(/^pay_ils_(\d+)$/);
      if (quick) {
        const ils = Number(quick[1]);
        try {
          const rate = await fetchTonPriceILS();
          const ton = Math.max(0.001, +(ils / rate).toFixed(3));
          await tg('sendMessage', {
            chat_id,
            text: donationText(ton),
            disable_web_page_preview: true,
            reply_markup: paymentKeyboard()
          });
        } catch (e) {
          console.error('[price quick]', e?.message || e);
          await tg('sendMessage', {
            chat_id,
            text: 'לא הצלחתי להביא שער כעת. הקלד/י סכום ב-TON (למשל: 1).',
            reply_markup: await buildMainMenu()
          });
        }
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        return;
      }

      if (data === 'pay_ils') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'הקלד/י סכום בש״ח…', show_alert: false });
        await tg('sendMessage', {
          chat_id,
          text: 'הקלד/י בבקשה סכום בש״ח (לדוגמה: 50). אמיר ל-TON ואחזיר הוראות 👇',
          reply_markup: await buildMainMenu()
        });
        return;
      }

      await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'בוצע', show_alert: false });
      return;
    }

    // MESSAGE
    const msg = update.message || update.edited_message;
    if (!msg) return;
    const chat_id = msg.chat.id;
    const text = (msg.text || '').trim();

    // /start — עם תמונה + תפריט דינמי
    if (text.startsWith('/start')) {
      const kb = await buildMainMenu();
      if (HERO_IMAGE_URL) {
        await tg('sendPhoto', {
          chat_id,
          photo: HERO_IMAGE_URL,
          caption: startCombinedCaption(),
          parse_mode: 'Markdown',
          reply_markup: kb
        });
      } else {
        await tg('sendMessage', {
          chat_id,
          text: startCombinedCaption(),
          parse_mode: 'Markdown',
          reply_markup: kb,
          disable_web_page_preview: true
        });
      }
      return;
    }

    // /menu
    if (text === '/menu') {
      await tg('sendMessage', { chat_id, text: 'תפריט:', reply_markup: await buildMainMenu() });
      return;
    }

    // הודעה שנראית כמו ₪ → חישוב + הוראות + כפתורי תשלום (טלגרם בלבד)
    const ilsMaybe = parseIlsLike(text);
    if (ilsMaybe) {
      try {
        const rate = await fetchTonPriceILS();
        const ton = Math.max(0.001, +(ilsMaybe / rate).toFixed(3));
        await tg('sendMessage', {
          chat_id,
          text: donationText(ton),
          disable_web_page_preview: true,
          reply_markup: paymentKeyboard()
        });
      } catch (e) {
        console.error('[price ils freeform]', e?.message || e);
        await tg('sendMessage', {
          chat_id,
          text: 'לא הצלחתי להביא שער כעת. הקלד/י את הסכום ב-TON (למשל: 1).',
          reply_markup: await buildMainMenu()
        });
      }
      return;
    }

    // טקסט חופשי → AI (אם קיים) אחרת קידום
    if (text) {
      let answer = null;
      if (OPENAI_API_KEY) {
        try { answer = await aiAnswer(text); } catch (e) { console.error('[openai]', e?.message || e); }
      }
      await tg('sendMessage', {
        chat_id,
        text: answer || `לתרומה/תשלום: ${FRONTEND_URL}`,
        reply_markup: await buildMainMenu()
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
