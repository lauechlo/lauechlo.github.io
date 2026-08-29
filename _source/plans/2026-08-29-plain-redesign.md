# Plain Homepage Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `index.html` as a single-column, prose-and-lists page in Newsreader (body) + Karla (metadata), removing every card/badge/metric/glow component while keeping the owner's personal features (Currently, magic mode, résumé logos, contact logos) unboxed, with all copy preserved verbatim.

**Architecture:** `index.html` stays a single self-contained file: `<head>` kept (fonts link swapped), the `<style>` block replaced wholesale by a ~170-line stylesheet, the `<main>` markup replaced section by section with copy transplanted from the tagged `v1-cards` version, and the inline JS pruned to the blocks that still have targets. `article.css` gets a typography-only swap. `_source/mobile-check.js` is updated first so it fails on the old page and passes on the new one.

**Tech Stack:** Static HTML/CSS/JS; Playwright WebKit gate (`node _source/mobile-check.js`, server on :8765); git tag `v1-cards` = the page before this work.

**Spec:** `_source/specs/2026-08-29-plain-redesign-design.md` (binding). Approved mockup: `.superpowers/brainstorm/772-1787977773/content/layout-v4.html`.

## Global Constraints

- **Copy is verbatim.** Every visible sentence in the new `index.html` must exist in `git show v1-cards:index.html`, copied not retyped. Sole exception: the H1 becomes "I came to Princeton for psychology and ended up running product." (the word "somehow" removed). Section headings keep their current wording.
- **No em dashes** (U+2014) in visible homepage copy or CSS `content:`. Use commas, periods, or "to" ("Sep '25 to now").
- **Fonts:** Newsreader (Google Fonts) for all text; Karla only for metadata (dates, roles, labels, captions, nav links, footer). No Fraunces anywhere after this plan. No uppercase transforms, no letter-spacing on labels.
- **No boxes:** no element on the homepage may have a border + background + radius "card" treatment. Hairline dividers (`1px solid var(--line)`) and image `border-radius` ≤ 6px are allowed. No hover lift/scale/shadow.
- **Kept features must keep working:** Currently list (with reading/spin rotation), magic mode (footer button, tweaks popover, keyboard eggs, curtains), résumé section with logos, contact channel logos.
- Do not rename `case-studies/ai-fluency-lab.html` or its assets. Do not touch sub-page copy.
- Work on branch `rewrite-plain`. Commit after each task. Local server: `python -m http.server 8765` from the site directory.
- Line numbers below refer to `git show v1-cards:index.html` (identical to the branch's current `index.html` at plan time). Verify with grep before editing; content, not line numbers, is authoritative.

---

### Task 1: Update the mobile-check gate for the new DOM

**Files:**
- Modify: `_source/mobile-check.js`

**Interfaces:**
- Produces: `node _source/mobile-check.js` → `PASS: all mobile checks green` only when the new page is in place; `FAIL` with named lines on the old page.

- [ ] **Step 1: Replace the per-page assertion block.** In the `page.evaluate` object and the checks below it, replace the old-DOM fields (`sideQuestCols`, `favCols`, `photoW`, `collageW`, `mobileMeShown`) with:

```js
        // inside page.evaluate(...) return {...}
        overflow: document.documentElement.scrollWidth - window.innerWidth,
        headerH: (q('.topbar') || q('.top')) ? (q('.topbar') || q('.top')).getBoundingClientRect().height : 0,
        workRows: document.querySelectorAll('a.work').length,
        nowRows: document.querySelectorAll('.now li').length,
        tinyText: [...document.querySelectorAll('body *')]
          .filter(e => e.childNodes.length && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()))
          .filter(e => getComputedStyle(e).display !== 'none' && parseFloat(getComputedStyle(e).fontSize) < 12).length,
        upperCase: [...document.querySelectorAll('body *')]
          .filter(e => getComputedStyle(e).display !== 'none' && getComputedStyle(e).textTransform === 'uppercase' && e.closest('#tweaks-popover') === null).length,
        boxes: [...document.querySelectorAll('main *')]
          .filter(e => { const s = getComputedStyle(e); return e.tagName !== 'IMG' && e.tagName !== 'IFRAME' && parseFloat(s.borderRadius) > 8 && s.borderStyle !== 'none' && s.borderWidth !== '0px'; }).length,
        fraunces: !![...document.styleSheets].find(ss => (ss.href||'').includes('Fraunces')) || !![...document.querySelectorAll('link')].find(l => (l.href||'').includes('Fraunces')),
        emDash: (document.querySelector('main')?.innerText || '').includes('—'),
```

and the checks:

```js
      if (m.overflow > 0) fail(`horizontal overflow ${m.overflow}px`);
      if (m.headerH > 64) fail(`header ${Math.round(m.headerH)}px tall`);
      if (path === '/index.html') {
        if (m.workRows !== 4) fail(`expected 4 a.work rows, found ${m.workRows}`);
        if (m.nowRows !== 4) fail(`expected 4 .now rows, found ${m.nowRows}`);
        if (m.upperCase > 0) fail(`${m.upperCase} uppercase-transformed elements`);
        if (m.boxes > 0) fail(`${m.boxes} card-like boxes (radius>8 with border) in main`);
        if (m.fraunces) fail(`Fraunces still loaded`);
        if (m.emDash) fail(`em dash in homepage copy`);
      }
      if (m.tinyText > 0) fail(`${m.tinyText} text elements under 12px`);
      errors.forEach(fail);
```

Keep the viewport list, the 404 collector, the global-playwright shim, the try/finally, and the PASS/FAIL printing exactly as they are.

- [ ] **Step 2: Run it on the OLD page and confirm it fails for the right reasons.**

Run: `node _source/mobile-check.js`
Expected: `FAIL` with lines including `expected 4 a.work rows, found 0`, `uppercase-transformed elements`, `card-like boxes`, `Fraunces still loaded`. No stack trace.

- [ ] **Step 3: Commit**

```bash
git add -f _source/mobile-check.js
git commit -m "test: retarget mobile gate at the plain homepage DOM"
```

---

### Task 2: New stylesheet in `index.html`

**Files:**
- Modify: `index.html` lines 1–~600 (`<head>` and the `<style id="theme">` block)

**Interfaces:**
- Produces the class vocabulary used by Task 3: `.top`, `.intro`, `.lede`, `.headshot`, `.now`, `h2.sect`, `a.work`, `.meta`, `.list`, `.photos`, `.cap`, `.katz`, `.resume`, `.res-col`, `.channels`, `.foot`, `.arr`, `.toast`, `#tweaks-popover` (kept).

- [ ] **Step 1: Replace the Google Fonts link** (line ~23) with:

```html
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Karla:wght@400;500&display=swap" rel="stylesheet" />
```

- [ ] **Step 2: Delete the entire existing `<style id="theme">…</style>` block** (from line 24 to the closing `</style>` before `<body`, ~line 600) **except** keep the `:root{…}` colour tokens (lines 25–45, `--bone` through `--slate-dim`) and the `@keyframes`/rules that magic mode still needs (see Step 4). Then insert this stylesheet after the `:root` tokens:

```css
  html{background:var(--bone)}
  body{margin:0;background:var(--bone);color:var(--ink);font-family:'Newsreader',Georgia,serif;font-optical-sizing:auto;font-size:17px;line-height:1.5;-webkit-font-smoothing:antialiased}
  a{color:var(--forest);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}
  a:hover{color:var(--slate)}
  img{max-width:100%;display:block}
  p{margin:0 0 12px}
  .meta,.k,.cap,.foot,.top nav,.list .d,.res-col .lbl,.what,.channel-lbl{font-family:'Karla',ui-sans-serif,system-ui,sans-serif;font-size:12.5px;line-height:1.4;color:var(--muted)}
  main{max-width:640px;margin:0 auto;padding:36px 24px 64px}

  /* Top bar */
  .top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:34px}
  .top .brand{font-weight:500;font-size:17px;color:var(--ink);text-decoration:none}
  .top nav a{color:var(--muted);text-decoration:none;margin-left:16px}
  .top nav a:hover{color:var(--ink)}

  /* Intro */
  .intro{display:grid;grid-template-columns:1fr 150px;gap:26px;align-items:start}
  .lede{font-size:22px;line-height:1.3;margin-bottom:12px}
  .headshot{aspect-ratio:1;border-radius:6px;overflow:hidden;background:var(--bone-2)}
  .headshot img{width:100%;height:100%;object-fit:cover;object-position:50% 32%}

  /* Section headings */
  h2.sect{font-size:17px;font-weight:600;letter-spacing:0;margin:38px 0 10px}
  h2.sect .cta{font-family:'Karla',ui-sans-serif,system-ui,sans-serif;font-size:12.5px;font-weight:400;color:var(--muted);float:right;text-decoration:none;margin-top:4px}
  h2.sect .cta:hover{color:var(--ink)}

  /* Currently */
  .now{list-style:none;margin:0;padding:0}
  .now h2.sect{margin-top:8px}
  .now li{display:grid;grid-template-columns:20px 96px 1fr;gap:10px;padding:7px 0;border-top:1px solid var(--line);align-items:baseline}
  .now li:last-child{border-bottom:1px solid var(--line)}
  .now li::before{content:attr(data-icon);color:var(--forest)}
  .now .k{padding-top:2px}

  /* Work rows */
  a.work{display:grid;grid-template-columns:96px 1fr;gap:16px;margin:0 0 18px;color:var(--ink);text-decoration:none;align-items:start}
  a.work .thumb{aspect-ratio:16/10;overflow:hidden;background:var(--bone-2)}
  a.work .thumb img{width:100%;height:100%;object-fit:cover}
  a.work .meta{margin:0 0 2px}
  a.work b{font-weight:500}
  a.work p{margin:0}
  .arr{color:var(--forest);margin-left:6px;display:inline-block;transition:transform .15s ease}
  a.work:hover .arr,.list a:hover .arr{transform:translateX(4px)}

  /* Dated lists (side quests, notebook) */
  .list{list-style:none;margin:0;padding:0}
  .list li{display:grid;grid-template-columns:82px 1fr;gap:12px;padding:7px 0;border-top:1px solid var(--line)}
  .list li:last-child{border-bottom:1px solid var(--line)}
  .list .d{padding-top:4px}
  .list li>a{color:var(--ink);text-decoration:none}
  .list li>a b{font-weight:500}
  .list li>a.title{color:var(--forest);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:3px}

  /* About */
  .photos{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0 4px}
  .photos img{aspect-ratio:4/3;object-fit:cover;width:100%}
  .cap{margin:0 0 14px}
  .katz{display:block;border:0;border-radius:6px;width:100%;margin:8px 0 14px}

  /* Résumé */
  .resume{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
  .res-col .lbl{margin:0 0 4px}
  .res-col ul{list-style:none;margin:0;padding:0}
  .res-col li{display:grid;grid-template-columns:24px 1fr;gap:10px;padding:7px 0;border-top:1px solid var(--line);align-items:start}
  .res-col li:last-child{border-bottom:1px solid var(--line)}
  .res-col img{width:24px;height:24px;object-fit:contain;filter:grayscale(1) contrast(1.1);opacity:.85}
  .res-col .who{display:block;font-size:15px;line-height:1.3}
  .res-col .who a{color:var(--ink)}
  .res-col .what{display:block}

  /* Contact */
  .channels{display:flex;flex-wrap:wrap;gap:22px;margin:14px 0 0}
  .channel{display:flex;flex-direction:column;align-items:center;gap:6px;text-decoration:none;width:48px}
  .channel img{width:28px;height:28px;object-fit:contain}
  .channel:hover .channel-lbl{color:var(--ink)}

  /* Footer */
  .foot{display:flex;justify-content:space-between;margin-top:40px;padding-top:12px;border-top:1px solid var(--line)}
  .foot button{appearance:none;background:none;border:0;padding:0;font:inherit;color:var(--muted);cursor:pointer}
  .foot button:hover{color:var(--ink)}

  /* Toast (used by magic mode) */
  .toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%) translateY(8px);background:var(--ink);color:var(--bone);padding:8px 14px;border-radius:8px;font-family:'Karla',sans-serif;font-size:13px;opacity:0;pointer-events:none;transition:opacity .2s,transform .2s;z-index:300}
  .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}

  /* Phones */
  @media (max-width:767px){
    main{padding:24px 20px 56px}
    .top{margin-bottom:26px}
    .top nav a{margin-left:12px}
    .intro{grid-template-columns:1fr;gap:16px}
    .headshot{width:120px;order:-1}
    .lede{font-size:20px}
    a.work{grid-template-columns:72px 1fr;gap:12px}
    .list li{grid-template-columns:64px 1fr}
    .now li{grid-template-columns:18px 84px 1fr}
    .resume{grid-template-columns:1fr;gap:18px}
    .channels{gap:16px}
  }
  @media (hover:none){ .arr{transition:none} }
```

- [ ] **Step 3: Keep the tweaks-popover CSS** (`#tweaks-popover…`, `.twk-*`, the `.switch` styles, lines ~420–447 of the old block) verbatim, appended after the stylesheet above.

- [ ] **Step 4: Magic-mode CSS triage.** From the old `body[data-magic="on"]…` block (lines ~342–419) and its `@keyframes`, KEEP rules whose selectors still exist after Task 3: `body[data-magic="on"]::before` (aurora), `.magic-trail`/particle classes, `.curtain`/lantern/harp-ripple/bewitched overlays, `.toast`, anything on `h2.sect`. DELETE rules targeting removed selectors: `.card`, `.metrics-row`, `.project`, `.project-compact`, `.collage`, `.photo`, `.hero::before`, `.hero-portrait`, `.fav-card`, `.res-card`, `.channel-icon`, `.now-card`, `.topnav*`. List every deleted and kept selector in your report.

- [ ] **Step 5: Delete** the `[data-density]`, `[data-personality]`, `[data-font]`, `[data-hero]` rules and the paper-grain overlay; remove the corresponding `data-*` attributes from `<html>`/`<body>` (keep `data-magic="off"` on `<body>`).

- [ ] **Step 6: Verify the page still parses** — open http://localhost:8765/ and confirm no console errors from CSS; markup is still old at this point, so it will look broken. `node _source/mobile-check.js` is expected to still FAIL (rows missing). Commit:

```bash
git add index.html
git commit -m "style: replace homepage stylesheet with plain single-column system (Newsreader + Karla)"
```

---

### Task 3: New `<main>` markup

**Files:**
- Modify: `index.html` from `<body` to `</main>` (old lines ~606–1023)

**Interfaces:**
- Consumes the classes from Task 2. Element ids the kept JS needs: `#reading-rotation`, `#today-spin`, `#open-tweaks`, `#toast`, `#tweaks-popover` (popover markup at old lines 1025–1040 is kept verbatim).

- [ ] **Step 1: Replace everything from `<body` through `</main>` with the skeleton below.** Where a line says COPY, paste the exact text from `git show v1-cards:index.html` at the cited lines (`git show v1-cards:index.html | sed -n 'A,Bp'`). Never retype copy.

```html
<body data-magic="off">
<main id="top">
  <div class="top">
    <a class="brand" href="#top">Chloe Lau</a>
    <nav><a href="#writing">Writing</a><a href="RESUME_URL" target="_blank" rel="noopener">Résumé ↗</a><a href="mailto:chloelau@princeton.edu">Email</a></nav>
  </div>
  <!-- RESUME_URL = the docs.google.com href used at old line 619 -->

  <!-- INTRO -->
  <section class="intro">
    <div>
      <p class="lede">I came to Princeton for psychology and ended up running product.</p>
      <p><!-- COPY old line 638 (.sub) text --></p>
      <p><!-- COPY old line 639 (.hero-recruit) text, no italics --></p>
    </div>
    <div class="headshot"><img src="assets/headshot.jpg" alt="Chloe Lau" width="150" height="150" /></div>
  </section>

  <!-- CURRENTLY -->
  <section class="now-wrap" id="currently">
    <h2 class="sect">Currently</h2>
    <ul class="now">
      <li data-icon="✦"><span class="k">Building</span><span class="v"><!-- COPY old line 679 --></span></li>
      <li data-icon="※" class="researching"><span class="k">Researching</span><span class="v"><!-- COPY old line 683, keep the <a> --></span></li>
      <li data-icon="❀"><span class="k">Reading</span><span class="v" id="reading-rotation"><!-- COPY old line 687 --></span></li>
      <li data-icon="♪"><span class="k">Listening</span><span class="v" id="today-spin"><!-- COPY old line 691 --></span></li>
    </ul>
  </section>

  <!-- PROJECTS -->
  <h2 class="sect" id="projects">Selected work</h2>
  <!-- One a.work per old card i–iv (old lines 698–781), in the same order. For each: -->
  <a class="work" href="case-studies/disney.html">
    <div class="thumb"><img src="ASSET" alt="" loading="lazy" decoding="async" /></div>
    <div>
      <p class="meta">PM Intern, Disney+ Search, Summer '26</p>   <!-- old .role text with " · " → ", " and "→" → "to" -->
      <p><b><!-- COPY old h3 text --></b> <!-- COPY first sentence of old .blurb --><span class="arr">→</span></p>
    </div>
  </a>
  <!-- ASSET = the src of the card's .preview img at v1-cards. Hrefs: disney.html, hoagie.html, cariina.html, ai-fluency-lab.html -->

  <!-- SIDE QUESTS -->
  <h2 class="sect">Side quests</h2>
  <ul class="list">
    <!-- old v–vii (lines 785–810), each: -->
    <li><span class="d">YEAR</span><a href="REPO_URL" target="_blank" rel="noopener"><b><!-- COPY title --></b> <!-- COPY blurb --><span class="arr">→</span></a></li>
    <!-- YEAR: Unwrapped 2025, Spotify MCP 2025, Music sequencing 2026 (order: Unwrapped, Spotify MCP, Music sequencing as today). REPO_URL from each old .repo-link href. -->
  </ul>

  <!-- WRITING -->
  <h2 class="sect" id="writing">From the notebook</h2>
  <ul class="list">
    <!-- old posts 01–03 (lines 815–840), each: -->
    <li><span class="d">MON YYYY</span><a class="title" href="ESSAY_HREF"><!-- COPY h3 text --></a></li>
    <!-- dates from old .post-date, e.g. "Dec 2025"; hrefs from old post links -->
  </ul>

  <!-- ABOUT -->
  <h2 class="sect" id="about">A few things about me</h2>
  <p><!-- COPY old .about-lead text (line ~847) --></p>
  <p><!-- COPY the hobbies sentence "Outside of work I play the harp…" (old line ~850) --></p>
  <div class="photos">
    <img src="assets/harp-orchestra.jpg" alt="Playing harp with the orchestra" loading="lazy" decoding="async" />
    <img src="assets/rainier-hike.jpg" alt="Hiking near Mount Rainier" loading="lazy" decoding="async" />
  </div>
  <p class="cap">Harp with the orchestra. Rainier.</p>
  <p><!-- COPY the Katzenjammers sentence(s) from old .katz-lead (line ~872) --></p>
  <!-- COPY the old <iframe class="katz-iframe" …> (lines ~874–879) but with class="katz" -->

  <!-- RESUME -->
  <h2 class="sect" id="resume">Résumé at a glance <a class="cta" href="RESUME_URL" target="_blank" rel="noopener">Full résumé ↗</a></h2>
  <div class="resume">
    <!-- For each old .res-card (Education / Work / Leadership, lines 907–985): -->
    <div class="res-col">
      <p class="lbl">Education</p>
      <ul>
        <!-- COPY each old <li> verbatim, then: remove the <span class="res-chip"> wrapper (keep the <img>), remove <span class="res-entry"> wrapper (keep .who and .what spans), and in .what replace " → " with " to " -->
      </ul>
    </div>
  </div>

  <!-- CONTACT -->
  <h2 class="sect" id="contact">Let's build something.</h2>
  <p><!-- COPY old .lead (line 990) --></p>
  <div class="channels">
    <!-- COPY the five old <a class="channel"> blocks (lines 992–1011) verbatim, then remove the <span class="channel-icon"> wrapper around each <img>, and delete loading="lazy" if present -->
  </div>

  <div class="foot">
    <span>© Chloe Lau</span>
    <button id="open-tweaks" type="button" title="Toggle magic mode">click for magic ✨</button>
  </div>
</main>
```

- [ ] **Step 2: Keep** `<div class="toast" id="toast"></div>` and the whole `<div id="tweaks-popover" hidden>…</div>` block (old lines 1025–1040) after `</main>`, unchanged.

- [ ] **Step 3: Copy-fidelity check.** For each of these 10 strings, `grep -c` must return ≥1 in both the new file and `git show v1-cards:index.html`: "Right now that means Hoagie", "Recruiting for full-time PM", "Users couldn't find what they loved", "From one product to six", "Dashboards for districts that had stopped logging in", "Teaching AI to students outside computer science", "I built a coherence metric", "I grew up between classical music and code", "oldest co-ed a cappella group", "Email is best". Then `grep -c "—" index.html` must be 0 outside `<script>`.

- [ ] **Step 4: Run the gate.** `node _source/mobile-check.js` → expect PASS except possibly JS-related 404/console lines. View a full-page WebKit screenshot at 390 and 1280 and compare to `layout-v4.html`: same section order, image-left work rows, no boxes.

- [ ] **Step 5: Commit**

```bash
git add index.html
git commit -m "feat: rebuild homepage as single-column prose and lists with copy transplanted from v1-cards"
```

---

### Task 4: Prune the inline JavaScript

**Files:**
- Modify: `index.html` `<script>` blocks (old lines 1041–1640)

- [ ] **Step 1: Delete these blocks entirely** (identify by the `// ────────── NAME ──────────` banners / function names): HOME SCROLL MEMORY (`restoreScroll`, ~1067–1100), the scroll-spy `window.addEventListener('scroll', …)` (~1103–1116), FAV-CARD TYPEOUT (~1198–1216), `countUp` and its IntersectionObserver (~1226–1262), the collage parallax `mousemove` handler (~1295–1310), the `.project`/`.project-compact` click/keydown handlers (~1273–1290, rows are now real links), the third `<script>` (portrait flip, ~1630–1640) and the `document.body.onclick` shim inside it.

- [ ] **Step 2: Keep and null-guard**: `showToast`, `sparkle`, READING ROTATION, TODAY'S SPIN, MAGIC LAYER (`glyphSetForElement`, `burst`, `spawnParticle`, trail), all keyboard eggs (`harpRipple`, `bewitchedEgg`, `tangledEgg`, `lanternEgg`, `pluck500`, `goKonami`), TWEAKS PANEL OPENER, MAGIC MODE POPOVER (incl. the outside-click dismiss). Wherever kept code queries a removed element (`.card .val`, `.project`, `.collage`, `.hero-portrait`, `.fav-card`, `.post`, `#post-500`), either delete that branch or guard with `if(!el) return;` so nothing throws. `pluck500` was bound to the 500ms post's `mouseenter`; rebind it to the notebook link whose href contains `500ms-sound`.

- [ ] **Step 3: Verify.** Load http://localhost:8765/ in Playwright WebKit (desktop 1280 and iPhone 13) and assert: zero `pageerror`/console errors; `#reading-rotation` and `#today-spin` non-empty; clicking `#open-tweaks` opens `#tweaks-popover` (`.open`); toggling the magic switch sets `body[data-magic="on"]` and the aurora `::before` is visible; tapping outside closes the popover; typing "harp" fires the harp ripple without error. `node _source/mobile-check.js` → PASS.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "refactor: prune homepage JS to toast, rotation, magic mode, eggs and popover"
```

---

### Task 5: `article.css` typography swap

**Files:**
- Modify: `article.css` (tokens ~lines 20–24; `.topbar .home`, `.crumb`, `article h1/h2/p/li`, `.kicker`, `.subindex b`, `.my-role`, `figcaption`); the Google Fonts `<link>` in all 7 sub-pages.

- [ ] **Step 1:** In each of `case-studies/*.html` and `essays/*.html`, replace the Fraunces/Karla fonts `<link>` with the Newsreader/Karla link from Task 2 Step 1. No other change to sub-page HTML.
- [ ] **Step 2:** In `article.css` set `--font-heading:'Newsreader',Georgia,serif; --font-body:'Newsreader',Georgia,serif; --font-meta:'Karla',ui-sans-serif,system-ui,sans-serif;`. Body/`article p`/`li`: 17px/1.65. Headings keep their sizes. Set `.topbar .crumb`, `.kicker`, `.subindex b`, `.subindex`, `.my-role`, `.figure figcaption`, `.article-footer` to `font-family:var(--font-meta)`; remove every `text-transform:uppercase` and `letter-spacing` from those rules; `.crumb` and `.kicker` in normal case, 12.5px, `var(--muted)`.
- [ ] **Step 3:** Verify: `node _source/mobile-check.js` → PASS (no uppercase check applies to sub-pages, but tiny-text and Fraunces do not regress); WebKit screenshot of `/essays/working-with-ai.html` at 1280 shows Newsreader body and no uppercase crumb; network log has no `Fraunces` request.
- [ ] **Step 4: Commit**

```bash
git add article.css case-studies essays
git commit -m "style(article): Newsreader body and headings, Karla metadata, no uppercase labels"
```

---

### Task 6: CLAUDE.md, final sweep

**Files:**
- Modify: `CLAUDE.md` ("What this is", design system, "Navigating index.html", writing rules if they mention Fraunces/kickers)

- [ ] **Step 1:** Rewrite the design-system section: fonts (Newsreader body/headings, Karla metadata at 12.5px normal case), single 640px column, hairline dividers only, no cards/badges/uppercase/em dashes, what was removed and why (link the spec), `v1-cards` tag for the old page, and the new section landmarks (`<!-- INTRO -->` … `<!-- CONTACT -->`). Keep the sub-page notes and the `ai-fluency-lab` filename warning.
- [ ] **Step 2:** Full sweep: `node _source/mobile-check.js` → PASS; WebKit full-page screenshots at 390 and 1280 of `/index.html` and one case study; confirm against `layout-v4.html`; confirm magic mode toggles; confirm zero console errors on all 8 pages.
- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: describe the plain homepage design system and v1-cards tag"
```

Then hand off via superpowers:finishing-a-development-branch (merge to `main` is the owner's call; the old page remains at tag `v1-cards`).
