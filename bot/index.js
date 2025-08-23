import express from 'express';
import dotenv from 'dotenv';
import { Telegraf } from 'telegraf';

dotenv.config();

const app = express();
app.use(express.json());

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const PUBLIC_URL = (process.env.BOT_PUBLIC_URL || '').replace(/\/+$/,''); // בלי / בסוף
const FRONTEND_URL = process.env.FRONTEND_URL || 'https://tonfront.onrender.com';

if (!BOT_TOKEN) {
  console.error('TELEGRAM_BOT_TOKEN missing');
  process.exit(1);
}

const bot = new Telegraf(BOT_TOKEN, { handlerTimeout: 9_000 });

bot.start(async (ctx) => {
  const p = ctx.startPayload || '';
  if (p.startsWith('donate_')) {
    const amt = p.slice('donate_'.length);
    await ctx.reply(`מעולה! סכום מוצע: ${amt} TON.
1) פתחו את הארנק ובצעו תשלום.
2) חזרו לאתר לקבלת ההטבה: ${FRONTEND_URL}`);
  } else if (p === 'help') {
    await ctx.reply(`שאלות? אנחנו כאן. אפשר לחזור לאתר: ${FRONTEND_URL}`);
  } else {
    await ctx.reply('ברוך הבא! השתמשו בתפריט/פקודות לקבלת עזרה או מעבר לפלטפורמה.');
  }
});

// health
app.get('/health', (_req,res) => res.json({ ok:true, service:'bot', time:new Date().toISOString() }));

// webhook
const path = '/webhook';
app.use(bot.webhookCallback(path));

// set webhook on startup (idempotent)
async function setup() {
  if (!PUBLIC_URL) {
    console.error('BOT_PUBLIC_URL missing (e.g. https://tonbot-xxxx.onrender.com)');
    process.exit(1);
  }
  const hook = `${PUBLIC_URL}${path}`;
  await bot.telegram.setWebhook(hook);
  console.log('[bot] webhook set to', hook);
}
setup().catch(e => { console.error(e); process.exit(1); });

const port = Number(process.env.PORT || 8080);
app.listen(port, () => console.log(`[bot] listening on :${port}`));
