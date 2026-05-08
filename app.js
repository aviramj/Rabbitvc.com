// Rabbit Ventures — single-page reactive behaviors
(() => {
  'use strict';

  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Theme toggle (persisted) ----------
  const root = document.documentElement;
  const stored = localStorage.getItem('rv-theme');
  if (stored) root.setAttribute('data-theme', stored);
  $('#theme-toggle')?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('rv-theme', next);
  });

  // ---------- Scroll-aware nav (transparent over hero, solid after) ----------
  const nav = $('#nav');
  const onScroll = () => nav.classList.toggle('scrolled', scrollY > 80);
  onScroll();
  addEventListener('scroll', onScroll, { passive: true });

  // ---------- Mobile menu ----------
  const menuBtn = $('#menu-btn'), mobileMenu = $('#mobile-menu');
  if (menuBtn && mobileMenu) {
    const setOpen = (open) => {
      mobileMenu.hidden = !open;
      menuBtn.setAttribute('aria-expanded', String(open));
    };
    menuBtn.addEventListener('click', () => setOpen(mobileMenu.hidden));
    $$('#mobile-menu a').forEach(a => a.addEventListener('click', () => setOpen(false)));
  }

  // ---------- Reveal-on-scroll ----------
  if ('IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.isIntersecting) {
          e.target.classList.add('in');
          io.unobserve(e.target);
        }
      }
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    $$('.reveal').forEach(el => io.observe(el));
  } else {
    $$('.reveal').forEach(el => el.classList.add('in'));
  }

  // ---------- Hero parallax (subtle, on scroll) ----------
  const heroInner = $('.hero-inner');
  const heroBg = $('.hero-bg img');
  if (heroInner && heroBg && !reduceMotion) {
    let ticking = false;
    const update = () => {
      const y = Math.min(scrollY, innerHeight);
      heroInner.style.transform = `translate3d(0, ${y * 0.18}px, 0)`;
      heroInner.style.opacity = String(Math.max(0, 1 - y / (innerHeight * 0.85)));
      heroBg.style.transform = `translate3d(0, ${y * 0.35}px, 0) scale(1.05)`;
      ticking = false;
    };
    addEventListener('scroll', () => {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
  }

  // ---------- Active section highlight ----------
  const sectionIds = ['top', 'about', 'team', 'portfolio', 'contact'];
  const sections = sectionIds.map(id => document.getElementById(id)).filter(Boolean);
  const navLinks = new Map(
    $$('.nav-links a[href^="#"]').map(a => [a.getAttribute('href').slice(1), a])
  );
  if (sections.length && 'IntersectionObserver' in window) {
    const sio = new IntersectionObserver((entries) => {
      for (const e of entries) {
        const link = navLinks.get(e.target.id);
        if (!link) continue;
        if (e.isIntersecting) {
          navLinks.forEach(l => l.classList.remove('active'));
          link.classList.add('active');
        }
      }
    }, { rootMargin: '-45% 0px -50% 0px' });
    sections.forEach(s => sio.observe(s));
  }
})();
