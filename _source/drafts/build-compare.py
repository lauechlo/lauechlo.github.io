#!/usr/bin/env python3
"""Build the two comparison pages from the real homepage.

Run from the site root:  python _source/drafts/build-compare.py

Writes, next to this file (unpublished: _-prefixed dirs are skipped by Pages):
  ground-compare.html   the homepage under three grounds, plus a band and a deep close
  hover-compare.html    the homepage with the hover-preview variants switchable
  now/*.jpg|png, thumbs/*, logos-mono/*.png   small preview assets the pages use

Everything is derived from index.html at build time, so the copy is always current.
"""
import re
import pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / '_source' / 'drafts'
SRC = (ROOT / 'index.html').read_text(encoding='utf-8')


# ---------- shared helpers ----------

def relink(html):
    """Point the homepage's relative links at the site root from _source/drafts/."""
    return (html.replace('"assets/', '"../../assets/')
                .replace('"case-studies/', '"../../case-studies/')
                .replace('"essays/', '"../../essays/'))


def set_title(html, title):
    return re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html, count=1)


def inject(html, css, bar, script):
    html = html.replace('</style>', css + '\n</style>', 1)
    html = html.replace('<main id="top">', bar + '\n<main id="top">', 1)
    html = html.replace('</body>', script + '\n</body>', 1)
    return html


def resize(src, dst, width):
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    if im.mode in ('P', 'LA'):
        im = im.convert('RGBA')
    w, h = im.size
    im = im.resize((width, round(h * width / w)), Image.LANCZOS)
    if dst.suffix.lower() in ('.jpg', '.jpeg'):
        im.convert('RGB').save(dst, quality=82, optimize=True)
    else:
        im.save(dst, optimize=True)


BAR_CSS = """
  /* comparison chrome */
  .bar{position:sticky;top:0;z-index:5;background:var(--bone-2);padding:10px 24px;font-family:var(--font-meta);font-size:13px;display:flex;gap:6px 22px;flex-wrap:wrap;align-items:center}
  .bar .g{display:inline-flex;gap:10px;align-items:center}
  .bar .g b{font-weight:500;margin-right:2px}
  .bar label{display:inline-flex;gap:5px;align-items:center;cursor:pointer;white-space:nowrap}
  .bar .which{margin-left:auto;color:var(--muted)}
  html[data-embed] .bar{display:none}
  html[data-rm] *{transition:none !important}
"""


# ---------- ground-compare ----------

GROUND_CSS = BAR_CSS + """
  html[data-ground="sage"]{--bone:#E9F0EC;--bone-2:#D5E3DB}
  html[data-ground="mist"]{--bone:#E4E9ED;--bone-2:#D2DBE2}

  /* one band behind Currently */
  html[data-band] #currently{position:relative;isolation:isolate;padding:12px 0 10px;margin:24px 0 6px}
  html[data-band] #currently::before{content:"";position:absolute;z-index:-1;top:0;bottom:0;left:calc(50% - 50vw);width:100vw;background:#E6ECE7;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
  html[data-band] #currently h2.sect{margin-top:0}

  /* deep close: contact and the copyright line live in a footer after main */
  main{padding-bottom:0}
  .close .col{max-width:640px;margin:0 auto;padding:0 24px 64px}
  .close .channel img.mono{display:none}
  html[data-deep] .close{background:#172E22;color:#D3E0D8;margin-top:48px}
  html[data-deep] .close .col{padding:36px 24px 28px}
  html[data-deep] .close h2.sect{margin:0 0 10px;color:#D3E0D8}
  html[data-deep] .close .channel img{display:none}
  html[data-deep] .close .channel img.mono{display:block;opacity:.85}
  html[data-deep] .close .channel:hover img.mono{opacity:1}
  html[data-deep] .close .channel-lbl{color:#AFBFB6}
  html[data-deep] .close .channel:hover .channel-lbl{color:var(--bone)}
  html[data-deep] .close .foot{margin-top:36px;border-top:1px solid rgba(238,241,244,.14);color:#AFBFB6}
  @media (max-width:767px){html[data-deep] .close .col{padding:28px 20px 24px}}

  .cariina-note{display:none;font-family:var(--font-meta);font-size:13px;color:var(--muted);margin:-10px 0 18px 112px}
  html:not([data-ground="haze"]) .cariina-note{display:block}

  /* split view: current ground on the left, the selection on the right; each pane is a desktop-width page scaled to fit */
  .split{display:none}
  html[data-split] main,html[data-split] .close{display:none}
  html[data-split] .split{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px;height:calc(100vh - 62px);box-sizing:border-box}
  .split .cell{overflow:hidden;position:relative}
  .split iframe{position:absolute;top:0;left:0;width:1000px;border:0;transform-origin:0 0}
"""

