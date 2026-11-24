(() => {
  'use strict';
  const path = location.pathname.replace(/\/?$/, '/');
  const pages = {control: '/branding/reason-ai/', improved: '/ads/reason-ai/diagnosis/'};
  const formPath = '/inquiry/reason-ai/';
  const params = new URLSearchParams(location.search);
  const allowed = {
    utm_source: ['fb', 'ig', 'facebook', 'instagram', 'meta'],
    utm_medium: ['paid_social'],
    utm_campaign: ['reason_ai_202611'],
    utm_content: ['A', 'D', 'F', 'A_ORANGE', 'F_QUESTION'],
    lp_test: ['orange_lp_1'],
    tracking_qa: ['1']
  };
  const fields = {};
  for (const [key, values] of Object.entries(allowed)) {
    const value = params.get(key);
    if (values.includes(value)) fields[key] = value;
  }
  const pendingKey = 'wellenetz_ra_receipt_v1';
  const variant = Object.keys(pages).find(key => pages[key] === path);
  if (variant) {
    for (const anchor of document.querySelectorAll('a[href]')) {
      const url = new URL(anchor.href, location.href);
      if (url.origin !== location.origin || url.pathname !== formPath) continue;
      for (const [key, value] of Object.entries({...fields, lp_variant: variant})) url.searchParams.set(key, value);
      anchor.href = url.href;
    }
    return;
  }
  if (path === formPath) {
    const form = document.getElementById('contact-inquiry-form');
    if (!form) return;
    const lp = params.get('lp_variant');
    if (Object.hasOwn(pages, lp)) {
      fields.lp_variant = lp;
      const originField = form.elements.namedItem('お問い合わせ元ページ');
      if (originField) originField.value = location.origin + pages[lp];
    }
    // The page prevents the first submit to display its review. Only the
    // uncancelled final submit should add attribution and arm a completion.
    document.addEventListener('submit', event => {
      if (event.target !== form || event.defaultPrevented) return;
      let id = crypto.randomUUID();
      try {
        const meta = JSON.parse(sessionStorage.getItem('wellenetz_reason_ai_pending_v1'));
        const age = meta ? Date.now() - meta.time : -1;
        if (age >= 0 && age < 5000 && /^reason_ai_[0-9]+_[a-z0-9]+$/.test(meta.id)) id = meta.id;
      } catch (_) { /* Receipt fields also work when storage is unavailable. */ }
      const record = {...fields, submission_id: id};
      for (const [name, value] of Object.entries(record)) {
        const input = form.elements.namedItem(name) || document.createElement('input');
        input.type = 'hidden';
        input.name = name;
        input.value = value;
        if (!input.parentNode) form.appendChild(input);
      }
      try { sessionStorage.setItem(pendingKey, JSON.stringify({time: Date.now(), record})); } catch (_) {}
    });
    return;
  }
  if (path !== '/inquiry/thanks/' || params.get('form') !== 'reason-ai') return;
  let pending;
  try {
    pending = JSON.parse(sessionStorage.getItem(pendingKey));
    sessionStorage.removeItem(pendingKey);
  } catch (_) { return; }
  if (!pending || !pending.record || !pending.record.submission_id) return;
  const age = Date.now() - pending.time;
  if (age < 0 || age >= 1800000) return;
  // Use the Google tag already configured in GTM, with its existing consent settings.
  // The separate Meta tag already queues Lead; do not send a second Meta event.
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  gtag('event', 'reason_ai_diagnosis_complete', {
    ...pending.record, content_name: 'reason_ai_diagnosis', send_to: 'G-9JF0Q28R0W'
  });
})();
