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
const COMMUNITY = process.env.TELEGRAM_COMMUNITY_LINK || 'https://t.me/+HIzvM8sEgh1kNWY0';
const BOT_LINK  = process.env.TELEGRAM_BOT_LINK || 'https://t.me/hbdcommunity_bot';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';

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

// תפריט ראשי: 3 לחצנים
function mainMenuKeyboard() {
  return {
    inline_keyboard: [
      [{ text: 'חזרה לאתר', url: FRONTEND_URL }],
      [{ text: 'לקבוצה שלנו', url: COMMUNITY }],
      [{ text: 'סטייקינג — בקרוב', callback_data: 'staking_soon' }],
    ]
  };
}

// הודעת תרומה בסיסית (לשימוש עתידי אם תרצה)
function donationText(amt) {
  const amount = Number(amt) || 1;
  const nano = Math.round(amount * 1e9);
  const tonDeep = SELLER
    ? `ton://transfer/${SELLER}?amount=${nano}&text=${encodeURIComponent('Thanks for your work!')}`
    : null;
  const siteUrl = `${FRONTEND_URL}?donate=${encodeURIComponent(amount)}`;
  const lines = [];
  if (tonDeep) lines.push(`ארנק TON (deeplink): ${tonDeep}`);
  lines.push(`סכום מוצע: ${amount} TON`);
  lines.push(`אתר: ${siteUrl}`);
  lines.push(`Telegram Wallet: https://t.me/wallet`);
  return lines.join('\n');
}

// תשובת AI (אם הוגדר OPENAI_API_KEY)
async function aiAnswer(userText) {
  if (!OPENAI_API_KEY) return null;
  const { default: OpenAI } = await import('openai');
  const client = new OpenAI({ apiKey: OPENAI_API_KEY });
  const system = [
    'אתה עוזר חכם עבור קהילת TON.',
    'הנחיה: הפנה משתמשים לתשלום/תרומה דרך האתר או הארנק; אל תבקש פרטים אישיים.',
    `קישור אתר: ${FRONTEND_URL}.`,
    COMMUNITY ? `קהילה: ${COMMUNITY}.` : '',
    BOT_LINK ? `בוט: ${BOT_LINK}.` : '',
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

// בריאות
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'bot', time: new Date().toISOString() });
});

// Webhook
app.post('/webhook', async (req, res) => {
  try {
    const update = req.body;
    res.json({ ok: true }); // עונים מיידית לטלגרם

    // --- CALLBACK (לחיצה על כפתור ב-Inline Keyboard) ---
    if (update.callback_query) {
      const cq = update.callback_query;
      const chat_id = cq.message?.chat?.id;
      const data = cq.data || '';

      if (data === 'staking_soon') {
        // Toast קטן למעלה
        await tg('answerCallbackQuery', {
          callback_query_id: cq.id,
          text: 'בקרוב! צוות הפיתוח עובד על זה 🚧',
          show_alert: false
        });
        // הודעה רגילה לצ׳אט (אופציונלי)
        if (chat_id) {
          await tg('sendMessage', {
            chat_id,
            text: 'סטייקינג — בקרוב 🔜.\nנעדכן בקבוצה כשהפיצ׳ר יוכרז.',
            reply_markup: mainMenuKeyboard()
          });
        }
      } else {
        await tg('answerCallbackQuery', {
          callback_query_id: cq.id,
          text: 'בוצע',
          show_alert: false
        });
      }
      return;
    }

    // --- MESSAGE ---
    const msg = update.message || update.edited_message;
    if (!msg) return;
    const chat_id = msg.chat.id;
    const text = (msg.text || '').trim();

    // /start עם payload
    if (text.startsWith('/start')) {
      const payload = text.split(' ')[1] || '';
      if (payload.startsWith('donate_')) {
        const amt = payload.split('_')[1] || '1';
        await tg('sendMessage', {
          chat_id,
          text: `תרומה/תשלום ב-TON\n\n${donationText(amt)}`,
          disable_web_page_preview: true,
          reply_markup: mainMenuKeyboard()
        });
        return;
      }
      // /start רגיל → תפריט 3 לחצנים
      await tg('sendMessage', {
        chat_id,
        text: `ברוך הבא!`,
        reply_markup: mainMenuKeyboard()
      });
      return;
    }

    // /menu — הצגת התפריט בכל רגע
    if (text === '/menu') {
      await tg('sendMessage', {
        chat_id,
        text: 'תפריט:',
        reply_markup: mainMenuKeyboard()
      });
      return;
    }

    // טקסט חופשי → AI (אם קיים), אחרת תשובה קצרה + תפריט
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
