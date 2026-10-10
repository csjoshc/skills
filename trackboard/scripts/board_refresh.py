#!/usr/bin/env python3
"""Build .plan/board/board.json from ticket sources, append stage history, export renderers."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import hashlib

from board_export import PLACEHOLDER, TARGETS, export
from board_sources import (
    DEFAULT_STAGE_RULES,
    STAGES,
    blank_ticket,
    covers_hash,
    merge_overview,
    normalize_stage,
    parse_brief,
    parse_evidence,
    parse_prd,
    parse_sequence_acs,
    parse_stages_override,
    parse_task_sequence,
    parse_ticket_file,
    ticket_digest,
)

__all__ = ["DEFAULT_STAGE_RULES", "PLACEHOLDER", "STAGES", "cycle_for", "main", "normalize_stage",
           "parse_brief", "parse_ticket_file"]

SCHEMA_VERSION = 1
DEFAULT_VIEWS = ["overview", "spec", "proof", "now", "timeline", "dag", "gates", "burn"]

Json = dict[str, Any]


def board_paths(root: Path) -> dict[str, Path]:
    bd = root / ".plan" / "board"
    return {
        "dir": bd, "board": bd / "board.json", "history": bd / "history.jsonl",
        "config": bd / "config.json", "tickets": root / ".tickets",
        "sequence": root / ".plan" / "task-sequence.md", "prd": root / ".plan" / "PRD.md",
        "brief": bd / "brief.md",
    }


def read_json(path: Path, default: Any) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def read_history(path: Path) -> list[Json]:
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def cycle_for(day: str, cycles: list[Json]) -> str | None:
    for c in cycles:
        if c.get("start", "") <= day <= c.get("end", ""):
            return str(c["id"])
    return None


def collect(root: Path) -> tuple[list[Json], list[Json], list[Json]]:
    """Return (tickets, sources, drift) with stage values merged across sources."""
    p = board_paths(root)
    per_source: list[tuple[str, str, list[Json]]] = []
    files = sorted(p["tickets"].glob("*.md")) if p["tickets"].is_dir() else []
    if files:
        per_source.append(("tickets", ".tickets/*.md", [parse_ticket_file(f) for f in files]))
    if p["sequence"].exists():
        rows = parse_task_sequence(p["sequence"])
        if rows:
            per_source.append(("task-sequence", ".plan/task-sequence.md", rows))
    override = parse_stages_override(p["dir"])
    known = {r["id"] for _, _, rows in per_source for r in rows}
    orphans = {k: v for k, v in override.items() if known and k not in known}
    override = {k: v for k, v in override.items() if k not in orphans}
    if override:
        rows = [dict(blank_ticket(k), stage=v) for k, v in override.items()]
        per_source.append(("stages", ".plan/board/stages.yaml", rows))

    order = {"task-sequence": 0, "tickets": 1, "stages": 2}
    merged: dict[str, Json] = {}
    stage_votes: dict[str, dict[str, str]] = {}
    for kind, _, rows in sorted(per_source, key=lambda s: order[s[0]]):
        for row in rows:
            tid = row["id"]
            if row["stage"]:
                stage_votes.setdefault(tid, {})[kind] = row["stage"]
            if tid not in merged:
                merged[tid] = dict(row)
            elif kind == "tickets":
                keep = merged[tid]
                merged[tid] = {k: (v if v not in (None, [], "") else keep.get(k)) for k, v in row.items()}
    if p["sequence"].exists():
        seq_acs = parse_sequence_acs(p["sequence"], list(merged))
        for tid, t in merged.items():
            if not t["acceptance"]:
                t["acceptance"] = seq_acs.get(tid, [])
    sources = [{"kind": k, "path": path, "count": len(rows)} for k, path, rows in per_source]
    kind_rank = {"tickets": 0, "task-sequence": 1, "stages": 2}
    drift: list[Json] = [{"ticket": k, "kind": "orphan-override", "values": {"stages": v}}
                         for k, v in sorted(orphans.items())]
    gate_ids = {t["gate"] for t in merged.values() if t["gate"]}
    for tid, t in merged.items():
        votes = dict(sorted(stage_votes.get(tid, {}).items(), key=lambda kv: kind_rank[kv[0]]))
        values = set(votes.values())
        t["stage"] = next(iter(votes.values()), "NEW")
        t["is_gate"] = bool(t["is_gate"] or tid in gate_ids)
        if len(values) > 1:
            drift.append({"ticket": tid, "kind": "stage-mismatch", "values": votes})
        for v in values - set(STAGES):
            drift.append({"ticket": tid, "kind": "unknown-stage", "values": {"stage": v}})
    return list(merged.values()), sources, drift


def compute_burn(cycles: list[Json], events: list[Json]) -> list[Json]:
    out: list[Json] = []
    for c in cycles:
        moves = [e for e in events if e.get("cycle") == c["id"] and e["from"] != e["to"]]
        latest: dict[str, str | None] = {}
        for e in events:
            if e["ts"] <= c["end"] and e["from"] != e["to"]:
                latest[e["ticket"]] = e["to"]
        out.append({
            "cycle": c["id"],
            "started": len({e["ticket"] for e in moves if e["to"] == "BUILD"}),
            "completed": len({e["ticket"] for e in moves if e["to"] == "COMPLETE"}),
            "open_at_end": sum(1 for s in latest.values() if s and s != "COMPLETE"),
        })
    return out


def short_digest(t: Json) -> str:
    blob = json.dumps(ticket_digest(t), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def staleness(authored: Json | None, tickets: list[Json], prev: Json | None, events: list[Json]) -> Json:
    """Compare the brief's covers hash with the tickets now; name the tickets that changed."""
    if authored is None:
        return {"stale": False, "changed": [], "covered": {}}
    digests = {t["id"]: short_digest(t) for t in tickets}
    if authored["covers"] == covers_hash(tickets):
        return {"stale": False, "changed": [], "covered": digests}
    prev = prev or {}
    snap = prev.get("covered") if (prev.get("authored") or {}).get("covers") == authored["covers"] else None
    if snap:
        changed = sorted(i for i in set(digests) | set(snap) if digests.get(i) != snap.get(i))
    else:
        changed = sorted({e["ticket"] for e in events if e["from"] != e["to"] and e["ts"] > authored["written_at"]})
    return {"stale": True, "changed": changed, "covered": snap or {}}


