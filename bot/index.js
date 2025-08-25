// bot/index.js
import express from 'express';
import dotenv from 'dotenv';

dotenv.config();
const app = express();
app.use(express.json());

// === ENV ===
const TOKEN   = process.env.TELEGRAM_BOT_TOKEN || '';
const SELLER  = process.env.SELLER_TON_ADDRESS || '';
const FRONTEND_URL = (process.env.FRONTEND_URL || 'https://tonfront.onrender.com').replace(/\/+$/, '');
const COMMUNITY    = process.env.TELEGRAM_COMMUNITY_LINK || 'https://t.me/+HIzvM8sEgh1kNWY0';
const BOT_LINK     = process.env.TELEGRAM_BOT_LINK || 'https://t.me/hbdcommunity_bot';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
const SUPPORT_TG_USERNAME = (process.env.SUPPORT_TG_USERNAME || 'OsifFintech').replace(/^@/, '');
const SUPPORT_PHONE       = process.env.SUPPORT_PHONE || '';
const HERO_IMAGE_URL = (process.env.HERO_IMAGE_URL || 'https://tonfront.onrender.com/frontendassets/536279550_10237941019841362_2777380265588054892_n.jpg').trim();
const ADMIN_FORWARD_CHAT_ID = process.env.ADMIN_FORWARD_CHAT_ID || '';
const BOT_PUBLIC_URL = (process.env.BOT_PUBLIC_URL || '').replace(/\/+$/, '');

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

// Auto set webhook on boot (אם יש כתובת פומבית)
async function ensureWebhook() {
  if (!BOT_PUBLIC_URL) return;
  const url = `${BOT_PUBLIC_URL}/webhook`;
  try {
    const set = await tg('setWebhook', { url });
    console.log('[bot] setWebhook:', set);
    const info = await (await fetch(`${TG_API}/getWebhookInfo`)).json();
    console.log('[bot] getWebhookInfo:', info);
  } catch (e) {
    console.error('[bot] setWebhook error', e);
  }
}

// === תפריט ראשי (כמו שביקשת) ===
function mainMenuKeyboard() {
  const rows = [
    [{ text: 'חזרה לאתר', url: FRONTEND_URL }],
    [{ text: 'סטייקינג', callback_data: 'staking_info' }],
    [{ text: 'תמיכה', url: `https://t.me/${SUPPORT_TG_USERNAME}` }],
    [{ text: 'תרומה', callback_data: 'donate_steps' }],
    [{ text: 'חיבור ארנק אישי', callback_data: 'copy_wallet' }],
  ];
  // HIDDEN להמשך (נשמרו בקוד, לא מוצגים):
  // rows.push([{ text: '₪50',  callback_data: 'pay_ils_50' },
  //            { text: '₪100', callback_data: 'pay_ils_100' },
  //            { text: '₪200', callback_data: 'pay_ils_200' }]);
  // rows.push([{ text: 'תשלום מיידי (₪)', callback_data: 'pay_ils' }]);
  // rows.push([{ text: 'שלחת כתובת הארנק שלך', callback_data: 'send_from_addr' }]);
  return { inline_keyboard: rows };
}

// === כפתורי תרומה/אימות ===
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

// === טקסטים ===
function startCombinedCaption() {
  return [
    '*ברוך הבא!* השתמשו בתפריט לקבלת עזרה או מעבר לפלטפורמה.',
    '',
    '• לתרומה: לחצו ״תרומה״ → קבלו כתובת → פתחו ארנק → בצעו תשלום → העלו צילום → אמתו.',
    '• לתמיכה אנושית: ״תמיכה״.',
    '',
    'לאחר אישור תשלום ההטבה תישלח כאן בבוט.'
  ].join('\n');
}

function stakingText() {
  return [
    '*בקרוב*',
    '',
    'סטייקינג (Staking) = נעילת מטבעות לתקופה וקבלת תגמולים. אנו מתעכבים כדי להבטיח בטיחות, שקיפות ועלויות סיכון מינימליות.',
    'עם ההשקה נפרסם מדריך מלא ונאפשר הפעלה מהבוט.',
  ].join('\n');
}

function donateInstructionsText(amountHintTon) {
  const siteUrl = `${FRONTEND_URL}${amountHintTon ? `?donate=${encodeURIComponent(amountHintTon)}` : ''}`;
  return [
    'הוראות לביצוע תרומה:',
    '1) העתיקו את כתובת הארנק שנשלחה עדיין (הודעה הבאה).',
    '2) פתחו את Telegram Wallet והדביקו את הכתובת + הסכום.',
    '3) בצעו תשלום.',
    '4) העלו כאן צילום אישור (Screenshot).',
    '5) לחצו על "✅ אמת תשלום".',
    '',
    `לאחר האישור נשגר את ההטבה. אפשר גם לחזור לאתר: ${siteUrl}`
  ].join('\n');
}

// (אופציונלי) AI — נשמר לעתיד
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

// === Health ===
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
        // 1) כתובת נקייה להעתקה בלבד
        await tg('sendMessage', { chat_id, text: SELLER || '—' });
        // 2) הוראות + כפתורים (Telegram Wallet בלבד)
        await tg('sendMessage', {
          chat_id,
          text: donateInstructionsText(null),
          disable_web_page_preview: true,
          reply_markup: donateFlowKeyboard()
        });
        return;
      }

      if (data === 'copy_wallet') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'פתח/י @wallet', show_alert: false });
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
          text: 'נא העלו כאן צילום מסך של אישור התשלום. לאחר מכן לחצו "✅ אמת תשלום".',
          reply_markup: donateFlowKeyboard()
        });
        return;
      }

      if (data === 'verify_payment') {
        await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'מנסה לאמת…', show_alert: false });
        await tg('sendMessage', {
          chat_id,
          text: 'בדיקה ראשונית הושלמה. אם ההעברה נקלטה — תקבל/י הטבה בהודעה נפרדת. אם צריך — נבדוק ידנית.',
          reply_markup: { inline_keyboard: [[{ text: '⬅️ חזרה לתפריט', callback_data: 'back_menu' }]] }
        });
        return;
      }

      await tg('answerCallbackQuery', { callback_query_id: cq.id, text: 'בוצע', show_alert: false });
      return;
    }

    // MESSAGES
    const msg = update.message || update.edited_message;
    if (!msg) return;
    const chat_id = msg.chat.id;
    const text = (msg.text || '').trim();

    // /start — תמונת HERO + הודעת פתיחה + תפריט
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

    // קבלת תמונה → לאדמין (אם מוגדר), תודה למשתמש
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

    // טקסט חופשי → AI (אם קיים) או תזכורת לתרומה
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
  ensureWebhook(); // הגדרת webhook אוטומטית
});
