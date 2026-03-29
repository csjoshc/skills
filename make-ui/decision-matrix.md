# Decision Matrix & Prohibited Patterns

## Vertical-to-Aesthetic Mapping

For greenfield projects or when the existing stack gives no design signal. **Existing project patterns always take precedence.**

| Vertical | Aesthetic | Key Traits | Reference Products |
|----------|-----------|------------|-------------------|
| Dev Tool / AI / LLM | Code-Editor Core | Monospaced accents, dark default, high density, neon/cyber accents | Raycast, Linear, Vercel |
| Fintech / Banking | Trust-Refined | Deep slates/navys, high-contrast type, generous padding, sharp borders | Stripe, Mercury, Sofi |
| Creative / SaaS | Editorial Grid | Asymmetric layouts, fluid type, display serif fonts, grain/noise textures | Framer, Readymag, Notion |
| E-commerce / Marketplace | Product-Forward | Large product imagery, clean cards, strong CTAs, warm accent palette | Shopify, Gumroad |
| Health / Wellness | Organic Calm | Rounded shapes, muted earth tones, generous whitespace, soft shadows | Headspace, Calm |
| Education / Docs | Structured Clarity | Strong hierarchy, sidebar nav, code-friendly, reading-optimized spacing | Stripe Docs, GitBook |
| Gaming / Entertainment | Immersive Chrome | Dark backgrounds, vibrant accents, bold type, atmospheric gradients | Steam, Discord |
| Internal Tool / Dashboard | Data-Dense Utility | Compact spacing, monospace data, status-light colors, panel-based layout | Grafana, Retool, Ableton |
| Default / Unknown | Trust-Refined | Safe fallback with professional polish | Stripe |

## Greenfield Technical Defaults

Existing stack overrides all of these:
- Components: Shadcn/ui (Radix Primitives)
- Icons: lucide-react (primary), simple-icons (brands)
- Motion: framer-motion for state transitions, CSS for micro-interactions
- Colors: CSS custom properties with semantic naming

## Prohibited Patterns

Defaults — user can override in Consultation Mode.

- NO "Generic SaaS" purple-to-blue gradients on white backgrounds
- NO default system fonts (Inter, Roboto, Arial) for customer-facing apps. Exception: internal tools, or user explicitly keeps them.
- NO simple "Fade-In" as the only animation. Use stagger, layoutId, or orchestrated sequences.
- NO emojis as UI icons. Use SVG icon libraries.
- NO generic box shadows. Use layered ambient shadows or sharp hard borders.
- NO copy-pasted style strings across files. Extract shared components.
- NO raw color token drift at scale (`slate-*`/`gray-*`). Use semantic names.
- NO flat backgrounds with zero depth. Minimum: subtle gradient or texture.

## Anchoring Reference Products

For Consultation Mode step 4. When the user doesn't know what direction to take, **name the closest existing product to their current UI** to anchor the conversation.

| Direction | Example Products | Why They Work |
|-----------|-----------------|---------------|
| Refined dark tool | Linear, Raycast, Vercel Dashboard | Subtle gradients on dark surfaces, precise spacing, smooth transitions |
| Editorial / studio | Readymag, Framer, Stripe Docs | Strong type hierarchy, serif/sans pairings, generous whitespace |
| Industrial / DAW | Ableton Live, Blender, Bitwig | Extreme density, monospace, hard edges, status lights |
| Grafana-level polish | Grafana, n8n, Retool | Data-dense dark panels, good visual hierarchy, consistent tokens |
| Minimal polish | shadcn/ui, Radix Themes | Same stack, just consistent tokens and extracted components |
