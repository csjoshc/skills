"""Copy board.json into a renderer template. Reads board.json only."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from board_sources import STAGES

Json = dict[str, Any]
PLACEHOLDER = "__TRACKBOARD_DATA__"
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
TARGETS = {
    "html": "board.html",
    "md": "board.md",
}


def inline_json(board: Json, html: bool) -> str:
    text = json.dumps(board, indent=2, ensure_ascii=False)
    text = text.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    if html:
        text = text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return text


def md_cell(value: Any) -> str:
    return str(value if value not in (None, "") else "").replace("|", "\\|").replace("\n", " ")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(md_cell(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def md_links(items: list[Json]) -> str:
    return ", ".join(f"[{e['label']}]({e['url']})" for e in items)


def md_ac(item: Json) -> str:
    checked = item.get("checked")
    box = "" if checked is None else ("[x] " if checked else "[ ] ")
    return f"- {box}{item['text']}"


def md_claim(c: Json) -> str:
    return str(c["text"]) + "".join(f" `[{t}]`" for t in c.get("tags", []))


def brief_notice(brief: Json) -> str | None:
    """One-line provenance and staleness note shared by every renderer."""
    a = brief.get("authored")
    if not a:
        return None
    if brief.get("stale"):
        n = len(brief.get("changed", []))
        ids = f" ({', '.join(brief['changed'])})" if n else ""
        what = f"{n} ticket{'s' if n != 1 else ''} changed since{ids}" if n else "sources changed since"
        return f"Brief written {a['written_at']}; {what}. Written by {a['written_by'] or 'unknown'}."
    return f"Brief written {a['written_at']} by {a['written_by'] or 'unknown'}."


def render_brief(board: Json) -> list[str]:
    brief, tickets, parts = board.get("brief", {}), board["tickets"], []
    notice = brief_notice(brief)
    if notice:
        parts.append(f"_{notice}_")
    ov = brief.get("overview")
    if ov:
        text = [f"## What we are building: {ov['title']}".rstrip(": "), " ".join(map(md_claim, ov["goal"]))]
        for label, key in (("Not building", "non_goals"), ("Constraints", "constraints")):
            if ov[key]:
                text.append(f"**{label}**\n\n" + "\n".join(f"- {md_claim(x)}" for x in ov[key]))
        text.append(f"Source: `{ov['source']}`")
        parts.append("\n\n".join(t for t in text if t))
    specced = [t for t in tickets if t.get("acceptance") or t.get("intent")]
    if specced:
        text = ["## What defines done"]
        extra = sorted({str(t["stage"]) for t in specced} - set(STAGES))
        for stage in (*STAGES, *extra):
            for t in (x for x in specced if str(x["stage"]) == stage):
                intent = md_claim({"text": t["intent"], "tags": t.get("intent_tags", [])}) if t.get("intent") else ""
                head = f"**{t['id']} {t['title']}** ({stage})" + (f": {intent}" if intent else "")
                text.append("\n".join([head, *map(md_ac, t.get("acceptance", []))]))
        parts.append("\n\n".join(text))
    rules = brief.get("stage_rules")
    if rules:
        note = {"default": " (generic defaults; set `stage_rules` in `.plan/board/config.json`)",
                "brief": " (from `.plan/board/brief.md` where tagged)"}.get(brief.get("stage_rules_source", ""), "")
        tags = brief.get("stage_rule_tags", {})
        text = [f"## What proves each stage\n\nStage exit rules{note}:\n\n" + md_table(
            ["Stage", "Exit rule"], [[s, md_claim({"text": rules[s], "tags": tags.get(s, [])})]
                                     for s in STAGES if s in rules])]
        for g in brief.get("gates", []):
            mark = "met" if g["met"] else "not met"
            lines = [f"**{g['id']}** ({mark}): {g['question']}", *map(md_ac, g["acceptance"])]
            if g.get("note"):
                lines.append(f"Note: {md_claim(g['note'])}")
            if g["evidence"]:
                lines.append(f"Evidence: {md_links(g['evidence'])}")
            text.append("\n".join(lines))
        if brief.get("proof_notes"):
            text.append("\n".join(f"- {md_claim(c)}" for c in brief["proof_notes"]))
        parts.append("\n\n".join(text))
    return parts


def render_tracking(board: Json) -> list[str]:
    tickets, parts = board["tickets"], []
    now = [t for t in tickets if t["stage"] in ("BUILD", "REVIEW", "BLOCKED")]
    if now:
        parts.append("## Now\n\n" + md_table(["ID", "Title", "Stage", "Owner", "Note"],
                     [[t["id"], t["title"], t["stage"], t["owner"], t["note"]] for t in now]))
    if board["drift"]:
        parts.append("## Drift\n\n" + md_table(["Ticket", "Kind", "Values"],
                     [[d["ticket"], d["kind"], json.dumps(d["values"])] for d in board["drift"]]))
    gates = [t for t in tickets if t["is_gate"]]
    if gates:
        parts.append("## Gates\n\n" + md_table(["Gate", "Stage", "Feeds", "Evidence"], [[
            g["id"], g["stage"], ", ".join(t["id"] for t in tickets if t["gate"] == g["id"]) or ", ".join(g["deps"]),
            md_links(g["evidence"])] for g in gates]))
    if board["burn"]:
        names = {c["id"]: c.get("name", c["id"]) for c in board["cycles"]}
        parts.append("## Burn by cycle\n\n" + md_table(["Cycle", "Started", "Completed", "Open at end"], [[
            names.get(b["cycle"], b["cycle"]), b["started"], b["completed"], b["open_at_end"]] for b in board["burn"]]))
    moves = [e for e in board["events"] if e["from"] != e["to"]][-10:]
    if moves:
        parts.append("## Recent stage changes\n\n" + md_table(["Date", "Cycle", "Ticket", "From", "To"], [[
            e["ts"], e["cycle"], e["ticket"], e["from"] or "(new)", e["to"]] for e in reversed(moves)]))
    parts.append("## All tickets\n\n" + md_table(["ID", "Title", "Stage", "Deps", "Gate"], [[
        t["id"], t["title"], t["stage"], ", ".join(t["deps"]), t["gate"]] for t in tickets]))
    return parts


def render_md(board: Json) -> str:
    counts = {s: sum(1 for t in board["tickets"] if t["stage"] == s) for s in STAGES}
    head = [f"# {board['title']}", f"Generated {board.get('generated_at', '')}. "
            + ", ".join(f"{s} {n}" for s, n in counts.items() if n) + "."]
    return "\n\n".join(head + render_brief(board) + render_tracking(board))


def export(board_path: Path, target: str, out: Path) -> int:
    if not board_path.exists():
        print("ERROR: no board.json; run `init` or `refresh` first", file=sys.stderr)
        return 1
    board = json.loads(board_path.read_text(encoding="utf-8"))
    template = (TEMPLATES / TARGETS[target]).read_text(encoding="utf-8")
    body = render_md(board) if target == "md" else inline_json(board, html=target == "html")
    if template.count(PLACEHOLDER) != 1:
        print(f"ERROR: template {TARGETS[target]} must hold {PLACEHOLDER} once", file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(template.replace(PLACEHOLDER, body), encoding="utf-8")
    print(f"Exported {target} -> {out}")
    return 0