GROUND_BAR = """<div class="bar">
  <span class="g"><b>Ground</b>
    <label><input type="radio" name="ground" value="haze" checked /> 1 haze, current</label>
    <label><input type="radio" name="ground" value="sage" /> 2 sage paper #E9F0EC</label>
    <label><input type="radio" name="ground" value="mist" /> 3 deeper mist #E4E9ED</label></span>
  <span class="g"><label><input type="checkbox" id="band" /> b band behind Currently</label></span>
  <span class="g"><label><input type="checkbox" id="deep" /> d deep close</label></span>
  <span class="g"><label><input type="checkbox" id="split" /> s split, current beside the pick</label></span>
  <span class="which">keys 1 2 3, b, d, s</span>
</div>
<div class="split"><div class="cell"><iframe id="L" title="current"></iframe></div><div class="cell"><iframe id="R" title="pick"></iframe></div></div>"""

GROUND_JS = """<script>
(function(){
  const root=document.documentElement, q=new URLSearchParams(location.search);
  const cb=id=>document.getElementById(id);
  const radios=[...document.querySelectorAll('input[name="ground"]')];
  if(q.has('embed')) root.dataset.embed='';
  const g=q.get('ground'); if(g) radios.forEach(r=>r.checked=(r.value===g));
  cb('band').checked=q.has('band'); cb('deep').checked=q.has('deep');
  function apply(){
    root.dataset.ground=radios.find(r=>r.checked).value;
    root.toggleAttribute('data-band',cb('band').checked);
    root.toggleAttribute('data-deep',cb('deep').checked);
    root.toggleAttribute('data-split',cb('split').checked);
    if(cb('split').checked){
      const base=location.pathname;
      const pick='?ground='+root.dataset.ground+(cb('band').checked?'&band':'')+(cb('deep').checked?'&deep':'')+'&embed';
      if(cb('L').getAttribute('src')!==base+'?ground=haze&embed') cb('L').src=base+'?ground=haze&embed';
      if(cb('R').getAttribute('src')!==base+pick) cb('R').src=base+pick;
      fit();
    }
  }
  function fit(){
    document.querySelectorAll('.split .cell').forEach(cell=>{
      const f=cell.querySelector('iframe'), s=cell.clientWidth/1000;
      f.style.transform='scale('+s+')'; f.style.height=(cell.clientHeight/s)+'px';
    });
  }
  window.addEventListener('resize',fit);
  radios.forEach(r=>r.addEventListener('change',apply));
  ['band','deep','split'].forEach(id=>cb(id).addEventListener('change',apply));
  document.addEventListener('keydown',e=>{
    if(e.target.tagName==='INPUT') return;
    const k={'1':'haze','2':'sage','3':'mist'}[e.key];
    if(k){ radios.forEach(r=>r.checked=(r.value===k)); apply(); }
    const t={b:'band',d:'deep',s:'split'}[e.key];
    if(t){ cb(t).checked=!cb(t).checked; apply(); }
  });
  apply();
})();
</script>"""


