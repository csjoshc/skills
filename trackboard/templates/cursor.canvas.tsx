import {
  BarChart, Callout, Card, CardBody, CardHeader, CollapsibleSection, Grid, H1, H2, H3, Pill, Row, Stack, Stat,
  Table, Text, computeDAGLayout, useHostTheme, useState,
} from "cursor/canvas";
import type { TableRowTone } from "cursor/canvas";

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
const TONE: Record<Stage, TableRowTone> = {
  NEW: "neutral", BUILD: "info", REVIEW: "warning", BLOCKED: "danger", COMPLETE: "success",
};
const VIEW_LABEL: Record<string, string> = {
  overview: "Overview", spec: "Spec", proof: "Proof",
  now: "Now", timeline: "Timeline", dag: "Graph", gates: "Gates", burn: "Burn",
};
const GROUPS: { id: string; label: string; views: string[] }[] = [
  { id: "brief", label: "Brief", views: ["overview", "spec", "proof"] },
  { id: "tracking", label: "Tracking", views: ["now", "timeline", "dag", "gates", "burn"] },
];
const ticketById = new Map(BOARD.tickets.map((t) => [t.id, t]));
const cycleName = new Map(BOARD.cycles.map((c) => [c.id, c.name || c.id]));
const specced = BOARD.tickets.filter((t) => (t.acceptance ?? []).length > 0 || t.intent);

function evidenceText(items: Evidence[]): string {
  return items.map((e) => `[${e.label}](${e.url})`).join(", ");
}

function Tags({ tags }: { tags?: string[] }) {
  const theme = useHostTheme();
  if (!tags || tags.length === 0) return null;
  return (
    <>
      {tags.map((t) => (
        <span key={t} style={{
          marginLeft: 6, padding: "0 6px", borderRadius: 999, fontSize: 11, lineHeight: "16px",
          color: theme.text.tertiary, border: `1px solid ${theme.stroke.tertiary}`, whiteSpace: "nowrap",
        }}>{t}</span>
      ))}
    </>
  );
}

function ClaimText({ claim, size }: { claim: Claim; size?: "small" }) {
  return <Text size={size}>{claim.text}<Tags tags={claim.tags} /></Text>;
}

function Bullets({ items }: { items: Claim[] }) {
  const theme = useHostTheme();
  return (
    <ul style={{ margin: 0, paddingLeft: 18, color: theme.text.primary, fontSize: 14, lineHeight: "20px" }}>
      {items.map((x) => <li key={x.text}>{x.text}<Tags tags={x.tags} /></li>)}
    </ul>
  );
}

function briefNotice(): string | null {
  const a = BOARD.brief?.authored;
  if (!a) return null;
  const by = a.written_by || "unknown";
  if (!BOARD.brief?.stale) return `Brief written ${a.written_at} by ${by}.`;
  const changed = BOARD.brief?.changed ?? [];
  const what = changed.length
    ? `${changed.length} ticket${changed.length === 1 ? "" : "s"} changed since (${changed.join(", ")})`
    : "sources changed since";
  return `Brief written ${a.written_at}; ${what}. Written by ${by}.`;
}

function AcItem({ item }: { item: Acceptance }) {
  const theme = useHostTheme();
  const box = item.checked === undefined ? (
    <circle cx={6} cy={8} r={2.5} fill={theme.text.tertiary} />
  ) : (
    <>
      <rect x={1} y={3} width={10} height={10} rx={2} fill="none" stroke={theme.stroke.primary} />
      {item.checked && <path d="M3.5 8 L5.5 10 L9 5.5" fill="none" stroke={theme.category.green} strokeWidth={1.6} />}
    </>
  );
  return (
    <Row gap={6} align="start">
      <svg width={12} height={16} style={{ flexShrink: 0 }}>{box}</svg>
      <Text size="small" tone={item.checked ? "secondary" : "primary"}>{item.text}</Text>
    </Row>
  );
}

function AcList({ items }: { items: Acceptance[] }) {
  if (items.length === 0) return null;
  const head = items.slice(0, 3);
  const rest = items.slice(3);
  return (
    <Stack gap={2}>
      {head.map((a) => <AcItem key={a.text} item={a} />)}
      {rest.length > 0 && (
        <CollapsibleSection title="More criteria" count={rest.length}>
          <Stack gap={2}>{rest.map((a) => <AcItem key={a.text} item={a} />)}</Stack>
        </CollapsibleSection>
      )}
    </Stack>
  );
}

