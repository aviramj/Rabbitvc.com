// Rabbit Ventures — single-page reactive behaviors
(() => {
  'use strict';

  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Year ----------
  const yr = $('#yr'); if (yr) yr.textContent = new Date().getFullYear();

  // ---------- Theme toggle (persisted) ----------
  const root = document.documentElement;
  const stored = localStorage.getItem('rv-theme');
  if (stored) root.setAttribute('data-theme', stored);
  $('#theme-toggle')?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('rv-theme', next);
  });

  // ---------- Scroll-aware nav ----------
  const nav = $('#nav');
  const onScroll = () => nav.classList.toggle('scrolled', scrollY > 8);
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

  // ---------- Active section highlight ----------
  const sectionIds = ['approach', 'team', 'podcast', 'contact'];
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

  // ---------- Counters ----------
  const counters = $$('.num[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    const cio = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        const el = e.target;
        const target = parseFloat(el.dataset.count);
        const suffix = el.dataset.suffix || '';
        const dur = 1100;
        const start = performance.now();
        const tick = (now) => {
          const t = Math.min(1, (now - start) / dur);
          const eased = 1 - Math.pow(1 - t, 3);
          const v = Math.round(target * eased);
          el.textContent = v + (target >= 10 ? '+' : '') + suffix;
          if (t < 1) requestAnimationFrame(tick);
        };
        if (reduceMotion) {
          el.textContent = target + (target >= 10 ? '+' : '') + suffix;
        } else {
          requestAnimationFrame(tick);
        }
        cio.unobserve(el);
      }
    }, { threshold: 0.4 });
    counters.forEach(c => cio.observe(c));
  }

  // ---------- Hero card parallax (pointer) ----------
  const heroArt = $('.hero-art');
  const tilts = $$('.tilt');
  if (heroArt && tilts.length && !reduceMotion && matchMedia('(pointer: fine)').matches) {
    let raf = 0, tx = 0, ty = 0;
    heroArt.addEventListener('pointermove', (ev) => {
      const r = heroArt.getBoundingClientRect();
      tx = ((ev.clientX - r.left) / r.width  - 0.5) * 2;
      ty = ((ev.clientY - r.top)  / r.height - 0.5) * 2;
      if (!raf) raf = requestAnimationFrame(apply);
    });
    heroArt.addEventListener('pointerleave', () => {
      tx = 0; ty = 0;
      if (!raf) raf = requestAnimationFrame(apply);
    });
    const apply = () => {
      raf = 0;
      for (const el of tilts) {
        const d = parseFloat(el.dataset.depth || '1');
        el.style.transform =
          `translate3d(${tx * d * 8}px, ${ty * d * 8}px, 0) rotateX(${-ty * d * 3}deg) rotateY(${tx * d * 3}deg)`;
      }
    };
  }

  // ---------- Pitch form (no backend; mailto fallback) ----------
  const form = $('#pitchForm');
  if (form) {
    const status = $('.form-status', form);
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      const required = ['name', 'email', 'pitch'];
      const missing = required.filter(k => !String(data[k] || '').trim());
      if (missing.length) {
        status.className = 'form-status err';
        status.textContent = 'Please fill in: ' + missing.join(', ') + '.';
        return;
      }
      const subject = encodeURIComponent(`Pitch — ${data.company || data.name}`);
      const body = encodeURIComponent(
        `Name: ${data.name}\nCompany: ${data.company || ''}\nEmail: ${data.email}\n\n${data.pitch}`
      );
      // open the user's mail client; we don't have a backend
      window.location.href = `mailto:hello@rabbitvc.com?subject=${subject}&body=${body}`;
      status.className = 'form-status ok';
      status.textContent = 'Opening your email client…';
      form.reset();
    });
  }

  // ---------- Lightweight canvas starfield (subtle) ----------
  const cv = document.getElementById('bgfx');
  if (cv && !reduceMotion) {
    const ctx = cv.getContext('2d');
    let w, h, dots = [];
    const resize = () => {
      const dpr = Math.min(devicePixelRatio || 1, 2);
      w = cv.width  = innerWidth  * dpr;
      h = cv.height = innerHeight * dpr;
      cv.style.width = innerWidth + 'px';
      cv.style.height = innerHeight + 'px';
      const count = Math.min(110, Math.floor((innerWidth * innerHeight) / 18000));
      dots = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        r: (Math.random() * 1.4 + 0.3) * dpr,
        vx: (Math.random() - 0.5) * 0.12 * dpr,
        vy: (Math.random() - 0.5) * 0.12 * dpr,
        a: Math.random() * 0.6 + 0.2,
      }));
    };
    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      const isLight = root.getAttribute('data-theme') === 'light';
      ctx.fillStyle = isLight ? 'rgba(20,20,30,1)' : 'rgba(255,255,255,1)';
      for (const d of dots) {
        d.x += d.vx; d.y += d.vy;
        if (d.x < 0) d.x = w; else if (d.x > w) d.x = 0;
        if (d.y < 0) d.y = h; else if (d.y > h) d.y = 0;
        ctx.globalAlpha = d.a * (isLight ? 0.4 : 0.7);
        ctx.beginPath(); ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2); ctx.fill();
      }
      requestAnimationFrame(draw);
    };
    resize();
    addEventListener('resize', resize);
    requestAnimationFrame(draw);
  }
})();
