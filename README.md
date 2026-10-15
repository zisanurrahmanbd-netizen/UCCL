# UCCL — Unique Consultancy & Collection Ltd.

Corporate website for a financial recovery & collection consultancy firm (Dhaka, Bangladesh).

Static, dependency-free single-page site: `index.html` + `assets/css/styles.css` + `assets/js/main.js`.
No build step required — open `index.html` or serve the folder with any static server.

## Run locally

```bash
python3 -m http.server 3000 --bind 0.0.0.0
# then open http://localhost:3000
```

## Site structure

| # | Section | Anchor |
|---|---------|--------|
| 1 | Hero (headline, CTAs, at-a-glance panel) | `#home` |
| 2 | Trust bar / animated stats strip | — |
| 3 | About Us | `#about` |
| 4 | Our Services (7 cards) | `#services` |
| 5 | Why UCCL — Mission / Vision / 6 Core Values | `#why-uccl` |
| 6 | Operational Capacity (ring-fenced teams, scaling) | `#capacity` |
| 7 | Nationwide Coverage (map + district list) | `#coverage` |
| 8 | Leadership — Board of Directors | `#leadership` |
| 9 | Corporate Governance (org chart) | `#governance` |
| 10 | Clients & Partners (logo wall) | `#partners` |
| 11 | Facilities (image gallery) | `#facilities` |
| 12 | Code of Conduct / Compliance | `#compliance` |
| 13 | Contact / CTA (functional form) | `#contact` |
| 14 | Footer | — |

## Features

- Sticky navigation with anchor links, active-section highlighting, mobile hamburger menu
- Subtle scroll-triggered fade-ins (respects `prefers-reduced-motion`)
- Animated stat counters
- Fully responsive, mobile-first (2 breakpoints: 980px, 640px)
- Print styles included

## Brand assets & palette

The site is themed from the UCCL company logo (charcoal-black mark + red crescent + white).

- `assets/img/logo-lockup.png` — **the full official lockup** (mark + two-line wordmark + red tagline), used as-is in header + footer
- `assets/img/favicon.png` — browser tab icon (mark variant, for visibility on white tabs)
- `assets/img/logo-mark.png` / `logo-mark-white.png` / `logo-mark-mono.png` — mark-only variants (generated extras, not referenced by the site)

The coverage map is generated from real geographic data by `tools/make_map.py`
(geoBoundaries ADM0, CC BY 4.0 — attribution printed under the map).

The lockup is rendered by `tools/make_lockup.py`; the mark variants by
`tools/make_logo.py`. To swap in the official artwork, overwrite
`assets/img/logo-lockup.png` (same 1600×360 transparent canvas) — no code changes
needed. The footer places the dark lockup on a plain white plate so it reads
unchanged against the charcoal footer.

Brand tokens live at the top of `assets/css/styles.css`: `--gold-500` is the brand red
(`#E1251B`), `--navy-900` is the charcoal black (`#201C1E`), backgrounds are white/light gray.

## Placeholders to replace before launch

| Item | Location | Current value |
|------|----------|---------------|
| Phone number | `.topbar`, `#contact`, footer | `+880 1711-000000` |
| Email | same | `info@uccl.com.bd` |
| Office address | `#contact` | `Dhaka, Bangladesh` |
| Corporate profile PDF | project root | `corporate-profile.pdf` kept on disk but **no longer linked anywhere on the site** |
| Leadership photos | `#leadership` (`.team-card__photo`) | Initials placeholders — swap `<div>` for `<img>` |
| Facility photos | `#facilities` (`.gallery__tile`) | SVG placeholder frames — swap for real `<img>` |
| Partner logos | `#partners` (`.logo-tile`) | Styled text wordmarks — swap for logo `<img>` files |
| Social links | footer `.social-link` | `href="#"` |

## Contact form

The form validates client-side (name, email, phone, message) and shows a confirmation.
To deliver submissions to an inbox, set an endpoint in `assets/js/main.js`:

```js
var FORM_ENDPOINT = "https://formspree.io/f/YOUR_FORM_ID";
```

Supported: any endpoint accepting a JSON POST (Formspree, Basin, Getform, a custom API, …).

## Deployment

Upload the folder as-is to any static host (Netlify, Vercel, Cloudflare Pages, cPanel, etc.).
# UCCL
