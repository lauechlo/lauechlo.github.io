// _source/mobile-check.js — run: node _source/mobile-check.js
// Lives in _source/ (Jekyll skips _-prefixed dirs, so GitHub Pages does not publish it).
// Do not add a .nojekyll file without moving this.
const { execSync } = require('child_process');
try { module.paths.push(execSync('npm root -g', { encoding: 'utf8' }).trim()); } catch (_) {}
const { webkit, devices } = require('playwright');
const BASE = 'http://localhost:8765';
const ALL_PAGES = ['/index.html','/case-studies/cariina.html','/case-studies/hoagie.html',
  '/case-studies/ai-fluency-lab.html','/case-studies/disney.html',
  '/essays/working-with-ai.html','/essays/major-as-method.html','/essays/500ms-sound.html',
  '/essays/poems.html'];
// PAGES=/index.html node _source/mobile-check.js  -> quick run on a subset
const PAGES = process.env.PAGES ? process.env.PAGES.split(',') : ALL_PAGES;
const VIEWPORTS = [
  { name: 'SE 375',      ...devices['iPhone 13'], viewport: { width: 375, height: 667 } },
  { name: 'i14 390',     ...devices['iPhone 13'], viewport: { width: 390, height: 664 } },
  { name: 'ProMax 430',  ...devices['iPhone 15 Pro Max'] },
  { name: 'ProMax land', ...devices['iPhone 15 Pro Max landscape'] },
];

