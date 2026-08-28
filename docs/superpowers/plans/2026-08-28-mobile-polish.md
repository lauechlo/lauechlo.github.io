# Mobile Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make chloelau.io render cleanly on iPhones (SE 375px, 13/14 390px, Pro Max 430px, plus Pro Max landscape 814×380) with no horizontal scroll, no broken grids, and touch-reachable interactions.

**Architecture:** All fixes are CSS/markup edits inside the existing `@media (max-width:767px)` block of `index.html` (lines ~456–536) and `article.css`'s mobile block, plus a few small JS/attribute changes. A Playwright WebKit check script asserts the measurable defects (scrollWidth, header height, grid column counts, photo sizes) so every task has a pass/fail gate. No new fonts, no copy changes, no restructuring.

**Tech Stack:** Static HTML/CSS/JS, Playwright 1.62 (WebKit) already installed globally, `python -m http.server` for local preview.

**Spec:** The four audit reports from the 2026-08-28 session (iPhone SE, iPhone 13/14, iPhone 15 Pro Max portrait+landscape, static CSS audit). Screenshots under `C:\Users\lauec\AppData\Local\Temp\claude\C--Users-lauec\188a2cd5-6aee-49fd-9e57-418f97d04494\scratchpad\{se,i14,promax}\`.

## Global Constraints

- No new font families or weights (site uses Fraunces + Karla only).
- Do not rewrite any visible copy; only layout/CSS/attributes change.
- Do not rename `case-studies/ai-fluency-lab.html` or its assets (CLAUDE.md).
- Specificity trap: desktop rules like `.projects-compact.side-quests` and `.photo.p1` are (0,2,0); every mobile override must match or exceed that specificity (repeat the compound selector inside the media query).
- Verify with WebKit, not Chromium — iOS Safari ignores `overflow-x:hidden` on `body` alone.
- Commit after each task on `main` (plain GitHub Pages deploy; small commits are easy to revert).

---

### Task 1: Mobile check harness

**Files:**
- Create: `_source/mobile-check.js`

**Interfaces:**
- Produces: `node _source/mobile-check.js` — exits 0 and prints `PASS` if all assertions hold, otherwise prints `FAIL` + one line per failure. Later tasks only run this command.

- [ ] **Step 1: Start the local server (leave running in a second terminal)**

```powershell
cd "C:\Users\lauec\Desktop\Princeton\Personal Website"; python -m http.server 8765
```

- [ ] **Step 2: Write the check script**

```js
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
```

- [ ] **Step 3: Run it and confirm it fails on the current site**

Run: `node _source/mobile-check.js`
Expected: `FAIL` with lines including `horizontal overflow`, `header 1xxpx tall`, `side-quests has 3 cols`, `fav-strip has 2 cols`, `collage photo only ~9xpx wide`, `404 .../image-slot.js`. (If `require('playwright')` fails: `npm i -g playwright` then `npx playwright install webkit`.)

- [ ] **Step 4: Commit**

```bash
git add _source/mobile-check.js
git commit -m "test: add Playwright WebKit mobile check script"
```

---

### Task 2: Top nav, header height, anchor offset, hero blob

**Files:**
- Modify: `index.html:113` (scroll-margin), mobile block after line ~458 (`main{...}`), lines ~461–465 (`.mobile-me` mobile rules)

- [ ] **Step 1: Add mobile topnav rules** — insert immediately after `main{padding:20px 20px 64px;max-width:100%;margin:0}` inside `@media (max-width:767px)`:

```css
    /* Top nav: brand + CTA only; section links are one scroll away */
    .topnav{padding:10px 16px}
    .topnav-brand{white-space:nowrap}
    .topnav-links{gap:12px}
    .topnav-links a:not(.topnav-cta){display:none}
    .topnav-cta{padding:7px 12px;white-space:nowrap}
    /* Sticky nav already shows the name; drop the duplicate strip */
    .mobile-me{display:none}
    /* 520px decorative glow overflows a phone viewport */
    .hero::before{display:none}
    #top, #projects, #writing, #about, #resume, #contact, #currently{scroll-margin-top:60px}
```

Also add `justify-self:center;` to the existing `.hero-portrait, [data-hero="split"] .hero-portrait{...}` mobile rule — the desktop `justify-self:end` otherwise pins the 320px portrait to the right edge (`margin:0 auto` does not override it).

- [ ] **Step 2: Delete** the existing `.mobile-me{display:flex;...}` line and its four `.mobile-me .av` / `.n` companions from the mobile block (lines ~461–465). Leave the markup at line ~618 in place — it stays hidden via line 448.

- [ ] **Step 3: Verify**

Run: `node _source/mobile-check.js`
Expected: no `header ... tall`, `horizontal overflow`, or `.mobile-me still shown` lines for `/index.html` portrait. Other failures (grids, photos, 404) remain.

- [ ] **Step 4: Eyeball** — Chrome DevTools device mode at 375px: header is one row (name left, pill CTA right, ~48px). Navigate to `#projects`; heading is not hidden under the header.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "fix(mobile): compact topnav, hide duplicate name strip, remove hero glow overflow"
```

---

### Task 3: Specificity fixes — side quests, fav strip, collage

**Files:**
- Modify: `index.html` mobile block lines ~494 (`.projects-compact`), ~510 (`.fav-card`), ~516–519 (collage)

- [ ] **Step 1: Side quests** — change `.projects-compact{grid-template-columns:1fr}` to:

```css
    .projects-compact, .projects-compact.side-quests{grid-template-columns:1fr;gap:12px}
