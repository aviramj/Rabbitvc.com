// Rabbit Ventures: single-page reactive behaviors
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

  // ---------- Episode count (derived, so adding a card is enough) ----------
  const epCount = $('.podcast-count');
  if (epCount) {
    const n = $$('.ep-grid .ep-card').length;
    if (n) epCount.textContent = n === 1 ? '1 episode' : `${n} episodes`;
  }

  // ---------- Active section highlight ----------
  const sectionIds = ['top', 'about', 'team', 'advisors', 'portfolio', 'contact'];
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

  // ---------- Hero ticker and Latest ----------
  // Both read from content already on the site, so the hero stays current
  // as the portfolio and the news page grow.
  /* ---- ticker: names come from this page's own portfolio section ---- */
  function portfolioNames(){
    var names = [];
    document.querySelectorAll('#portfolio .pf-card').forEach(function(card){
      var img = card.querySelector('.pf-logo img[alt]');
      var wm  = card.querySelector('.pf-wm');
      var name = card.dataset.name || (img ? img.getAttribute('alt') : (wm ? wm.textContent : ''));
      name = (name || '').trim();
      if (name) names.push(name);
    });
    return names;
  }
  function fillRow(el, list){
    if (!el || !list.length) return;
    var html = list.map(function(n){
      return '<span>' + n.replace(/&/g,'&amp;').replace(/</g,'&lt;') + '</span>';
    }).join('');
    el.innerHTML = html + html;          /* doubled so the -50% loop is seamless */
  }
  var names = portfolioNames();
  if (names.length){
    var half = Math.ceil(names.length / 2);
    fillRow(document.getElementById('rv-row-a'), names.slice(0, half));
    fillRow(document.getElementById('rv-row-b'), names.slice(half));
  } else {
    var t = document.querySelector('.rv-ticker');
    if (t) t.style.display = 'none';     /* never show an empty rail */
  }

  /* ---- keep the nav in the hero's colours for as long as the hero is behind it ---- */
  var hero = document.querySelector('.rv-hero'), navEl = document.getElementById('nav');
  if (hero && navEl){
    var syncNav = function(){
      navEl.classList.toggle('rv-over-hero', hero.getBoundingClientRect().bottom > 72);
    };
    syncNav();
    addEventListener('scroll', syncNav, { passive:true });
    addEventListener('resize', syncNav);
  }

  /* ---- Latest: served copy is correct; refresh it from the news page ---- */
  var list = document.getElementById('rv-latest-list');
  if (!list || !window.fetch || !window.DOMParser) return;
  fetch('./news/', { credentials:'same-origin' })
    .then(function(r){ return r.ok ? r.text() : Promise.reject(r.status); })
    .then(function(html){
      var doc   = new DOMParser().parseFromString(html, 'text/html');
      var cards = [].slice.call(doc.querySelectorAll('.news-card')).slice(0, 4);
      if (cards.length < 4) return;                       /* keep the served copy */
      var frag = document.createDocumentFragment();
      cards.forEach(function(card){
        var title = card.querySelector('.news-card-title');
        var date  = card.querySelector('.news-date');
        if (!title) return;
        var a = document.createElement('a');
        a.className = 'rv-item';
        a.href = card.getAttribute('href') || './news/';
        if (a.href && !/^\.\.\/news/.test(card.getAttribute('href') || '')) {
          a.target = '_blank';
          a.rel = 'noopener';
        }
        var t = document.createElement('time');
        t.textContent = date ? date.textContent.trim() : '';
        var s = document.createElement('span');
        s.className = 'rv-item-title';
        s.textContent = title.textContent.trim();
        a.appendChild(t); a.appendChild(s);
        frag.appendChild(a);
      });
      if (frag.childNodes.length === 4){
        list.innerHTML = '';
        list.appendChild(frag);
      }
    })
    .catch(function(){ /* offline or moved: the served copy stands */ });
})();
