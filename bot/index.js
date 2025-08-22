import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import { Telegraf, Markup } from 'telegraf';
import OpenAI from 'openai';

const {
  TELEGRAM_BOT_TOKEN,
  FRONTEND_URL = 'https://tonfront.onrender.com',
  TELEGRAM_COMMUNITY_LINK = 'https://t.me/YourCommunity',
  OPENAI_API_KEY,
  BOT_PUBLIC_URL, // נעדכן אחרי הדיפלוי הראשון
  PORT
} = process.env;

if (!TELEGRAM_BOT_TOKEN) {
  console.error('[bot] TELEGRAM_BOT_TOKEN missing');
  process.exit(1);
}

const bot = new Telegraf(TELEGRAM_BOT_TOKEN);

// ---- Handlers ----
bot.start((ctx) => ctx.reply(
  'ברוכים הבאים! כאן תוכלו לתמוך ביוצר דרך TON ולקבל גישה לתוכן.\nבחרו פעולה:',
  Markup.inlineKeyboard([
    [Markup.button.url('כניסה לפלטפורמה', FRONTEND_URL)],
    [Markup.button.url('הצטרפות לקהילה', TELEGRAM_COMMUNITY_LINK)],
    [Markup.button.callback('איך זה עובד?', 'HOWITWORKS')]
  ])
));

bot.action('HOWITWORKS', async (ctx) => {
  await ctx.answerCbQuery();
  await ctx.reply('נכנסים לפלטפורמה, בוחרים סכום תרומה, ולוחצים "תרום עכשיו". אפשר דרך ארנק TON בנייד/דפדפן.');
});

bot.command('donate', (ctx) => {
  ctx.reply('לתרומה מהירה:', Markup.inlineKeyboard([
    [Markup.button.url('פתח את חנות ה-TON', FRONTEND_URL)]
  ]));
});

bot.command('ask', async (ctx) => {
  const prompt = ctx.message.text.replace('/ask', '').trim();
  if (!prompt) return ctx.reply('שלחו: /ask <שאלה>');
  if (!OPENAI_API_KEY) return ctx.reply('תכונת AI מושבתת (אין OPENAI_API_KEY).');
  try {
    const openai = new OpenAI({ apiKey: OPENAI_API_KEY });
    const resp = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are a helpful assistant that routes users to a TON tip-based storefront." },
        { role: "user", content: prompt }
      ]
    });
    const text = resp.choices?.[0]?.message?.content?.trim() || '—';
    await ctx.reply(text + `\n\n👉 פתח תשלומים ב-TON: ${FRONTEND_URL}`);
  } catch (e) {
    console.error(e);
    await ctx.reply('שגיאה בפניית AI.');
  }
});

// ---- Webhook server ----
const app = express();
app.use(express.json());
app.get('/health', (_req, res) => res.json({ ok: true, service: 'bot', time: new Date().toISOString() }));

// כל קריאות ה-webhook יגיעו לנתיב /webhook
app.use('/webhook', bot.webhookCallback('/webhook'));

// קובע webhook אוטומטית פעם אחת כשהשרת עולה (אם יש URL ציבורי)
(async () => {
  const base = (BOT_PUBLIC_URL || '').replace(/\/$/, '');
  if (base.startsWith('http')) {
    const url = `${base}/webhook`;
    try {
      await bot.telegram.setWebhook(url);
      console.log('[bot] setWebhook:', url);
    } catch (e) {
      console.error('[bot] setWebhook error:', e.message);
    }
  } else {
    console.warn('[bot] BOT_PUBLIC_URL not set yet; set it to your Render URL and redeploy.');
  }
})();

const port = Number(PORT || 10000);
app.listen(port, () => console.log(`[bot] listening on :${port}`));
