// Cookie consent for recruityard.com — see docs/cookies.md for the register of every cookie.
//
// Categories
//   necessary  – always on (this consent record, contact-form security). No banner choice.
//   statistics – Google Analytics 4 (measurement id in GA_MEASUREMENT_ID below).
//   marketing  – embedded third-party media that may track (YouTube).
//
// Nothing in "statistics" or "marketing" loads until the visitor allows it. Google Consent
// Mode v2 signals are sent so Google tags respect the choice. The choice is stored in
// localStorage ("ry-consent") for 12 months, then the banner asks again.
(() => {
  const STORE_KEY = 'ry-consent';
  const VERSION = 1;               // bump when categories/vendors change materially → re-ask
  const MAX_AGE_DAYS = 365;
  // Google Analytics 4 property "Recruityard website". This is the only Google tag on the site;
  // it is the official gtag.js snippet, loaded below only after Statistics consent.
  const GA_MEASUREMENT_ID = 'G-XM9KZGKH6B';
  const policyHref = (document.querySelector('a[href*="cookie-policy.html"]') || {}).getAttribute?.('href')
    || './cookie-policy.html';

  // ---- Google Consent Mode v2: everything denied until the visitor decides ----
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); } // eslint-disable-line prefer-rest-params
  window.gtag = window.gtag || gtag;
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied',
    functionality_storage: 'granted',
    security_storage: 'granted',
    wait_for_update: 500,
  });

  // ---- stored choice ----
  const read = () => {
    try {
      const c = JSON.parse(localStorage.getItem(STORE_KEY));
      const fresh = c && c.v === VERSION && Date.now() - c.ts < MAX_AGE_DAYS * 864e5;
      return fresh ? c : null;
    } catch { return null; }
  };
  const save = (statistics, marketing) => {
    const c = { v: VERSION, ts: Date.now(), statistics: !!statistics, marketing: !!marketing };
    try { localStorage.setItem(STORE_KEY, JSON.stringify(c)); } catch { /* private mode: session only */ }
    return c;
  };

  // ---- applying a choice ----
  let analyticsLoaded = false;
  const loadAnalytics = () => {
    if (analyticsLoaded) return;
    analyticsLoaded = true;
    const tag = document.createElement('script');
    tag.async = true;
    tag.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
    document.head.append(tag);
    gtag('js', new Date());
    gtag('config', GA_MEASUREMENT_ID);
  };

  // Withdrawing consent: remove Google Analytics cookies (on this host and its parent domain).
  const clearAnalyticsCookies = () => {
    const host = location.hostname;
    const domains = ['', host, `.${host}`, `.${host.split('.').slice(-2).join('.')}`];
    document.cookie.split(';').map((c) => c.trim().split('=')[0])
      .filter((name) => /^_ga($|_)|^_gid$|^_gat/.test(name))
      .forEach((name) => domains.forEach((d) => {
        document.cookie = `${name}=; Max-Age=0; path=/${d ? `; domain=${d}` : ''}`;
      }));
  };

  const apply = (c) => {
    if (!c.statistics) {
      clearAnalyticsCookies();
      if (analyticsLoaded) { location.reload(); return; } // scripts already running can't be unloaded
    }
    gtag('consent', 'update', {
      analytics_storage: c.statistics ? 'granted' : 'denied',
      ad_storage: c.marketing ? 'granted' : 'denied',
      ad_user_data: c.marketing ? 'granted' : 'denied',
      ad_personalization: c.marketing ? 'granted' : 'denied',
    });
    if (c.statistics) loadAnalytics();
    document.dispatchEvent(new CustomEvent('ry:consent', { detail: c }));
  };

  // ---- UI ----
  const el = (tag, attrs = {}, html = '') => {
    const n = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => n.setAttribute(k, v));
    n.innerHTML = html;
    return n;
  };

  let banner;
  const close = () => { banner?.remove(); banner = null; };

  const show = (withSettings = false) => {
    close();
    const current = read() || { statistics: false, marketing: false };
    banner = el('section', { class: 'ry-consent', role: 'dialog', 'aria-modal': 'false', 'aria-labelledby': 'ry-consent-title' }, `
      <h2 id="ry-consent-title">We value your privacy</h2>
      <p>We use cookies that are needed for the site to work. With your permission we'd also like to
      use analytics cookies to understand how the site is used, and to load content from third parties
      like YouTube. You can change your choice at any time via “Cookie settings” in the footer.
      <a href="${policyHref}">Cookie policy</a></p>
      <form class="ry-consent-settings" ${withSettings ? '' : 'hidden'}>
        <label><input type="checkbox" checked disabled> <strong>Necessary</strong>
          <span>Remembers this choice and protects the contact form from spam. Always on.</span></label>
        <label><input type="checkbox" name="statistics" ${current.statistics ? 'checked' : ''}> <strong>Statistics</strong>
          <span>Google Analytics: anonymous visit statistics that help us improve the site.</span></label>
        <label><input type="checkbox" name="marketing" ${current.marketing ? 'checked' : ''}> <strong>Marketing &amp; media</strong>
          <span>Embedded videos from YouTube, which may set its own cookies.</span></label>
      </form>
      <div class="ry-consent-actions">
        <button type="button" data-act="reject">Reject all</button>
        <button type="button" data-act="${withSettings ? 'save' : 'settings'}">${withSettings ? 'Save choices' : 'Settings'}</button>
        <button type="button" data-act="accept" class="ry-consent-primary">Accept all</button>
      </div>`);
    banner.addEventListener('click', (e) => {
      const act = e.target.closest('button')?.dataset.act;
      if (!act) return;
      if (act === 'settings') { show(true); return; }
      const form = banner.querySelector('form');
      const c = act === 'accept' ? save(true, true)
        : act === 'reject' ? save(false, false)
        : save(form.statistics.checked, form.marketing.checked);
      close();
      apply(c);
    });
    document.body.append(banner);
    banner.querySelector('button[data-act="accept"]').focus({ preventScroll: true });
  };

  window.ryConsent = {
    get: () => read(),
    open: () => show(true),
    allowMarketing: () => { const c = read() || {}; apply(save(c.statistics, true)); },
  };

  // "Cookie settings" next to every footer "Cookies Policy" link, and any [data-ry-consent-open] button
  const addSettingsLinks = () => {
    document.querySelectorAll('a[href*="cookie-policy.html"]').forEach((a) => {
      if (!/cookie/i.test(a.textContent) || a.closest('.ry-consent')) return;
      const host = a.closest('p') || a;
      if (host.nextElementSibling?.classList.contains('ry-consent-link')) return;
      const copy = host.cloneNode(true);
      copy.classList.add('ry-consent-link');
      const link = copy.matches('a') ? copy : copy.querySelector('a');
      link.removeAttribute('href');
      link.setAttribute('role', 'button');
      link.setAttribute('tabindex', '0');
      link.textContent = link.textContent.replace(/Cookies? Policy/i, 'Cookie settings');
      host.after(copy);
    });
  };

  const start = () => {
    addSettingsLinks();
    document.addEventListener('click', (e) => {
      if (e.target.closest('.ry-consent-link [role="button"], .ry-consent-link[role="button"], [data-ry-consent-open]')) {
        e.preventDefault();
        show(true);
      }
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && e.target.closest?.('.ry-consent-link [role="button"]')) show(true);
    });
    const c = read();
    if (c) apply(c); else show(false);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