(async () => {
  const browser = await webkit.launch();
  const failures = [];
  try {
    for (const vp of VIEWPORTS) {
      const ctx = await browser.newContext(vp);
      for (const path of PAGES) {
        const page = await ctx.newPage();
        const errors = [];
        page.on('response', r => { if (r.status() === 404) errors.push(`404 ${r.url()}`); });
        page.on('pageerror', e => errors.push(`page error: ${e.message}`));
        try {
          await page.goto(BASE + path, { waitUntil: 'networkidle' });
        } catch (e) {
          throw new Error(`cannot reach ${BASE + path} — is the server running? (${e.message})`);
        }
        const m = await page.evaluate(() => {
          const q = s => document.querySelector(s);
          return {
            overflow: document.documentElement.scrollWidth - window.innerWidth,
            headerH: (q('.topbar') || q('.top')) ? (q('.topbar') || q('.top')).getBoundingClientRect().height : 0,
            workRows: document.querySelectorAll('a.work').length,
            nowRows: document.querySelectorAll('.now li').length,
            tinyText: [...document.querySelectorAll('body *')]
              .filter(e => e.closest('#tweaks-popover') === null && e.getClientRects().length > 0 && parseFloat(getComputedStyle(e).fontSize) < 12).length,
            upperCase: [...document.querySelectorAll('body *')]
              .filter(e => getComputedStyle(e).display !== 'none' && getComputedStyle(e).textTransform === 'uppercase' && e.closest('#tweaks-popover') === null).length,
            boxes: [...document.querySelectorAll('main *')]
              .filter(e => { const s = getComputedStyle(e); return e.tagName !== 'IMG' && e.tagName !== 'IFRAME' && parseFloat(s.borderRadius) > 8 && s.borderStyle !== 'none' && s.borderWidth !== '0px'; }).length,
            fraunces: !![...document.styleSheets].find(ss => (ss.href||'').includes('Fraunces')) || !![...document.querySelectorAll('link')].find(l => (l.href||'').includes('Fraunces')),
            emDash: (document.querySelector('main')?.innerText || '').includes('—'),
            ground: getComputedStyle(document.body).backgroundColor,
            topbar: (el => el ? getComputedStyle(el).backgroundColor : '')(document.querySelector('.topbar')),
            icon96: document.querySelectorAll('link[rel="icon"][sizes="96x96"], link[rel="icon"][href="/favicon.ico"]').length,
            personLd: [...document.querySelectorAll('script[type="application/ld+json"]')].filter(s => /"Person"/.test(s.textContent) && /"WebSite"/.test(s.textContent)).length,
            oldFonts: [...document.querySelectorAll('link[rel="stylesheet"]')].filter(l => /Vollkorn|Commissioner/.test(l.href || '')).length,
            // 2026-09-03 pass: metadata roles must use a second face, not inherit the body serif
            metaInBodyFace: [...document.querySelectorAll('.now .k, .list .d, a.work .meta, .channel-lbl')]
              .filter(e => getComputedStyle(e).fontFamily === getComputedStyle(document.body).fontFamily).length,
            magicLeftovers: document.querySelectorAll('#tweaks-popover, [data-magic], .foot button, .toast, #open-tweaks, .magic-particle').length,
            rotationLeftovers: document.querySelectorAll('#reading-rotation, #today-spin, .now li[data-icon]').length,
            resumeGrid: document.querySelectorAll('.resume, .res-col').length,
            slides: document.querySelectorAll('#slides img').length,
            brandMark: document.querySelectorAll('.hero .brand svg[role="img"][aria-label="Chloe Lau"]').length,
            // 2026-10-22 lettering piece: the wordmark is the hero, the pen marks are the nav, a numbered contents list, paper prints
            heroMarkH: (e => e ? e.getBoundingClientRect().height : 0)(document.querySelector('.hero .brand svg')),
            iconNav: document.querySelectorAll('.iconnav a > svg[aria-hidden="true"]').length,
            toc: document.querySelectorAll('.toc li a[href^="#"]').length,
            deadAnchors: [...document.querySelectorAll('.toc a[href^="#"], .iconnav a[href^="#"]')].filter(a => !document.getElementById(a.getAttribute('href').slice(1))).length,
            smooth: getComputedStyle(document.documentElement).scrollBehavior,
            prints: document.querySelectorAll('.headshot.print, .stack > #slides').length,
            topBar: document.querySelectorAll('.top').length,
            iconNavRows: new Set([...document.querySelectorAll('.iconnav a')].map(a => Math.round(a.getBoundingClientRect().top))).size,
            poemsLink: document.querySelectorAll('a[href="essays/poems.html"]').length,
            nowMarks: document.querySelectorAll('.now li > svg[aria-hidden="true"]').length,
            slidesAspect: (r => r.height ? r.width / r.height : 0)((document.getElementById('slides') || document.body).getBoundingClientRect()),
            slidesNoAlt: [...document.querySelectorAll('#slides img')].filter(i => !i.getAttribute('alt')).length,
            // 2026-09-12 pass: no separator dots or typographic arrows in visible text
            dots: ([...document.querySelectorAll('main, article, .topbar, .article-footer')].map(e => e.innerText || '').join(' ').match(/·/g) || []).length,
            arrows: ([...document.querySelectorAll('main, article, .topbar, .article-footer')].map(e => e.innerText || '').join(' ').match(/[→←↗]/g) || []).length,
            arrs: document.querySelectorAll('.arr').length,
          };
        });
        const fail = (what) => failures.push(`${vp.name} ${path}: ${what}`);
        if (m.overflow > 0) fail(`horizontal overflow ${m.overflow}px`);
        if (m.headerH > 64) fail(`header ${Math.round(m.headerH)}px tall`);
        if (m.icon96 < 2) fail(`missing the 96px icon or the root favicon.ico (Google needs a 48-multiple icon)`);
        if (path === '/index.html' && m.personLd < 1) fail(`homepage lacks the WebSite + Person structured data`);
        if (m.ground !== 'rgb(250, 243, 209)') fail(`ground is ${m.ground}, expected the butter paper rgb(250, 243, 209)`);
        if (m.topbar && !m.topbar.startsWith('rgba(250, 243, 209')) fail(`topbar is ${m.topbar}, expected the butter paper with alpha`);
        if (m.oldFonts > 0) fail(`Vollkorn or Commissioner still requested (owner chose Newsreader + Karla on 2026-09-04)`);
        if (path === '/index.html') {
          if (m.workRows !== 4) fail(`expected 4 a.work rows, found ${m.workRows}`);
          if (m.nowRows !== 5) fail(`expected 5 .now rows, found ${m.nowRows}`);
          if (m.upperCase > 0) fail(`${m.upperCase} uppercase-transformed elements`);
          if (m.boxes > 0) fail(`${m.boxes} card-like boxes (radius>8 with border) in main`);
          if (m.fraunces) fail(`Fraunces still loaded`);
          if (m.emDash) fail(`em dash in homepage copy`);
          if (m.metaInBodyFace > 0) fail(`${m.metaInBodyFace} metadata elements still in the body face`);
          if (m.magicLeftovers > 0) fail(`${m.magicLeftovers} magic-mode elements still in the DOM`);
          if (m.rotationLeftovers > 0) fail(`${m.rotationLeftovers} rotation ids or data-icon glyphs still in the DOM`);
          if (m.resumeGrid > 0) fail(`${m.resumeGrid} résumé grid elements still in the DOM`);
          if (m.slides < 11) fail(`expected at least 11 slideshow photos, found ${m.slides}`);
          if (m.brandMark !== 1) fail(`expected the handwritten wordmark svg in .hero .brand, found ${m.brandMark}`);
          if (m.heroMarkH < 120) fail(`wordmark hero is ${Math.round(m.heroMarkH)}px tall, expected at least 120`);
          if (m.iconNav !== 5) fail(`expected 5 pen-mark svgs in the icon nav, found ${m.iconNav}`);
          if (m.toc !== 7) fail(`expected 7 contents entries, found ${m.toc}`);
          if (m.deadAnchors > 0) fail(`${m.deadAnchors} nav or contents links point at missing ids`);
          if (m.smooth !== 'smooth') fail(`scroll-behavior is ${m.smooth}, expected smooth`);
          if (m.prints !== 2) fail(`expected the headshot print and the framed slideshow, found ${m.prints}`);
          if (m.topBar > 0) fail(`old .top bar still in the DOM`);
          if (m.iconNavRows !== 1) fail(`icon nav wraps to ${m.iconNavRows} rows`);
          if (m.poemsLink < 1) fail(`the poems page is not linked from the homepage`);
          if (m.nowMarks !== 5) fail(`expected 5 pen-mark svgs on the Currently rows, found ${m.nowMarks}`);
          if (m.slidesAspect < 0.76 || m.slidesAspect > 0.84) fail(`slideshow box is ${m.slidesAspect.toFixed(2)} wide per tall, expected a fixed 4:5 portrait`);
          if (m.slidesNoAlt > 0) fail(`${m.slidesNoAlt} slideshow photos without alt text`);
        }
        if (m.dots > 0) fail(`${m.dots} middle-dot separators in visible text`);
        if (m.arrows > 0) fail(`${m.arrows} typographic arrows in visible text`);
        if (path === '/index.html') {
          if (m.arrs > 0) fail(`${m.arrs} .arr arrow spans still in the DOM`);
        }
        if (m.tinyText > 0) fail(`${m.tinyText} text elements under 12px`);
        errors.forEach(fail);
        await page.close();
      }
      await ctx.close();
    }
  } finally {
    await browser.close();
  }
  if (failures.length) { console.log('FAIL\n' + failures.join('\n')); process.exitCode = 1; }
  else console.log('PASS: all mobile checks green');
})().catch(e => { console.error(e.message); process.exitCode = 1; });
