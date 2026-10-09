import React, { useState } from "react";

type Stage = "NEW" | "BUILD" | "REVIEW" | "BLOCKED" | "COMPLETE";
type Evidence = { label: string; url: string };
type Acceptance = { text: string; checked?: boolean };
type Ticket = {
  id: string; title: string; stage: Stage; deps: string[]; gate: string | null;
  is_gate: boolean; owner: string | null; note: string | null; evidence: Evidence[];
  intent?: string | null; intent_tags?: string[]; acceptance?: Acceptance[];
};
type Claim = { text: string; tags: string[] };
type Overview = { title: string; goal: Claim[]; non_goals: Claim[]; constraints: Claim[]; source: string };
type GateProof = {
  id: string; question: string; stage: Stage; acceptance: Acceptance[]; evidence: Evidence[]; met: boolean;
  note?: Claim | null;
};
type Authored = { path: string; written_at: string; written_by: string; covers: string };
type Brief = {
  overview: Overview | null; stage_rules: Record<string, string>; stage_rule_tags?: Record<string, string[]>;
  stage_rules_source: "config" | "default" | "brief"; gates: GateProof[]; proof_notes?: Claim[];
  authored?: Authored | null; stale?: boolean; changed?: string[]; covered?: Record<string, string>;
  untagged?: string[];
};
type Cycle = { id: string; name: string; start: string; end: string };
type BoardEvent = {
  ts: string; cycle: string | null; ticket: string; from: Stage | null; to: Stage; evidence: Evidence[];
};
type Burn = { cycle: string; started: number; completed: number; open_at_end: number };
type Drift = { ticket: string; kind: string; values: Record<string, string> };
type Board = {
  schema_version: number; title: string; generated_at: string;
  sources: { kind: string; path: string; count: number }[];
  cycles: Cycle[]; views: { order: string[] }; brief?: Brief; tickets: Ticket[]; events: BoardEvent[];
  burn: Burn[]; drift: Drift[];
};

const BOARD: Board = __TRACKBOARD_DATA__;

const STAGES: Stage[] = ["NEW", "BUILD", "REVIEW", "BLOCKED", "COMPLETE"];
const STAGE_COLOR: Record<Stage, string> = {
  NEW: "#7a7a85", BUILD: "#2f6fcf", REVIEW: "#b07210", BLOCKED: "#c0392b", COMPLETE: "#23855a",
};
const ink = { fg: "#1d1d1f", muted: "#6b6b73", line: "#dedee3", fill: "#f4f4f6", bg: "#ffffff" };
const page: React.CSSProperties = {
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  fontSize: 14, lineHeight: "20px", color: ink.fg, background: ink.bg, padding: 20, maxWidth: 1100,
};
const th: React.CSSProperties = {
  textAlign: "left", fontSize: 12, color: ink.muted, fontWeight: 600, padding: "6px 8px",
  borderBottom: `1px solid ${ink.line}`,
};
const td: React.CSSProperties = { padding: "6px 8px", borderBottom: `1px solid ${ink.line}`, verticalAlign: "top" };

function StagePill({ stage }: { stage: Stage | null }) {
  if (!stage) return <span style={{ color: ink.muted }}>(new)</span>;
  return (
    <span style={{
      display: "inline-block", padding: "0 8px", borderRadius: 999, fontSize: 12,
      border: `1px solid ${ink.line}`, background: ink.fill, color: STAGE_COLOR[stage], whiteSpace: "nowrap",
    }}>{stage}</span>
  );
}

function Links({ items }: { items: Evidence[] }) {
  return (
    <>
      {items.map((e, i) => (
        <span key={e.url}>
          {i > 0 ? ", " : ""}
          <a href={/^https?:\/\//.test(e.url) ? e.url : "#"} target="_blank" rel="noopener noreferrer"
            style={{ color: STAGE_COLOR.BUILD }}>{e.label}</a>
        </span>
      ))}
    </>
  );
}

function Table({ headers, rows }: { headers: string[]; rows: React.ReactNode[][] }) {
  return (
    <table style={{ borderCollapse: "collapse", width: "100%" }}>
      <thead><tr>{headers.map((h) => <th key={h} style={th}>{h}</th>)}</tr></thead>
      <tbody>
        {rows.map((r, i) => <tr key={i}>{r.map((c, j) => <td key={j} style={td}>{c}</td>)}</tr>)}
      </tbody>
    </table>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginTop: 24 }}>
      <h2 style={{ fontSize: 16, margin: "0 0 10px" }}>{title}</h2>
      {children}
    </section>
  );
}

