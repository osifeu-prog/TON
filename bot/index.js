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
const API_BASE = (process.env.API_BASE || 'https://ton-2eg2.onrender.com').replace(/\/+$/, '');
const ADMIN_FORWARD_CHAT_ID = process.env.ADMIN_FORWARD_CHAT_ID || '';

if (!TOKEN) console.warn('[bot] TELEGRAM_BOT_TOKEN missing');
const TG_API = `https://api.telegram.org/bot${TOKEN}`;

// === STATE ===
const lastAmountByChat   = new Map(); // chat_id -> last TON amount
const lastAskTsByChat    = new Map(); // chat_id -> ms when asked to pay
const awaitingProof      = new Map(); // chat_id -> waiting for screenshot
const awaitingWallet     = new Map(); // chat_id -> waiting user address
const walletByChat       = new Map(); // chat_id -> EQ../UQ..

// === helpers ===
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
function parseIlsLike(text) {
  if (!text) return null;
  const cleaned = text.replace(/[^\d.,]/g, '').replace(',', '.');
  const v = Number(cleaned);
  return isFinite(v) && v > 0 ? v : null;
}

// אימות דרך ה-API שלך
async function verifyDonationViaAPI({ amountTon, from, sinceTs }) {
  try {
    const u = new URL(API_BASE + '/verify-donation');
    if (amountTon) u.searchParams.set('amountTon', String(amountTon));
    if (from)      u.searchParams.set('from', String(from));
    if (sinceTs)   u.searchParams.set('since', String(sinceTs));
    const r = await fetch(u.toString());
    const j = await r.json();
    if (j && typeof j.verified !== 'undefined') {
      return { ok: true, verified: !!j.verified, via: j.via || 'unknown' };
    }
    return { ok: false, error: 'bad_response' };
  } catch (e) {
    console.error('[verifyDonationViaAPI]', e);
    return { ok: false, error: 'fetch_failed' };
  }
}

// === keyboards ===
async function buildMainMenu() {
  // תוויות דינמיות (כולל מינימום 0.001 TON)
  let minBtnLabel = 'תרומה מזערית 0.001 TON';
  let btn50 = '₪50', btn100 = '₪100', btn200 = '₪200', payAny = 'תשלום מיידי (₪)';
  try {
    const rate = await fetchTonPriceILS();
    minBtnLabel += ` (~${formatILS(0.001 * rate)})`;
    btn50  = `₪50 (~${formatTON(50/rate)} TON)`;
    btn100 = `₪100 (~${formatTON(100/rate)} TON)`;
    btn200 = `₪200 (~${formatTON(200/rate)} TON)`;
    payAny = `תשלום מיידי (₪) • שער ${formatILS(rate)}/TON`;
  } catch {}

  const rows = [
    [{ text: 'חזרה לאתר', url: FRONTEND_URL }],
    [{ text: 'לקבוצה שלנו', url: COMMUNITY }],
    [{ text: 'סטייקינג — בקרוב', callback_data: 'staking_soon' }],
    [{ text: 'תמיכה ב-Telegram', url: `https://t.me/${SUPPORT_TG_USERNAME}` }],
    [{ text: '📋 כתובת שליחה', callback_data: 'copy_addr' }],
    [{ text: '📋 ‏חיבור ארנק אישי', callback_data: 'copy_wallet' }],
    [{ text: '📮 שליחת כתובת הארנק (EQ…/UQ…)', callback_data: 'send_wallet' }],
    [{ text: '✅ אמת תשלום', callback_data: 'verify_payment' }],
  ];
  if (SUPPORT_PHONE) rows.push([{ text: 'תמיכה (טלפון)', url: `tel:${SUPPORT_PHONE}` }]);
  rows.push([{ text: minBtnLabel, callback_data: 'pay_min_ton' }]);
  rows.push([
    { text: btn50,  callback_data: 'pay_ils_50' },
    { text: btn100, callback_data: 'pay_ils_100' },
    { text: btn200, callback_data: 'pay_ils_200' }
  ]);
  rows.push([{ text: payAny, callback_data: 'pay_ils' }]);
  return { inline_keyboard: rows };
}

// deeplink ל-TON (לתשלום ישיר בקליק)
function tonDeepLink(amountTon) {
  const amount = Math.max(0.001, Number(amountTon) || 0.001);
  const nano = Math.round(amount * 1e9);
  const text = encodeURIComponent('Thanks for your work!');
  return SELLER ? `ton://transfer/${SELLER}?amount=${nano}&text=${text}` : null;
}