def build_brief(root: Path, config: Json, tickets: list[Json], prev: Json | None, events: list[Json]) -> Json:
    p = board_paths(root)
    authored = parse_brief(p["brief"]) if p["brief"].exists() else None
    a = authored or {"spec": {}, "proof": {}, "proof_notes": [], "untagged": []}
    for t in tickets:
        if t["id"] in a["spec"]:
            t["intent"], t["intent_tags"] = a["spec"][t["id"]]["text"], a["spec"][t["id"]]["tags"]
    rules = {**DEFAULT_STAGE_RULES, **config.get("stage_rules", {})}
    source = "default" if rules == DEFAULT_STAGE_RULES else "config"
    from_brief = {k: v for k, v in a["proof"].items() if k in STAGES}
    rules.update({k: v["text"] for k, v in from_brief.items()})
    gate_ids = {t["id"] for t in tickets if t["is_gate"]}
    notes = a["proof_notes"] + [{"text": f"{k}: {v['text']}", "tags": v["tags"]}
                                for k, v in a["proof"].items() if k not in STAGES and k not in gate_ids]
    gates = [{
        "id": t["id"], "question": t["intent"] or t["title"], "stage": t["stage"],
        "acceptance": t["acceptance"], "evidence": t["evidence"],
        "met": t["stage"] == "COMPLETE" and bool(t["evidence"]), "note": a["proof"].get(t["id"]),
    } for t in tickets if t["is_gate"]]
    meta = None if authored is None else {"path": ".plan/board/brief.md", **{
        k: authored[k] for k in ("written_at", "written_by", "covers")}}
    return {
        "overview": merge_overview(parse_prd(p["prd"], ".plan/PRD.md"), authored),
        "stage_rules": {s: rules[s] for s in [*STAGES, *rules] if s in rules},
        "stage_rule_tags": {k: v["tags"] for k, v in from_brief.items()},
        "stage_rules_source": "brief" if from_brief else source,
        "gates": gates,
        "proof_notes": notes,
        "authored": meta,
        **staleness(authored, tickets, (prev or {}).get("brief"), events),
        "untagged": a["untagged"],
    }


def upgrade_views(views: Json) -> Json:
    """Prepend the brief views to a config that still holds the original five-view order."""
    if views.get("order") == DEFAULT_VIEWS[3:]:
        return {**views, "order": DEFAULT_VIEWS}
    return views