def mono_logo(name, rule):
    """A white silhouette of a contact logo for the dark close.
    rule: which pixel classes are the figure (kept, painted white) vs counters (cut out)."""
    src = ROOT / 'assets' / 'logos' / f'{name}-logo.png'
    dst = OUT / 'logos-mono' / f'{name}.png'
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert('RGBA')
    px = im.load()
    w, h = im.size
    out = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            keep = 1.0
            if rule == 'cut-white':       # LinkedIn, YouTube: white letters and triangle become holes
                keep = 1.0 - max(0.0, min(1.0, (min(r, g, b) - 190) / 50))
            elif rule == 'cut-black':     # Spotify: black waves become holes
                keep = max(0.0, min(1.0, (max(r, g, b) - 40) / 80))
            op[x, y] = (255, 255, 255, round(a * keep))
    out = out.resize((128, round(h * 128 / w)), Image.LANCZOS)
    out.save(dst, optimize=True)


def build_ground():
    html = relink(set_title(SRC, 'Ground comparison'))
    # move Get in touch and the copyright line into a footer after main
    start = html.index('<!-- CONTACT -->')
    end = html.index('</main>')
    block = html[start:end]
    html = html[:start] + '</main>\n<footer class="close"><div class="col">\n' + block + '</div></footer>\n' + html[end + len('</main>'):]
    # a mono twin of each contact logo, shown only in the deep close
    for name, rule in [('gmail', 'keep'), ('linkedin', 'cut-white'), ('github', 'keep'), ('spotify', 'cut-black'), ('youtube', 'cut-white')]:
        mono_logo(name, rule)
        html = html.replace(f'<img src="../../assets/logos/{name}-logo.png" alt="" />',
                            f'<img src="../../assets/logos/{name}-logo.png" alt="" /><img class="mono" src="logos-mono/{name}.png" alt="" />')
    # the Cariina cover keeps the old ground on purpose
    html, n = re.subn(r'(<a class="work" href="\.\./\.\./case-studies/cariina\.html">.*?</a>)',
                      r'\1\n<p class="cariina-note">The Cariina cover still carries the old ground; the real change recolours it to match.</p>', html, count=1, flags=re.S)
    assert n == 1
    html = inject(html, GROUND_CSS, GROUND_BAR, GROUND_JS)
    html = html.replace('<html lang="en">', '<html lang="en" data-ground="haze">')
    (OUT / 'ground-compare.html').write_text(html, encoding='utf-8')


# ---------- hover-compare ----------

TELL = {
    'disney': 'start with the person who can say no.',
    'hoagie': 'It turned out to be the only reason the thing shipped at all.',
    'cariina': 'A sixth feature on a product nobody opened was not going to change that.',
    'ai-fluency-lab': 'The program runs again in the fall whether or not I am the one running it.',
}
ALT_THUMB = {
    'disney': 'disney-intern-cohort.jpg',
    'hoagie': 'hoagie-cal-beta.png',
    'cariina': 'cariina-automation-apps-script.jpg',
    'ai-fluency-lab': 'ai-fluency-lab-poster-session.jpg',
}
DECK = {
    '500ms-sound': 'Play someone half a second of sound.',
    'working-with-ai': 'Most people I know open a chat window, type what they want, and hope for the best.',
    'major-as-method': 'People ask how a psychology major ended up running product.',
}
MARGIN = {  # Currently row -> existing photo; Reading and Eating wait for Chloe's photos
    'Building': 'hoagie-cal-beta.png',
    'Researching': 'smpc-talk.jpg',
    'Listening': 'harp-orchestra.jpg',
}
HANDLE = {
    'Email': 'chloelau@princeton.edu',
    'LinkedIn profile': 'linkedin.com/in/chloe-hc-lau',
    'GitHub profile': 'github.com/lauechlo',
    'Spotify playlist': 'open.spotify.com, the harp playlist',
    'Princeton Katzenjammers on YouTube': 'youtube.com/@princetonkatzenjammers4504',
}