// כפתורי הוראות תשלום: Telegram Wallet + deeplink + כלים
function paymentKeyboard(amountTon) {
  const deeplink = tonDeepLink(amountTon);
  const rows = [];
  if (deeplink) rows.push([{ text: 'שלם עכשיו (deeplink)', url: deeplink }]);
  rows.push([{ text: 'פתיחה ב-Telegram Wallet', url: 'https://t.me/wallet' }]);
  rows.push([{ text: '📋 כתובת להעתקה', callback_data: 'copy_addr' }]);
  rows.push([{ text: '⬆️ העלאת אישור תשלום', callback_data: 'upload_proof' }]);
  rows.push([{ text: '✅ אמת תשלום', callback_data: 'verify_payment' }]);
  rows.push([{ text: '⬅️ חזרה לתפריט', callback_data: 'back_menu' }]);
  return { inline_keyboard: rows };
}

// === texts ===
function startCombinedCaption() {
  return [
    'ברוך הבא! השתמשו בתפריט/פקודות לקבלת עזרה או מעבר לפלטפורמה.',
    '',
    'לאחר אישור התשלום ההטבה תישלח כאן בבוט.'
  ].join('\n');
}
function donationText(amtTon) {
  const amount = Math.max(0.001, Number(amtTon) || 0.001);
  const siteUrl = `${FRONTEND_URL}?donate=${encodeURIComponent(amount)}`;
  return [
    `סכום התרומה: ${amount} TON.`,
    '',
    'כעת האפליקציה תעביר אתכם לארנק שלכם כדי לבצע תשלום ישירות לכתובת:',
    SELLER || '—',
    '',
    'לאחר התשלום תתבקשו להזין תמונה של אישור תשלום מהארנק שלכם.',
    'את צילום המסך העלו לכאן להמשך.',
    '',
    `בסיום — חזרו לאתר לקבלת ההטבה: ${siteUrl}`
  ].join('\n');
}

// === health ===
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'bot', time: new Date().toISOString() });
});