def plan_refresh(root: Path, today: str, evidence: list[str]) -> tuple[Json, list[Json], Json | None]:
    """Return (board without generated_at, new history events, previous board)."""
    p = board_paths(root)
    config = read_json(p["config"], {})
    cycles = config.get("cycles", [])
    prev = read_json(p["board"], None)
    prev_stage = {t["id"]: t["stage"] for t in prev["tickets"]} if prev else {}
    history = read_history(p["history"])
    tickets, sources, drift = collect(root)
    drifted = {d["ticket"] for d in drift if d["kind"] == "stage-mismatch"}
    cycle = cycle_for(today, cycles)
    new_events: list[Json] = []
    for t in tickets:
        tid = t["id"]
        if tid in drifted:
            t["stage"] = prev_stage.get(tid, t["stage"])
            continue
        if prev_stage.get(tid) != t["stage"]:
            new_events.append({
                "ts": today, "cycle": cycle, "ticket": tid, "from": prev_stage.get(tid),
                "to": t["stage"], "evidence": t["evidence"],
            })
    by_id = {t["id"]: t for t in tickets}
    seen_urls = {(e["ticket"], ev["url"]) for e in history for ev in e.get("evidence", [])}
    for spec in evidence:
        tid, _, rest = spec.partition("=")
        items = parse_evidence([rest])
        if tid not in by_id or not items or (tid, items[0]["url"]) in seen_urls:
            continue
        stage = by_id[tid]["stage"]
        new_events.append({"ts": today, "cycle": cycle, "ticket": tid, "from": stage, "to": stage,
                           "evidence": items})
    events = history + new_events
    for t in tickets:
        urls = {ev["url"] for ev in t["evidence"]}
        for e in events:
            for ev in e.get("evidence", []):
                if e["ticket"] == t["id"] and ev["url"] not in urls:
                    t["evidence"].append(ev)
                    urls.add(ev["url"])
    board = {
        "schema_version": SCHEMA_VERSION,
        "title": config.get("title") or root.resolve().name,
        "sources": sources,
        "cycles": cycles,
        "views": upgrade_views(config.get("views", {"order": DEFAULT_VIEWS})),
        "brief": build_brief(root, config, tickets, prev, events),
        "tickets": tickets,
        "events": events,
        "burn": compute_burn(cycles, events),
        "drift": drift,
    }
    return board, new_events, prev


def strip_generated(board: Json | None) -> Json | None:
    return None if board is None else {k: v for k, v in board.items() if k != "generated_at"}


def warn_brief(brief: Json) -> None:
    if brief["untagged"]:
        print(f"WARN brief_untagged: {len(brief['untagged'])} claim line(s) without a source tag")
    if brief["stale"]:
        print(f"WARN brief_stale: tickets changed since {brief['authored']['written_at']}: "
              f"{', '.join(brief['changed']) or 'unknown'}")


def refresh(root: Path, today: str, stamp: str, evidence: list[str], check: bool, strict: bool = False) -> int:
    p = board_paths(root)
    board, new_events, prev = plan_refresh(root, today, evidence)
    unchanged = not new_events and strip_generated(prev) == board
    warn_brief(board["brief"])
    if check:
        if not unchanged:
            print(f"STALE: board.json differs from sources ({len(new_events)} pending events)")
            return 1
        if board["drift"]:
            for d in board["drift"]:
                print(f"DRIFT: {d['ticket']} {d['kind']} {json.dumps(d['values'])}")
            return 2
        if strict and board["brief"]["stale"]:
            return 3
        print("OK: board.json matches sources")
        return 0
    if unchanged:
        print("No change.")
        return 0
    p["dir"].mkdir(parents=True, exist_ok=True)
    with p["history"].open("a", encoding="utf-8") as fh:
        for e in new_events:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    board = {"schema_version": board["schema_version"], "title": board["title"],
             "generated_at": stamp, **{k: v for k, v in board.items() if k not in ("schema_version", "title")}}
    p["board"].write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {p['board']} ({len(board['tickets'])} tickets, {len(new_events)} new events, "
          f"{len(board['drift'])} drift)")
    return 0


def init(root: Path, today: str, stamp: str) -> int:
    p = board_paths(root)
    p["dir"].mkdir(parents=True, exist_ok=True)
    if not p["config"].exists():
        cfg = {"schema_version": SCHEMA_VERSION, "title": root.resolve().name, "cycles": [],
               "views": {"order": DEFAULT_VIEWS}, "stage_rules": DEFAULT_STAGE_RULES}
        p["config"].write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    p["history"].touch()
    print(f"Config: {p['config']} (add cycles: id, name, start, end as YYYY-MM-DD; edit stage_rules)")
    return refresh(root, today, stamp, [], check=False)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("init", "refresh", "export", "brief-hash"):
        sp = sub.add_parser(name)
        sp.add_argument("--root", type=Path, default=Path.cwd(), help="project root")
        sp.add_argument("--today", help="YYYY-MM-DD; defaults to the local date")
        if name == "refresh":
            sp.add_argument("--check", action="store_true", help="exit 1 if stale, 2 on drift; no writes")
            sp.add_argument("--evidence", action="append", default=[], metavar="ID=LABEL|URL")
            sp.add_argument("--strict-brief", action="store_true", help="with --check, exit 3 if brief.md is stale")
        if name == "export":
            sp.add_argument("--target", choices=sorted(TARGETS), required=True)
            sp.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    root: Path = args.root
    today = args.today or datetime.now().astimezone().date().isoformat()
    stamp = (f"{args.today}T00:00:00Z" if args.today
             else datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
    if args.cmd == "init":
        return init(root, today, stamp)
    if args.cmd == "refresh":
        return refresh(root, today, stamp, args.evidence, args.check, args.strict_brief)
    if args.cmd == "brief-hash":
        print(covers_hash(plan_refresh(root, today, [])[0]["tickets"]))
        return 0
    return export(board_paths(root)["board"], args.target, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