HOVER_CSS = BAR_CSS + """
  /* the arrows are gone in every variant; the reveal is the affordance */

  /* case-study rows: the reserved line plus 8px keeps a revealed line attached to its own row, not the next */
  a.work{margin:0 0 8px}
  a.work .tell{font-family:var(--font-meta);font-size:13px;line-height:18px;color:var(--muted);margin:0;min-height:18px;opacity:0;transition:opacity .15s ease}
  html[data-a="1"] a.work:hover .tell,html[data-a="1"] a.work:focus-visible .tell{opacity:1}
  a.work .thumb img.alt{display:none}
  html[data-a="2"] a.work .thumb{position:relative}
  html[data-a="2"] a.work .thumb img{position:absolute;inset:0;width:100%;height:100%;transition:opacity .25s ease}
  html[data-a="2"] a.work .thumb img.alt{display:block;opacity:0}
  html[data-a="2"] a.work:hover .thumb img.alt{opacity:1}
  html[data-a="3"] a.work .thumb img{filter:grayscale(1);transition:filter .2s ease}
  html[data-a="3"] a.work:hover .thumb img{filter:none}

  /* blogs */
  .list .deck{grid-column:2;font-size:15px;line-height:1.4;color:var(--muted);min-height:21px;opacity:0;transition:opacity .15s ease}
  html[data-b="1"] .list li:hover .deck,html[data-b="1"] .list li:focus-within .deck{opacity:1}
  html[data-b="2"] .list .deck{display:none}

  /* currently: a photo in the margin */
  .mg{display:none}
  @media (hover:hover) and (min-width:1000px){
    .now li{position:relative}
    html[data-c="1"] .mg,html[data-c="2"] .mg{display:block;position:absolute;top:-6px;width:132px;height:auto;border-radius:4px;opacity:0;transition:opacity .15s ease;pointer-events:none}
    html[data-c="1"] .mg{left:calc(100% + 28px)}
    html[data-c="2"] .mg{right:calc(100% + 28px)}
    .now li:hover .mg{opacity:1}
  }

  /* about slideshow caption */
  .side{align-self:start}
  .slides-cap{font-family:var(--font-meta);font-size:13px;line-height:1.5;color:var(--muted);margin:6px 0 0;min-height:20px;opacity:0;transition:opacity .2s ease}
  html[data-f="1"] .side:hover .slides-cap{opacity:1}
  html[data-f="3"] .slides-cap{display:none}

  /* contact handles */
  .channels{position:relative}
  html[data-g] .channels{padding-bottom:24px}
  .channel::after{content:attr(data-handle);position:absolute;left:0;bottom:0;font-family:var(--font-meta);font-size:13px;line-height:1.5;color:var(--muted);opacity:0;transition:opacity .15s ease;white-space:nowrap}
  html[data-g] .channel:hover::after{opacity:1}

  /* sub-page footer, mocked with the article.css rules */
  .mock-lbl{font-family:var(--font-meta);font-size:13px;color:var(--muted);margin:46px 0 10px}
  .article-footer{font-family:var(--font-meta);padding:32px 0 0;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:flex-start;font-size:13px;color:var(--muted)}
  .article-footer a{color:var(--ink-2);text-decoration:none;display:inline-block;transition:color .15s}
  .article-footer a>span{border-bottom:1px solid var(--line);padding-bottom:1px}
  .article-footer a:hover{color:var(--slate-2)}
  .article-footer a[data-deck]::after{content:attr(data-deck);display:block;font-size:13px;color:var(--muted);margin-top:4px;min-height:19px;opacity:0;transition:opacity .15s;text-align:right}
  html[data-e="1"] .article-footer a:hover::after{opacity:1}

  /* touch rules, the same ones the real change puts under @media (hover:none) */
  html[data-touch]:not([data-static]) :is(a.work .tell,.list .deck,.slides-cap){display:none}
  html[data-touch]:not([data-static]) a.work{margin:0 0 18px}
  html[data-touch][data-static] :is(a.work .tell,.list .deck){opacity:1}
  html[data-touch] .mg,html[data-touch] .channel::after,html[data-touch] .article-footer a::after{display:none !important}

  /* phone view: this page again in a 390px frame, so the site's own phone layout applies */
  .phone{display:none}
  html[data-phone] main{display:none}
  html[data-phone] .phone{display:flex;justify-content:center;padding:12px;height:calc(100vh - 62px);box-sizing:border-box}
  .phone iframe{width:390px;height:100%;border:1px solid var(--hair);background:var(--bone)}
"""

