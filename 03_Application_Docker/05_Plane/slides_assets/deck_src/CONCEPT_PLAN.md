# CONCEPT_PLAN — concept units for the Plane × Agile deck (rev 2026-09-01)

Blueprint for the "detailed theory" upgrade. Every core concept of the course becomes a **unit** of 2–4 slides that
follows the same template, is illustrated with an Excalidraw diagram and/or a realistic photo, and ends on a **real
Plane screenshot** + the LAB where the student practises it. Authors: read `STYLE_GUIDE.md` (markup) and
`PLANE_REFERENCE.md` (facts about Plane v1.4.2 — never guess) before writing.

## Unit template (checklist from the course brief)

| Slide | Eyebrow suffix | Must contain |
|---|---|---|
| **A · นิยาม** | `· นิยาม` | Definition (1–2 sentences, quotable) · Why it matters · Problem it solves (before/after) · usually a realistic photo (`real_*`) on the right |
| **B · กลไก** | `· กลไก` | How it works · Components · Workflow — the Excalidraw diagram is the hero (`.fig`), 3 cards or a table beside/below |
| **C · ตัวอย่าง** | `· ตัวอย่าง` | Real-world example (use the CampusEats story of the labs) · Common misunderstanding (❌ → ✅ cards) |
| **D · ใน Plane** | `· ใน Plane` | How Plane implements it (menu path, field/table names from PLANE_REFERENCE, CE limits) · Related Plane feature · **real screenshot** (`t-*` or `labN:*`) · Related LAB tag · Mini exercise / review question (`.note a`) |

Small concepts (marked *2–3 slides*) merge C into A or D. Slides already in the deck that cover a part of a unit are
**moved into the unit** (listed as "reuse") — do not duplicate them.

Audience: students with no prior Agile/Scrum/Kanban/SPM background. Thai prose, precise, no fluff; every claim about
Plane must match `PLANE_REFERENCE.md`; every screenshot must be a real capture (never a drawing of the UI).

## Assets

### Diagrams (Excalidraw, `slides_assets/dNN-name.svg`, key = `dNN`) — NEW d20–d42

