# KAIROS: The Life Arbitrage Engine

## Quick Start

### Backend

macOS / Linux / WSL:

```bash
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --reload-dir app
```

Windows PowerShell:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --reload-dir app
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Verification

```bash
cd backend && python3 -m compileall app
cd frontend && npm run build
```

## Environment Notes

- Keep the backend virtualenv at the repo root as `venv/` when you are running Uvicorn from Windows. A nested `backend/.venv` can break `--reload` when it contains Linux-style symlinks.
- Use `--reload-dir app` for the backend dev server so Uvicorn only watches source files.
- Install frontend dependencies in the same shell you will use to run them. If you use PowerShell, run both `npm install` and `npm run dev` in PowerShell so Windows `next.cmd` shims are present.
- This repo is not a root-level Node workspace. If a root `package-lock.json` appears, remove it.

## 1. Thesis
KAIROS can win a hackathon because it attacks a real emotional problem, not just a workflow problem: college students do not need another calendar, they need a system that resolves the tension between academic guilt, social FOMO, and passive idling. The MVP should feel magical by doing one thing extremely well: turning a vague tradeoff into a visible, emotionally charged decision, then proving it with the Dynamic Shuffle. If the demo clearly shows coursework being priced, a high-value Cornell social pocket being detected, and the schedule physically reorganizing itself to unlock that moment, judges will understand the product in under 30 seconds and remember it after every other “AI planner” blurs together.

## 2. The Exact Demo Story
1. Open the dashboard already seeded with a believable Cornell day.
2. Start on the hero state: KAIROS shows current Work Debt, Social Readiness, and a live opportunity forming around Libe Slope.
3. Upload a syllabus PDF. The parser responds instantly with extracted assignments and a higher-confidence Work Debt Ledger.
4. Highlight the Work Debt panel: show hours owed, procrastination drag, and urgency multipliers.
5. Move to Social Gravity: KAIROS shows a 45-minute sunset pocket with 5 friends free at Libe Slope.
6. Trigger Idle Intervention: “20 mins of YouTube vs. Sunset at the Slope.”
7. Click `Trigger Dynamic Shuffle` or `Play demo story`.
8. The schedule animates. A work block snaps earlier, the social block appears, and the tradeoff statement updates: `If you focus for the next hour at 1.2x pace, you unlock Sunset at the Slope with 5 friends.`
9. End on the social/readiness framing: KAIROS did not just organize tasks, it created a better life outcome.

### What is real for the demo
- Backend API contract
- Work Debt scoring
- Social pocket detection
- Dynamic Shuffle output and animation
- Syllabus upload request flow

### What is mocked on purpose
- Syllabus parsing internals
- Friend calendar integrations
- Weather feed
- Idle browser signal

### What should stay hardcoded for speed
- Cornell-specific locations
- Seeded friend names and overlapping availability
- The first showcase opportunity around sunset

## 3. MVP Feature Cutline

### Must-have
- Premium dashboard with strong visual identity
- Syllabus upload interaction
- Work Debt Ledger with urgency and delay cost
- Social Gravity list with Cornell-specific opportunities
- Dynamic Shuffle animation as the centerpiece
- Idle Intervention card tied to Social Readiness

### Nice-to-have
- Adjustable user assumptions
- Demo autopilot / guided story mode
- SQLite persistence for seeded demo state
- Weather-aware activity suggestions

### Cut
- Real auth
- Real calendar write-back
- Multi-user collaboration
- Production-grade optimization engine
- Shipping a browser extension during the hackathon

## 4. Product Spec

### Main screens
- `Landing + Hero`: immediately explains the product as a life optimization engine, not a task app.
- `Dashboard`: the main demo screen with Work Debt, Social Gravity, Dynamic Shuffle, Idle Intervention, and Social Readiness.
- `Upload flow`: lightweight overlay or button interaction that updates the ledger after syllabus parsing.

### Key user actions
- Upload a syllabus.
- Inspect the Work Debt Ledger.
- Review the best social opportunity.
- Trigger Dynamic Shuffle.
- Respond to the idle intervention.

### Core states and outputs
- `Work Debt state`: total effort hours, debt score, urgency multipliers, interest drag.
- `Social state`: top opportunities, friends available, context, claimability.
- `Shuffle state`: before schedule, after schedule, required focus boost, unlocked minutes.
- `Readiness state`: projected social hours vs target, gap, current status.

