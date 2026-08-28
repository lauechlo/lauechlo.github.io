# chloelau.me

Personal site for Chloe Lau, Princeton '27. Static, no build step.

## Structure

```
index.html          the homepage: all markup, CSS, and JS in one file
article.css         shared styles for every sub-page
case-studies/       Disney+ Search, Hoagie, Cariina, AI Exploration Lab
essays/             500ms of sound, working with AI, psychology to product
assets/             photos, logos, favicons
CNAME               custom domain for GitHub Pages
```

## Running it locally

```
python -m http.server 8765
```

Then open <http://127.0.0.1:8765/index.html>. Fonts load from Google Fonts, so
the first load needs a connection.

## Design system

Tokens live in the `:root` block at the top of `index.html` and are mirrored in
`article.css`. Two typefaces only: **Fraunces** for headings, **Karla** for body
and labels. Never hardcode a `font-family`; use `var(--font-heading)` or
`var(--font-body)`.

Every text color is checked against the page background for WCAG AA (4.5:1).
Headings are sentence case throughout.