| key | file | content (Thai labels on the diagram) |
|---|---|---|
| d20 | d20-sdlc-phases | SDLC loop: Requirements → Design → Implementation → Testing → Deployment → Maintenance with feedback arrows; footnote: one long pass = Waterfall, many short passes = iterative/Agile |
| d21 | d21-issue-lifecycle | Issue-tracking lifecycle: Report/Create → Triage (accept · decline · duplicate · snooze) → Prioritise (backlog order) → Plan (cycle) → In progress → Review → Done → (Reopen); Plane state groups shown beneath the stages |
| d22 | d22-workflow-states | Workflow = states + transitions + policies; Plane's 5 state groups (backlog · unstarted · started · completed · cancelled) each holding custom states; entering *completed* sets `completed_at`; note "CE: no transition rules / WIP limit" |
| d23 | d23-plane-architecture | Plane logical architecture: Browser → proxy (Caddy) → web · admin · space · live · api; api ↔ PostgreSQL · Valkey · RabbitMQ → worker · beat-worker; MinIO for uploads; migrator one-shot |
| d24 | d24-plane-hierarchy | Instance → Workspace → Project → {Cycles, Modules, Views, Pages, Intake, States, Labels, Estimates, Members} → Work item → sub-work items · relations · comments · attachments · activity |
| d25 | d25-compose-architecture | Anatomy of `docker-compose.yml` + `plane.env`: 13 services grouped (app / infra), named volumes, `${VAR}` from env file, depends_on/healthcheck order, single published port via proxy |
| d26 | d26-agile-iteration | Agile iteration loop: ordered backlog → plan → build → test → review/feedback → adapt backlog → next iteration; increments accumulate; small inset contrasting one long Waterfall pass |
| d27 | d27-scrum-workflow | Scrum flow: Product Backlog (PO) → Sprint Planning → Sprint Backlog → Sprint (1–4 wk, Daily Scrum) → Increment → Sprint Review → Retrospective → loop; roles annotated; Plane names in small grey text (Cycle, work items, Page) |
| d28 | d28-story-hierarchy | Epic → User Story → Task → Subtask; Bug as a type that can sit at story/task level; right column: Plane mapping Module → Work item → Sub-work item; Bug = label (CE) |
| d29 | d29-relative-estimation | Relative estimation: reference story = 2 pt; "about twice" → 5, "half" → 1, "much bigger" → 8/13; absolute hours vs relative size; team-specific scale |
| d30 | d30-fibonacci-scale | Modified Fibonacci 1 2 3 5 8 13 20 40 100 as cards growing in size; gap widens with uncertainty; "≥ 13 → split"; T-shirt sizes as alternative |
| d31 | d31-planning-poker | Planning Poker steps: PO reads story → everyone picks a card privately → reveal together → highest/lowest explain → re-vote → converge & record; 2-round example (3·5·5·13 → 5·5·8·5) |
| d32 | d32-velocity-forecast | Velocity bars 18 · 22 · 20 → average 20 pts/sprint → remaining 120 pts ÷ 20 = 6 sprints, range 5.5–6.7; "history predicts, not a target" |
| d33 | d33-burndown-burnup | Side by side: Burndown (remaining vs ideal, staircase) and Burn-up (done cumulative + scope line with a scope-change step) |
| d34 | d34-kanban-workflow | Kanban board: Backlog → Ready → In Progress (WIP 3) → Review (WIP 2) → Done; pull arrows; explicit policy strip under each column |
| d35 | d35-wip-limit-effect | Before/after WIP limit: WIP 12 ÷ 3 per day = 4 days vs WIP 6 → 2 days (Little's Law); full column = stop pulling, "stop starting · start finishing" |
| d36 | d36-cfd-annotated | Cumulative Flow Diagram: stacked bands To do / In progress / Done over time with annotations: vertical gap = WIP, horizontal gap = approx. lead time, slope of Done = throughput, widening middle band = bottleneck |
| d37 | d37-continuous-improvement | PDCA/Kaizen loop: Measure (burndown · cycle time · CFD) → Retrospective (inspect) → Decide 1–2 actions → Do next sprint → Measure again; Plane hooks: Analytics · Page (retro) · work items for action items |
| d38 | d38-theory-plane-lab-map | Theory concept → Plane feature → LAB table-as-diagram (SDLC/Issue/Workflow → LAB 1–3 · Scrum cluster → LAB 4 · Kanban cluster → LAB 5 · Epic/Module/Analytics → LAB 6 · API/Webhooks/Dashboard → LAB 7–9) |
| d39 | d39-lead-vs-cycle-time | One work item's timeline: created → started → done; Lead time bracket (customer view) vs Cycle time bracket (team view); waiting vs working segments; P85 note |
| d40 | d40-prioritization | Prioritisation: value × effort 2×2, MoSCoW, WSJF = cost of delay ÷ duration → ONE ordered backlog; Plane: priority field + drag order (sort_order); urgent = Expedite class |
| d41 | d41-backlog-refinement | Refinement funnel: raw ideas (bottom, large & vague) → refined (INVEST, acceptance criteria, estimate) → "Ready" (top, small & detailed); DEEP; happens continuously, not an event |
| d42 | d42-product-vs-sprint-backlog | Product Backlog (all work, ordered by PO, commitment = Product Goal) → Sprint Backlog (selected + plan, owned by Developers, commitment = Sprint Goal) → Increment (commitment = DoD); Plane: project work items → cycle work items → state group completed |

Existing diagrams reused inside units: `d01` (Scrum ↔ Plane), `d02` (lead/cycle time + Little's Law + WIP), `d04`
(waterfall vs agile), `d06` (work-item anatomy), `d08` (ER model), `d07`/`d12` (request path / celery), `d14` (first run).

### Realistic photos (Codex image gen, `slides_assets/photos/*.jpg`, key = stem)

`real_sdlc_requirements` · `real_daily_standup` · `real_planning_poker` · `real_kanban_wall` · `real_retrospective` ·
`real_backlog_refinement` · `real_developer_workflow` · `real_bug_triage` · `real_devops_dashboard` · `real_sprint_review` ·
`real_software_professional` · `real_customer_collaboration` · `real_metrics_review` · `real_estimation_whiteboard` ·
`real_support_ticket` · `real_continuous_improvement` · `real_university_lab` · `real_roadmap_wall`

Use at most one photo per slide, as `.fig` (object-fit cover, ≤ 430 px tall) — photos illustrate the *human* side of a
concept; they never stand in for Plane's UI.

### Real Plane screenshots for theory slides (`slides_assets/screenshots/t-*.png`, key = stem)

Captured with Playwright from the continuous instance (workspace *DevTools Lab*, project *Plane Lab* `PLAB`, story
CampusEats, after LAB 1→6 state). Each file has a sibling `t-*.txt` describing exactly what is on screen — read it
before writing the caption.

| key | page / state |
|---|---|
| t-home | workspace Home with widgets |
| t-projects | Projects list showing *Plane Lab* (PLAB) |
| t-features-settings | Project settings › Features (Cycles · Modules · Views · Pages · Intake toggles) |
| t-workitems-list | PLAB work items, List layout grouped by state — the product backlog |
| t-workitem-create | *Create new work item* modal filled with a CampusEats story |
| t-workitem-detail | a story's detail: description/acceptance criteria, properties (state · priority · assignee · estimate · labels · cycle · module · dates) |
| t-subworkitems | sub-work items panel of a story (tasks/subtasks) with progress x/y |
| t-relations | Blocked by / Blocking / Relates to on a work item |
| t-activity | activity log of a work item (state transitions with actor + time) |
| t-labels-settings | Project settings › Labels (incl. `bug`) |
| t-states-settings | Project settings › States grouped by the 5 groups (custom *In Review*) |
| t-estimates-settings | Project settings › Estimates (Fibonacci points) |
| t-priority-picker | priority dropdown open on a work item (Urgent · High · Medium · Low · None) |
| t-cycles-list | Cycles list: completed Sprint 1, active Sprint 2 |
| t-cycle-active | active cycle page with Progress side panel + burndown (Work items mode) |
| t-cycle-burndown-points | the same burndown switched to Estimates (points) mode |
| t-cycle-add-items | *Add existing work items* modal — choosing the sprint backlog |
| t-cycle-completed | completed Sprint 1 with transfer snapshot |
| t-board-state | Board layout, group by State (Kanban columns) |
| t-board-swimlanes | Board with sub-group by Assignee (WIP per person visible) |
| t-display-filters | Display/filters dropdown (layout · group by · order by priority) |
| t-modules-list | Modules (Epics) list/gallery with progress |
| t-module-detail | one module's detail with progress and its work items |
| t-views-list | saved Views list |
| t-view-detail | a saved view opened with its filters |
| t-intake | Intake page with pending/accepted/declined items |
| t-pages | a project Page (Definition of Done / retro) |
| t-timeline | Timeline (Gantt) layout |
| t-calendar | Calendar layout |
| t-spreadsheet | Table/spreadsheet layout |
| t-analytics-overview | Workspace Analytics › Overview |
| t-analytics-workitems | Analytics › Work items (created vs resolved) |
| t-members | Workspace settings › Members with roles |
| t-project-members | Project settings › Members |
| t-api-tokens | Settings › Developer › Personal Access Tokens |
| t-webhooks | Workspace settings › Webhooks |
| t-godmode | god-mode general page |

Lab screenshots (`labN:<stem>`) remain available for LAB-specific slides.

## Deck structure after the upgrade (fragment files, sorted by name)

```
10_cover · 12_agenda
20_topic1                              ตอนที่ 1 (existing; + photos)
30_topic2  (#1–2)                      ตอนที่ 2 divider + SDLC overview
30a_u_sdlc                             U-SDLC
30b_topic2_tools (#3–5)                toolchain · app/tool/platform · single source of truth
30c_u_issue_tracking                   U-ISSUE-TRACKING
30d_u_workflow                         U-WORKFLOW
30e_u_plane_architecture               U-PLANE-ARCH (hierarchy d24 · logical d23 · compose d25 · deployment)
30f_topic2_plane (#6–21)               anatomy · request path · celery · ER · config · deploy · security · … · summary
40_topic3  (#1–4)                      ตอนที่ 3 divider + history + manifesto values + principles
40a_u_agile                            U-AGILE
40b_u_scrum                            U-SCRUM (reuse #5–#8)
40c_u_product_backlog                  U-PRODUCT-BACKLOG
40d_u_sprint_backlog                   U-SPRINT-BACKLOG
40e_u_sprint_cycle                     U-SPRINT-CYCLE
40f_u_backlog_refinement               U-BACKLOG-REFINEMENT
40g_u_prioritization                   U-PRIORITIZATION
41_topic3_workitems                    sub-divider 3.2 ลำดับชั้นของงาน
41a_u_epic                             U-EPIC
41b_u_user_story                       U-USER-STORY (reuse #9 INVEST)
41c_u_task_subtask_bug                 U-TASK-SUBTASK-BUG
42_topic3_estimation                   sub-divider 3.3 การประมาณและ metrics ของ Scrum
42a_u_story_point                      U-STORY-POINT (reuse #10)
42b_u_relative_estimation              U-RELATIVE-ESTIMATION
42c_u_fibonacci                        U-FIBONACCI
42d_u_planning_poker                   U-PLANNING-POKER
42e_u_velocity                         U-VELOCITY (reuse #11)
42f_u_burndown                         U-BURNDOWN (reuse #12)
42g_u_burnup                           U-BURNUP
43_topic3_kanban                       sub-divider 3.4 Kanban และ flow
43a_u_kanban                           U-KANBAN (reuse #13)
43b_u_wip_limit                        U-WIP + U-WIP-LIMIT
43c_u_lead_cycle_time                  U-LEAD-TIME + U-CYCLE-TIME (reuse #14)
43d_u_cfd                              U-CFD (reuse #15)
43e_u_continuous_improvement           U-CONTINUOUS-IMPROVEMENT
44_topic3_plane (#16–25)               Scrum·Kanban·Scrumban · mapping · terms · states · board · cycles · estimates · run scrum · anti-patterns · summary
50_topic4                              ตอนที่ 4 (existing; + photos, + pointers to units)
60_labs · 70_summary (+ d38 map slide) · 90_tail
```

Sub-dividers (41_, 42_, 43_) are `slide section` slides **without** `data-sec` (the overview groups them under ตอนที่ 3).

## Units

Notation: **[A/B/C/D]** = template slides; *reuse* = existing slide moved into the unit; assets by key; LAB = related lab.

### ตอนที่ 2

**U-SDLC** (4) — SDLC · Software Development Life Cycle
A: นิยาม (วงจรของกิจกรรมตั้งแต่ความต้องการถึงบำรุงรักษา) · why (shared map of work; every tool exists for a phase) · problem (unplanned work, missing tests, no maintenance budget) · photo `real_sdlc_requirements`
B: `d20` phases + activities + artifacts table; models: Waterfall (one pass) · Iterative · Agile (many short passes) — link to `d04`
C: CampusEats semester project walked through the phases; misunderstanding: "SDLC = Waterfall", "Agile has no design/testing phase" (it has them every iteration)
D: Plane covers Requirements (backlog work items) · Planning (Cycles) · Tracking (States) · Release (Modules) · Feedback (Intake, comments); screenshot `t-workitems-list`; LAB 1–2; exercise: map your last project's activities to the phases

**U-ISSUE-TRACKING** (4)
A: นิยาม (issue = บันทึกงานหนึ่งหน่วยที่มีเจ้าของ สถานะ และประวัติ) · why (organisational memory, accountability, single source of truth) · problem (chat/email/spreadsheet chaos: lost requests, "who is doing what") · photo `real_support_ticket`
B: `d21` lifecycle; components table (id · title · description · state · priority · assignee · labels · dates · estimate · comments · activity · relations · attachments)
C: a CampusEats bug reported by a student → triage → fix → verify; misunderstanding: "issue = bug only" (it is any unit of work), "closing = done" (DoD)
D: Plane *work item* (`issues` table, `sequence_id` never reused, activity log) — screenshot `t-workitem-detail` + `t-activity`; LAB 3; exercise: write one professional work item for a feature you know

**U-WORKFLOW** (3)
A: นิยาม (states + allowed transitions + policies = ความหมายร่วมของคำว่า "เสร็จ") · why · problem (each person's "done" differs; hidden WIP) · photo `real_developer_workflow`
B: `d22`; state groups semantics (backlog/unstarted/started/completed/cancelled), `completed_at`, custom states, Jira transitions vs Plane simplicity
D: screenshot `t-states-settings`; CE limits (no transition rules, no WIP limit → policy Page + script, LAB 5); exercise: design states for a support team

**U-PLANE-ARCH** (4) — สถาปัตยกรรมของ Plane
1: `d24` hierarchy (Instance → Workspace → Project → … → Work item) + screenshot `t-projects` / `t-features-settings`
2: `d23` logical architecture (services & data stores) — prose from PLANE_REFERENCE §2
3: `d25` compose anatomy + env vars that matter (APP_DOMAIN, WEB_URL, CORS, secrets, storage) — PLANE_REFERENCE §3
4: dependencies & boot order (migrator → api → worker/beat; what breaks when redis/mq/db stop) + LAB 1–2 tag; exercise: which container answers `/api/v1/...`?

### ตอนที่ 3.1 Agile & Scrum

**U-AGILE** (3) A: นิยาม (iterative & incremental delivery with feedback each 1–4 weeks) · why · problem (late discovery of wrong product) · photo `real_customer_collaboration` · B: `d26` iteration loop; components (backlog, iteration, increment, feedback) · C/D merged: CampusEats example; misunderstanding "Agile = no plan / no documents"; Plane: Cycles + re-ordered backlog — screenshot `t-cycles-list`; LAB 4; exercise

**U-SCRUM** (5) A: นิยาม (lightweight framework: 3 accountabilities · 5 events · 3 artifacts) · why · problem · photo `real_daily_standup` · B: `d27` · reuse #5 (empirical), #6 (roles), #7 (events), #8 (artifacts) · C: CampusEats Sprint 1 story + misunderstandings (Scrum Master = manager; sprint = mini-deadline; Daily = status report) · D: Plane: Cycle = Sprint, Page = DoD/retro, Board = Daily — screenshot `t-cycle-active`; LAB 4; exercise

**U-PRODUCT-BACKLOG** (3) A: นิยาม (single ordered list of everything the product might need; one owner) · why · problem (many lists, no order) · photo `real_backlog_refinement` · B: `d42` + DEEP properties, ordering rules, Product Goal · D: Plane: project work items (state group backlog), drag order = `sort_order`, priority, filters — screenshot `t-workitems-list`; LAB 3–4; exercise

**U-SPRINT-BACKLOG** (2) A+B: นิยาม (items selected for this sprint + plan, owned by Developers, Sprint Goal) · `d42` right half · D: Plane: work items in the Cycle (`cycle_issues`), *Add existing work items* — screenshot `t-cycle-add-items`; LAB 4; exercise

**U-SPRINT-CYCLE** (4) A: นิยาม (fixed timebox ≤ 1 month, produces a usable increment; new sprint starts immediately) · why (rhythm, forecastability) · problem · photo `real_sprint_review` · B: sprint anatomy timeline (planning → daily → review → retro) reuse the events table if useful; rules (no goal-breaking changes, cancel only by PO) · C: CampusEats Sprint 1/2 and what happened to unfinished work; misunderstanding: "extend the sprint", "sprint = release" · D: Plane Cycle: start/end dates, status computed from dates, one active, Transfer of unfinished items, progress snapshot — screenshots `t-cycles-list` + `t-cycle-completed`; LAB 4; exercise

**U-BACKLOG-REFINEMENT** (3) A: นิยาม (ongoing activity to split, detail, estimate top items until "Ready") · why · problem (planning takes hours; stories too big) · photo `real_estimation_whiteboard` · B: `d41` + Definition of Ready checklist · D: Plane: description/acceptance criteria, sub-work items, estimates, labels; refinement happens in the List layout — screenshot `t-workitem-detail`; LAB 3–4; exercise

**U-PRIORITIZATION** (3) A: นิยาม (deciding order, not urgency labels) · why · problem (everything urgent) · B: `d40` methods (value×effort, MoSCoW, WSJF/cost of delay, class of service) · D: Plane: priority field (urgent/high/medium/low/none), order by priority, drag order, Expedite = urgent + policy — screenshots `t-priority-picker` + `t-display-filters`; LAB 5; exercise

### ตอนที่ 3.2 ลำดับชั้นของงาน

**U-EPIC** (3) A: นิยาม (large body of work spanning sprints, split into stories) · why (roadmap-level tracking) · problem · photo `real_roadmap_wall` · B: `d28` hierarchy; epic life: planned → in progress → completed; progress = done stories/total · D: Plane Module (lead, members, dates, status, progress) — screenshots `t-modules-list` + `t-module-detail`; LAB 6; exercise

**U-USER-STORY** (3) A: นิยาม (As a … I want … so that …; a promise of a conversation) · why · problem (specs nobody reads) · reuse #9 (INVEST) as B · D: Plane: work item title = story sentence, description = acceptance criteria, labels; screenshot `t-workitem-create`; LAB 3; exercise

**U-TASK-SUBTASK-BUG** (3) A: นิยาม of Task (technical step, hours–days), Subtask (child of a story/task), Bug (defect: expected vs actual, repro steps, severity) · why · problem · photo `real_bug_triage` · B: `d28` lower part + bug report anatomy table (title · steps · expected · actual · env · severity · priority) · D: Plane: sub-work items (parent), relations (blocked by), `bug` label (CE has no work-item types → label), sequence ids — screenshots `t-subworkitems` + `t-relations` + `t-labels-settings`; LAB 3; exercise

### ตอนที่ 3.3 การประมาณและ metrics ของ Scrum

**U-STORY-POINT** (3) A: นิยาม (unit of relative size = effort + complexity + uncertainty) · why · problem (hours are wrong and become commitments) · reuse #10 as B (planning poker example table stays there) · D: Plane Estimates (points system, `EstimatePoint.value`, one system per project, burndown in Estimates mode) — screenshot `t-estimates-settings`; LAB 4; exercise

**U-RELATIVE-ESTIMATION** (2) A+B: นิยาม (compare to a reference story, not to a clock) · `d29` · why humans estimate relative size better · D: Plane: estimate dropdown on work item; consistency check via List ordered by estimate — screenshot `t-workitem-detail` (estimate property); LAB 4; exercise (rank 5 CampusEats stories relative to a 2-pt reference)

**U-FIBONACCI** (2) A+B: `d30` why gaps widen (uncertainty grows with size), modified sequence, ≥ 13 → split, alternatives (T-shirt, powers of 2) · D: Plane Estimates templates Fibonacci · Linear · Squares · Custom (CE: points & categories; Time = paid) — screenshot `t-estimates-settings`; LAB 4; exercise

**U-PLANNING-POKER** (3) A: นิยาม (consensus estimation game: private pick → simultaneous reveal → discuss → converge) · why (avoids anchoring, surfaces hidden work) · photo `real_planning_poker` · B: `d31` steps + rules (PO does not vote; timebox; 2–3 rounds max) · D: Plane has no poker tool: run it in the meeting, record the result as estimate + comment — screenshot `t-workitem-detail`; LAB 4; exercise

**U-VELOCITY** (3) A: นิยาม (Σ points Done per sprint; team's own yardstick) · why (forecast, capacity for planning) · problem · B: reuse #11 + `d32` · D: Plane: no velocity chart in CE — compute from completed cycles (`velocity.py`, progress snapshot) — screenshot `t-cycle-completed`; LAB 4; exercise

**U-BURNDOWN** (3) A: นิยาม (remaining work vs time against an ideal line) · why · problem (percent-complete illusions) · B: reuse #12 (patterns) + `d33` left · D: Plane: cycle Progress panel, formula remaining(d)=total−Σ completed_at ≤ d, Work items vs Estimates mode — screenshots `t-cycle-active` + `t-cycle-burndown-points`; LAB 4; exercise (read a real chart)

**U-BURNUP** (2) A+B: นิยาม (done cumulative + scope line) · `d33` right · why it shows scope creep that burndown hides · D: Plane CE: no burn-up chart — derive from `completed_at` + cycle membership (LAB 4 `cycle_report.py`, LAB 9 dashboard) — screenshot `lab9:` dashboard if available else `t-cycle-active`; exercise

### ตอนที่ 3.4 Kanban และ flow

**U-KANBAN** (4) A: นิยาม (a method to improve flow: visualise, limit WIP, manage flow, explicit policies, feedback loops, improve) · why · problem (invisible work, overload) · photo `real_kanban_wall` · B: reuse #13 + `d34` · C: CampusEats support board example; misunderstanding "Kanban = a board with columns", "no planning in Kanban" · D: Plane Board layout, group by State, states = columns, policies in a Page — screenshot `t-board-state`; LAB 5; exercise

**U-WIP-LIMIT** (4) — WIP and WIP limit
A: นิยาม (WIP = started, not finished; limit = max per column/person) · why (Little's Law) · problem (everything 80 % done) · B: `d35` + reuse `d02` panel; how to choose a limit; what to do when full · C: example numbers; misunderstanding "limit = laziness", "limits per person only" · D: Plane CE has no WIP limit: swimlanes by assignee show WIP per person; policy Page + `wip_guard.py` — screenshot `t-board-swimlanes`; LAB 5; exercise

**U-LEAD-CYCLE-TIME** (3) A: นิยาม both, customer vs team view · why · problem (averages hide tails → P85) · B: `d39` + reuse #14 (flow metrics table) · D: Plane data: `created_at`, first move to *started* (IssueActivity field=state), `completed_at` — screenshot `t-activity`; LAB 5 (`flow_metrics.py`), LAB 9; exercise (compute from a timeline)

**U-CFD** (3) A: นิยาม (stacked count per state over time) · why (WIP, lead time, throughput, bottleneck in one picture) · B: `d36` + reuse #15 (how to read) · D: Plane CE has no CFD — build from activity log (LAB 9 dashboard) — screenshot `lab9:` CFD panel if available else `t-analytics-workitems`; exercise (read a CFD)

**U-CONTINUOUS-IMPROVEMENT** (3) A: นิยาม (Kaizen/PDCA: small, evidence-based changes every cycle) · why · problem (retro without actions) · photo `real_continuous_improvement` · B: `d37` loop + retro formats (Start/Stop/Continue, 4Ls) + action items as work items · D: Plane: Page (retro), Analytics, activity log, work items labelled `improvement` — screenshots `t-pages` + `t-analytics-overview`; LAB 4 (retro) · LAB 9 (metrics); exercise

### ตอนที่ 4 (additions only)
* `50_topic4` slide #2 ("การติดตาม คือวงจร") gains photo `real_metrics_review`; slide #19 (Intake) gains `t-intake` if the lab shot is weaker; no new units.
* `70_summary` gains a figs slide with `d38` (Theory → Plane → LAB map) before the existing table.
* `20_topic1` slide #2 gains `real_software_professional`; `60_labs` divider gains `real_university_lab`.

## Quality gates
1. `python3 build_deck.py --only <fragment> --out /tmp/x.html && python3 check_deck.py --deck /tmp/x.html --shots /tmp/xshots all` → no overflow / broken images / JS errors; then look at every PNG.
2. Every Plane statement traceable to `PLANE_REFERENCE.md`; CE limitations stated explicitly.
3. Every screenshot key exists (`slides_assets/screenshots/t-*.png` or `00N_LAB_*/images/*.png`); captions describe what is really on screen (read the sibling `.txt`).
4. `python3 ../../scripts/check_materials.py` → `0 fail · 0 warn`.
