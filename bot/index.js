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
// תמונת HERO לפתיחת /start
const HERO_IMAGE_URL = (process.env.HERO_IMAGE_URL || 'https://tonfront.onrender.com/frontendassets/536279550_10237941019841362_2777380265588054892_n.jpg').trim();

// (אופציונלי) לאדמין: chat_id אליו יגיעו צילומי מסך לאישור ידני
const ADMIN_FORWARD_CHAT_ID = process.env.ADMIN_FORWARD_CHAT_ID || ''; // לדוגמה: "123456789"

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

// === תפריט ראשי (מינימלי לפי הדרישה) ===
function mainMenuKeyboard() {
  const rows = [
    [{ text: 'חזרה לאתר', url: FRONTEND_URL }],
    [{ text: 'סטייקינג', callback_data: 'staking_info' }],
    [{ text: 'תמיכה', url: `https://t.me/${SUPPORT_TG_USERNAME}` }],
    [{ text: 'תרומה', callback_data: 'donate_steps' }],
    [{ text: 'חיבור ארנק אישי', callback_data: 'copy_wallet' }],
  ];
  // HIDDEN (נשמר לעתיד): קיצורי ₪ ו-“תשלום מיידי”
  // rows.push([{ text: '₪50', callback_data: 'pay_ils_50' }, { text: '₪100', callback_data: 'pay_ils_100' }, { text: '₪200', callback_data: 'pay_ils_200' }]);
  // rows.push([{ text: 'תשלום מיידי (₪)', callback_data: 'pay_ils' }]);
  // HIDDEN: “שלחת כתובת הארנק שלך”
  // rows.push([{ text: 'שלחת כתובת הארנק שלך', callback_data: 'send_from_addr' }]);
  return { inline_keyboard: rows };
}

// === כפתורי תרומה/אימות לאחר הוראות ===
function donateFlowKeyboard() {
  return {
    inline_keyboard: [
      [{ text: 'פתיחה ב-Telegram Wallet', url: 'https://t.me/wallet' }],
      [{ text: '⬆️ העלאת אישור', callback_data: 'upload_receipt' }],
      [{ text: '✅ אמת תשלום', callback_data: 'verify_payment' }],
      [{ text: '⬅️ חזרה לתפריט', callback_data: 'back_menu' }],
    ]
  };
}

// === הודעת /start מאוחדת (תמונה + כיתוב) ===
function startCombinedCaption() {
  return [
    '*ברוך הבא!* השתמשו בתפריט לקבלת עזרה או מעבר לפלטפורמה.',
    '',
    '• לתרומה: לחצו על ״תרומה״ → קבלו כתובת → פתחו ארנק → בצעו תשלום → העלו צילום → אמתו.',
    '• תמיכה אנושית: לחצו ״תמיכה״.',
    '',
    'לאחר אישור תשלום ההטבה תישלח כאן בבוט.'
  ].join('\n');
}

// === הודעת הוראות תרומה (הודעה #2) ===
function donateInstructionsText(amountHintTon) {
  const lineAmt = amountHintTon ? `סכום שבחרתם קודם: ~${amountHintTon} TON\n\n` : '';
  const siteUrl = `${FRONTEND_URL}?donate=${encodeURIComponent(amountHintTon || 1)}`;
  return [
    `${lineAmt}הוראות לביצוע תרומה:`,
    '1) העתיקו את כתובת הארנק (הודעה מעל).',
    '2) פתחו את Telegram Wallet והדביקו את הכתובת + הסכום.',
    '3) בצעו תשלום.',
    '4) העלו כאן צילום אישור התשלום (Screenshot).',
    '5) לחצו על "✅ אמת תשלום".',
    '',
    `לאחר האישור נשגר לכם את ההטבה. ניתן גם לחזור לאתר: ${siteUrl}`
  ].join('\n');
}

// === טקסט "סטייקינג — בקרוב" ===
function stakingText() {
  return [
    '*בקרוב*',
    '',
    'סטייקינג (Staking) מאפשר לנעול מטבעות לתקופה ולקבל תגמולים. אנחנו מתעכבים בשלב זה כדי לוודא בטיחות משתמשים, שקיפות ודמי סיכון מינימליים.',
    'עם השקת המנגנון נפרסם מדריך מלא בקהילה שלנו ונספק אפשרות ״חד-לחיצה״ מהבוט.',
  ].join('\n');
}

