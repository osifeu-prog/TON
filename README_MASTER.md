# SLH FULL SUITE – TON Engine · Botshop · SLH Wallet

מונורפו מאוחד שמכיל את שלושת הרכיבים העיקריים של האקו־סיסטם:

- `TON-engine/` – מנוע ניתוח טכני, ניהול סיכונים, ושרת Flask כולל דשבורד ו-Web Portal.
- `botshop/` – שער כניסה קהילתי / בוט טלגרם לקמפיינים, לידים וקבוצות SLH.
- `slh-wallet/` – שירות ארנק SLH / API פיננסי.

## הרצה מהירה ל-TON-engine + אתר

```bash
cd SLH_FULL_SUITE/TON-engine
python -m venv .venv
.venv\Scripts\activate  # ב-Windows
pip install -r requirements.txt
python "🌐 SERVER & API/app.py"
```

ואז:

- `http://localhost:8080/site` – אתר ה-Web שמדבר עם ה-API של המנוע (`/health`, `/analysis`, `/multi_analysis`).
- כפתור "בדיקת יתרות ארנק" קורא לשירות SLH Wallet בכתובת שמוגדרת בקבוע `WALLET_BASE_URL` בקובץ `web/app.js`.

## המשך

- להריץ את `slh-wallet` על פורט 8081 (לדוגמה) ולוודא שיש endpoint כמו `/balances`.
- להתאים את `WALLET_BASE_URL` לערך המתאים.
- לחבר את Botshop ככניסה שיווקית ולשלב ניתוחים טכניים ובדיקת ארנק כחלק מזרימת המשתמשים.
