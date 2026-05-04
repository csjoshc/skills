# Vibe Quick-Pick — Aesthetic Matrix (Slim)

Single-glance reference. For the full matrix with hybrids and density rules, see [/make-design-md](../../make-design-md/references/decision-matrix.md).

## Matrix

| Vertical | Aesthetic | References |
|---|---|---|
| Dev tool / AI / LLM | Code-Editor Core | Raycast, Linear, Vercel |
| Fintech | Trust-Refined | Stripe, Mercury |
| Creative / SaaS | Editorial Grid | Framer, Notion |
| E-commerce | Product-Forward | Shopify |
| Health / wellness | Organic Calm | Headspace, Calm |
| Docs / education | Structured Clarity | Stripe Docs, GitBook |
| Gaming | Immersive Chrome | Steam, Discord |
| Internal / dashboard | Data-Dense Utility | Grafana, Retool |
| Enterprise SaaS | Enterprise Neutral | C3, IBM Carbon |
| Default | Trust-Refined | Stripe |

## Density

Compact / Balanced (default) / Airy. Pick once, before building.

## Greenfield defaults

- Components: shadcn/ui (Radix Primitives)
- Icons: lucide-react
- Motion: framer-motion (layout) + CSS (micro)
- Tokens: CSS custom properties with semantic names

## Prohibited patterns

- Generic SaaS purple→blue gradient on white
- System fonts (Inter / Roboto / Arial) for customer-facing apps
- Fade-In as the only animation
- Emojis as UI icons
- `shadow-sm` / `shadow-md` everywhere (use one deliberate elevation system)
- Copy-pasted style strings across files
- Raw `slate-*` / `gray-*` tokens at scale
- Flat backgrounds with zero depth