function OverviewView() {
  const ov = BOARD.brief?.overview;
  if (!ov) return null;
  const lists = [
    { label: "Not building", items: ov.non_goals },
    { label: "Constraints", items: ov.constraints },
  ].filter((l) => l.items.length > 0);
  return (
    <Stack gap={10}>
      <H2>{ov.title ? `What we are building: ${ov.title}` : "What we are building"}</H2>
      {ov.goal.length > 0 && <Stack gap={4}>{ov.goal.map((c) => <ClaimText key={c.text} claim={c} />)}</Stack>}
      {lists.length > 0 && (
        <Grid columns={lists.length} gap={16}>
          {lists.map((l) => (
            <Stack key={l.label} gap={4}>
              <Text size="small" weight="semibold" tone="secondary">{l.label}</Text>
              <Bullets items={l.items} />
            </Stack>
          ))}
        </Grid>
      )}
      <Text size="small" tone="tertiary">{`Source: \`${ov.source}\``}</Text>
    </Stack>
  );
}

function SpecView() {
  if (specced.length === 0) return null;
  return (
    <Stack gap={12}>
      <H2>What defines done for each ticket</H2>
      {STAGES.filter((s) => specced.some((t) => t.stage === s)).map((s) => (
        <Stack key={s} gap={8}>
          <H3>{`${s} (${specced.filter((t) => t.stage === s).length})`}</H3>
          {specced.filter((t) => t.stage === s).map((t) => (
            <Stack key={t.id} gap={4} style={{ paddingLeft: 4 }}>
              <Text weight="semibold">{`${t.id} ${t.title}`}</Text>
              {t.intent && <Text size="small" tone="secondary">{t.intent}<Tags tags={t.intent_tags} /></Text>}
              <AcList items={t.acceptance ?? []} />
            </Stack>
          ))}
        </Stack>
      ))}
    </Stack>
  );
}

function ProofView() {
  const theme = useHostTheme();
  const brief = BOARD.brief;
  if (!brief) return null;
  const rules = STAGES.filter((s) => brief.stage_rules[s]);
  return (
    <Stack gap={12}>
      <H2>What proves each stage</H2>
      {rules.length > 0 && (
        <Stack gap={6}>
          <Table headers={["Stage", "Exit rule"]}
            rows={rules.map((s) => [s, <ClaimText key={s} size="small"
              claim={{ text: brief.stage_rules[s], tags: brief.stage_rule_tags?.[s] ?? [] }} />])}
            rowTone={rules.map((s) => TONE[s])} />
          {brief.stage_rules_source === "default" && (
            <Text size="small" tone="tertiary">
              Generic defaults. Set `stage_rules` in `.plan/board/config.json` to replace them.
            </Text>
          )}
        </Stack>
      )}
      {(brief.proof_notes ?? []).length > 0 && <Bullets items={brief.proof_notes ?? []} />}
      {brief.gates.length > 0 && (
        <Grid columns={brief.gates.length > 1 ? 2 : 1} gap={12}>
          {brief.gates.map((g) => (
            <Card key={g.id}>
              <CardHeader trailing={<Pill size="sm" active={g.met}>{g.met ? "Met" : "Not met"}</Pill>}>
                {g.id}
              </CardHeader>
              <CardBody>
                <Stack gap={6}>
                  <Text weight="medium">{g.question}</Text>
                  {g.note && <ClaimText claim={g.note} size="small" />}
                  <AcList items={g.acceptance} />
                  <Row gap={6} align="center">
                    <svg width={8} height={8}>
                      <circle cx={4} cy={4} r={4} fill={g.met ? theme.category.green : theme.category.yellow} />
                    </svg>
                    <Text size="small" tone="secondary">
                      {g.met ? "COMPLETE with evidence" : `${g.stage}, ${g.evidence.length} evidence link(s); needs COMPLETE and evidence`}
                    </Text>
                  </Row>
                  {g.evidence.length > 0 && <Text size="small">{`Evidence: ${evidenceText(g.evidence)}`}</Text>}
                </Stack>
              </CardBody>
            </Card>
          ))}
        </Grid>
      )}
    </Stack>
  );
}

function NowView() {
  const now = BOARD.tickets.filter((t) => t.stage === "BUILD" || t.stage === "REVIEW" || t.stage === "BLOCKED");
  if (now.length === 0) return null;
  return (
    <Stack gap={8}>
      <H2>Now: tickets in BUILD, REVIEW or BLOCKED</H2>
      <Table
        headers={["Ticket", "Title", "Stage", "Owner", "Note"]}
        rows={now.map((t) => [t.id, t.title, t.stage, t.owner ?? "", t.note ?? ""])}
        rowTone={now.map((t) => TONE[t.stage])}
      />
    </Stack>
  );
}

