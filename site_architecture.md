# Read the Room — Site Architecture
*Last updated: May 5, 2026*

---

## Overview

**URL:** readtheroom.news (recommended domain — verify availability)
**Stack:** Static HTML + GitHub Pages
**Launch target:** June 2, 2026
**Build deadline:** May 17, 2026 (Simba travels May 18–June 1)

---

## Brand Structure

**Read the Room** is the umbrella brand. Two newsletters sit beneath it:

| Newsletter | Cadence | Focus |
|---|---|---|
| Read the Room | Weekly · Tuesdays | National politics, one topic, both sides |
| The Frequency | Weekly · Thursdays | Alabama/Chambers County local politics, 5 stories |

---

## Full Site Map

```
readtheroom.news/
├── index.html                          ← Homepage
├── about/
│   ├── read-the-room/index.html        ← About RTR
│   └── the-frequency/index.html        ← About The Frequency
├── read-the-room/
│   ├── index.html                      ← Subscribe + section intro
│   ├── archive/index.html              ← All issues index
│   └── issue/[n]/index.html            ← Full HTML issue pages
├── the-frequency/
│   ├── index.html                      ← Subscribe + section intro
│   ├── archive/index.html              ← All issues index
│   ├── issue/[n]/index.html            ← Full HTML issue pages
│   ├── signals/
│   │   ├── index.html                  ← Signals index
│   │   └── [slug]/index.html           ← Individual signal pieces
│   └── waves/
│       ├── index.html                  ← Waves index
│       └── [slug]/index.html           ← Individual community profiles
└── games/
    ├── index.html                      ← Games hub
    └── [slug]/index.html               ← Original RTR game (TBD)
```

---

## Content Types

### Read the Room
- **Issues** — Weekly deep-dive, one national topic, both sides. Full HTML published to `/read-the-room/issue/[n]/`.

### The Frequency
- **Issues** — Weekly Thursday roundup, 5 Alabama/Chambers County stories. Full HTML published to `/the-frequency/issue/[n]/`.
- **Signals** — Immediate standalone pieces on breaking/time-sensitive topics that can't wait a week. Published to `/the-frequency/signals/[slug]/`.
- **Waves** — Long-form community profiles. People making waves in East Alabama. Published to `/the-frequency/waves/[slug]/`. Existing: Hazel Floyd, Christopher Davis, Lee McInnis.

---

## Beehiiv Workflow (Path 2 — Teaser Model)

1. Build full HTML issue → push to GitHub → live on site
2. Claude generates teaser copy (hook + headlines + link) → paste into Beehiiv → send
3. Beehiiv handles subscriber list, delivery, and analytics
4. Two separate Beehiiv publications: one for RTR, one for The Frequency
5. Two separate subscribe embeds on the site

**Weekly deliverables (per issue, both newsletters):**
1. Full HTML newsletter (published to site)
2. Thumbnail HTML (1200×630px, screenshot for Beehiiv OG image)
3. Beehiiv teaser copy + link (Claude generates)
4. SEO title/subtitle (2–3 options)
5. Social copy: Facebook, X, Bluesky, Instagram (2 options each)

---

## Games

- Original RTR-branded game only (no Atlas Valley Books games transferred)
- Concept TBD — discuss after design phase
- Lives at `/games/[slug]/`

---

## Homepage Section Order (approved)

1. Top bar — 3px gold
2. Nav — sticky, dark, logo mark left
3. Hero — dark, logo centered, subtle grid texture, tagline
4. Gold band — "◆ Latest Issues ◆"
5. Split panel — Latest issues: RTR dark left | TF warm parchment right, 3px gold divider, ghost issue numbers
6. Subscribe strip — Column-aligned below split panel: RTR dark | TF cream
7. Signals & Waves band — Warm cream, two cards (Signals copper | Waves slate). **Only renders when content exists.** Eyebrow: "Also From The Frequency."
8. Games section — Dark bg, split layout, tilted game board visual
9. Footer — Very dark, logo, newsletter + site links

## Design Decisions (approved)
- Nav: near-black #1a1a18, gold rule + tagline beneath brand name
- Accent palette: Brand Gold #c8a96e · Signal Copper #b8782a · Wave Slate #5a8a9a
- The Frequency background: warm parchment #ede8df (not white)
- Ghost issue numbers float in split panel at low opacity for depth
- All design changes require Simba's approval before building