### MVP scoring concepts
- `Work Debt`: a weighted effort score, not a task count.
- `Social Readiness`: a simple weekly balance score showing whether the student is on track for a healthy college week.
- `Opportunity detection`: a score based on friend overlap, timing, duration, and emotional context.

### Screen-level intent
- Work Debt should feel high-stakes.
- Social Gravity should feel tempting and concrete.
- Dynamic Shuffle should feel like the app is making life happen.
- Idle Intervention should feel urgent, not naggy.

## 5. Architecture

### Stack
- Frontend: `Next.js + React + TypeScript + Framer Motion`
- Backend: `FastAPI`
- Persistence: `SQLite via stdlib sqlite3`
- AI layer: mock parser abstraction, ready to swap for OpenAI

### Repo structure

```text
.
├── AGENTS.md
├── README.md
├── backend
│   ├── app
│   │   ├── db.py
│   │   ├── main.py
│   │   ├── mock_data.py
│   │   ├── schema.sql
│   │   ├── schemas.py
│   │   └── services
│   │       ├── parser.py
│   │       └── scheduler.py
│   └── requirements.txt
└── frontend
    ├── app
    │   ├── layout.tsx
    │   ├── page.tsx
    │   └── globals.css
    ├── package.json
    ├── next.config.mjs
    └── src
        ├── App.tsx
        ├── api.ts
        └── types.ts
```

### Frontend vs backend responsibilities
- Backend owns anything that should feel “smart”: work debt, social pockets, shuffle planning, readiness scoring, seeded persistence.
- Frontend owns presentation, motion, guided demo sequencing, and stateful reveal logic.

### Data flow
1. Backend seeds the demo database.
2. Frontend requests `/api/v1/dashboard/overview`.
3. Backend returns the entire story payload.
4. Frontend renders the dashboard and animates the Dynamic Shuffle.
5. Uploading a syllabus hits `/api/v1/syllabus/parse` and updates assignments plus ledger.

## 6. Data Model

### Minimum tables
- `users`: profile + assumptions
- `courses`: uploaded or seeded courses
- `assignments`: parsed academic tasks
- `friends`: friend circle
- `availability_windows`: mocked availability
- `schedule_blocks`: current day plan
- `idle_events`: last idle signal
- `weather_context`: current contextual weather
- `opportunities`: optional persisted pockets for later growth

### Why this is enough
- It covers the entire demo flow without overbuilding.
- It is extensible to real sync later.
- It supports believable persistence without introducing heavy ORM work.

## 7. API Plan

### `GET /health`
Simple health check.

### `GET /api/v1/dashboard/overview`
Returns the full seeded demo state.

Example response shape:

```json
{
  "tagline": "Live the life you planned, not the one you fell into.",
  "ledger": {
    "work_debt_score": 71.4,
    "interest_drag_hours": 4.6
  },
  "social_readiness": {
    "score": 74.3,
    "gap_hours": 1.8
  },
  "pockets": [
    {
      "title": "Sunset at the Slope",
      "friend_names": ["Maya", "Jonah", "Sana", "Eli", "Priya"]
    }
  ],
  "shuffle_plan": {
    "focus_boost_multiplier": 1.2,
    "unlocked_minutes": 45
  }
}
```

### `POST /api/v1/syllabus/parse`
Accepts multipart upload.

Returns:
- parsed course
- parsed assignments
- recomputed ledger

### `POST /api/v1/social/pockets`
Accepts friend windows and returns ranked opportunities.

### `POST /api/v1/shuffle/plan`
Accepts schedule plus target pockets and returns the reshuffled plan.

### `POST /api/v1/interventions/idle-alert`
Accepts an idle event and returns a tradeoff alert.

## 8. Scoring Logic

### Work Debt
For each assignment:

```text
adjusted_effort =
  base_effort_hours
  * major_difficulty_multiplier
  / historical_productivity_multiplier

debt_contribution =
  adjusted_effort
  * urgency_multiplier
  * (1 + estimated_weight / 10)
```

### Procrastination cost / interest rate
- `< 12h to due`: `1.9x`
- `< 24h`: `1.6x`
- `< 48h`: `1.35x`
- `< 72h`: `1.2x`
- otherwise `1.05x`

This is intentionally not academically perfect. It is demo-perfect because students instantly understand the compounding pressure.

### Social opportunity score

```text
opportunity_score =
  friend_count * 18
  + urgency_bonus
  + duration_bonus
  + context_bonus
```

