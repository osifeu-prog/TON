import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Health
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'api', time: new Date().toISOString() });
});

// /config — קורא ENV ואם חסר משתמש בברירות מחדל שלך
app.get('/config', (_req, res) => {
  const seller = process.env.SELLER_TON_ADDRESS
    || 'UQBX966g9mS9mQfuoZbFpwtX63wiBaX2t7cdHvH6htm7O4-v'; // fallback ציבורי
  const minAmt = Number(process.env.MIN_DONATION_TON || 1);
  const frontendUrl = process.env.FRONTEND_URL || 'https://tonfront.onrender.com';
  const community = process.env.TELEGRAM_COMMUNITY_LINK
    || 'https://t.me/+HIzvM8sEgh1kNWY0';
  const bot = process.env.TELEGRAM_BOT_LINK
    || 'https://t.me/hbdcommunity_bot';

  res.json({
    ok: true,
    sellerTonAddress: seller,
    minDonationTon: minAmt,
    frontendUrl,
    communityLink: community,
    botLink: bot
  });
});

// לוג תרומות (placeholder)
app.post('/log-donation', (req, res) => {
  console.log('[donation]', req.body);
  res.json({ ok: true });
});

// דף שורש ידידותי
app.get('/', (_req, res) => {
  res.type('text/plain').send('TON API is running. Try GET /health or /config');
});

// Render מספק PORT; לוקאלית 4000
const port = Number(process.env.PORT) || 4000;
app.listen(port, () => {
  console.log(`[api] listening on http://0.0.0.0:${port}`);
});
