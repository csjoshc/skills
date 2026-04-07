# Markdown templates

Copy and adjust titles/paths. Replace `…` placeholders.

## Hub page

```markdown
# {Area} (`docs/{path}/`)

**Summary:** {One paragraph: what this area covers, main trust boundaries, what is intentionally out of scope.}

**Run locally:** {Bullets or numbered commands—no secrets.}

**Code / entrypoints:** {Links to services, apps, or modules—whatever your repo uses.}

**More detail:** [Architecture](architecture.md) · [Network](network.md) · [Ports](ports.md) · [Env](env.md) · …
```

## Satellite page

```markdown
# {Topic}

**Summary:** {Answer in one breath—what this page is for.}

**Follow-up:** {Mechanics, links to code paths, edge cases. Optional short numbered list.}

{Optional: single Mermaid diagram}

**See also:** [Hub](README.md) · [Related topic](related.md)
```

## Lookup page (env, secrets, URLs)

```markdown
# {Secrets and environment | URLs and ports}

**Summary:** {Where values live; never commit real values; pointer to `.env.example` or vault pattern.}

| Name / pattern | Owner | In client bundle? |
|----------------|-------|-------------------|
| `VAR_NAME` | Service | Never / Yes — … |

**See also:** [Hub](README.md) · [Local dev](local-dev.md)
```

## Platform notes

- **Confluence / wiki:** Keep the same **Summary / Follow-up** labels (use a short paragraph or built-in panel/excerpt for Summary). Replace relative links with **internal page links** or stable URLs.
- **GitHub / GitLab Markdown:** Use relative links and standard heading anchors.
- **Notion / other wikis:** Adapt link style to the platform's conventions; the structure and labels stay the same.