Where:
- `urgency_bonus` rewards opportunities that expire soon
- `duration_bonus` prefers 45-60 minute windows
- `context_bonus` rewards emotionally attractive contexts like clear weather on Libe Slope

### Social Readiness

```text
projected_social_hours =
  scheduled_social_hours
  + top_opportunity_hours
  + baseline_existing_social_time

social_readiness_score =
  min(projected_social_hours / weekly_target_hours, 1.0) * 100
```

### Reshuffling priority
- Only move `movable` blocks.
- Protect fixed obligations.
- Prefer creating a social window with minimal total work movement.
- Allow a modest focus compression up to roughly `1.25x` to make the tradeoff feel plausible.

## 9. Frontend Interaction Design

### Visual direction
- Warm parchment background, Cornell red accents, editorial typography, glassmorphism surfaces.
- The product should feel more like a premium personal command center than a school dashboard.

### Motion priorities
- Fade and rise on initial load.
- Staggered reveal for cards.
- Layout animation for schedule blocks using Framer Motion.
- Story rail that walks judges through the demo sequence.

### Dynamic Shuffle
- Use one vertical day view.
- Render `before_blocks` and `after_blocks` in the same component.
- Animate with `layout` transitions so blocks physically relocate rather than re-rendering in place.
- Pair the animation with a plain-English tradeoff sentence.

### Emotional payoff
- The best pocket should sound like something a Cornell student would actually want to do.
- Idle Intervention should feel like KAIROS is rescuing the student from a forgettable evening.

## 10. Code Scaffolding

### Backend
- [main.py](/mnt/c/Kairos/backend/app/main.py#L1): FastAPI routes and overview assembly
- [db.py](/mnt/c/Kairos/backend/app/db.py#L1): seeded SQLite store
- [schemas.py](/mnt/c/Kairos/backend/app/schemas.py#L1): API models
- [scheduler.py](/mnt/c/Kairos/backend/app/services/scheduler.py#L1): Work Debt, Social Gravity, Social Readiness, Dynamic Shuffle logic
- [parser.py](/mnt/c/Kairos/backend/app/services/parser.py#L1): mock parser abstraction

### Frontend
- [App.tsx](/mnt/c/Kairos/frontend/src/App.tsx#L1): main demo surface
- [api.ts](/mnt/c/Kairos/frontend/src/api.ts#L1): frontend API client
- [types.ts](/mnt/c/Kairos/frontend/src/types.ts#L1): response types
- [styles.css](/mnt/c/Kairos/frontend/src/styles.css#L1): visual system and layout

### Local run

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Production build:

```bash
cd frontend
npm run build
npm run start
```

## Git Hygiene

The repository includes a root [.gitignore](/mnt/c/Kairos/.gitignore#L1) with the standard local-only artifacts already excluded.

### Do not commit
- virtual environments like `.venv/`, `venv/`, or `env/`
- frontend dependencies and build output such as `node_modules/`, `dist/`, and generated `*.tsbuildinfo`
- Next.js build output such as `frontend/.next/`
- local databases like `backend/kairos.db`, `*.db`, or `*.sqlite3`
- machine-specific config like `.env`, `.env.*`, `.idea/`, `.vscode/`, `.DS_Store`
- logs, temp folders, and local coverage artifacts

### Safe to commit
- source code in `backend/app` and `frontend/src`
- `README.md`, `AGENTS.md`, schema files, and dependency manifests
- intentionally checked-in mock data and demo configuration

## 11. Build Order For The Hackathon
1. Build the single overview endpoint and seed it with a perfect Cornell day.
2. Build the dashboard shell and vertical schedule.
3. Implement the Dynamic Shuffle animation before anything else. This is the demo.
4. Add Work Debt scoring and the ledger visualization.
5. Add Social Gravity ranking with emotionally attractive copy.
6. Add the idle intervention and Social Readiness framing.
7. Add syllabus upload last, using a mocked parser if necessary.

### Risky parts
- Overbuilding the backend instead of polishing the one demo path.
- A weak shuffle animation that feels like a data refresh instead of a life optimization engine.
- Generic UI language that makes the product sound like another student planner.

### Perceived sophistication per hour spent
- Highest ROI: strong seeded data, premium UI, motion polish, crisp narrative copy.
- Medium ROI: simple but believable formulas.
- Low ROI during hackathon: real integrations unless they are already trivial.

### Final rule
If a feature is not visible in the 3-5 minute judge demo, it should not outrank polish on the Dynamic Shuffle, the idle alert, or the Cornell-specific social pocket.