// === AI (אופציונלי) — נשמר לעתיד ===
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

    // CALLBACKS
    if (update.callback_query) {
      const cq = update.callback_query;
      const chat_id = cq.message?.chat?.id;
      const data = cq.data || '';
      if (!chat_id) { await tg('answerCallbackQuery', { callback_query_id: cq.id }); return; }

      if (data === 'back_menu') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        await tg('sendMessage', { chat_id, text: 'תפריט:', reply_markup: mainMenuKeyboard() });
        return;
      }

      if (data === 'staking_info') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        await tg('sendMessage', { chat_id, text: stakingText(), parse_mode: 'Markdown', reply_markup: mainMenuKeyboard() });
        return;
      }

      if (data === 'donate_steps') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        // הודעה #1 — רק הכתובת שלך (נקי להעתקה)
        await tg('sendMessage', { chat_id, text: SELLER || '—' });
        // הודעה #2 — הוראות + כפתורים
        await tg('sendMessage', {
          chat_id,
          text: donateInstructionsText(/* amountHintTon */ null),
          disable_web_page_preview: true,
          reply_markup: donateFlowKeyboard()
        });
        return;
      }

      if (data === 'copy_wallet') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'שלחתי @wallet', show_alert: false });
        await tg('sendMessage', {
          chat_id,
          text: 'כדי לחבר/להתקין ארנק, פתח/י @wallet:',
          reply_markup: {
            inline_keyboard: [
              [{ text: 'פתיחה ב-Telegram Wallet', url: 'https://t.me/wallet' }],
              [{ text: '⬅️ חזרה לתפריט', callback_data: 'back_menu' }]
            ]
          }
        });
        return;
      }

      if (data === 'upload_receipt') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id });
        await tg('sendMessage', {
          chat_id,
          text: 'נא העלו כאן צילום מסך של אישור התשלום (תמונה). לאחר מכן לחצו "✅ אמת תשלום".',
          reply_markup: donateFlowKeyboard()
        });
        return;
      }

      if (data === 'verify_payment') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'מנסה לאמת…', show_alert: false });
        // כאן אפשר לשלב אימות on-chain דרך ה-API שלך (verify-donation) — נשאר לעתיד:
        // await fetch(`${YOUR_API}/verify-donation?...`)
        await tg('sendMessage', {
          chat_id,
          text: 'בדיקה ראשונית הושלמה. אם ההעברה נקלטה — תקבלי/תקבל הטבה בהודעה נפרדת. במקרה הצורך נבדוק ידנית.',
          reply_markup: {
            inline_keyboard: [
              [{ text: '⬅️ חזרה לתפריט', callback_data: 'back_menu' }]
            ]
          }
        });
        return;
      }

      // HIDDEN (לשלבים הבאים): קיצורי ₪ / תשלום מיידי / שלחת כתובת הארנק שלך
      // if (data === 'pay_ils_50' || data === 'pay_ils_100' || data === 'pay_ils_200' || data === 'pay_ils' || data === 'send_from_addr') {
      //   await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'בשלב זה לא זמין בתפריט', show_alert: false });
      //   return;
      // }

      await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'בוצע', show_alert: false });
      return;
    }

    // MESSAGES
    const msg = update.message || update.edited_message;
    if (!msg) return;
    const chat_id = msg.chat.id;
    const text = (msg.text || '').trim();

    // /start — תמונת HERO + הודעה מאוחדת + תפריט
    if (text.startsWith('/start')) {
      if (HERO_IMAGE_URL) {
        await tg('sendPhoto', {
          chat_id,
          photo: HERO_IMAGE_URL,
          caption: startCombinedCaption(),
          parse_mode: 'Markdown',
          reply_markup: mainMenuKeyboard()
        });
      } else {
        await tg('sendMessage', {
          chat_id,
          text: startCombinedCaption(),
          parse_mode: 'Markdown',
          reply_markup: mainMenuKeyboard(),
          disable_web_page_preview: true
        });
      }
      return;
    }

    // קבלת תמונה — נעביר לאדמין (אם קיים), נודה למשתמש
    if (msg.photo && msg.photo.length) {
      await tg('sendMessage', { chat_id, text: 'התקבל צילום מסך. תודה! נעדכן לאחר אימות.', reply_markup: mainMenuKeyboard() });
      if (ADMIN_FORWARD_CHAT_ID) {
        const file_id = msg.photo[msg.photo.length - 1].file_id;
        const fromUser = msg.from?.username ? `@${msg.from.username}` : `${msg.from?.first_name || ''} ${msg.from?.last_name || ''}`.trim();
        await tg('sendPhoto', {
          chat_id: ADMIN_FORWARD_CHAT_ID,
          photo: file_id,
          caption: `אישור תשלום התקבל מ־${fromUser || 'משתמש'} (chat_id=${chat_id}).`,
          reply_markup: {
            inline_keyboard: [
              [{ text: 'אשר', callback_data: `admin_approve_${chat_id}` }],
              [{ text: 'דחה',  callback_data: `admin_reject_${chat_id}` }]
            ]
          }
        });
      }
      return;
    }

    // טקסט חופשי → AI (אם קיים) או קידום כללי
    if (text) {
      let answer = null;
      if (OPENAI_API_KEY) {
        try { answer = await aiAnswer(text); } catch (e) { console.error('[openai]', e?.message || e); }
      }
      await tg('sendMessage', {
        chat_id,
        text: answer || `לתרומה/תשלום: לחצו על "תרומה" בתפריט.`,
        reply_markup: mainMenuKeyboard()
      });
      return;
    }
  } catch (e) {
    console.error('[webhook handler]', e);
  }
});

const PORT = Number(process.env.PORT || 8080);
app.listen(PORT, () => {
  console.log(`[bot] listening on http://0.0.0.0:${PORT}`);
  console.log(`[bot] FRONTEND_URL=${FRONTEND_URL}`);
  console.log(`[bot] SELLER (present)=${!!SELLER}`);
});
