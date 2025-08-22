# TON Shop Starter — חנות תרומות מהירה על רשת TON + בוט טלגרם

MVP מוכן להרמה מהירה: דף חנות מעוצב, קישור תרומה בכמה קליקים, וקהילה בטלגרם עם בוט AI שמנתב אנשים לתשלום.

## מה בפנים
- **frontend/** — אתר סטטי (Nginx) עם UI מודרני (Tailwind CDN). דף "מידע/מוצר" עם כפתור "תרום כדי לתמוך".
- **api/** — Express קטן ל־/health ו־/config שמגיש קונפיג ל־frontend (כתובת TON, סכום ברירת מחדל, לינק לטלגרם).
- **bot/** — בוט טלגרם (Telegraf). /start שולח כפתורים: "כניסה לפלטפורמה" ו-"הצטרפות לקהילה". /ask (אופציונלי) משתמש ב־OpenAI אם יש API key.
- **docker-compose.yml** — הרמה בפקודה אחת.
- **.env.example** — ערכי סביבה (העתק ל־`.env` ועדכן).

> הערה: זהו מודל תרומה "רכה" (Soft Paywall) שמנגיש את המידע ומשדל לתרום. אפשר להקשיח בהמשך ע"י אימות טרנזאקציה מק链 (Toncenter/TonAPI).

---

## הרמה מהירה (Docker)

1) התקן Docker + Docker Compose (Windows/Mac/Linux).
2) פרוס את ה־ZIP לתיקייה, פתח טרמינל בתיקייה הראשית, צור `.env`:
```
cp .env.example .env
```
3) ערוך את `.env` (לפחות את `SELLER_TON_ADDRESS` ו־`TELEGRAM_BOT_TOKEN` אם תרצה בוט פעיל).
4) הרם:
```
docker compose up --build
```
5) דפדפן: http://localhost:8080  
   API: http://localhost:4000/health

> אם אין לך עדיין טוקן לבוט טלגרם, קבל מ־@BotFather והדבק ל־`.env`.

---

## קבצי קונפיג
**.env.example**
```
# כתובת ה-TON שתקבל אליה תרומות
SELLER_TON_ADDRESS=EQC_your_TON_wallet_address_here

# סכום ברירת מחדל לתרומה (ב-TON, ניתן לשנות בדף עצמו)
MIN_DONATION_TON=0.5

# כתובת בסיס של הפרונט
FRONTEND_URL=http://localhost:8080

# קישור לקהילה בטלגרם
TELEGRAM_COMMUNITY_LINK=https://t.me/YourCommunity

# טוקן בוט טלגרם (לא חובה אם לא מריצים את השירות bot)
TELEGRAM_BOT_TOKEN=

# OpenAI API Key (לא חובה, רק אם רוצים /ask בבוט)
OPENAI_API_KEY=

# אופציונלי: מפתח Toncenter אם רוצים הקשחה ואימות on-chain (לא בשימוש ב-MVP)
TONCENTER_API_KEY=
```

---

## כיצד זה עובד (MVP)
- ה־frontend מושך `/config` מה־api כדי לדעת:
  - לאן לשלוח את התרומה (SELLER_TON_ADDRESS)
  - סכום ברירת מחדל
  - קישור לקהילה בטלגרם
- כפתור "תרום עכשיו" יוצר **Deep Link** לפורמט `ton://transfer/<address>?amount=<nanoTon>&text=<comment>`
  - מתאים לאפליקציות/תוספי ארנק TON נפוצים. במובייל ייפתח ארנק מותקן; בדסקטופ הרחבת ארנק.
  - יש גם קישור "חלופי" ל־tonhub (ברירת מחדל בסיסית), וכפתור "העתק כתובת".
- הבוט מפיץ את הקישור לפלטפורמה, עוזר למשתמשים ומפנה אותם לתשלומים.

> בהמשך אפשר לשלב **TON Connect** עבור חוויית חיבור ארנק עשירה יותר, אימות טרנזאקציות, QR, וממשק דינמי.

---

## פקודות שימושיות
- עצירה: `Ctrl+C` בחלון הרצה, או `docker compose down`
- ניקוי מלא (כולל בניה מחדש): `docker compose down -v && docker compose up --build`
- לוגים לשירות ספציפי: `docker compose logs -f api` (או `frontend` / `bot`)

---

## הערות אבטחה
- לעולם אל תחשוף מפתחות API/טוקנים. שמור אותם ב-`.env` מקומי/סודי בלבד.
- זהו MVP, ללא אימות תשלומים קשיח. אל תסמוך על זה להכנסות מחייבות בלי אימות on-chain בצד השרת.
- מומלץ להוסיף HTTPS הפוכה (Nginx/Traefik) לפרודקשן.

תהנה 🚀