// === webhook ===
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

      // ← תיקון: מחזיר רק את הכתובת, ואז כפתורי תשלום
      if (data === 'copy_addr') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'הכתובת נשלחה', show_alert: false });
        await tg('sendMessage', { chat_id, text: SELLER || '—' });
        const amt = lastAmountByChat.get(chat_id) || 0.001;
        await tg('sendMessage', {
          chat_id,
          text: 'אפשרויות תשלום:',
          reply_markup: paymentKeyboard(amt)
        });
        return;
      }

      if (data === 'copy_wallet') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'נשלח @wallet', show_alert: false });
        await tg('sendMessage', { chat_id, text: '@wallet' });
        return;
      }

      if (data === 'send_wallet') {
        awaitingWallet.set(chat_id, true);
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'הקלד/י את כתובת הארנק', show_alert: false });
        await tg('sendMessage', { chat_id, text: 'אנא הדבק/י כאן את כתובת הארנק שלך (EQ… או UQ…).' });
        return;
      }

      if (data === 'verify_payment') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'בודק…', show_alert: false });
        const amount = lastAmountByChat.get(chat_id) || 0.001;
        const from   = walletByChat.get(chat_id) || '';
        const since  = lastAskTsByChat.get(chat_id) || (Date.now() - 90 * 60 * 1000);
        if (!from) {
          await tg('sendMessage', { chat_id, text: 'לא התקבלה כתובת ארנק. לחצו "📮 שליחת כתובת הארנק" ושלחו EQ…/UQ…' });
          return;
        }
        const v = await verifyDonationViaAPI({ amountTon: amount, from, sinceTs: since });
        if (v.ok && v.verified) {
          await tg('sendMessage', {
            chat_id,
            text: `אימות הצליח ✅\nסכום: ${amount} TON\nמקור: ${from}\n(דרך ${v.via})\nההטבה תישלח כאן בבוט בהמשך התהליך.`
          });
        } else {
          await tg('sendMessage', {
            chat_id,
            text: 'טרנזקציה לא אותרה עדיין. זה יכול לקחת עד דקה. נסו שוב מאוחר יותר או העלו צילום אישור תשלום.'
          });
        }
        return;
      }

      if (data === 'back_menu') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        await tg('sendMessage', { chat_id, text: 'תפריט:', reply_markup: await buildMainMenu() });
        return;
      }

      if (data === 'upload_proof') {
        awaitingProof.set(chat_id, true);
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'העלו צילום מסך כהודעת תמונה', show_alert: false });
        await tg('sendMessage', { chat_id, text: 'נא לשלוח צילום מסך של אישור התשלום כהודעת *תמונה* (לא קובץ).', parse_mode: 'Markdown' });
        return;
      }

      // מינימום 0.001 TON
      if (data === 'pay_min_ton') {
        const tonAmt = 0.001;
        lastAmountByChat.set(chat_id, tonAmt);
        lastAskTsByChat.set(chat_id, Date.now());
        awaitingProof.set(chat_id, false);
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        await tg('sendMessage', {
          chat_id,
          text: donationText(tonAmt),
          disable_web_page_preview: true,
          reply_markup: paymentKeyboard(tonAmt)
        });
        return;
      }

      // ₪ מהירים
      const quick = data.match(/^pay_ils_(\d+)$/);
      if (quick) {
        const ils = Number(quick[1]);
        try {
          const rate = await fetchTonPriceILS();
          const ton = Math.max(0.001, +(ils / rate).toFixed(3));
          lastAmountByChat.set(chat_id, ton);
          lastAskTsByChat.set(chat_id, Date.now());
          awaitingProof.set(chat_id, false);
          await tg('sendMessage', {
            chat_id,
            text: donationText(ton),
            disable_web_page_preview: true,
            reply_markup: paymentKeyboard(ton)
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

    // /start — תמונה + תפריט
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

    // אם מצפים להוכחה — קבל צילום
    if (awaitingProof.get(chat_id) && msg.photo && msg.photo.length) {
      const file_id = msg.photo[msg.photo.length - 1].file_id;
      const amount = lastAmountByChat.get(chat_id) || null;

      await tg('sendMessage', { chat_id, text: 'תודה! קיבלנו את צילום האישור. נבדוק ונשלח את ההטבה לאחר אימות ✅' });
      if (ADMIN_FORWARD_CHAT_ID) {
        await tg('sendPhoto', {
          chat_id: ADMIN_FORWARD_CHAT_ID,
          photo: file_id,
          caption: `אישור תשלום מהמשתמש.\nChat: ${chat_id}\nAmount: ${amount ?? '-'} TON`
        });
      }
      awaitingProof.set(chat_id, false);
      return;
    }

    // אם מצפים לכתובת ארנק — שמור
    if (awaitingWallet.get(chat_id) && text) {
      const addr = text.replace(/\s+/g,'').trim();
      const ok = /^[EU]Q[A-Za-z0-9_-]{46,}$/.test(addr);
      if (ok) {
        walletByChat.set(chat_id, addr);
        awaitingWallet.set(chat_id, false);
        await tg('sendMessage', {
          chat_id,
          text: `כתובת נשמרה: ${addr.slice(0,6)}…${addr.slice(-6)}\nכעת ניתן ללחוץ "✅ אמת תשלום".`,
          reply_markup: await buildMainMenu()
        });
        return;
      } else {
        await tg('sendMessage', { chat_id, text: 'הכתובת לא נראית תקינה. ודאו EQ…/UQ… ונסו שוב.' });
        return;
      }
    }

    // הודעה שנראית כמו ₪ → המרה + הוראות + כפתורי תשלום
    const ilsMaybe = parseIlsLike(text);
    if (ilsMaybe) {
      try {
        const rate = await fetchTonPriceILS();
        const ton = Math.max(0.001, +(ilsMaybe / rate).toFixed(3));
        lastAmountByChat.set(chat_id, ton);
        lastAskTsByChat.set(chat_id, Date.now());
        awaitingProof.set(chat_id, false);
        await tg('sendMessage', {
          chat_id,
          text: donationText(ton),
          disable_web_page_preview: true,
          reply_markup: paymentKeyboard(ton)
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

    // טקסט חופשי → AI (אם קיים) או קידום
    if (text) {
      let answer = null;
      if (OPENAI_API_KEY) {
        try {
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
            messages: [{ role: 'system', content: system }, { role: 'user', content: text }],
            temperature: 0.3,
            max_tokens: 350
          });
          answer = resp.choices?.[0]?.message?.content?.trim() || null;
        } catch(e) { console.error('[openai]', e?.message || e); }
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