function TimelineView() {
  const moves = [...BOARD.events].reverse().filter((e) => e.from !== e.to || e.evidence.length > 0);
  if (moves.length === 0) return null;
  const keys = Array.from(new Set(moves.map((e) => e.cycle ?? "")));
  return (
    <Stack gap={8}>
      <H2>Stage changes and evidence by cycle</H2>
      {keys.map((k) => {
        const rows = moves.filter((e) => (e.cycle ?? "") === k);
        return (
          <Stack key={k} gap={6}>
            <H3>{k ? cycleName.get(k) ?? k : "Outside any cycle"}</H3>
            <Table
              headers={["Date", "Ticket", "From", "To", "Evidence"]}
              rows={rows.map((e) => [
                e.ts, e.ticket, e.from === e.to ? "evidence" : e.from ?? "(new)", e.to,
                <Text size="small">{evidenceText(e.evidence)}</Text>,
              ])}
              rowTone={rows.map((e) => TONE[e.to])}
            />
          </Stack>
        );
      })}
    </Stack>
  );
}

function DagView() {
  const theme = useHostTheme();
  const edges = BOARD.tickets.flatMap((t) =>
    t.deps.filter((d) => ticketById.has(d)).map((d) => ({ from: d, to: t.id })));
  if (edges.length === 0) return null;
  const color: Record<Stage, string> = {
    NEW: theme.category.gray, BUILD: theme.category.blue, REVIEW: theme.category.yellow,
    BLOCKED: theme.category.red, COMPLETE: theme.category.green,
  };
  const W = 150;
  const H = 40;
  const layout = computeDAGLayout({
    nodes: BOARD.tickets.map((t) => ({ id: t.id })), edges, direction: "horizontal",
    nodeWidth: W, nodeHeight: H, rankGap: 48, nodeGap: 14,
  });
  return (
    <Stack gap={8}>
      <H2>Dependency graph, outlined by stage</H2>
      <Row gap={12} wrap>
        {STAGES.map((s) => (
          <Row key={s} gap={4} align="center">
            <svg width={10} height={10}><rect width={10} height={10} rx={2} fill={color[s]} /></svg>
            <Text size="small" tone="secondary">{s}</Text>
          </Row>
        ))}
        <Text size="small" tone="secondary">Thick outline marks a gate.</Text>
      </Row>
      <div style={{ overflowX: "auto" }}>
        <svg width={layout.width} height={layout.height} viewBox={`0 0 ${layout.width} ${layout.height}`}>
          {layout.edges.map((e) => (
            <line key={`${e.from}-${e.to}`} x1={e.sourceX} y1={e.sourceY} x2={e.targetX} y2={e.targetY}
              stroke={theme.stroke.secondary} strokeWidth={1.5} strokeDasharray={e.isBackEdge ? "4 3" : undefined} />
          ))}
          {layout.nodes.map((n) => {
            const t = ticketById.get(n.id);
            if (!t) return null;
            return (
              <g key={n.id}>
                <title>{t.title}</title>
                <rect x={n.x} y={n.y} width={W} height={H} rx={6} fill={theme.fill.tertiary}
                  stroke={color[t.stage]} strokeWidth={t.is_gate ? 3 : 1.5} />
                <text x={n.x + 10} y={n.y + 17} fontSize={12} fill={theme.text.primary}>{t.id}</text>
                <text x={n.x + 10} y={n.y + 31} fontSize={11} fill={theme.text.secondary}>{t.stage}</text>
              </g>
            );
          })}
        </svg>
      </div>
    </Stack>
  );
}

function GatesView() {
  const gates = BOARD.tickets.filter((t) => t.is_gate);
  if (gates.length === 0) return null;
  return (
    <Stack gap={8}>
      <H2>Gates and the evidence behind them</H2>
      <Grid columns={gates.length > 1 ? 2 : 1} gap={12}>
        {gates.map((g) => {
          const feeds = BOARD.tickets.filter((t) => t.gate === g.id);
          const list = feeds.length > 0 ? feeds : BOARD.tickets.filter((t) => g.deps.includes(t.id));
          const done = list.filter((t) => t.stage === "COMPLETE").length;
          return (
            <Card key={g.id}>
              <CardHeader trailing={<Pill size="sm" active={g.stage === "COMPLETE"}>{g.stage}</Pill>}>
                {`${g.id} ${g.title}`}
              </CardHeader>
              <CardBody>
                <Stack gap={6}>
                  {list.length > 0 && (
                    <Text size="small" tone="secondary">
                      {`Feeding tickets complete: ${done} of ${list.length} (${list.map((t) => `${t.id} ${t.stage}`).join(", ")})`}
                    </Text>
                  )}
                  {g.evidence.length > 0 && <Text size="small">{`Evidence: ${evidenceText(g.evidence)}`}</Text>}
                </Stack>
              </CardBody>
            </Card>
          );
        })}
      </Grid>
    </Stack>
  );
}