function Dag({ tickets }: { tickets: Ticket[] }) {
  const ids = new Map(tickets.map((t) => [t.id, t]));
  const rank = new Map<string, number>();
  const rankOf = (id: string, seen: Set<string>): number => {
    const known = rank.get(id);
    if (known !== undefined) return known;
    if (seen.has(id)) return 0;
    seen.add(id);
    const t = ids.get(id);
    const r = t ? Math.max(0, ...t.deps.filter((d) => ids.has(d)).map((d) => rankOf(d, seen) + 1)) : 0;
    rank.set(id, r);
    return r;
  };
  tickets.forEach((t) => rankOf(t.id, new Set()));
  const cols = new Map<number, string[]>();
  tickets.forEach((t) => {
    const r = rank.get(t.id) ?? 0;
    cols.set(r, [...(cols.get(r) ?? []), t.id]);
  });
  const W = 150, H = 34, GX = 50, GY = 14;
  const pos = new Map<string, { x: number; y: number }>();
  cols.forEach((list, r) => list.forEach((id, i) => pos.set(id, { x: r * (W + GX) + 8, y: i * (H + GY) + 8 })));
  const width = cols.size * (W + GX);
  const height = Math.max(...Array.from(cols.values()).map((l) => l.length)) * (H + GY) + 8;
  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        {tickets.flatMap((t) => t.deps.filter((d) => pos.has(d)).map((d) => {
          const a = pos.get(d)!, b = pos.get(t.id)!;
          return <line key={`${d}-${t.id}`} x1={a.x + W} y1={a.y + H / 2} x2={b.x} y2={b.y + H / 2}
            stroke={ink.line} strokeWidth={1.5} />;
        }))}
        {tickets.map((t) => {
          const p = pos.get(t.id)!;
          return (
            <g key={t.id}>
              <title>{t.title}</title>
              <rect x={p.x} y={p.y} width={W} height={H} rx={6} fill={ink.fill}
                stroke={STAGE_COLOR[t.stage]} strokeWidth={t.is_gate ? 2.5 : 1.5} />
              <text x={p.x + 8} y={p.y + 21} fontSize={11} fill={ink.fg}>{`${t.id}  ${t.stage}`}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function Tags({ tags }: { tags?: string[] }) {
  if (!tags || tags.length === 0) return null;
  return (
    <>
      {tags.map((t) => (
        <span key={t} style={{
          marginLeft: 6, padding: "0 6px", borderRadius: 999, fontSize: 11, color: ink.muted,
          border: `1px solid ${ink.line}`, whiteSpace: "nowrap",
        }}>{t}</span>
      ))}
    </>
  );
}

function briefNotice(b: Board): string | null {
  const a = b.brief?.authored;
  if (!a) return null;
  const by = a.written_by || "unknown";
  if (!b.brief?.stale) return `Brief written ${a.written_at} by ${by}.`;
  const changed = b.brief?.changed ?? [];
  const what = changed.length
    ? `${changed.length} ticket${changed.length === 1 ? "" : "s"} changed since (${changed.join(", ")})`
    : "sources changed since";
  return `Brief written ${a.written_at}; ${what}. Written by ${by}.`;
}

function AcList({ items }: { items: Acceptance[] }) {
  const [open, setOpen] = useState(false);
  if (items.length === 0) return null;
  const shown = open ? items : items.slice(0, 3);
  return (
    <ul style={{ margin: "4px 0 0", paddingLeft: 0, listStyle: "none", fontSize: 13 }}>
      {shown.map((a) => (
        <li key={a.text} style={{ color: a.checked ? ink.muted : ink.fg }}>
          {a.checked === undefined ? "\u2022 " : a.checked ? "[x] " : "[ ] "}{a.text}
        </li>
      ))}
      {items.length > 3 && (
        <li>
          <button onClick={() => setOpen(!open)} style={{
            border: "none", background: "none", padding: 0, color: STAGE_COLOR.BUILD, cursor: "pointer", fontSize: 12,
          }}>{open ? "Show fewer" : `${items.length - 3} more`}</button>
        </li>
      )}
    </ul>
  );
}

function BriefViews({ b }: { b: Board }) {
  const ov = b.brief?.overview;
  const specced = b.tickets.filter((t) => (t.acceptance ?? []).length > 0 || t.intent);
  const rules = STAGES.filter((s) => b.brief?.stage_rules[s]);
  const gates = b.brief?.gates ?? [];
  const label: React.CSSProperties = { fontSize: 12, fontWeight: 600, color: ink.muted, marginTop: 8 };
  return (
    <>
      {ov && (
        <Section title={ov.title ? `What we are building: ${ov.title}` : "What we are building"}>
          {ov.goal.length > 0 && (
            <p style={{ margin: "0 0 8px" }}>
              {ov.goal.map((c) => <span key={c.text}>{c.text}<Tags tags={c.tags} />{" "}</span>)}
            </p>
          )}
          {([["Not building", ov.non_goals], ["Constraints", ov.constraints]] as const)
            .filter(([, xs]) => xs.length > 0).map(([name, xs]) => (
              <div key={name}>
                <div style={label}>{name}</div>
                <ul style={{ margin: "4px 0", paddingLeft: 18 }}>
                  {xs.map((x) => <li key={x.text}>{x.text}<Tags tags={x.tags} /></li>)}
                </ul>
              </div>
            ))}
          <div style={{ fontSize: 12, color: ink.muted }}>Source: {ov.source}</div>
        </Section>
      )}
      {specced.length > 0 && (
        <Section title="What defines done for each ticket">
          {STAGES.filter((s) => specced.some((t) => t.stage === s)).map((s) => (
            <div key={s} style={{ marginBottom: 10 }}>
              <div style={label}>{s}</div>
              {specced.filter((t) => t.stage === s).map((t) => (
                <div key={t.id} style={{ margin: "6px 0 10px" }}>
                  <b>{t.id} {t.title}</b>
                  {t.intent && <div style={{ fontSize: 13, color: ink.muted }}>{t.intent}<Tags tags={t.intent_tags} /></div>}
                  <AcList items={t.acceptance ?? []} />
                </div>
              ))}
            </div>
          ))}
        </Section>
      )}
      {(rules.length > 0 || gates.length > 0) && (
        <Section title="What proves each stage">
          {rules.length > 0 && (
            <Table headers={["Stage", "Exit rule"]}
              rows={rules.map((s) => [<StagePill stage={s} />,
                <span>{b.brief?.stage_rules[s]}<Tags tags={b.brief?.stage_rule_tags?.[s]} /></span>])} />
          )}
          {b.brief?.stage_rules_source === "default" && (
            <div style={{ fontSize: 12, color: ink.muted, marginTop: 4 }}>
              Generic defaults. Set stage_rules in .plan/board/config.json to replace them.
            </div>
          )}
          {(b.brief?.proof_notes ?? []).length > 0 && (
            <ul style={{ margin: "8px 0", paddingLeft: 18 }}>
              {(b.brief?.proof_notes ?? []).map((c) => <li key={c.text}>{c.text}<Tags tags={c.tags} /></li>)}
            </ul>
          )}
          {gates.map((g) => (
            <div key={g.id} style={{ border: `1px solid ${ink.line}`, borderRadius: 6, padding: 10, marginTop: 10 }}>
              <div>
                <b>{g.id}</b> <span style={{ color: g.met ? STAGE_COLOR.COMPLETE : STAGE_COLOR.REVIEW }}>
                  {g.met ? "Met" : "Not met"}
                </span>
              </div>
              <div>{g.question}</div>
              {g.note && <div style={{ fontSize: 13 }}>{g.note.text}<Tags tags={g.note.tags} /></div>}
              <AcList items={g.acceptance} />
              {g.evidence.length > 0 && <div style={{ fontSize: 13 }}>Evidence: <Links items={g.evidence} /></div>}
            </div>
          ))}
        </Section>
      )}
    </>
  );
}

export default function Trackboard() {
  const b = BOARD;
  const hasBrief = Boolean(b.brief?.overview) || b.tickets.some((t) => (t.acceptance ?? []).length > 0 || t.intent)
    || Object.keys(b.brief?.stage_rules ?? {}).length > 0;
  const [tab, setTab] = useState<"brief" | "tracking">(hasBrief ? "brief" : "tracking");
  const [stageFilter, setStageFilter] = useState<Stage | null>(null);
  const names = new Map(b.cycles.map((c) => [c.id, c.name || c.id]));
  const now = b.tickets.filter((t) => t.stage === "BUILD" || t.stage === "REVIEW" || t.stage === "BLOCKED");
  const moves = [...b.events].reverse().filter((e) => e.from !== e.to || e.evidence.length > 0);
  const gates = b.tickets.filter((t) => t.is_gate);
  const hasEdges = b.tickets.some((t) => t.deps.some((d) => b.tickets.some((x) => x.id === d)));
  const shown = stageFilter ? b.tickets.filter((t) => t.stage === stageFilter) : b.tickets;
  const cycleKeys = Array.from(new Set(moves.map((e) => e.cycle ?? "")));

  return (
    <div style={page}>
      <h1 style={{ fontSize: 22, margin: "0 0 4px" }}>{b.title}</h1>
      <div style={{ fontSize: 12, color: ink.muted }}>
        Generated {b.generated_at} from {b.sources.map((s) => s.path).join(", ")}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", margin: "14px 0" }}>
        {STAGES.filter((s) => b.tickets.some((t) => t.stage === s)).map((s) => (
          <button key={s} onClick={() => setStageFilter(stageFilter === s ? null : s)} style={{
            border: `1px solid ${stageFilter === s ? STAGE_COLOR[s] : ink.line}`, background: ink.fill,
            borderRadius: 6, padding: "4px 10px", cursor: "pointer", color: ink.fg, fontSize: 13,
          }}>
            <b style={{ color: STAGE_COLOR[s] }}>{b.tickets.filter((t) => t.stage === s).length}</b> {s}
          </button>
        ))}
      </div>
      {briefNotice(b) && (
        <div style={{ fontSize: 12, color: ink.muted, marginTop: 8 }}>{briefNotice(b)}</div>
      )}
      {b.drift.length > 0 && (
        <div style={{ border: `1px solid ${STAGE_COLOR.BLOCKED}`, borderRadius: 6, padding: "10px 12px" }}>
          <b>Drift: sources disagree</b>
          {b.drift.map((d) => <div key={d.ticket + d.kind}>{d.ticket} {d.kind} {JSON.stringify(d.values)}</div>)}
        </div>
      )}
      {hasBrief && (
        <div style={{ display: "flex", gap: 6, marginTop: 14 }}>
          {(["brief", "tracking"] as const).map((k) => (
            <button key={k} onClick={() => setTab(k)} style={{
              border: `1px solid ${tab === k ? ink.fg : ink.line}`, background: tab === k ? ink.fill : ink.bg,
              borderRadius: 999, padding: "2px 12px", cursor: "pointer", color: ink.fg, fontSize: 13,
            }}>{k === "brief" ? "Brief" : "Tracking"}</button>
          ))}
        </div>
      )}
      {tab === "brief" && <BriefViews b={b} />}
      {tab === "tracking" && now.length > 0 && (
        <Section title="Now">
          <Table headers={["ID", "Title", "Stage", "Owner", "Note"]}
            rows={now.map((t) => [t.id, t.title, <StagePill stage={t.stage} />, t.owner, t.note])} />
        </Section>
      )}
      {tab === "tracking" && moves.length > 0 && (
        <Section title="Timeline by cycle">
          {cycleKeys.map((k) => (
            <div key={k} style={{ marginBottom: 12 }}>
              <div style={{ fontSize: 12, color: ink.muted, margin: "6px 0" }}>
                {k ? names.get(k) ?? k : "Outside any cycle"}
              </div>
              <Table headers={["Date", "Ticket", "Change", "Evidence"]}
                rows={moves.filter((e) => (e.cycle ?? "") === k).map((e) => [
                  e.ts, e.ticket,
                  e.from === e.to ? "evidence" : <span><StagePill stage={e.from} /> to <StagePill stage={e.to} /></span>,
                  <Links items={e.evidence} />,
                ])} />
            </div>
          ))}
        </Section>
      )}
      {tab === "tracking" && hasEdges && <Section title="Dependency graph"><Dag tickets={b.tickets} /></Section>}
      {tab === "tracking" && gates.length > 0 && (
        <Section title="Gates and evidence">
          <Table headers={["Gate", "Stage", "Feeds", "Evidence"]} rows={gates.map((g) => {
            const feeds = b.tickets.filter((t) => t.gate === g.id);
            const list = feeds.length ? feeds : b.tickets.filter((t) => g.deps.includes(t.id));
            return [`${g.id} ${g.title}`, <StagePill stage={g.stage} />,
              list.map((f) => `${f.id} ${f.stage === "COMPLETE" ? "done" : "open"}`).join(", "),
              <Links items={g.evidence} />];
          })} />
        </Section>
      )}
      {tab === "tracking" && b.burn.length > 0 && (
        <Section title="Burn by cycle">
          {b.burn.map((c) => {
            const total = Math.max(1, c.completed + c.open_at_end);
            return (
              <div key={c.cycle} style={{ marginBottom: 12 }}>
                <div>{names.get(c.cycle) ?? c.cycle}
                  <span style={{ fontSize: 12, color: ink.muted }}>
                    {`  started ${c.started}, completed ${c.completed}, open at end ${c.open_at_end}`}
                  </span>
                </div>
                <div style={{ display: "flex", height: 10, borderRadius: 5, overflow: "hidden", background: ink.fill }}>
                  <div style={{ width: `${(100 * c.completed) / total}%`, background: STAGE_COLOR.COMPLETE }} />
                  <div style={{ width: `${(100 * c.open_at_end) / total}%`, background: STAGE_COLOR.BUILD, opacity: 0.35 }} />
                </div>
              </div>
            );
          })}
        </Section>
      )}
      {tab === "tracking" && (
      <Section title={stageFilter ? `Tickets in ${stageFilter}` : "All tickets"}>
        <Table headers={["ID", "Title", "Stage", "Deps", "Gate"]}
          rows={shown.map((t) => [t.id, t.title, <StagePill stage={t.stage} />, t.deps.join(", "), t.gate])} />
      </Section>
      )}
    </div>
  );
}
