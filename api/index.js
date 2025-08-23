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

// Config (ENV → JSON)  — כולל botLink
app.get('/config', (_req, res) => {
  const seller = process.env.SELLER_TON_ADDRESS || '';
  const minAmt = Number(process.env.MIN_DONATION_TON || 0.5);
  const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:8080';
  const community = process.env.TELEGRAM_COMMUNITY_LINK || '';
  const bot = process.env.TELEGRAM_BOT_LINK || '';

  res.json({
    ok: true,
    sellerTonAddress: seller,
    minDonationTon: minAmt,
    frontendUrl,
    communityLink: community,
    botLink: bot
  });
});

// Placeholder לוג תרומה
app.post('/log-donation', (req, res) => {
  console.log('[donation]', req.body);
  res.json({ ok: true });
});

// דף שורש ידידותי
app.get('/', (_req, res) => {
  res.type('text/plain').send('TON API is running. Try GET /health or /config');
});

const port = Number(process.env.PORT) || 4000;
app.listen(port, () => {
  console.log(`[api] listening on http://0.0.0.0:${port}`);
});
