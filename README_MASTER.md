# SLH FULL SUITE – TON Engine · Botshop · SLH Wallet

מונורפו מאוחד שמכיל את שלושת הרכיבים העיקריים של האקו־סיסטם:

- `TON-engine/` – מנוע ניתוח טכני, ניהול סיכונים, ושרת Flask כולל דשבורד ו-Web Portal.
- `botshop/` – שער כניסה קהילתי / בוט טלגרם לקמפיינים, לידים וקבוצות SLH.
- `slh-wallet/` – שירות ארנק SLH / API פיננסי (FastAPI + Telegram integration).

בנוסף, בתוך `TON-engine/web/` נוצר אתר סטטי שמתממשק ישירות ל-API של מנוע הניתוח (`/health`, `/analysis`, `/multi_analysis`).

---

## 1. דרישות מערכת

- Python 3.10+ מותקן במכונה
- pip מותקן
- אופציונלי: virtualenv / venv
- חשבון Railway / שרת דפLOYment לבוטים (לא חובה לשלב ראשון)

---

## 2. הרצה מקומית – מנוע TON + אתר אינטרנט

```bash
cd TON-engine

# יצירת סביבה וירטואלית (מומלץ)
python -m venv .venv
source .venv/bin/activate  # ב-Windows: .venv\Scripts\activate

# התקנת תלויות
pip install -r requirements.txt

# הרצת השרת (Flask)
python "🌐 SERVER & API/app.py"
```

לאחר ההפעלה:

- דשבורד קיים בכתובת: `http://localhost:8080/`
- אתר ה-Web החדש: `http://localhost:8080/site`  
  שם ניתן:
  - להריץ `/health` דרך כפתור "בדיקת בריאות מערכת"
  - להריץ `/analysis` ו-`/multi_analysis` דרך הכפתורים והקלט

> שים לב: חלק מהפיצ'רים (כמו ML, Whale Tracker, Correlation) דורשים מפתחות API מוגדרים בקובץ `.env` / משתני סביבה.

---

## 3. קובצי ENV חשובים

### עבור TON-engine

יש להגדיר (לדוגמה בקובץ `.env`/משתני מערכת):

- `TELEGRAM_BOT_TOKEN`
- `USER_CHAT_ID`
- `GROUP_CHAT_ID`
- `ADMIN_GROUP_CHAT_ID`
- `BINANCE_API_KEY`
- `BINANCE_API_SECRET`
- `ENV=dev` או `staging` או `production`

עיין גם ב-`⚙️ CONFIGURATION/config.py` בתוך תיקיית `TON-engine`.

---

## 4. Botshop – שער קהילתי / בוט אקו־סיסטם

בתיקיית `botshop/` תמצא:

- קבצי בוט SLHNET (Python + PHP במידת הצורך).
- תיקיית `templates/` ו-`static/` עבור דפי נחיתה.
- `docs/` – תיעוד מלא, כולל `API_SPEC.md`, `ARCHITECTURE.md`, ו-README לפריסה.

לשלב ראשון מומלץ:

```bash
cd botshop
# קרא את README_DEPLOY_FULL.md ו-README_BOTSHOP_V11.txt
```

בוט זה יכול לשמש כשכבת כניסה שיווקית לקהילה שלך, המקושרת לניתוחים שמספק מנוע ה-TON.

---

## 5. SLH Wallet – שירות ארנק ומערכת פיננסית

בתיקיית `slh-wallet/` תמצא:

- שירות FastAPI / שירות API לארנק SLH
- Alembic migrations
- אינטגרציית Telegram בסיסית (`app/telegram.py`)
- README_*.md עם הוראות Railway ופריסה

הרצה בסיסית (דוגמה):

```bash
cd slh-wallet

python -m venv .venv
source .venv/bin/activate  # ב-Windows: .venv\Scripts\activate
pip install -r requirements.txt  # אם קיים בפרויקט
# או לפי README הפרויקט

# הרצת השירות (דוגמה מתוך README הקיים):
# uvicorn app.main:app --host 0.0.0.0 --port 8081
```

ניתן לקשר בין TON-engine ל-SLH Wallet ברמת config (למשל URL של wallet service) ולהרחיב בהמשך לניתוח תיקי לקוחות/קבוצות.

---

## 6. אינטגרציה ל-Web Portal

אתר ה-Web ב-`TON-engine/web/` עושה שימוש ישיר ב-EndPoints הבאים מתוך `🌐 SERVER & API/app.py`:

- `GET /health` – בריאות מערכת.
- `GET /analysis?symbol=TONUSDT` – ניתוח סימבול אחד.
- `GET /multi_analysis` – ניתוח מרובה מטבעות.

זה מאפשר לך:

- לבדוק את דיוק הניתוחים הטכניים בזמן אמת מתוך דפדפן.
- לשמש את האתר כדף נחיתה/הדגמה למשקיעים/משתמשים.

באפשרותך להרחיב את ה-HTML/JS כדי:

- להציג גרפים (באמצעות ספריות JS כמו Chart.js – להוסיף ידנית בעתיד).
- לחבר לטפסי רישום לבוט `botshop`.
- לחבר ל-API של `slh-wallet` להצגת יתרות/נתוני ארנק (דרך קריאות AJAX נוספות).

---

## 7. פריסה ל-Railway (באופן כללי)

עבור כל אחד מהרכיבים ניתן ליצור שירות נפרד ב-Railway:

1. צור שירות חדש והעלה את התיקייה המתאימה (`TON-engine`, `botshop`, `slh-wallet`).
2. ודא שבכל שירות ה-Procfile/command מפנה לנקודת הכניסה הנכונה.
3. הגדר את משתני הסביבה כפי שמפורטים ב-README של כל רכיב.
4. בדוק שה-URL החיצוני נגיש והגדר אם צריך Webhook לבוטי טלגרם.

---

## 8. המשך פיתוח

- ניתן להרחיב את קבצי ML ב-`TON-engine/🧠 MACHINE LEARNING/` לצורך תחזיות מתקדמות.
- לחבר את Botshop ו-SLH Wallet ל-TON Engine דרך API calls או Webhooks.
- לבנות Dashboard משולב שמציג:
  - מצב קהילה (botshop)
  - מצב ארנק/כספים (slh-wallet)
  - מצב שוק וניתוח טכני (TON-engine)

הפרויקט בנוי כך שתוכל להתנסות, לרוץ מקומית, ולהעלות לשרתים שונים – תוך שמירה על חלוקה ברורה לשכבות ותפקידים.
