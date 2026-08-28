// _source/mobile-check.js — run: node _source/mobile-check.js
const { webkit, devices } = require('playwright');
const BASE = 'http://localhost:8765';
const PAGES = ['/index.html','/case-studies/cariina.html','/case-studies/hoagie.html',
  '/case-studies/ai-fluency-lab.html','/case-studies/disney.html',
  '/essays/working-with-ai.html','/essays/major-as-method.html','/essays/500ms-sound.html'];
const VIEWPORTS = [
  { name: 'SE 375',      ...devices['iPhone 13'], viewport: { width: 375, height: 667 } },
  { name: 'i14 390',     ...devices['iPhone 13'], viewport: { width: 390, height: 664 } },
  { name: 'ProMax 430',  ...devices['iPhone 15 Pro Max'] },
  { name: 'ProMax land', ...devices['iPhone 15 Pro Max landscape'] },
];

(async () => {
  const browser = await webkit.launch();
  const failures = [];
  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext(vp);
    for (const path of PAGES) {
      const page = await ctx.newPage();
      const errors = [];
      page.on('response', r => { if (r.status() === 404) errors.push(`404 ${r.url()}`); });
      await page.goto(BASE + path, { waitUntil: 'networkidle' });
      const m = await page.evaluate(() => {
        const q = s => document.querySelector(s);
        const cols = s => q(s) ? getComputedStyle(q(s)).gridTemplateColumns.split(' ').length : null;
        const hdr = q('.topnav') || q('.topbar');
        const p1 = q('.photo.p1');
        return {
          overflow: document.documentElement.scrollWidth - window.innerWidth,
          headerH: hdr ? hdr.getBoundingClientRect().height : 0,
          sideQuestCols: cols('.projects-compact.side-quests'),
          favCols: cols('.fav-strip'),
          photoW: p1 ? p1.getBoundingClientRect().width : null,
          collageW: q('.collage') ? q('.collage').getBoundingClientRect().width : null,
          tinyText: [...document.querySelectorAll('.card .lbl,.card .delta,.post-date,.channel-lbl')]
            .filter(e => parseFloat(getComputedStyle(e).fontSize) < 12).length,
          mobileMeShown: q('.mobile-me') ? getComputedStyle(q('.mobile-me')).display !== 'none' : false,
        };
      });
      const isMobile = vp.viewport.width < 768;
      const fail = (what) => failures.push(`${vp.name} ${path}: ${what}`);
      if (m.overflow > 0) fail(`horizontal overflow ${m.overflow}px`);
      if (m.headerH > 64) fail(`header ${Math.round(m.headerH)}px tall`);
      if (path === '/index.html' && isMobile) {
        if (m.sideQuestCols !== 1) fail(`side-quests has ${m.sideQuestCols} cols`);
        if (m.favCols !== 1) fail(`fav-strip has ${m.favCols} cols`);
        if (m.photoW < m.collageW * 0.45) fail(`collage photo only ${Math.round(m.photoW)}px wide`);
        if (m.tinyText > 0) fail(`${m.tinyText} labels under 12px`);
        if (m.mobileMeShown) fail(`.mobile-me still shown`);
      }
      errors.forEach(fail);
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  if (failures.length) { console.log('FAIL\n' + failures.join('\n')); process.exit(1); }
  console.log('PASS: all mobile checks green');
})();
