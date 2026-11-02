/* Lawment Derneği — ortak davranışlar. Kütüphane yok. */
window.LM_READY = true;
(function () {
  'use strict';
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var animOn = function () { return root.classList.contains('anim') && !reduce.matches; };

  /* ---------- menü ---------- */
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  if (header && toggle) {
    var label = toggle.querySelector('.nav-toggle-text');
    var setOpen = function (open) {
      header.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      if (label) { label.textContent = open ? 'Kapat' : 'Menü'; }
    };
    toggle.addEventListener('click', function () { setOpen(toggle.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && header.classList.contains('is-open')) { setOpen(false); toggle.focus(); }
    });
    header.querySelectorAll('.nav a').forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
  }

  /* ---------- tema düğmesi: seçim bu tarayıcıda hatırlanır ---------- */
  var themeBtn = document.querySelector('[data-theme-toggle]');
  if (themeBtn) {
    // açık tema varsayılan: koyu tema yalnızca ziyaretçi düğmeyle seçerse açılır
    var isDark = function () { return root.getAttribute('data-theme') === 'dark'; };
    var syncBtn = function () { themeBtn.setAttribute('aria-label', isDark() ? 'Açık temaya geç' : 'Koyu temaya geç'); };
    themeBtn.addEventListener('click', function () {
      var next = isDark() ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('lm-theme', next); } catch (e) {}
      syncBtn();
    });
    syncBtn();
  }

  /* ---------- kaydırınca küçülen header + hero parallax (tek scroll dinleyicisi, rAF ile) ---------- */
  var heroImg = document.querySelector('.hero-media img');
  var ticking = false;
  var onScroll = function () {
    var y = window.scrollY;
    if (header) { header.classList.toggle('is-scrolled', y > 24); }
    // okuma çubuğu: sayfanın ne kadarının okunduğu
    var docH = root.scrollHeight - window.innerHeight;
    root.style.setProperty('--sp', docH > 0 ? Math.min(1, y / docH).toFixed(4) : '0');
    if (heroImg && !reduce.matches && y < window.innerHeight * 1.2) {
      heroImg.style.setProperty('--py', (y * 0.08).toFixed(1) + 'px');
    }
    if (timeline && animOn()) { fillTimeline(); }
    if (!reduce.matches) { progressEls.forEach(updateProgress); }
    if (animOn()) { pinEls.forEach(updatePin); litEls.forEach(updateLit); }
    ticking = false;
  };

  /* ---------- [data-pin]: sabitlenen sahneler; ilerleme --pp (0 → 1) ---------- */
  var pinEls = Array.prototype.slice.call(document.querySelectorAll('[data-pin]'));
  function updatePin(el) {
    var r = el.getBoundingClientRect();
    var vh = window.innerHeight;
    if (r.bottom < 0 || r.top > vh) { return; }
    var span = el.offsetHeight - vh;
    var p = span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 0;
    el.style.setProperty('--pp', p.toFixed(4));
  }
  // yatay galeri: ray ekran genişliğinden ne kadar uzunsa o kadar kayar
  var sizeGalleries = function () {
    document.querySelectorAll('.hgal').forEach(function (g) {
      var track = g.querySelector('.hgal-track');
      if (track) { g.style.setProperty('--hgal-max', Math.max(0, track.scrollWidth - window.innerWidth) + 'px'); }
    });
  };
  window.addEventListener('resize', sizeGalleries);
  window.addEventListener('load', sizeGalleries);
  sizeGalleries();

  /* ---------- [data-lit]: kaydırdıkça kelime kelime aydınlanan metin ---------- */
  var litEls = Array.prototype.slice.call(document.querySelectorAll('[data-lit]')).map(function (el) {
    return { el: el, words: el.querySelectorAll('.lw'), last: -1 };
  });
  function updateLit(o) {
    var r = o.el.getBoundingClientRect();
    var vh = window.innerHeight;
    // metnin üstü ekranın %85'ine gelince başlar, altı %40'a gelince biter
    var p = Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.45)));
    var lit = Math.round(p * o.words.length);
    if (lit === o.last) { return; }
    o.last = lit;
    for (var i = 0; i < o.words.length; i++) { o.words[i].classList.toggle('on', i < lit); }
  }

  /* ---------- [data-chapters]: zamana bağlı hikâye ----------
     Yıllar en yenisinden eskiye kendiliğinden ilerler. Zamanı, aktif yıl düğmesinin altındaki çizgi gösterir
     (CSS animasyonu ch-fill; bitince animationend sıradaki yılı açar, sonuncudan sonra en yeniye döner).
     Zaman şu durumlarda durur: bölüm ekranda değil, fare ya da klavye odağı bölümün üstünde, sekme gizli
     ya da ziyaretçi "Duraklat"a bastı. Yıl düğmeleriyle istenen yıla geçilir.
     Animasyon yoksa (JS kapalı, hareketi azalt) dört yıl alt alta, normal düzende görünür; kaydırmaya bağlı değildir. */
  var chaptersEl = document.querySelector('[data-chapters]');
  if (chaptersEl && animOn()) {
    var chItems = Array.prototype.slice.call(chaptersEl.querySelectorAll('.chapter'));
    var chBtns = Array.prototype.slice.call(chaptersEl.querySelectorAll('[data-chapter-go]'));
    var chPlay = chaptersEl.querySelector('[data-chapter-play]');
    var chLive = chaptersEl.querySelector('[data-ch-live]');
    var chStage = chaptersEl.querySelector('.chapters-stage');
    var chN = chItems.length;
    var chCur = -1, chStarted = false;
    var chPaused = false, chHover = false, chFocus = false, chInView = false;

    // bölüm açılınca rakam 0'dan son değere sayar (HTML'de son değer yazılıdır)
    var chapterCount = function (el) {
      var target = parseFloat(el.getAttribute('data-count-to'));
      if (!isFinite(target)) { return; }
      var t0 = null;
      var step = function (t) {
        if (t0 === null) { t0 = t; }
        var k = Math.min(1, (t - t0) / 1400);
        el.textContent = Math.round(target * (1 - Math.pow(1 - k, 4))).toLocaleString('tr-TR');
        if (k < 1) { window.requestAnimationFrame(step); }
      };
      window.requestAnimationFrame(step);
    };
    var holdChapters = function () {
      chaptersEl.classList.toggle('is-held', chPaused || chHover || chFocus || !chInView || document.hidden);
    };
    var showChapter = function (i, manual) {
      i = (i + chN) % chN;
      if (i === chCur) { return; }
      chCur = i;
      chItems.forEach(function (c, j) {
        c.classList.toggle('is-on', j === i);
        if (j === i) { c.setAttribute('aria-current', 'step'); } else { c.removeAttribute('aria-current'); }
      });
      chBtns.forEach(function (b, j) {
        if (j === i) { b.setAttribute('aria-current', 'step'); } else { b.removeAttribute('aria-current'); }
      });
      // ekran okuyucu: kendiliğinden ilerlerken sessiz; ziyaretçi seçince ya da duraklatınca yeni yıl duyurulur
      if (chLive) {
        chLive.setAttribute('aria-live', manual || chPaused ? 'polite' : 'off');
        var h = chItems[i].querySelector('h3');
        var yr = chItems[i].querySelector('.chapter-meta span');
        if (h && yr) { chLive.textContent = yr.textContent + ': ' + h.textContent; }
      }
      var num = chItems[i].querySelector('[data-count-to]');
      if (num && chStarted && !reduce.matches) { chapterCount(num); }
    };

    // ilk kez ekrana girince en yeni yıl açılır ve zaman başlar
    new IntersectionObserver(function (entries) {
      chInView = entries[0].isIntersecting;
      if (chInView && !chStarted) { chStarted = true; showChapter(0); }
      holdChapters();
    }, { threshold: 0.3 }).observe(chStage);

    chBtns.forEach(function (b, i) { b.addEventListener('click', function () { showChapter(i, true); }); });
    chaptersEl.addEventListener('animationend', function (e) {
      if (e.animationName === 'ch-fill') { showChapter(chCur + 1); }
    });
    if (chPlay) {
      chPlay.addEventListener('click', function () {
        chPaused = !chPaused;
        chPlay.textContent = chPaused ? 'Oynat' : 'Duraklat';
        holdChapters();
      });
    }
    chStage.addEventListener('pointerenter', function () { chHover = true; holdChapters(); });
    chStage.addEventListener('pointerleave', function () { chHover = false; holdChapters(); });
    // yalnızca klavye odağı durdurur: fareyle tıklanan düğmede odak kalsa da zaman akmaya devam eder
    chStage.addEventListener('focusin', function (e) { chFocus = e.target.matches(':focus-visible'); holdChapters(); });
    chStage.addEventListener('focusout', function () { chFocus = false; holdChapters(); });
    document.addEventListener('visibilitychange', holdChapters);
    holdChapters();
  }
  /* ---------- [data-progress]: öğenin ekrandan geçiş oranı (0 → 1) --p olarak yazılır;
     data-speed varsa buna göre --py (parallax kayması) da hesaplanır ---------- */
  var progressEls = Array.prototype.slice.call(document.querySelectorAll('[data-progress]'));
  function updateProgress(el) {
    var r = el.getBoundingClientRect();
    var vh = window.innerHeight;
    if (r.bottom < -200 || r.top > vh + 200) { return; }
    var p = Math.min(1, Math.max(0, (vh - r.top) / (vh + r.height)));
    el.style.setProperty('--p', p.toFixed(4));
    var speed = parseFloat(el.getAttribute('data-speed'));
    if (speed) { el.style.setProperty('--py', ((p - 0.5) * speed * 320).toFixed(1) + 'px'); }
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
  }, { passive: true });

  /* ---------- arşiv: zaman çizelgesi çizgisi kaydırdıkça dolar ---------- */
  var timeline = document.querySelector('[data-timeline]');
  function fillTimeline() {
    var r = timeline.getBoundingClientRect();
    var mid = window.innerHeight * 0.6;
    var p = Math.min(1, Math.max(0, (mid - r.top) / r.height));
    timeline.style.setProperty('--fill', p.toFixed(4));
    timeline.querySelectorAll('[data-t-item]').forEach(function (item) {
      item.classList.toggle('is-past', item.getBoundingClientRect().top < mid);
    });
  }
  onScroll();

  /* ---------- kaydırınca beliren içerik ---------- */
  document.querySelectorAll('[data-reveal="stagger"]').forEach(function (group) {
    Array.prototype.forEach.call(group.children, function (child, i) { child.style.setProperty('--d', i); });
  });
  var revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- sayfa içi menü: ekranda okunan bölümün bağlantısını işaretler ---------- */
  var spy = document.querySelector('[data-spy]');
  if (spy && 'IntersectionObserver' in window) {
    var spyLinks = spy.querySelectorAll('a[href^="#"]');
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) { return; }
        spyLinks.forEach(function (a) {
          var on = a.getAttribute('href') === '#' + en.target.id;
          if (on) { a.setAttribute('aria-current', 'true'); } else { a.removeAttribute('aria-current'); }
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    spyLinks.forEach(function (a) {
      var sec = document.getElementById(a.getAttribute('href').slice(1));
      if (sec) { sio.observe(sec); }
    });
  }

  /* ---------- Lawment Insights: kaydırdıkça sayfası çevrilen dergi ----------
     Bölüm sabitlenir; ilerleme (0 → 1) önce kapağı öne döndürür, sonra yaprakları sırayla çevirir.
     f = açık sayfa çifti (0 kapak, n arka kapak); yaprak i, f i'den i+1'e giderken 0° → -180° döner. */
  // dergi görselleri 3D dönüşüm ve sabitlenen sahne içinde: bazı mobil tarayıcılar tembel yüklemeyi
  // hiç tetiklemiyor. Bölüm yaklaşınca hepsini hemen yüklemeye geçir.
  var mags = document.querySelectorAll('[data-flipbook]');
  if (mags.length && 'IntersectionObserver' in window) {
    var mio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) { return; }
        en.target.querySelectorAll('img[loading="lazy"]').forEach(function (img) { img.loading = 'eager'; });
        mio.unobserve(en.target);
      });
    }, { rootMargin: '800px 0px' });
    mags.forEach(function (el) { mio.observe(el); });
  }

  var fb = document.querySelector('[data-flipbook]');
  if (fb && animOn()) {
    var book = fb.querySelector('.fb-book');
    var leaves = Array.prototype.slice.call(fb.querySelectorAll('[data-leaf]'));
    var count = fb.querySelector('[data-fb-count]');
    var n = leaves.length;
    // ilerleme: %16 giriş (dev başlık geri çekilir, dergi yükselip öne döner), %72 sayfa çevirme, %12 kapanış
    var INTRO = 0.16, SPAN = 0.72, OUTRO = 0.12;
    var stage = fb.querySelector('.fb-stage');
    var caps = Array.prototype.slice.call(fb.querySelectorAll('.fb-caps li'));
    var outroEl = fb.querySelector('.fb-outro');
    var ease = function (t) { return 1 - Math.pow(1 - t, 3); };
    fb.style.setProperty('--fb-len', String(2 + n * 0.75));
    var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
    var lastK = -1;
    var progress = function () {
      var r = fb.getBoundingClientRect();
      return clamp(-r.top / (fb.offsetHeight - window.innerHeight), 0, 1);
    };
    var render = function () {
      var p = progress();
      var intro = clamp(p / INTRO, 0, 1);
      var f = clamp((p - INTRO) / SPAN, 0, 1) * n;
      leaves.forEach(function (leaf, i) {
        var t = clamp(f - i, 0, 1);
        leaf.style.setProperty('--r', (-180 * t).toFixed(2) + 'deg');
        leaf.style.setProperty('--z', t > 0.5 ? String(i + 1) : String(n - i + 1));
      });
      var shift = f < 1 ? -25 * (1 - f) : (f > n - 1 ? 25 * (f - (n - 1)) : 0);
      var e = ease(intro);
      var outro = clamp((p - INTRO - SPAN) / OUTRO, 0, 1);
      book.style.setProperty('--fb-shift', shift.toFixed(2) + '%');
      book.style.setProperty('--fb-tilt', (22 * (1 - e)).toFixed(2) + 'deg');
      book.style.setProperty('--fb-turn', (-38 * (1 - e)).toFixed(2) + 'deg');
      book.style.setProperty('--fb-scale', ((0.62 + 0.38 * e) * (1 - 0.16 * outro)).toFixed(4));
      book.style.setProperty('--fb-lift', ((1 - e) * 16 - outro * 4).toFixed(2) + 'vh');
      stage.style.setProperty('--fb-title', (1 - e).toFixed(3));
      stage.style.setProperty('--fb-title-scale', (1 + 0.12 * e).toFixed(4));
      stage.style.setProperty('--fb-glow', (0.35 + 0.65 * e * (1 - 0.4 * outro)).toFixed(3));
      stage.style.setProperty('--fb-prog', p.toFixed(4));
      stage.style.setProperty('--fb-out', outro.toFixed(3));
      if (outroEl) { outroEl.classList.toggle('is-on', outro > 0.5); }
      var k = Math.round(f);
      // sayfa çiftinin başlığı: giriş bitmeden ve kapanışta gizli
      var capIndex = intro < 0.85 || outro > 0.3 ? -1 : k;
      caps.forEach(function (c, i) { c.classList.toggle('is-on', i === capIndex); });
      if (k !== lastK && count) {
        lastK = k;
        count.textContent = k === 0 ? 'Kapak' : (k === n ? 'Arka kapak' : 'Sayfa ' + (2 * k - 1) + '–' + (2 * k) + ' / ' + (2 * n - 1));
      }
    };
    var fbTick = false;
    window.addEventListener('scroll', function () {
      if (!fbTick) { fbTick = true; window.requestAnimationFrame(function () { render(); fbTick = false; }); }
    }, { passive: true });
    window.addEventListener('resize', render);
    // oklar: bir sonraki/önceki sayfa çiftinin kaydırma konumuna gider
    var go = function (dir) {
      var f = clamp((progress() - INTRO) / SPAN, 0, 1) * n;
      var k = clamp(Math.round(f) + dir, 0, n);
      var top = fb.getBoundingClientRect().top + window.scrollY;
      var y = top + (INTRO + (k / n) * SPAN) * (fb.offsetHeight - window.innerHeight);
      window.scrollTo({ top: y + 2, behavior: 'smooth' });
    };
    fb.querySelector('[data-fb-prev]').addEventListener('click', function () { go(-1); });
    fb.querySelector('[data-fb-next]').addEventListener('click', function () { go(1); });
    render();
  }

  /* ---------- sayarak yükselen rakamlar ---------- */
  // HTML'de son değer yazılıdır (JS yoksa doğru görünür); animasyon açıksa sıfırdan sayar.
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length && animOn() && 'IntersectionObserver' in window) {
    var run = function (el) {
      var target = parseFloat(el.getAttribute('data-count'));
      var dur = 1600, t0 = null;
      var step = function (t) {
        if (t0 === null) { t0 = t; }
        var k = Math.min(1, (t - t0) / dur);
        var eased = 1 - Math.pow(1 - k, 4);
        el.textContent = Math.round(target * eased).toLocaleString('tr-TR');
        if (k < 1) { window.requestAnimationFrame(step); }
      };
      window.requestAnimationFrame(step);
    };
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { run(en.target); cio.unobserve(en.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) { el.textContent = '0'; }
      cio.observe(el);
    });
  }

  /* ---------- kayan şeritler: fareyle üzerine gelince yavaşlar ---------- */
  document.querySelectorAll('.marquee').forEach(function (mq) {
    var track = mq.querySelector('.mq-track');
    if (!track || !track.getAnimations) { return; }
    var setRate = function (rate) {
      track.getAnimations().forEach(function (a) {
        if (a.updatePlaybackRate) { a.updatePlaybackRate(rate); } else { a.playbackRate = rate; }
      });
    };
    mq.addEventListener('pointerenter', function () { setRate(0.25); });
    mq.addEventListener('pointerleave', function () { setRate(1); });
  });

  /* ---------- ekip: departman filtresi, kartlar yumuşak geçişle yeniden dizilir (FLIP) ---------- */
  var team = document.querySelector('[data-team]');
  if (team) {
    var cards = Array.prototype.slice.call(team.querySelectorAll('[data-dept]'));
    var buttons = document.querySelectorAll('[data-filter]');
    var status = document.querySelector('[data-team-status]');
    buttons.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-filter');
        buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
        var first = new Map();
        cards.forEach(function (c) { if (!c.hidden) { first.set(c, c.getBoundingClientRect()); } });
        var shown = 0;
        cards.forEach(function (c) {
          // bir kişi birden çok departmanda olabilir: data-dept boşlukla ayrılmış liste
          var inDept = (c.getAttribute('data-dept') || '').split(' ').indexOf(f) !== -1;
          // not kartı (üyesi olmayan departman) yalnızca kendi filtresinde görünür
          var match = c.classList.contains('member--note') ? inDept : (f === 'hepsi' || inDept);
          c.hidden = !match;
          if (match && !c.classList.contains('member--note')) { shown++; }
        });
        if (status) { status.textContent = shown + ' kişi gösteriliyor'; }
        if (reduce.matches || !cards[0].animate) { return; }
        cards.forEach(function (c) {
          if (c.hidden) { return; }
          var last = c.getBoundingClientRect();
          var prev = first.get(c);
          if (prev) {
            var dx = prev.left - last.left, dy = prev.top - last.top;
            if (dx || dy) {
              c.animate([{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }],
                { duration: 520, easing: 'cubic-bezier(.16,1,.3,1)' });
            }
          } else {
            c.animate([{ opacity: 0, transform: 'scale(.92)' }, { opacity: 1, transform: 'none' }],
              { duration: 420, easing: 'cubic-bezier(.16,1,.3,1)' });
          }
        });
      });
    });
  }

  /* ---------- formlar ----------
     Şimdilik e-posta taslağı açar. Wix'e geçince yalnızca `send` fonksiyonu değiştirilir:
     form verisi `collect(form)` ile düz bir nesne olarak hazırlanır (alan adı -> değer). */
  var Forms = {
    to: 'info@lawment.org',
    collect: function (form) {
      var data = {};
      form.querySelectorAll('input, select, textarea').forEach(function (el) {
        if (!el.name) { return; }
        var lab = form.querySelector('label[for="' + el.id + '"]');
        var key = el.type === 'checkbox' ? 'KVKK onayı' : (lab ? lab.textContent.trim() : el.name);
        data[key] = el.type === 'checkbox' ? (el.checked ? 'Evet' : 'Hayır') : el.value.trim();
      });
      return data;
    },
    send: function (subject, data) {
      var body = Object.keys(data).map(function (k) { return k + ': ' + data[k]; }).join('\n');
      window.location.href = 'mailto:' + Forms.to + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      return Promise.resolve();
    }
  };
  window.LawmentForms = Forms;
  /* hata metni alanın altında, Türkçe ve nedenini söyleyerek gösterilir; tarayıcının kendi balonu kullanılmaz */
  var fieldSeq = 0;
  var errText = function (el) {
    if (el.validity.valueMissing) { return el.type === 'checkbox' ? 'Devam etmek için onay vermelisin.' : 'Bu alan zorunlu.'; }
    if (el.validity.typeMismatch && el.type === 'email') { return 'Geçerli bir e-posta adresi yaz, örneğin ad@ornek.com.'; }
    return 'Bu alanı kontrol et.';
  };
  var clearError = function (el) {
    el.removeAttribute('aria-invalid');
    el.removeAttribute('aria-describedby');
    var old = document.getElementById(el.id + '-hata');
    if (old) { old.remove(); }
  };
  var showError = function (el) {
    clearError(el);
    var p = document.createElement('p');
    p.className = 'field-error';
    p.id = el.id + '-hata';
    p.textContent = errText(el);
    var holder = el.closest('.field') || el.closest('.consent') || el.parentNode;
    if (holder.classList.contains('consent')) { holder.after(p); } else { holder.appendChild(p); }
    el.setAttribute('aria-invalid', 'true');
    el.setAttribute('aria-describedby', p.id);
  };
  document.querySelectorAll('form[data-form]').forEach(function (form) {
    form.noValidate = true;
    var fields = form.querySelectorAll('input, select, textarea');
    fields.forEach(function (el) {
      if (!el.id) { el.id = 'alan-' + (++fieldSeq); }
      var recheck = function () { if (el.hasAttribute('aria-invalid') && el.checkValidity()) { clearError(el); } };
      el.addEventListener('input', recheck);
      el.addEventListener('change', recheck);
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstBad = null;
      fields.forEach(function (el) {
        if (el.checkValidity()) { clearError(el); } else { showError(el); firstBad = firstBad || el; }
      });
      if (firstBad) { firstBad.focus(); return; }
      var status = form.querySelector('.form-status');
      Forms.send(form.getAttribute('data-form'), Forms.collect(form)).then(function () {
        if (status) {
          status.textContent = form.getAttribute('data-status') ||
            'E-posta uygulamanda hazır bir taslak açılıyor. Açılmazsa bilgilerini info@lawment.org adresine gönderebilirsin.';
        }
      });
    });
  });

  var year = document.querySelector('[data-year]');
  if (year) { year.textContent = new Date().getFullYear(); }
})();
