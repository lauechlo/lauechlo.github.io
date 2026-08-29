# chloelau.me homepage redesign: "a well-written page"

Date: 2026-08-29. Branch: `rewrite-plain` (from `main` @ 9af5f64; the pre-redesign page is tagged `v1-cards`).
Approved mockup: `.superpowers/brainstorm/772-1787977773/content/layout-v4.html` (direction A, v4).

## Why

Four research passes (human-feeling personal sites, typography tells, vibe-coded layout catalogue, audit of this site) agreed: the current homepage reads as AI-generated because of its *structure* more than any one font. It uses ~18 visual components (metric cards with count-up, Currently widget, roman-numeral cards with three metrics each, uppercase tracked kickers, italic accent word in the H1, blurred glow, rotated collage, favourites cards, icon-button contact row, magic mode, "Built with charm and Claude"). The content needs about five. Fraunces was also named in a public "slop fonts" list; the italic-accent-word and uppercase-kicker devices are the two most consistently documented tells.

The owner's constraint: personal but still credible to a recruiter in the first screen; existing copy preserved; no em dashes.

## What the page becomes

One column, ~640px measure, bone background and forest-green links as today. Prose plus dated lists. Sections and their exact contents, top to bottom:

1. **Top bar** (not sticky). Left: "Chloe Lau". Right, in Karla 12px: Writing · Résumé ↗ · Email. No CTA pill, no scroll-spy, no mobile strip.
2. **Intro.** Two-column at ≥768px: text left, current headshot right (same crop, ~150px, `border-radius:6px`, no hover swap, no cue, no glow). Text, verbatim from the live site except one proposed edit:
   - Lede (22px): "I came to Princeton for psychology and ended up running product." **[proposed edit: remove "somehow"; owner may veto → keep the original sentence]**
   - "Right now that means Hoagie, a lab I started for non-CS students, and this past summer on Disney+ Search."
   - "Recruiting for full-time PM and Applied AI roles, starting 2027." (roman, not italic)
3. **Selected work.** Four rows. Each row is one `<a>` to the case study: 96px-wide screenshot (existing project image, 16:10, `object-fit:cover`, no border/shadow/radius) left; right: a Karla 12.5px meta line (role, company, dates, plain case, commas, "to now" instead of arrows), then the existing card headline in weight 500 followed by the card's first sentence, ending in a green →. Order and copy exactly as the current cards i–iv. No metrics.
4. **Side quests.** Three rows in a dated list (year left in Karla, text right): existing title + existing blurb + →, whole row links to the GitHub repo. No roman numerals, no GitHub icon.
5. **From the notebook.** Three rows: date left, essay title right (linked). Existing titles and dates. No "№", no blurbs.
6. **A few things about me.** The existing About lead + the existing hobby sentence as one or two paragraphs (copy unchanged, order may be adjusted). Then two photos side by side, unrotated, 4:3, `harp-orchestra.jpg` and `rainier-hike.jpg`, with a one-line Karla caption. Then the existing Katzenjammers sentence with the existing Spotify embed below it, plain (no card). The "comfort watch / comfort song" pair is **dropped** from the homepage (content stays in git; can return later as a single sentence).
7. **Let's build something.** Existing heading and email sentence; then one sentence listing LinkedIn, GitHub, Spotify, YouTube as text links. No icon row.
8. **Footer.** "© Chloe Lau" left, "Full résumé ↗" right, Karla 12.5px, hairline top border. No colophon line, no magic toggle.

**Removed entirely** (markup, CSS, and JS): metrics row and count-up, Currently card and daily-rotation JS, hero glow and portrait aurora, portrait hover swap and ⟳ cue, `.mobile-me`, kickers, roman numerals, "Résumé at a glance" chips section (résumé link covers it), photo collage and parallax, favourites cards, contact icon channels, scroll-spy, toast, tweaks popover and magic mode (CSS, curtains, particles, keyboard eggs), "Built with charm and Claude", "click for magic", the `[data-hero]`/`[data-density]`/`[data-font]` variant system, `image-slot` CSS. The `v1-cards` tag preserves all of it.

## Typography

- Body: **Newsreader** (Google Fonts, variable, opsz axis; load wght 400/500/600 + italic 400), 17px / 1.5, colour `--ink`. `font-optical-sizing:auto`.
- Lede: Newsreader 22px / 1.3, weight 400. Section headings: Newsreader 17px, weight 600, roman, normal case, `letter-spacing:0`. No italic accent words anywhere on the homepage.
- Metadata (dates, roles, captions, top-bar links, footer): **Karla** 12.5px, weight 400/500, `--muted` colour, **normal case, no letter-spacing**. Karla is kept only for this role.
- Links: green `--forest`, 1px underline, `text-underline-offset:3px`. Row-links (work, side quests) are not underlined; the → is the affordance. Hover: → shifts 4px right; nothing lifts, scales, or shadows.
- Drop the Fraunces `<link>` from `index.html`. **Sub-pages** (`article.css`): swap Fraunces → Newsreader for `h1`/`h2`/`.home`, keep Karla for `.crumb` and metadata; remove uppercase/tracking from `.crumb`, `.kicker`, `.subindex b`. Article body text also becomes Newsreader 17px/1.65, so the whole site reads in one voice. `.my-role`, `.figure figcaption` in Karla 12.5px.
- Punctuation rule: no em dashes (—) in any homepage copy or new CSS-generated content. Existing sub-page copy is not edited in this project.

## Layout and responsive

- `main{max-width:640px;margin:0 auto;padding:40px 24px 64px}`. No `[data-density]` tokens.
- Intro grid `1fr 150px`, gap 26px; at ≤767px it becomes one column with the headshot 120px, left-aligned, above the text. Work rows keep image-left at all widths (96px → 72px on phones). Side-quest/notebook rows: `82px 1fr` → `64px 1fr` on phones.
- Photos pair: `1fr 1fr` at all widths.
- Reuse `_source/mobile-check.js` as the regression gate, with assertions updated to the new DOM: no horizontal overflow at 375/390/430/landscape, top bar ≤64px, no text under 12px, no 404s, the four `.work` rows present, no element with `border-radius` > 8px except images. Remove assertions for selectors that no longer exist.

## Copy handling

- Every sentence on the new homepage is one that exists on the live site today, except the single proposed edit above. The implementer copies text from `index.html` @ `v1-cards`, never retypes it.
- Sub-page copy is untouched.
- Section headings keep their current wording.

## Files

- `index.html`: rewritten (new CSS block, new markup, ~1/5 the size). Keep `<head>` meta, favicons, preconnects; replace the Google Fonts link.
- `article.css`: typography swap only (see above); layout rules stay.
- `assets/`: no new files. Project thumbnails reuse the existing four project screenshots.
- `_source/mobile-check.js`: assertions updated.
- `CLAUDE.md`: update the design-system and "Navigating index.html" sections to describe the new page (fonts, sections, what was removed and why, `v1-cards` tag).

## Out of scope

Sub-page layout changes, `srcset` image variants, `CNAME` change to chloelau.me, copy rewrites beyond the one proposed edit.

## Acceptance

1. `node _source/mobile-check.js` passes on the new page.
2. Visual check at 1280 and 390 matches `layout-v4.html`: five section headings, four image-left work rows, no cards, no uppercase labels, no arrows except the row →, Newsreader body, Karla meta.
3. `grep -c "—" index.html` is 0 in visible copy.
4. `git diff v1-cards -- index.html` shows every visible sentence in the new file exists in the old (spot-check 10 sentences).
5. Desktop and sub-pages render with Newsreader; no request for Fraunces in the network log.