function BurnView() {
  if (BOARD.burn.length === 0) return null;
  return (
    <Stack gap={8}>
      <H2>Tickets per cycle: started, completed, open at cycle end</H2>
      <BarChart
        categories={BOARD.burn.map((b) => cycleName.get(b.cycle) ?? b.cycle)}
        series={[
          { name: "Started (moved to BUILD)", data: BOARD.burn.map((b) => b.started), tone: "info" },
          { name: "Completed", data: BOARD.burn.map((b) => b.completed), tone: "success" },
          { name: "Open at cycle end", data: BOARD.burn.map((b) => b.open_at_end), tone: "neutral" },
        ]}
        valueSuffix=" tickets"
        height={220}
      />
      <Text size="small" tone="tertiary">
        {`X axis: cycle. Y axis: ticket count. Source: .plan/board/history.jsonl, ${BOARD.cycles
          .map((c) => `${c.name || c.id} ${c.start} to ${c.end}`).join("; ")}`}
      </Text>
    </Stack>
  );
}

const VIEWS: Record<string, typeof NowView> = {
  overview: OverviewView, spec: SpecView, proof: ProofView,
  now: NowView, timeline: TimelineView, dag: DagView, gates: GatesView, burn: BurnView,
};
const HAS_DATA: Record<string, boolean> = {
  overview: Boolean(BOARD.brief?.overview),
  spec: specced.length > 0,
  proof: Boolean(BOARD.brief) && (Object.keys(BOARD.brief?.stage_rules ?? {}).length > 0
    || (BOARD.brief?.gates.length ?? 0) > 0),
  now: BOARD.tickets.some((t) => t.stage === "BUILD" || t.stage === "REVIEW" || t.stage === "BLOCKED"),
  timeline: BOARD.events.length > 0,
  dag: BOARD.tickets.some((t) => t.deps.some((d) => ticketById.has(d))),
  gates: BOARD.tickets.some((t) => t.is_gate),
  burn: BOARD.burn.length > 0,
};

export default function Trackboard() {
  const order = (BOARD.views?.order ?? Object.keys(VIEWS)).filter((v) => v in VIEWS && HAS_DATA[v]);
  const groups = GROUPS.map((g) => ({ ...g, views: order.filter((v) => g.views.includes(v)) }))
    .filter((g) => g.views.length > 0);
  const [groupId, setGroupId] = useState<string>(groups[0]?.id ?? "tracking");
  const [focus, setFocus] = useState<string | null>(null);
  const group = groups.find((g) => g.id === groupId) ?? groups[0];
  const views = group ? group.views : [];
  const shown = focus && views.includes(focus) ? [focus] : views;
  const counts = STAGES.map((s) => [s, BOARD.tickets.filter((t) => t.stage === s).length] as const)
    .filter(([, n]) => n > 0);
  return (
    <Stack gap={20}>
      <Stack gap={4}>
        <H1>{BOARD.title}</H1>
        <Text size="small" tone="secondary">
          {`Generated ${BOARD.generated_at} from ${BOARD.sources.map((s) => s.path).join(", ")}`}
        </Text>
      </Stack>
      <Row gap={24} wrap>
        {counts.map(([s, n]) => (
          <Stat key={s} value={n} label={s}
            tone={s === "COMPLETE" ? "success" : s === "BLOCKED" ? "danger" : s === "REVIEW" ? "warning" : undefined} />
        ))}
      </Row>
      {briefNotice() && (
        <Text size="small" tone={BOARD.brief?.stale ? "secondary" : "tertiary"}>{briefNotice()}</Text>
      )}
      {BOARD.drift.length > 0 && (
        <Callout tone="danger" title={`Drift: ${BOARD.drift.length} ticket(s) where sources disagree`}>
          {BOARD.drift.map((d) => `${d.ticket} ${d.kind} ${JSON.stringify(d.values)}`).join("; ")}
        </Callout>
      )}
      <Stack gap={8}>
        {groups.length > 1 && (
          <Row gap={6} wrap>
            {groups.map((g) => (
              <Pill key={g.id} active={group?.id === g.id} onClick={() => { setGroupId(g.id); setFocus(null); }}>
                {g.label}
              </Pill>
            ))}
          </Row>
        )}
        {views.length > 1 && (
          <Row gap={6} wrap>
            <Pill size="sm" active={!focus} onClick={() => setFocus(null)}>{`All ${group?.label ?? ""}`.trim()}</Pill>
            {views.map((v) => (
              <Pill key={v} size="sm" active={focus === v} onClick={() => setFocus(v)}>{VIEW_LABEL[v] ?? v}</Pill>
            ))}
          </Row>
        )}
      </Stack>
      {shown.map((v) => {
        const View = VIEWS[v];
        return <View key={v} />;
      })}
    </Stack>
  );
}