```

- [ ] **Step 2: Fav strip** — insert above `.fav-card{...}`:

```css
    .fav-strip{grid-template-columns:1fr;gap:14px}
```

- [ ] **Step 3: Collage** — replace the mobile `.photo{position:static;...}` line with:

```css
    .photo, .photo.p1, .photo.p2, .photo.p3, .photo.p4{position:static;top:auto;right:auto;bottom:auto;left:auto;width:100%;height:auto;aspect-ratio:1;transform:none !important;border-radius:10px}
    .photo image-slot{position:static;display:block;width:100%;height:100%}
```

Keep the existing `.photo img{position:static !important;...}` line.

- [ ] **Step 4: Verify**

Run: `node _source/mobile-check.js`
Expected: no `side-quests has`, `fav-strip has`, or `collage photo` lines. Visually: three side-quest cards stacked; two fav cards stacked; four square photos filling a 2×2 grid.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "fix(mobile): collapse side quests, fav strip and collage to phone grids"
```

---

### Task 4: Spacing alignment, contact channels, text floors

**Files:**
- Modify: `index.html` mobile block (`.now-row`, `.post`, `.res-card`, `.fav-card`, `.contact*`, `.card .lbl/.delta`, `.post-date`, `.channel-lbl`, top of block)

- [ ] **Step 1: Remove mobile-only indents on borderless blocks** — edit the existing lines' values (do not add duplicate rules):

```css
    .now-row{grid-template-columns:18px 84px 1fr;gap:8px;padding:11px 0;font-size:13px}
    .post{padding:22px 0;gap:8px}
    .res-card{padding:0}
    .fav-card{grid-template-columns:80px 1fr;padding:0;gap:12px}
    .contact{padding:28px 0}
    .contact .channels{gap:16px;justify-content:flex-start}
    .channel-icon{width:48px;height:48px}
```

- [ ] **Step 2: Raise 10px labels to 12px and tighten section rhythm** — change the existing lines to:

```css
    .card .lbl, .card .delta{font-size:12px}
    .post-date{font-size:12px}
    .channel-lbl{font-size:12px}
```

and add at the top of the mobile block:

```css
    [data-density="compact"]{--gap-section:28px}
    h2.sect{font-size:22px;flex-wrap:wrap}
```

- [ ] **Step 3: Verify**

Run: `node _source/mobile-check.js`
Expected: no `labels under 12px` line. Visually at 375px: five contact channels on one row (5×48 + 4×16 = 304px ≤ 335px); Currently rows and résumé entries share the h2 left edge.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "fix(mobile): align section padding, fit contact channels, 12px label floor"
```

---

### Task 5: Touch interactions — portrait flip, hover gating, popover dismiss

**Files:**
- Modify: `index.html:131–135` (portrait hover), `:262` (`.photo:hover`), `:328` (`.hero-portrait:hover::before`), `:428` (`.twk-x`), `:~1605` (popover JS), mobile block (`.photo:hover`)

- [ ] **Step 1: Tap-toggleable portrait** — replace lines 131, 132, 135 with:

```css
  .hero-portrait:hover .portrait-headshot, .hero-portrait.flip .portrait-headshot{opacity:0}
  .hero-portrait:hover .portrait-harp,     .hero-portrait.flip .portrait-harp{opacity:1}
  .hero-portrait:hover .portrait-cue,      .hero-portrait.flip .portrait-cue{opacity:0;transform:scale(0.85)}
```

Add before `</body>`:

```html
<script>
  (function(){
    var p = document.querySelector('.hero-portrait');
    if(!p) return;
    p.addEventListener('click', function(){ p.classList.toggle('flip'); });
  })();
</script>
```

- [ ] **Step 2: Gate hover-only effects** — wrap `.hero-portrait:hover::before{opacity:0.9}` and the desktop `.photo:hover{...}` rule in `@media (hover:hover){ ... }`. Delete the mobile-block line `.photo:hover{transform:scale(1.02) !important}`.

- [ ] **Step 3: Popover outside-tap dismiss** — after `closeBtn.addEventListener('click', hidePopover);` add:

```js
    document.addEventListener('click', function(e){
      if(popover.hidden || !popover.classList.contains('open')) return;
      if(popover.contains(e.target) || e.target.closest('#open-tweaks')) return;
      hidePopover();
    });
```

Change `#tweaks-popover .twk-x` to `width:32px;height:32px`.

