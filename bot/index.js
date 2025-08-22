import dotenv from 'dotenv';
dotenv.config();

import { Telegraf, Markup } from 'telegraf';
import OpenAI from 'openai';

const token = process.env.TELEGRAM_BOT_TOKEN;
if (!token) {
  console.log('[bot] TELEGRAM_BOT_TOKEN not set. Bot will not start.');
  process.exit(0);
}

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:8080';
const COMMUNITY = process.env.TELEGRAM_COMMUNITY_LINK || 'https://t.me/YourCommunity';
const openaiKey = process.env.OPENAI_API_KEY;

const bot = new Telegraf(token);

bot.start((ctx) => {
  return ctx.reply(
    'ברוכים הבאים! כאן תוכלו לתמוך ביוצר דרך TON ולקבל גישה לתוכן.\nבחרו פעולה:',
    Markup.inlineKeyboard([
      [Markup.button.url('כניסה לפלטפורמה', FRONTEND_URL)],
      [Markup.button.url('הצטרפות לקהילה', COMMUNITY)],
      [Markup.button.callback('איך זה עובד?', 'HOWITWORKS')]
    ])
  );
});

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
  if (!openaiKey) return ctx.reply('תכונת AI מושבתת (אין OPENAI_API_KEY).');

  try {
    const openai = new OpenAI({ apiKey: openaiKey });
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

bot.launch().then(() => {
  console.log('[bot] started');
});

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));