/*
 * Ad loading strategy
 * -------------------
 * 1. No AdSense script is requested until the visitor has answered the consent
 *    prompt (required for EEA/UK traffic under the Google EU user consent policy).
 * 2. The library is injected once, then each reserved slot is pushed to
 *    `adsbygoogle` only when it is about to enter the viewport, which keeps the
 *    initial page load light without changing layout (slots are pre-sized in CSS).
 */

const ADSENSE_CLIENT = 'ca-pub-0000000000000000'; // TODO: replace with your real publisher ID
const CONSENT_KEY = 'demo-ads-consent';

let libraryPromise = null;

function loadAdSenseLibrary() {
  if (libraryPromise) return libraryPromise;
  libraryPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.async = true;
    script.crossOrigin = 'anonymous';
    script.src =
      'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' +
      encodeURIComponent(ADSENSE_CLIENT);
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
  return libraryPromise;
}

function fillSlot(ins) {
  if (ins.dataset.filled === 'true') return;
  ins.dataset.filled = 'true';
  loadAdSenseLibrary()
    .then(() => {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    })
    .catch(() => {
      ins.dataset.filled = 'false';
    });
}

function observeAdSlots() {
  const slots = document.querySelectorAll('ins.adsbygoogle');
  if (!slots.length) return;

  if (!('IntersectionObserver' in window)) {
    slots.forEach(fillSlot);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        fillSlot(entry.target);
      });
    },
    { rootMargin: '300px 0px' }
  );

  slots.forEach((slot) => observer.observe(slot));
}

function setConsent(value) {
  try {
    localStorage.setItem(CONSENT_KEY, value);
  } catch (err) {
    /* storage disabled: consent applies to this page view only */
  }
  const banner = document.querySelector('.consent');
  if (banner) banner.classList.remove('is-visible');
  if (value === 'granted') observeAdSlots();
}

function readConsent() {
  try {
    return localStorage.getItem(CONSENT_KEY);
  } catch (err) {
    return null;
  }
}

function initConsent() {
  const banner = document.querySelector('.consent');
  const stored = readConsent();

  if (stored === 'granted') {
    observeAdSlots();
    return;
  }
  if (stored === 'denied' || !banner) return;

  banner.classList.add('is-visible');
  banner.querySelector('[data-consent="granted"]').addEventListener('click', () => setConsent('granted'));
  banner.querySelector('[data-consent="denied"]').addEventListener('click', () => setConsent('denied'));
}

/* Coupons: hide expired cards client-side and copy codes on click. */

function hideExpiredCoupons() {
  const today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll('.coupon-list').forEach((list) => {
    let visible = 0;
    list.querySelectorAll('.coupon[data-expires]').forEach((card) => {
      if (card.dataset.expires < today) {
        card.hidden = true;
      } else {
        visible += 1;
      }
    });
    const empty = list.parentElement.querySelector('.empty-state');
    if (empty && visible === 0) empty.hidden = false;
  });
}

function showToast(text) {
  const toast = document.querySelector('.toast');
  if (!toast) return;
  toast.textContent = text;
  toast.classList.add('is-visible');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove('is-visible'), 1800);
}

function initCopyButtons() {
  document.querySelectorAll('.copy-code').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const code = btn.dataset.code;
      try {
        await navigator.clipboard.writeText(code);
      } catch (err) {
        const range = document.createRange();
        range.selectNodeContents(btn.querySelector('.code'));
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
      }
      btn.classList.add('is-copied');
      btn.querySelector('.copy-label').textContent = '已複製';
      showToast('已複製優惠碼 ' + code);
      setTimeout(() => {
        btn.classList.remove('is-copied');
        btn.querySelector('.copy-label').textContent = '複製';
      }, 2000);
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  hideExpiredCoupons();
  initCopyButtons();
  initConsent();
});