- [ ] **Step 4: Verify** — DevTools device mode: tap portrait → harp; tap again → headshot. Open tweaks popover from colophon, tap background → closes. `node _source/mobile-check.js` → no regressions.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "fix(touch): tap-to-flip portrait, hover gating, popover outside-tap dismiss"
```

---

### Task 6: Asset hygiene — 404, favicon, lazy loading, avatar

**Files:**
- Modify: `index.html:12–13`, `:~619`, `:846–855`, `:959, 982–998`, `:1029`; `article.css:83–87`; `case-studies/disney.html` (intern-cohort img)

- [ ] **Step 1:** Delete line 1029 `<script src="image-slot.js"></script>` (file doesn't exist at root; 404 every load).
- [ ] **Step 2:** Delete lines 12–13 (JPEG `rel="icon"` / `apple-touch-icon` → 372KB `headshot.jpg`; PNG favicons on 7–9 already cover it).
- [ ] **Step 3:** In `.mobile-me` markup change `src="assets/headshot.jpg"` to `src="assets/favicon-192.png"`.
- [ ] **Step 4:** Add `loading="lazy" decoding="async"` to the four collage `<img>` tags and to `disney-intern-cohort.jpg` in `case-studies/disney.html`.
- [ ] **Step 5:** Remove `loading="lazy"` from small logo `<img>`s (`gmail/linkedin/spotify/youtube-logo.png`, `hoagie-club-logo.png`, `nytt-logo.png`, `princeton-logo.png`) — they paint late on first scroll.
- [ ] **Step 6:** In `article.css` `.figure img` add `height:auto;`.
- [ ] **Step 7: Verify** — `node _source/mobile-check.js` → no `404` lines. DevTools Network at 375px: `headshot.jpg` requested once (hero), not as favicon.
- [ ] **Step 8: Commit**

```bash
git add index.html article.css case-studies/disney.html
git commit -m "chore(assets): drop 404 script and JPEG favicon, lazy-load collage, eager small logos"
```

---

### Task 7: Article pages — tap targets and short-viewport landscape

**Files:**
- Modify: `article.css` (`.subindex a`, `.article-footer a`, `.topbar .crumb`, media queries at bottom)

- [ ] **Step 1: Tap targets**

```css
.subindex a{display:inline-block;padding:8px 0}
.article-footer a{display:inline-block;padding:8px 0}
.topbar .crumb{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:55%}
```

- [ ] **Step 2: Unify breakpoint and handle short landscape** — change `@media (max-width:640px)` to `@media (max-width:767px)` and append:

```css
/* Phone landscape: don't spend 1.5 screens on padding + hero before the title */
@media (max-height:500px){
  article{padding-top:28px}
  .hero-image{aspect-ratio:21/9;margin-bottom:20px}
  .topbar{padding:8px 20px}
}
```

- [ ] **Step 3: Verify** — `node _source/mobile-check.js` → PASS (header ≤64px landscape). DevTools 814×380 on an essay: h1 visible within ~1 screen of scroll.

- [ ] **Step 4: Commit**

```bash
git add article.css
git commit -m "fix(article): 44px tap targets, unify 767px breakpoint, short-viewport landscape"
```

---

### Task 8: Tablet block (768–1023, incl. Pro Max landscape)

**Files:**
- Modify: `index.html:451–455`

- [ ] **Step 1:** Extend the tablet block to:

```css
  @media (min-width: 768px) and (max-width: 1023px){
    [data-density="compact"]{--pad-main:56px}
    .hero h1{font-size:36px}
    .resume{grid-template-columns:1fr 1fr}
    .projects-compact.side-quests{grid-template-columns:1fr 1fr}
  }
```

- [ ] **Step 2: Verify** — `node _source/mobile-check.js` → PASS; at 814×380 hero headline ≤4 lines; résumé chips no longer wrap to three lines.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "fix(tablet): 2-col résumé and side quests, smaller hero headline"
```

---

### Task 9: Final sweep and deploy

- [ ] **Step 1:** `node _source/mobile-check.js` → `PASS`.
- [ ] **Step 2:** Re-run the audit screenshot scripts (`scratchpad\i14\audit.js`, `scratchpad\promax\audit.js`) and eyeball index at 390 and 430: one-row header, single-column sections except metrics 2×2 and collage 2×2, five contact icons on one row, no clipped text.
- [ ] **Step 3:** `git push origin main`; check https://chloelau.io on a real iPhone: no sideways drag, portrait flips on tap, anchor links land below the header.

## Deferred (not in this plan)
- `srcset` / 800px image variants (1600px hero JPEGs at ~370KB each) — needs an image-generation pass; do after layout fixes ship.
- Cariina hero infographic and Apps Script/Hoagie screenshots are illegible at 350px — needs a mobile crop or replacement asset (content decision).
- `viewport-fit=cover` + `env(safe-area-inset-*)` — only matters in PWA/fullscreen; skip.
