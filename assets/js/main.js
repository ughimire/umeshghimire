// Umesh Ghimire — portfolio site interactions
(function () {
  'use strict';

  const root = document.documentElement;

  // ---------- Theme toggle (persists across pages) ----------
  const stored = localStorage.getItem('ug-theme');
  root.setAttribute('data-theme', stored || 'light');

  document.addEventListener('click', function (e) {
    const t = e.target.closest('#themeToggle');
    if (!t) return;
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('ug-theme', next);
  });

  // ---------- Mobile nav toggle ----------
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('#navMenu');
    const nav = document.getElementById('nav');
    if (!nav) return;
    if (btn) {
      const open = nav.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', String(open));
      return;
    }
    // Close menu when a link inside is clicked (helps for in-page anchors)
    if (e.target.closest('.nav__links a')) {
      nav.classList.remove('is-open');
      const m = document.getElementById('navMenu');
      if (m) m.setAttribute('aria-expanded', 'false');
      return;
    }
    if (nav.classList.contains('is-open') && !e.target.closest('.nav__links') && !e.target.closest('#navMenu')) {
      nav.classList.remove('is-open');
      const m = document.getElementById('navMenu');
      if (m) m.setAttribute('aria-expanded', 'false');
    }
  });

  // Close menu on escape key
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    const nav = document.getElementById('nav');
    if (nav && nav.classList.contains('is-open')) {
      nav.classList.remove('is-open');
      const m = document.getElementById('navMenu');
      if (m) m.setAttribute('aria-expanded', 'false');
    }
  });

  // ---------- Active nav link by current path ----------
  (function () {
    const path = location.pathname.replace(/\/$/, '') || '/';
    document.querySelectorAll('.nav__links a').forEach(a => {
      const href = (a.getAttribute('href') || '').replace(/\/$/, '') || '/';
      if (href === path) a.classList.add('active');
    });
  })();

  // ---------- Footer year ----------
  const yr = document.getElementById('year');
  if (yr) yr.textContent = String(new Date().getFullYear());

  // ---------- Contact form success state (Netlify redirects with ?submitted=true) ----------
  if (location.search.indexOf('submitted=true') !== -1) {
    const form = document.getElementById('contact-form');
    const success = document.getElementById('contact-success');
    if (form) form.hidden = true;
    if (success) {
      success.hidden = false;
      success.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    const t = document.getElementById('toast');
    if (t) {
      t.hidden = false;
      setTimeout(() => { t.hidden = true; }, 6000);
    }
  }

  // ---------- CV print button (CSP-safe, no inline handler) ----------
  const cvPrint = document.getElementById('cvPrintBtn');
  if (cvPrint) cvPrint.addEventListener('click', () => window.print());

  // ---------- Count-up animation for hero stats (B2.2) ----------
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const counters = document.querySelectorAll('[data-count-target]');
  if (counters.length && 'IntersectionObserver' in window) {
    const animate = (el) => {
      const target = parseInt(el.dataset.countTarget, 10);
      const suffix = el.dataset.countSuffix || '';
      if (reduced) { el.textContent = target + suffix; return; }
      const duration = 1200;
      const start = performance.now();
      const easeOut = (t) => 1 - Math.pow(1 - t, 3);
      const tick = (now) => {
        const t = Math.min(1, (now - start) / duration);
        el.textContent = Math.round(target * easeOut(t)) + suffix;
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !entry.target.dataset.counted) {
          entry.target.dataset.counted = '1';
          animate(entry.target);
        }
      });
    }, { threshold: 0.4 });
    counters.forEach((el) => io.observe(el));
  }
})();
