// frontend/links-patch.js
(() => {
  const API_BASE = 'https://ton-2eg2.onrender.com';

  async function j(u){ const r=await fetch(u,{cache:'no-store'}); if(!r.ok) throw new Error('HTTP '+r.status); return r.json(); }

  async function init() {
    try {
      await j(API_BASE + '/health').catch(()=>{});
      const cfg = await j(API_BASE + '/config');
      console.debug('[CFG]', cfg);

      const top = document.getElementById('communityLinkTop');   // כפתור עליון
      const bot = document.getElementById('communityLinkBottom'); // כפתור תחתון

      // עליון: "לבוט שלנו"
      if (top) {
        top.textContent = 'לבוט שלנו';
        const url = (cfg.botLink || cfg.communityLink || '').trim();
        if (url) {
          top.href = url; top.target = '_blank'; top.rel = 'noopener';
        } else {
          top.href = '#';
          top.onclick = (e)=>{ e.preventDefault(); alert('לא הוגדר קישור לבוט/קהילה ב-API'); };
        }
      }

      // תחתון: "שליחת הודעה למנהל האתר"
      if (bot) {
        bot.textContent = 'שליחת הודעה למנהל האתר';
        const url = (cfg.supportLink || cfg.communityLink || '').trim();
        if (url) {
          bot.href = url; bot.target = '_blank'; bot.rel = 'noopener';
        } else {
          bot.href = '#';
          bot.onclick = (e)=>{ e.preventDefault(); alert('לא הוגדר איש קשר מנהל/קהילה ב-API'); };
        }
      }
    } catch (e) {
      console.error('[links-patch] failed:', e);
    }
  }

  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', init) : init();
})();
