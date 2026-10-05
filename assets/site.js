// Interactive behaviour that used to come from Framer's JavaScript runtime.
// Pair with assets/site.css.
(() => {

  // Make a non-button element (icon container, FAQ card) work with Enter/Space.
  const pressable = (el) => {
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        el.click();
      }
    });
  };

  /* ---------- Burger menu ----------
     The tablet/phone header only ships its closed layout. The open layout is kept in
     <template id="ry-menu"> and swapped in, reusing the page's existing variant CSS. */
  const menuTpl = document.getElementById('ry-menu');
  const CLOSED_VARIANT = 'framer-v-106a82v';
  const OPEN_VARIANT = 'framer-v-g3nlef';

  const setMenu = (header, open) => {
    if (open) {
      header._ryClosedHTML = header.innerHTML;
      header.innerHTML = menuTpl.innerHTML;
      header.classList.replace(CLOSED_VARIANT, OPEN_VARIANT);
    } else {
      header.innerHTML = header._ryClosedHTML;
      header.classList.replace(OPEN_VARIANT, CLOSED_VARIANT);
    }
    header.querySelectorAll('.ry-menu-toggle').forEach((t) => {
      t.setAttribute('aria-expanded', String(open));
      pressable(t);
    });
    header.querySelector('.ry-menu-toggle')?.focus({ preventScroll: true });
  };

  if (menuTpl) {
    document.querySelectorAll('.ry-menu-toggle').forEach(pressable);
    document.addEventListener('click', (e) => {
      const toggle = e.target.closest('.ry-menu-toggle');
      if (!toggle) return;
      const header = toggle.closest('header');
      setMenu(header, !header.classList.contains(OPEN_VARIANT));
    });
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape') return;
      document.querySelectorAll(`header.${OPEN_VARIANT}`).forEach((h) => setMenu(h, false));
    });
  }

  /* ---------- FAQ accordion ----------
     Desktop items swap Framer's closed/open variant classes (data-ry-closed / data-ry-open).
     Phone items have no data-ry-open: Framer's phone open variant put the answer beside the
     question, so they keep the closed layout and site.css stacks the answer underneath. */
  document.querySelectorAll('.ry-faq').forEach((item) => {
    const { ryClosed, ryOpen } = item.dataset;
    pressable(item);
    item.addEventListener('click', (e) => {
      if (e.target.closest('a')) return;
      const open = !item.classList.contains('ry-open');
      item.classList.toggle('ry-open', open);
      if (ryOpen) {
        item.classList.toggle(ryOpen, open);
        item.classList.toggle(ryClosed, !open);
      }
      item.setAttribute('aria-expanded', String(open));
    });
  });

  /* ---------- Slideshow ("Why choose us") ---------- */
  document.querySelectorAll('.ry-slideshow').forEach((section) => {
    const track = section.querySelector('ul');
    const count = track.children.length;
    if (count < 2) return;
    let index = 0;
    let timer = null;
    const show = (i) => {
      index = (i + count) % count;
      track.style.transform = `translateX(${-100 * index}%)`;
      [...track.children].forEach((li, n) => li.setAttribute('aria-hidden', String(n !== index)));
    };
    // Advance every 3s. With reduced motion the slide changes without the sliding transition (see site.css).
    const start = () => {
      if (timer) return;
      timer = setInterval(() => show(index + 1), 3000);
    };
    const stop = () => {
      clearInterval(timer);
      timer = null;
    };
    section.addEventListener('mouseenter', stop);
    section.addEventListener('mouseleave', start);
    section.addEventListener('focusin', stop);
    section.addEventListener('focusout', start);

    // Swipe on touch screens.
    let startX = null;
    section.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; stop(); }, { passive: true });
    section.addEventListener('touchend', (e) => {
      if (startX === null) return;
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) show(index + (dx < 0 ? 1 : -1));
      startX = null;
      start();
    });

    // Framer's markup doesn't list slides in display order; each slide's progress bar
    // ("loadbar") sits at its own position, so sort by that once the slideshow is laid out.
    let sorted = false;
    const sortSlides = () => {
      if (sorted || !section.offsetWidth) return;
      const barOffset = (li) => {
        const bar = li.querySelector('[data-framer-name="loadbar"] > *');
        return bar ? bar.getBoundingClientRect().left - li.firstElementChild.getBoundingClientRect().left : 0;
      };
      [...track.children].sort((a, b) => barOffset(a) - barOffset(b)).forEach((li) => track.append(li));
      sorted = true;
      show(0);
    };
    window.addEventListener('resize', sortSlides);

    show(0);
    sortSlides();
    start();
  });

  /* ---------- Contact form (Web3Forms) ---------- */
  document.querySelectorAll('form.ry-contact-form').forEach((form) => {
    const status = document.createElement('p');
    status.className = 'ry-form-status';
    status.setAttribute('role', 'status');
    form.append(status);

    form.querySelectorAll('.framer-form-input').forEach((input) => {
      const sync = () => input.classList.toggle('framer-form-input-empty', !input.value);
      input.addEventListener('input', sync);
      sync();
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      // hCaptcha (Web3Forms client script) adds its token as h-captcha-response.
      const captcha = form.querySelector('textarea[name="h-captcha-response"], input[name="h-captcha-response"]');
      if (form.querySelector('.h-captcha') && !captcha?.value) {
        status.dataset.state = 'error';
        status.textContent = 'Please confirm you are human by ticking the captcha box.';
        return;
      }
      const button = form.querySelector('[type="submit"]');
      button.disabled = true;
      status.dataset.state = '';
      status.textContent = 'Sending…';
      try {
        const res = await fetch(form.action, {
          method: 'POST',
          headers: { Accept: 'application/json' },
          body: new FormData(form),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok || data.success === false) throw new Error(data.message || res.statusText);
        form.reset();
        status.dataset.state = 'ok';
        status.textContent = 'Thank you! Your message has been sent.';
      } catch (err) {
        status.dataset.state = 'error';
        status.textContent = 'Sorry, your message could not be sent. Please try again or email us directly.';
      } finally {
        button.disabled = false;
        window.hcaptcha?.reset(); // a token is single-use
      }
    });
  });

  /* ---------- "For Companies" / "For Candidates" tabs (hire-talent) ----------
     The page only ships the companies listing; the candidates listing is kept in the
     <template> named by data-ry-tabs, and the two versions are swapped on click. */
  const TAB_LABELS = ['For Companies', 'For Candidates'];
  document.querySelectorAll('[data-ry-tabs]').forEach((companies) => {
    const tpl = document.getElementById(companies.dataset.ryTabs);
    if (!tpl) return;
    const candidates = tpl.content.firstElementChild.cloneNode(true);
    const views = { 'For Companies': companies, 'For Candidates': candidates };

    const wire = (view, activeLabel) => {
      view.querySelectorAll('p').forEach((p) => {
        const label = p.textContent.trim();
        if (!TAB_LABELS.includes(label)) return;
        const tab = p.parentElement.parentElement; // the pill around the label
        tab.parentElement.setAttribute('role', 'tablist');
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-selected', String(label === activeLabel));
        tab.tabIndex = 0;
        tab.style.cursor = 'pointer';
        pressable(tab);
        tab.addEventListener('click', (e) => {
          const target = views[label];
          if (target.isConnected) return;
          view.replaceWith(target);
          // Keep keyboard users on the tab they activated (e.detail is 0 for Enter/Space).
          if (e.detail === 0) target.querySelector('[role="tab"][aria-selected="true"]')?.focus({ preventScroll: true });
        });
      });
    };
    wire(companies, 'For Companies');
    wire(candidates, 'For Candidates');
  });

  /* ---------- Buttons whose link only covers the label ----------
     Framer's "See more"/"See all" buttons only link their text; make the whole button clickable.
     Elements with data-ry-href (e.g. "View all") are buttons that had no link at all. */
  document.querySelectorAll('[data-framer-name^="Button"], [data-framer-name="_button"], [data-ry-href]').forEach((btn) => {
    if (btn.closest('a')) return;
    const link = btn.querySelector('a[href]');
    const href = btn.dataset.ryHref;
    if (!link && !href) return;
    btn.style.cursor = 'pointer';
    if (href) {
      btn.setAttribute('role', 'link');
      btn.tabIndex = 0;
      btn.addEventListener('keydown', (e) => { if (e.key === 'Enter') window.location.href = href; });
    }
    btn.addEventListener('click', (e) => {
      if (e.target.closest('a')) return;
      if (link) link.click();
      else window.location.href = href;
    });
  });

  /* ---------- Job listing search / remote filter (jobs.html) ---------- */
  const jobList = document.querySelector('.ry-job-list');
  if (jobList) {
    const q = document.getElementById('ry-job-q');
    const remoteOnly = document.getElementById('ry-job-remote');
    const count = document.querySelector('.ry-jobs-count');
    const empty = document.querySelector('.ry-jobs-empty');
    const cards = [...jobList.children];
    const filter = () => {
      const terms = q.value.toLowerCase().split(/\s+/).filter(Boolean);
      let shown = 0;
      cards.forEach((card) => {
        const match = (!remoteOnly.checked || card.dataset.remote === 'true')
          && terms.every((t) => card.dataset.search.includes(t));
        card.hidden = !match;
        if (match) shown += 1;
      });
      count.textContent = `${shown} open position${shown === 1 ? '' : 's'}`;
      empty.hidden = shown > 0;
    };
    q.addEventListener('input', filter);
    remoteOnly.addEventListener('change', filter);
  }

  /* ---------- Embedded widgets (Zoho "Featured jobs") ----------
     The srcdoc iframes start at height 0 and post their content height ({embedHeight}) to the
     parent page; Framer used to apply it. */
  const embeds = [...document.querySelectorAll('iframe[srcdoc]')];
  if (embeds.length) {
    window.addEventListener('message', (e) => {
      const height = e.data && e.data.embedHeight;
      if (typeof height !== 'number') return;
      const frame = embeds.find((f) => f.contentWindow === e.source);
      if (frame) frame.style.height = `${Math.ceil(height)}px`;
    });
    const ask = (f) => f.contentWindow?.postMessage('getEmbedHeight', '*');
    embeds.forEach((f) => { f.addEventListener('load', () => ask(f)); ask(f); });
  }

  /* ---------- Nested links ----------
     Elements marked data-nested-link sit inside another <a>, so they can't be anchors themselves. */
  const openLink = (el, newTab) => {
    const href = el.getAttribute('href');
    if (!href) return;
    const a = document.createElement('a');
    a.href = href;
    a.target = newTab ? '_blank' : el.getAttribute('target') || '';
    a.rel = newTab ? '' : el.getAttribute('rel') || '';
    document.body.append(a);
    a.click();
    a.remove();
  };
  document.querySelectorAll('[data-nested-link]').forEach((el) => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      openLink(el, /Mac|iPod|iPhone|iPad/.test(navigator.userAgent) ? e.metaKey : e.ctrlKey);
    });
    el.addEventListener('auxclick', (e) => { e.preventDefault(); e.stopPropagation(); openLink(el, true); });
    el.addEventListener('keydown', (e) => {
      if (e.key !== 'Enter') return;
      e.preventDefault();
      e.stopPropagation();
      openLink(el, false);
    });
  });
})();