HOVER_BAR = """<div class="bar">
  <span class="g"><b>Case studies</b>
    <label><input type="radio" name="a" value="1" checked /> 1 the page's lesson, one line</label>
    <label><input type="radio" name="a" value="2" /> 2 cover crossfades to a photo</label>
    <label><input type="radio" name="a" value="3" /> 3 grey at rest</label></span>
  <span class="g"><b>Blogs</b>
    <label><input type="radio" name="b" value="1" checked /> first sentence</label>
    <label><input type="radio" name="b" value="2" /> none</label></span>
  <span class="g"><b>Currently</b>
    <label><input type="radio" name="c" value="1" checked /> photo in the right margin</label>
    <label><input type="radio" name="c" value="2" /> left margin</label>
    <label><input type="radio" name="c" value="3" /> none</label></span>
  <span class="g"><b>Footer</b>
    <label><input type="radio" name="e" value="1" checked /> next page's title</label>
    <label><input type="radio" name="e" value="2" /> none</label></span>
  <span class="g"><b>About photo</b>
    <label><input type="radio" name="f" value="3" checked /> none</label>
    <label><input type="radio" name="f" value="1" /> caption</label>
    <label><input type="radio" name="f" value="2" /> cursor scrubs</label></span>
  <span class="g"><label><input type="checkbox" id="g" /> contact handles</label></span>
  <span class="g"><label><input type="checkbox" id="phone" /> p phone view</label>
    <label><input type="checkbox" id="static" /> phones show the lines</label>
    <label><input type="checkbox" id="rm" /> r reduced motion</label></span>
  <span class="which">hover the rows, the marks, the photo and the links</span>
</div>
<div class="phone"><iframe id="P" title="phone view"></iframe></div>"""

HOVER_JS = """<script>
(function(){
  const root=document.documentElement, q=new URLSearchParams(location.search);
  const cb=id=>document.getElementById(id);
  // state can arrive in the URL (the phone frame loads this page again with the current picks)
  if(q.has('embed')) root.dataset.embed='';
  if(q.has('touch')) root.dataset.touch='';
  for(const n of ['a','b','c','e','f']){ const v=q.get(n); const el=v&&document.querySelector(`input[name="${n}"][value="${v}"]`); if(el) el.checked=true; }
  for(const id of ['g','static','rm']) if(q.has(id)) cb(id).checked=true;
  function state(){
    let s=''; for(const n of ['a','b','c','e','f']) s+='&'+n+'='+root.dataset[n];
    for(const id of ['g','static','rm']) if(cb(id).checked) s+='&'+id;
    return s;
  }
  function apply(){
    for(const n of ['a','b','c','e','f']) root.dataset[n]=document.querySelector(`input[name="${n}"]:checked`).value;
    root.toggleAttribute('data-g',cb('g').checked);
    root.toggleAttribute('data-static',cb('static').checked);
    root.toggleAttribute('data-rm',cb('rm').checked);
    root.toggleAttribute('data-phone',cb('phone').checked);
    if(cb('phone').checked){ const src=location.pathname+'?embed&touch'+state(); if(cb('P').getAttribute('src')!==src) cb('P').src=src; }
  }
  document.querySelectorAll('.bar input').forEach(i=>i.addEventListener('change',apply));
  document.addEventListener('keydown',e=>{
    if(e.target.tagName==='INPUT') return;
    const r={'1':'1','2':'2','3':'3'}[e.key];
    if(r){ const el=document.querySelector(`input[name="a"][value="${r}"]`); if(el){el.checked=true;apply();} }
    const t={p:'phone',r:'rm'}[e.key];
    if(t){ cb(t).checked=!cb(t).checked; apply(); }
  });
  apply();

  // caption follows whichever photo is showing; scrub maps the cursor's x to a photo
  const box=document.getElementById('slides'), cap=document.getElementById('slides-cap');
  if(box&&cap){
    const imgs=[...box.querySelectorAll('img')];
    const show=()=>{ const on=imgs.find(i=>i.classList.contains('on')); cap.textContent=on?on.alt:''; };
    new MutationObserver(show).observe(box,{attributes:true,subtree:true,attributeFilter:['class']});
    show();
    box.addEventListener('mousemove',e=>{
      if(root.dataset.f!=='2') return;
      const r=box.getBoundingClientRect(), i=Math.min(imgs.length-1,Math.max(0,Math.floor((e.clientX-r.left)/r.width*imgs.length)));
      imgs.forEach((im,k)=>im.classList.toggle('on',k===i));
    });
  }
})();
</script>"""

