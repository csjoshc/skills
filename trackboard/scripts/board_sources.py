"""Read ticket state and brief content from files that other skills own. Never writes."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

Json = dict[str, Any]

STAGES = ("NEW", "BUILD", "REVIEW", "BLOCKED", "COMPLETE")
DEFAULT_STAGE_RULES = {
    "NEW": "Ticket has a goal and acceptance criteria.",
    "BUILD": "Tests written and failing.",
    "REVIEW": "Tests pass, PR open, CI green.",
    "BLOCKED": "Blocker named, with who or what clears it.",
    "COMPLETE": "PR merged and evidence linked.",
}
STAGE_ALIASES = {
    "NEW": ("NEW", "TODO", "OPEN", "BACKLOG", "SPEC", "SPEC_SPLIT", "PLAN", "PLANNED", "READY"),
    "BUILD": ("BUILD", "IN_PROGRESS", "DOING", "WIP", "ACTIVE", "STARTED"),
    "REVIEW": ("REVIEW", "IN_REVIEW", "VERIFY", "QA"),
    "BLOCKED": ("BLOCKED", "FAILED", "ON_HOLD"),
    "COMPLETE": ("COMPLETE", "COMPLETED", "DONE", "MERGED", "CLOSED", "PASSED"),
}
ALIAS_TO_STAGE = {alias: stage for stage, aliases in STAGE_ALIASES.items() for alias in aliases}
KEY_ALIASES = {
    "id": ("id", "ticket", "ticket_id", "key"),
    "title": ("title", "name", "summary"),
    "stage": ("stage", "status"),
    "deps": ("depends_on", "deps", "depends", "dependencies", "blocked_by"),
    "gate": ("gate", "gate_id"),
    "owner": ("owner", "assignee"),
    "note": ("note", "notes"),
    "evidence": ("evidence",),
}
EMPTY_CELLS = {"", "-", "—", "–", "none", "n/a", "null", "[]"}
GOAL_RE = re.compile(r"goal|problem|summary|overview", re.IGNORECASE)
NON_GOAL_RE = re.compile(r"non-goals?|out of scope", re.IGNORECASE)
CONSTRAINT_RE = re.compile(r"constraints|principles", re.IGNORECASE)
AC_RE = re.compile(r"acceptance|\bACs?\b|done when", re.IGNORECASE)
BULLET_RE = re.compile(r"^\s{0,3}(?:[-*+]|\d+[.)])\s+(.*)$")
CHECK_RE = re.compile(r"^\[([ xX])\]\s+(.*)$")
SEQ_AC_RE = re.compile(r"^\s*[-*]\s+(?:\[([ xX])\]\s+)?AC:\s*(.+)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
BOLD_HEADING_RE = re.compile(r"^\*\*([^*]+?):?\*\*:?\s*$")
TAG_TAIL_RE = re.compile(r"(?:\s*\[[^\[\]]+\])+\s*$")
KEYED_RE = re.compile(r"^([A-Z][A-Z0-9_-]*):\s+(.*)$")
BRIEF_SECTIONS = {"building": "building", "not building": "not_building", "spec": "spec", "proof": "proof"}


def normalize_stage(raw: str) -> str:
    key = re.sub(r"[\s-]+", "_", raw.strip().upper())
    return ALIAS_TO_STAGE.get(key, key)


def norm_key(raw: str) -> str:
    return re.sub(r"[\s-]+", "_", raw.strip().lower())


def canonical(key: str) -> str | None:
    k = norm_key(key)
    return next((field for field, aliases in KEY_ALIASES.items() if k in aliases), None)


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def split_ids(value: str) -> list[str]:
    parts = [unquote(p) for p in re.split(r"[,\s]+", value.strip().strip("[]"))]
    return [p for p in parts if p.lower() not in EMPTY_CELLS]


def clean_inline(text: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"\s+", " ", text.replace("**", "").replace("__", "")).strip()


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rsplit(" ", 1)[0].rstrip(",;:") + "..."


def parse_evidence(items: list[str]) -> list[Json]:
    out: list[Json] = []
    for item in items:
        label, _, url = item.rpartition("|")
        if url.strip():
            out.append({"label": label.strip() or url.strip(), "url": url.strip()})
    return out


def split_frontmatter(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:i], lines[i + 1:]
    return lines[1:], []


def parse_frontmatter(lines: list[str]) -> dict[str, str | list[str]]:
    data: dict[str, str | list[str]] = {}
    key: str | None = None
    for line in lines:
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and key is not None:
            current = data.get(key)
            data[key] = [*(current if isinstance(current, list) else []), unquote(item.group(1))]
            continue
        kv = re.match(r"^([A-Za-z][\w -]*):\s*(.*)$", line)
        if kv:
            key, value = norm_key(kv.group(1)), kv.group(2).strip()
            data[key] = split_ids(value) if value.startswith("[") and value.endswith("]") else unquote(value)
    return data


def sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    """Split markdown into (heading, body lines); a whole-line bold label counts as a heading."""
    out: list[tuple[str, list[str]]] = [("", [])]
    fenced = False
    for line in lines:
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        h = HEADING_RE.match(line) or BOLD_HEADING_RE.match(line.strip())
        if h:
            out.append((h.group(h.lastindex or 1).strip(), []))
        else:
            out[-1][1].append(line)
    return out


def first_paragraph(lines: list[str]) -> str | None:
    block: list[str] = []
    for line in lines:
        s = line.strip()
        plain = s and not (BULLET_RE.match(line) or BOLD_HEADING_RE.match(s)
                           or s.startswith(("|", ">", "<!--", "#", "```")))
        if plain:
            block.append(s)
        elif block:
            break
    return clean_inline(" ".join(block)) if block else None


def bullets(lines: list[str], limit: int, width: int) -> list[str]:
    items = [clean_inline(m.group(1)) for m in map(BULLET_RE.match, lines) if m]
    return [truncate(i, width) for i in items if i][:limit]


def acceptance_items(lines: list[str]) -> list[Json]:
    out: list[Json] = []
    for m in filter(None, map(BULLET_RE.match, lines)):
        text, check = m.group(1), CHECK_RE.match(m.group(1))
        item: Json = {"text": truncate(clean_inline(check.group(2) if check else text), 200)}
        if check:
            item["checked"] = check.group(1) != " "
        if item["text"]:
            out.append(item)
    return out


def blank_ticket(tid: str) -> Json:
    return {
        "id": tid, "title": tid, "stage": "NEW", "deps": [], "gate": None, "is_gate": False,
        "owner": None, "note": None, "evidence": [], "intent": None, "intent_tags": [], "acceptance": [],
    }


def gate_fields(raw: str) -> tuple[str | None, bool]:
    low = raw.strip().lower()
    if low in ("true", "yes"):
        return None, True
    if low in EMPTY_CELLS or low in ("false", "no"):
        return None, False
    return raw.strip(), False


def pick(fm: dict[str, str | list[str]], field: str) -> str | list[str] | None:
    return next((fm[a] for a in KEY_ALIASES[field] if a in fm), None)


def as_text(value: str | list[str] | None) -> str:
    return ", ".join(value) if isinstance(value, list) else (value or "")


def as_list(value: str | list[str] | None, raw: bool = False) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value] if raw else split_ids(value)


def parse_ticket_file(path: Path) -> Json:
    fm_lines, body = split_frontmatter(path.read_text(encoding="utf-8"))
    fm = parse_frontmatter(fm_lines)
    tid = as_text(pick(fm, "id")) or path.stem
    t = blank_ticket(tid)
    h1 = next((ln[2:].strip() for ln in body if ln.startswith("# ")), "")
    t["title"] = as_text(pick(fm, "title")) or h1 or tid
    stage = as_text(pick(fm, "stage"))
    t["stage"] = normalize_stage(stage) if stage else None
    t["deps"] = as_list(pick(fm, "deps"))
    t["gate"], t["is_gate"] = gate_fields(as_text(pick(fm, "gate")))
    t["owner"] = as_text(pick(fm, "owner")) or None
    t["note"] = as_text(pick(fm, "note")) or None
    t["evidence"] = parse_evidence(as_list(pick(fm, "evidence"), raw=True))
    intent = first_paragraph(body)
    t["intent"] = truncate(intent, 200) if intent else None
    for heading, lines in sections(body):
        if heading and AC_RE.search(heading):
            t["acceptance"] = acceptance_items(lines)
            break
    return t


def parse_task_sequence(path: Path) -> list[Json]:
    """Rows of the first markdown table that has an ID/Ticket column."""
    rows = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    for i in range(len(rows) - 1):
        if not (rows[i].startswith("|") and re.match(r"^\|?\s*:?-{3,}", rows[i + 1])):
            continue
        headers = [canonical(clean_inline(h.replace("`", ""))) for h in rows[i].strip("|").split("|")]
        if "id" not in headers:
            continue
        out: list[Json] = []
        for row in rows[i + 2:]:
            if not row.startswith("|"):
                break
            cells = [clean_inline(c.replace("`", "")) for c in row.strip("|").split("|")]
            rec = {h: cells[j] for j, h in enumerate(headers) if h and j < len(cells)}
            if not rec.get("id"):
                continue
            t = blank_ticket(rec["id"])
            t["title"] = rec.get("title") or rec["id"]
            stage = rec.get("stage", "")
            t["stage"] = normalize_stage(stage) if stage.lower() not in EMPTY_CELLS else None
            t["deps"] = split_ids(rec.get("deps", ""))
            t["gate"], t["is_gate"] = gate_fields(rec.get("gate", ""))
            t["owner"] = rec.get("owner") or None
            out.append(t)
        return out
    return []


def parse_sequence_acs(path: Path, ids: list[str]) -> dict[str, list[Json]]:
    """`- AC: ...` lines grouped under the ticket ids named in the nearest heading above them."""
    out: dict[str, list[Json]] = {}
    current: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        h = HEADING_RE.match(line)
        if h:
            current = [i for i in ids if re.search(rf"(?<![\w-]){re.escape(i)}(?![\w-])", h.group(2))]
            continue
        m = SEQ_AC_RE.match(line)
        if not m:
            continue
        for tid in current:
            item: Json = {"text": truncate(clean_inline(m.group(2)), 200)}
            if m.group(1):
                item["checked"] = m.group(1) != " "
            out.setdefault(tid, []).append(item)
    return out


def parse_stages_override(board_dir: Path) -> dict[str, str]:
    """Flat `ID: STAGE` lines from stages.yaml, or a flat object in stages.json."""
    yml, js = board_dir / "stages.yaml", board_dir / "stages.json"
    if js.exists():
        return {str(k): normalize_stage(str(v)) for k, v in json.loads(js.read_text()).items()}
    if not yml.exists():
        return {}
    out: dict[str, str] = {}
    for line in yml.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" in line:
            k, v = line.split(":", 1)
            if v.strip():
                out[unquote(k)] = normalize_stage(unquote(v))
    return out


def parse_prd(path: Path, source: str) -> Json | None:
    """Title, goal and short lists from a PRD; None when the file is absent."""
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    title = next((ln[2:].strip() for ln in lines if ln.startswith("# ")), "")
    secs = sections(lines)
    goal_sec = next((b for h, b in secs if GOAL_RE.search(h) and not NON_GOAL_RE.search(h)), None)
    para = (first_paragraph(goal_sec) if goal_sec else None) or first_paragraph(
        [ln for _, b in secs for ln in b])
    goal = " ".join(re.split(r"(?<=[.!?])\s+", para)[:3]) if para else ""

    def listed(rx: re.Pattern[str]) -> list[str]:
        return next((bullets(b, 5, 160) for h, b in secs if rx.search(h)), [])

    def claims(items: list[str]) -> list[Json]:
        return [{"text": x, "tags": ["PRD"]} for x in items if x]

    return {
        "title": clean_inline(title), "goal": claims([truncate(goal, 300)]),
        "non_goals": claims(listed(NON_GOAL_RE)), "constraints": claims(listed(CONSTRAINT_RE)), "source": source,
    }


def parse_claim(line: str) -> tuple[Json | None, bool]:
    """Return ({text, tags}, tagged) for one brief line; None for a blank or comment line."""
    s = line.strip()
    if not s or s.startswith("<!--"):
        return None, False
    m = BULLET_RE.match(line)
    s = m.group(1).strip() if m else s
    tail = TAG_TAIL_RE.search(s)
    tags = re.findall(r"\[([^\[\]]+)\]", tail.group(0)) if tail else []
    text = truncate(clean_inline(s[: tail.start()] if tail else s), 300)
    return ({"text": text, "tags": [t.strip() for t in tags]} if text else None), bool(tags)


def parse_brief(path: Path) -> Json:
    """Sections, claims and frontmatter of an agent-written brief.md."""
    fm_lines, body = split_frontmatter(path.read_text(encoding="utf-8"))
    fm = parse_frontmatter(fm_lines)
    out: Json = {"written_at": as_text(fm.get("written_at")), "written_by": as_text(fm.get("written_by")),
                 "covers": as_text(fm.get("covers")), "sections": [], "building": [], "not_building": [],
                 "spec": {}, "proof": {}, "proof_notes": [], "untagged": []}
    for heading, lines in sections(body):
        key = BRIEF_SECTIONS.get(heading.strip().lower())
        if not key:
            continue
        out["sections"].append(key)
        for line in lines:
            claim, tagged = parse_claim(line)
            if claim is None:
                continue
            if key != "spec" and not tagged:
                out["untagged"].append(claim["text"])
            keyed = KEYED_RE.match(claim["text"]) if key in ("spec", "proof") else None
            if keyed:
                out[key][keyed.group(1)] = {"text": keyed.group(2), "tags": claim["tags"]}
            elif key == "proof":
                out["proof_notes"].append(claim)
            elif key != "spec":
                out[key].append(claim)
    return out


def ticket_digest(t: Json) -> list[Any]:
    return [t["id"], t["stage"], [a["text"] for a in t["acceptance"]]]


def covers_hash(tickets: list[Json]) -> str:
    """sha256 over compact JSON of [id, stage, [AC texts]] per ticket, sorted by id."""
    rows = sorted((ticket_digest(t) for t in tickets), key=lambda r: str(r[0]))
    blob = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def merge_overview(prd: Json | None, authored: Json | None) -> Json | None:
    """Brief sections win per section; PRD extraction fills the rest. None when neither has content."""
    a = authored or {"building": [], "not_building": []}
    if prd is None and not (a["building"] or a["not_building"]):
        return None
    srcs = [".plan/board/brief.md"] if a["building"] or a["not_building"] else []
    return {
        "title": prd["title"] if prd else "",
        "goal": a["building"] or (prd["goal"] if prd else []),
        "non_goals": a["not_building"] or (prd["non_goals"] if prd else []),
        "constraints": prd["constraints"] if prd else [],
        "source": ", ".join(srcs + ([prd["source"]] if prd else [])),
    }
