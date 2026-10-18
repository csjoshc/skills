# Reusable Design Spec

Read this only when the user asks for a portable design system or the UI work has durable visual decisions shared across multiple surfaces.

## Audit and decide

1. Read the project instructions, product context, existing UI, tokens, and brand assets. Fill the fixed inventory in [audit-template.md](audit-template.md); mark irrelevant or unavailable inputs explicitly.
2. Extract the design direction from existing product evidence. Use [brand-ingest.md](brand-ingest.md) when approved brand assets exist. Use [decision-matrix.md](decision-matrix.md) only when existing evidence does not establish a direction.
3. Resolve any material ambiguity with one focused question. Otherwise choose a coherent direction and proceed without asking the user to approve each section.

## Emit

Write these artifacts at the project root:

```text
DESIGN.md
preview-ui/preview.html
preview-ui/preview-dark.html
preview-ui/README.md
```

- Follow [stitch-format.md](stitch-format.md) for front matter and section order. Include the local project’s relevant tokens, states, accessibility behavior, responsive rules, and component patterns.
- Read both light and dark token sources when available; do not derive one palette by inverting the other. Keep token names paired across palettes.
- Generate both previews from [preview-template.html](preview-template.html). Match them to the emitted spec, then inspect them in a browser when available.
- Call the Skill tool with `stop-slop` on generated prose.

Completion: the spec and both previews agree with inspected project evidence, and the README explains how to view them.
