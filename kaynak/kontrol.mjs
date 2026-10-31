// Site kontrolü: her sayfa 1366px ve 390px, açık ve koyu temada ekran görüntüsü;
// yatay taşma, kırık iç bağlantı, konsol hatası, reduced-motion ve JS kapalıyken görünürlük.
// Kullanım: node kaynak/kontrol.mjs [sayfa.html ...]   (yerel sunucu http://127.0.0.1:8080 açık olmalı)
import { chromium } from 'playwright';
import { readdirSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SITE = join(ROOT, 'site');
const SHOTS = join(ROOT, 'kaynak', 'ekran');
const BASE = 'http://127.0.0.1:8080/';
mkdirSync(SHOTS, { recursive: true });

const pages = process.argv.slice(2).length ? process.argv.slice(2) : readdirSync(SITE).filter(f => f.endsWith('.html'));
const problems = [];
const say = (p, msg) => { problems.push(`${p}: ${msg}`); };

// Ayrı Chromium indirmek yerine Windows'ta hazır gelen Edge kullanılır.
const browser = await chromium.launch({ channel: 'msedge' });

async function scrollThrough(page) {
  await page.evaluate(async () => {
    // smooth scroll art arda çağrıları iptal ettiği için 'instant' kullanılır
    for (let y = 0; y < document.body.scrollHeight; y += 400) { window.scrollTo({ top: y, behavior: 'instant' }); await new Promise(r => setTimeout(r, 80)); }
    window.scrollTo({ top: 0, behavior: 'instant' });
  });
  await page.waitForTimeout(1400);
}

for (const file of pages) {
  for (const [w, h] of [[1366, 900], [390, 844]]) {
    for (const scheme of ['light', 'dark']) {
      const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: scheme, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      page.on('console', m => { if (m.type() === 'error') say(file, `konsol hatası (${w} ${scheme}): ${m.text()}`); });
      page.on('pageerror', e => say(file, `JS hatası: ${e.message}`));
      page.on('response', r => { if (r.status() >= 400 && r.url().startsWith(BASE)) say(file, `${r.status()} ${r.url()}`); });
      await page.goto(BASE + file, { waitUntil: 'networkidle' });
      await scrollThrough(page);
      const overflow = await page.evaluate(() => {
        const vw = document.documentElement.clientWidth;
        const out = [];
        if (document.documentElement.scrollWidth > vw) out.push(`sayfa genişliği ${document.documentElement.scrollWidth} > ${vw}`);
        // taşan ama kırpan bir ebeveynin (overflow hidden/clip) içinde kalan öğeler sorun değildir
        const clipped = el => { for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if (o !== 'visible') return true; } return false; };
        document.querySelectorAll('body *').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.width && r.right > vw + 1 && getComputedStyle(el).position !== 'fixed' && !clipped(el)) {
            out.push(`${el.tagName.toLowerCase()}.${[...el.classList].join('.')} sağ=${Math.round(r.right)}`);
          }
        });
        return out.slice(0, 6);
      });
      overflow.forEach(o => say(file, `taşma ${w}px: ${o}`));
      await page.screenshot({ path: join(SHOTS, `${file.replace('.html', '')}-${w}-${scheme}.png`), fullPage: true });
      await ctx.close();
    }
  }

  // iç bağlantılar
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(BASE + file);
  const links = await page.$$eval('a[href]', as => as.map(a => a.getAttribute('href')));
  for (const href of links) {
    if (/^(https?:|mailto:|tel:)/.test(href)) continue;
    const [path, hash] = href.split('#');
    const target = path || file;
    if (!existsSync(join(SITE, target))) { say(file, `kırık bağlantı: ${href}`); continue; }
    if (hash && target === file && !(await page.$(`[id="${hash}"]`))) say(file, `olmayan çapa: ${href}`);
  }
  await ctx.close();

  // reduced-motion: animasyon kalmamalı, her şey görünür olmalı
  const rm = await browser.newContext({ reducedMotion: 'reduce' });
  const rp = await rm.newPage();
  await rp.goto(BASE + file, { waitUntil: 'networkidle' });
  const rmState = await rp.evaluate(() => ({
    anims: document.getAnimations().filter(a => a.playState === 'running').length,
    hidden: [...document.querySelectorAll('main *')].filter(el => getComputedStyle(el).opacity === '0' && el.textContent.trim()).length,
    animClass: document.documentElement.classList.contains('anim'),
  }));
  if (rmState.anims) say(file, `reduced-motion açıkken ${rmState.anims} animasyon çalışıyor`);
  if (rmState.hidden) say(file, `reduced-motion açıkken ${rmState.hidden} öğe görünmez`);
  if (rmState.animClass) say(file, 'reduced-motion açıkken .anim sınıfı eklendi');
  await rm.close();

  // JS kapalı: hiçbir metin görünmez kalmamalı
  const nj = await browser.newContext({ javaScriptEnabled: false });
  const np = await nj.newPage();
  await np.goto(BASE + file);
  await np.waitForTimeout(2600);
  const hiddenNoJs = await np.evaluate(() => [...document.querySelectorAll('main *')].filter(el => getComputedStyle(el).opacity === '0' && el.textContent.trim()).length);
  if (hiddenNoJs) say(file, `JS kapalıyken ${hiddenNoJs} öğe görünmez`);
  await nj.close();
  console.log('kontrol edildi:', file);
}

await browser.close();
console.log(problems.length ? '\nSORUNLAR:\n' + problems.join('\n') : '\nSorun bulunmadı.');
