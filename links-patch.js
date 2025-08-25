// frontend/links-patch.js
(() => {
  // כתובת ה-API שלך
  const API_BASE = 'https://ton-2eg2.onrender.com';

  // Fallbacks אם ה-API ריק
  const FALLBACKS = {
    botLink: 'https://t.me/hbdcommunity_bot',     // בוט ברירת מחדל
    supportLink: 'https://t.me/OsifFintech',      // מנהל האתר (טלגרם)
  };

  async function fetchJSON(u) {
    const r = await fetch(u, { cache: 'no-store', mode: 'cors' });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return r.json();
  }

  async function init() {
    try {
      // ננסה להביא קונפיג מה-API
      await fetchJSON(API_BASE + '/health').catch(()=>{});
      const cfg = await fetchJSON(API_BASE + '/config');
      console.debug('[links-patch] /config:', cfg);

      const top = document.getElementById('communityLinkTop');    // הכפתור העליון (לבוט)
      const bottom = document.getElementById('communityLinkBottom'); // הכפתור התחתון (לתמיכה/מנהל)

      // יעד לכפתור העליון: "לבוט שלנו"
      if (top) {
        top.textContent = 'לבוט שלנו';
        const url = (cfg.botLink || cfg.communityLink || FALLBACKS.botLink || '').trim();
        if (url) {
          top.href = url; top.target = '_blank'; top.rel = 'noopener';
        } else {
          top.href = '#';
          top.onclick = (e) => { e.preventDefault(); alert('לא הוגדר קישור לבוט/קהילה ב-API'); };
        }
      }

      // יעד לכפתור התחתון: "שליחת הודעה למנהל האתר"
      if (bottom) {
        bottom.textContent = 'שליחת הודעה למנהל האתר';
        const url = (cfg.supportLink || cfg.communityLink || FALLBACKS.supportLink || '').trim();
        if (url) {
          bottom.href = url; bottom.target = '_blank'; bottom.rel = 'noopener';
        } else {
          bottom.href = '#';
          bottom.onclick = (e) => { e.preventDefault(); alert('לא הוגדר קישור מנהל/קהילה ב-API'); };
        }
      }
    } catch (e) {
      console.error('[links-patch] failed:', e);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
