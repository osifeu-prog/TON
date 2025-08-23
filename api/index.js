import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// MVP: לא מגבילים מקור (אפשר להקשיח מאוחר יותר)
app.use(cors());
app.use(express.json());

// בריאות
app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'api', time: new Date().toISOString() });
});

// קונפיג דינמי (קורא את ה-ENV בכל קריאה)
app.get('/config', (_req, res) => {
  const seller = process.env.SELLER_TON_ADDRESS || '';
  const minAmt = Number(process.env.MIN_DONATION_TON || 0.5);
  const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:8080';
  const community = process.env.TELEGRAM_COMMUNITY_LINK || '';
  const bot = process.env.TELEGRAM_BOT_LINK || ''; // אופציונלי: קישור ישיר לבוט

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
  console.log('[donation]', req.body); // { fromAddress, amountTon, txHash?, comment? }
  res.json({ ok: true });
});

// דף שורש ידידותי
app.get('/', (_req, res) => {
  res.type('text/plain').send('TON API is running. Try GET /health or /config');
});

// Render נותן PORT; לוקאלית נשתמש ב-4000
const port = Number(process.env.PORT) || 4000;
app.listen(port, () => {
  console.log(`[api] listening on http://0.0.0.0:${port}`);
});
