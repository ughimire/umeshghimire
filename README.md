# umeshghimire.com.np

Personal portfolio for **Umesh Ghimire** — senior PHP & WordPress developer in Nepal.

Static, multi-page, no build step. Plain HTML / CSS / JS, deployed to Netlify.

## Pages

| Path | Title | Markdown view |
|---|---|---|
| `/` | Home | `/index.md` |
| `/about/` | About | `/about.md` |
| `/services/` | Services + FAQ | `/services.md` |
| `/portfolio/` | Selected projects | `/portfolio.md` |
| `/experience/` | Career timeline | `/experience.md` |
| `/cv/` | Full CV (printable) | `/cv.md` |
| `/contact/` | Contact + form | `/contact.md` |

Each page has a **"View as Markdown"** button just above the footer that links to the matching `.md` file. The markdown views are aimed at AI / LLM crawlers and quick text consumption. `/llms.txt` is also published as the standard LLM index.

## Local preview

No build needed:

```bash
python3 -m http.server 8000
# or
npx serve .
```

Then open <http://localhost:8000/>.

## Updating markdown views

Markdown files are generated from the HTML pages by `build-markdown.py` (Python 3, standard library only). Run it any time you edit a page's HTML:

```bash
python3 build-markdown.py
```

It rewrites `index.md`, `about.md`, `services.md`, `portfolio.md`, `experience.md`, `cv.md` and `contact.md` based on each page's `<main>` content.

## Deploy to Netlify

1. Push this folder to GitHub.
2. In Netlify → **Add new site → Import from Git**, pick the repo.
3. Build settings:
   - **Build command:** *(leave empty)*
   - **Publish directory:** `.`
4. Connect domain `umeshghimire.com.np` under **Domain management**.
5. Enable **Netlify Forms** — the contact form already has `data-netlify="true"`.
6. (Optional) Configure form email notification: Site config → Forms → Form notifications → Email notification.

## SEO

- Unique `<title>`, meta description and canonical on every page.
- Open Graph + Twitter Card tags with a 1200×630 cover image (`/assets/img/og-cover.png`).
- Schema.org JSON-LD on every page: `Person`, `ProfessionalService`, `WebSite`, `AboutPage`, `ContactPage`, `CollectionPage`, `BreadcrumbList`, `ItemList`, `FAQPage`.
- `sitemap.xml` and `robots.txt` at the root. `llms.txt` for AI crawlers.
- Markdown views served with `Content-Type: text/markdown` and `X-Robots-Tag: index, follow`.
- Primary keywords targeted: *PHP Developer in Nepal*, *WordPress Developer Nepal*, *Hire WordPress Developer Nepal*, *Laravel Developer Nepal*, *Freelance PHP Developer Kathmandu*.

## Files

```
.
├── index.html           # Home
├── about/index.html
├── services/index.html
├── portfolio/index.html
├── experience/index.html
├── cv/index.html
├── contact/index.html
├── 404.html
├── *.md                 # Auto-generated markdown views
├── llms.txt             # AI / LLM site index
├── sitemap.xml
├── robots.txt
├── netlify.toml         # Build, redirects, headers, Content-Type
├── _headers             # Fallback header rules
├── _redirects           # Pretty-URL redirects
├── build-markdown.py    # Markdown view generator
├── assets/
│   ├── css/styles.css
│   ├── js/main.js
│   └── img/
│       ├── umesh-ghimire.jpg    # Profile photo (400×400 square)
│       ├── favicon-32.png
│       ├── favicon-192.png
│       ├── apple-touch-icon.png
│       ├── og-cover.png         # Social-share image (1200×630)
│       └── og-cover.svg         # Source for og-cover.png
└── README.md
```

## Production checklist

- [x] All pages return 200; no dead internal links.
- [x] Pretty URLs with no `.html` extension exposed.
- [x] PNG favicons (32, 192) and 180×180 Apple touch icon — your photo.
- [x] OG cover image 1200×630.
- [x] Responsive nav across desktop / tablet / phone (hamburger ≤ 900px).
- [x] Default theme is light; dark mode toggle remembered per device.
- [x] Print-styled CV page (Print → Save as PDF).
- [x] Netlify Forms wired with honeypot.
- [x] Security headers (HSTS, X-Frame-Options, CSP, Referrer-Policy, Permissions-Policy).
- [x] Long-cache for static assets, short-cache for sitemap / robots / markdown.
