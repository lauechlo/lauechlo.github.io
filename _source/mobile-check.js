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
            // 2026-09-03 pass: metadata roles must use a second face, not inherit the body serif
            metaInBodyFace: [...document.querySelectorAll('.now .k, .list .d, a.work .meta, .channel-lbl')]
              .filter(e => getComputedStyle(e).fontFamily === getComputedStyle(document.body).fontFamily).length,
            magicLeftovers: document.querySelectorAll('#tweaks-popover, [data-magic], .foot button, .toast, #open-tweaks, .magic-particle').length,
            rotationLeftovers: document.querySelectorAll('#reading-rotation, #today-spin, .now li[data-icon]').length,
            resumeGrid: document.querySelectorAll('.resume, .res-col').length,
            slides: document.querySelectorAll('#slides img').length,
            slidesNoAlt: [...document.querySelectorAll('#slides img')].filter(i => !i.getAttribute('alt')).length,
          };
        });
        const fail = (what) => failures.push(`${vp.name} ${path}: ${what}`);
        if (m.overflow > 0) fail(`horizontal overflow ${m.overflow}px`);
        if (m.headerH > 64) fail(`header ${Math.round(m.headerH)}px tall`);
        if (path === '/index.html') {
          if (m.workRows !== 4) fail(`expected 4 a.work rows, found ${m.workRows}`);
          if (m.nowRows !== 4) fail(`expected 4 .now rows, found ${m.nowRows}`);
          if (m.upperCase > 0) fail(`${m.upperCase} uppercase-transformed elements`);
          if (m.boxes > 0) fail(`${m.boxes} card-like boxes (radius>8 with border) in main`);
          if (m.fraunces) fail(`Fraunces still loaded`);
          if (m.emDash) fail(`em dash in homepage copy`);
          if (m.metaInBodyFace > 0) fail(`${m.metaInBodyFace} metadata elements still in the body face`);
          if (m.magicLeftovers > 0) fail(`${m.magicLeftovers} magic-mode elements still in the DOM`);
          if (m.rotationLeftovers > 0) fail(`${m.rotationLeftovers} rotation ids or data-icon glyphs still in the DOM`);
          if (m.resumeGrid > 0) fail(`${m.resumeGrid} résumé grid elements still in the DOM`);
          if (m.slides < 9) fail(`expected at least 9 slideshow photos, found ${m.slides}`);
          if (m.slidesNoAlt > 0) fail(`${m.slidesNoAlt} slideshow photos without alt text`);
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
