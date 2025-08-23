import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import { Telegraf, Markup } from 'telegraf';
// "ask" אופציונלי; אם אין OPENAI_API_KEY לא נשתמש
import OpenAI from 'openai';

const {
  TELEGRAM_BOT_TOKEN,
  FRONTEND_URL = 'https://tonfront.onrender.com',
  TELEGRAM_COMMUNITY_LINK = 'https://t.me/+HIzvM8sEgh1kNWY0',
  BOT_PUBLIC_URL = '', // לדוגמה: https://tonbot-n6q0.onrender.com  (בלי / בסוף)
  OPENAI_API_KEY,
  PORT
} = process.env;

if (!TELEGRAM_BOT_TOKEN) {
  console.error('[bot] Missing TELEGRAM_BOT_TOKEN');
  process.exit(1);
}

const bot = new Telegraf(TELEGRAM_BOT_TOKEN);

// ===== Handlers =====
bot.start((ctx) => ctx.reply(
  'ברוך הבא! כאן תוכל לתרום ליוצר ולקבל גישה לתוכן.\nבחר פעולה:',
  Markup.inlineKeyboard([
    [Markup.button.url('כניסה לפלטפורמה', FRONTEND_URL)],
    [Markup.button.url('הצטרפות לקהילה', TELEGRAM_COMMUNITY_LINK)],
    [Markup.button.callback('איך זה עובד?', 'HOWITWORKS')]
  ])
));

bot.action('HOWITWORKS', async (ctx) => {
  await ctx.answerCbQuery();
  await ctx.reply('נכנסים לפלטפורמה, בוחרים סכום, ולוחצים "שלם דרך הארנק" או משלימים דרך הטלגרם.');
});

bot.command('donate', (ctx) => {
  ctx.reply('לתרומה מהירה:', Markup.inlineKeyboard([
    [Markup.button.url('פתח את הפלטפורמה', FRONTEND_URL)]
  ]));
});

// אופציונלי: /ask אם תוסיף OPENAI_API_KEY
bot.command('ask', async (ctx) => {
  const prompt = ctx.message.text.replace('/ask', '').trim();
  if (!prompt) return ctx.reply('שלחו: /ask <שאלה>');
  if (!OPENAI_API_KEY) return ctx.reply('תכונת AI מושבתת (אין OPENAI_API_KEY).');

  try {
    const openai = new OpenAI({ apiKey: OPENAI_API_KEY });
    const resp = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a helpful assistant that routes users to a TON tip-based storefront.' },
        { role: 'user', content: prompt }
      ]
    });
    const text = resp.choices?.[0]?.message?.content?.trim() || '—';
    await ctx.reply(text + `\n\n👉 פתיחת תשלומים: ${FRONTEND_URL}`);
  } catch (e) {
    console.error(e);
    await ctx.reply('שגיאה בפניית AI.');
  }
});

// ===== Webhook server =====
const app = express();
app.use(express.json());

// בריאות + עמוד שורש נחמד
app.get('/health', (_req, res) => res.json({ ok: true, service: 'bot', time: new Date().toISOString() }));
app.get('/', (_req, res) => res.type('text/plain').send('TON bot is running. Webhook at /webhook'));

// כל קריאות ה-webhook יגיעו לנתיב /webhook
app.use('/webhook', bot.webhookCallback('/webhook'));

// קובע webhook אוטומטית כשהשרת עולה (אם יש URL ציבורי)
(async () => {
  const base = (BOT_PUBLIC_URL || '').replace(/\/$/, ''); // מוריד / בסוף אם יש
  if (base.startsWith('http')) {
    const url = `${base}/webhook`;
    try {
      await bot.telegram.setWebhook(url);
      console.log('[bot] setWebhook:', url);
    } catch (e) {
      console.error('[bot] setWebhook error:', e.message);
    }
  } else {
    console.warn('[bot] BOT_PUBLIC_URL not set; set it to your Render URL and redeploy.');
  }
})();

const port = Number(PORT || 10000);
app.listen(port, () => console.log(`[bot] listening on :${port}`));
