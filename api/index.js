import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors());

const cfg = {
  sellerTonAddress: process.env.SELLER_TON_ADDRESS || '',
  minDonationTon: Number(process.env.MIN_DONATION_TON || '0.5'),
  frontendUrl: process.env.FRONTEND_URL || 'http://localhost:8080',
  communityLink: process.env.TELEGRAM_COMMUNITY_LINK || 'https://t.me/YourCommunity'
};

app.get('/health', (_req, res) => {
  res.json({ ok: true, service: 'api', time: new Date().toISOString() });
});

app.get('/config', (_req, res) => {
  res.json(cfg);
});

// Placeholder for future on-chain verification (Toncenter/TonAPI)
app.post('/log-donation', (req, res) => {
  // Expected body: { fromAddress, amountTon, txHash?, comment? }
  console.log('[donation]', req.body);
  res.json({ ok: true });
});

const port = 4000;
app.listen(port, () => {
  console.log(`[api] listening on http://0.0.0.0:${port}`);
});