MOCK_FOOTER = """
<!-- SUB-PAGE FOOTER, mocked -->
<p class="mock-lbl">How a sub-page footer would read, here the end of the Disney case study</p>
<footer class="article-footer">
  <a href="#"><span>Back to portfolio</span></a>
  <a href="#" data-deck="Rebuilding Hoagie around event discovery."><span>Next: Hoagie</span></a>
</footer>
"""


def build_hover():
    html = relink(set_title(SRC, 'Hover comparison'))
    # arrows out everywhere
    html = html.replace('<span class="arr">→</span>', '')
    html = html.replace('>Résumé ↗<', '>Résumé<').replace('>Full version ↗<', '>Full version<')
    # case-study rows: the lesson line, and a second image for the crossfade variant
    for key, line in TELL.items():
        m = re.search(rf'(<a class="work" href="\.\./\.\./case-studies/{key}\.html">.*?</a>)', html, re.S)
        row = m.group(1)
        new = re.sub(r'</p>(\s*</div>\s*</a>)$', lambda mm: f'</p>\n      <p class="tell">{line}</p>' + mm.group(1), row)
        assert 'class="tell"' in new, key
        thumb = OUT / 'thumbs' / (key + pathlib.Path(ALT_THUMB[key]).suffix.lower().replace('.jpeg', '.jpg'))
        resize(ROOT / 'assets' / ALT_THUMB[key], thumb, 192)
        new = new.replace('loading="lazy" decoding="async" /></div>', f'loading="lazy" decoding="async" /><img class="alt" src="thumbs/{thumb.name}" alt="" loading="lazy" /></div>')
        assert new != row, key
        html = html.replace(row, new)
    # blogs: the first sentence
    for key, line in DECK.items():
        html, n = re.subn(rf'(<a class="title" href="\.\./\.\./essays/{key}\.html">.*?</a>)</li>', rf'\1<span class="deck">{line}</span></li>', html)
        assert n == 1, key
    # currently: a photo in the margin for the rows that have one
    for label, photo in MARGIN.items():
        dst = OUT / 'now' / (label.lower() + ('.png' if photo.endswith('.png') else '.jpg'))
        resize(ROOT / 'assets' / photo, dst, 264)
        html, n = re.subn(rf'(<span class="k">{label}</span><span>.*?</span>)</li>', rf'\1<img class="mg" src="now/{dst.name}" alt="" loading="lazy" /></li>', html)
        assert n == 1, label
    # about: caption under the slideshow
    html, n = re.subn(r'(<div class="slides" id="slides">.*?</div>)(\s*</section>)', r'<div class="side">\1<p class="slides-cap" id="slides-cap"></p></div>\2', html, count=1, flags=re.S)
    assert n == 1
    # contact handles
    for label, handle in HANDLE.items():
        html, n = re.subn(rf'(<a class="channel" [^>]*aria-label="{re.escape(label)}")>', rf'\1 data-handle="{handle}">', html)
        assert n == 1, label
    # a mocked sub-page footer at the end
    html = html.replace('<div class="foot">', MOCK_FOOTER + '\n<div class="foot">', 1)
    html = inject(html, HOVER_CSS, HOVER_BAR, HOVER_JS)
    html = html.replace('<html lang="en">', '<html lang="en" data-a="1" data-b="1" data-c="1" data-e="1" data-f="3">')
    (OUT / 'hover-compare.html').write_text(html, encoding='utf-8')


if __name__ == '__main__':
    build_ground()
    build_hover()
    print('built', OUT / 'ground-compare.html', 'and', OUT / 'hover-compare.html')
