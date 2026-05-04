# Decision Matrix — Aesthetic Direction

For greenfield projects or when current code gives no clear signal. **Existing patterns always take precedence.**

## Vertical → Aesthetic Mapping

| Vertical | Aesthetic | Key Traits | Reference Products |
|---|---|---|---|
| Dev Tool / AI / LLM | Code-Editor Core | Mono accents, dark default, high density, neon/cyber accents | Raycast, Linear, Vercel |
| Fintech / Banking | Trust-Refined | Deep slates/navys, high-contrast type, generous padding, sharp borders | Stripe, Mercury, Sofi |
| Creative / SaaS | Editorial Grid | Asymmetric layouts, fluid type, display serif, grain/noise | Framer, Readymag, Notion |
| E-commerce | Product-Forward | Large product imagery, clean cards, strong CTAs, warm palette | Shopify, Gumroad |
| Health / Wellness | Organic Calm | Rounded shapes, muted earth tones, generous whitespace, soft shadows | Headspace, Calm |
| Education / Docs | Structured Clarity | Strong hierarchy, sidebar nav, code-friendly, reading-optimized | Stripe Docs, GitBook |
| Gaming / Entertainment | Immersive Chrome | Dark backgrounds, vibrant accents, bold type, atmospheric gradients | Steam, Discord |
| Internal Tool / Dashboard | Data-Dense Utility | Compact spacing, monospace data, status-light colors, panel-based | Grafana, Retool, Ableton |
| Enterprise SaaS | Enterprise Neutral | Neutral grays, square buttons, semantic tokens, restrained color | C3, IBM Carbon, Atlassian |
| Default / Unknown | Trust-Refined | Safe fallback with professional polish | Stripe |

## Hybrid Combinations

Real projects often blend two directions. Pick a **primary** (drives layout, density, type, button geometry) and a **secondary** (drives accent color, motion, decorative texture).

| Hybrid | Primary | Secondary | Example use case |
|---|---|---|---|
| Industrial-editorial | Data-Dense Utility | Editorial Grid | Internal tool with marketing-page polish |
| Refined-cyber | Trust-Refined | Code-Editor Core | Fintech for developers (Plaid, Mercury for engineers) |
| Calm-data | Organic Calm | Data-Dense Utility | Health analytics, patient dashboards |
| Cinematic-utility | Immersive Chrome | Data-Dense Utility | Gaming analytics, esports dashboards |
| Editorial-trust | Editorial Grid | Trust-Refined | Premium B2B SaaS, design tools for finance |

**Rule:** never blend more than two. Three-way mixes become incoherent.

## Density Axis (always explicit)

Independent of aesthetic. Pick one before tokens are designed — affects spacing scale, type sizes, and component padding.

| Density | Body size | Card padding | Button height | Reference |
|---|---|---|---|---|
| Compact | 13px | space-03 (12px) | 28px | Linear, Ableton |
| Balanced | 14px | space-04 (16px) | 36px | Stripe, Notion |
| Airy | 16px | space-05 (24px) | 44px | Apple, Headspace |

## Greenfield Defaults

When the user has no opinion and the matrix gives no clear signal:

- **Aesthetic:** Trust-Refined
- **Density:** Balanced
- **Components:** shadcn/ui (Radix Primitives)
- **Icons:** lucide-react
- **Motion:** framer-motion for layouts, CSS for micro

## Prohibited Patterns (defaults; user can override)

- Generic SaaS purple-to-blue gradients on white
- System fonts (Inter / Roboto / Arial) for customer-facing apps
- Fade-In as the only animation
- Emojis as UI icons
- Generic box shadows (`shadow-sm` / `shadow-md` everywhere)
- Copy-pasted style strings across files
- Raw Tailwind tokens (`slate-*` / `gray-*`) at scale
- Flat backgrounds with zero depth
