# KAIROS: The Life Arbitrage Engine

## Quick Start

### Backend

macOS / Linux / WSL:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --reload-dir backend/app
```

Windows PowerShell:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --reload-dir backend/app
```

One-command Windows backend startup from the repo root:

```powershell
.\start-backend.ps1
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vercel deployment:
- Deploy the Next.js app from `frontend/`, or keep the repo root and use the included [vercel.json](/mnt/c/Kairos/vercel.json).
- Set `NEXT_PUBLIC_API_BASE_URL` in Vercel to your deployed backend URL.
- The FastAPI backend is exposed for Vercel at [api/index.py](/mnt/c/Kairos/api/index.py).
- For persistent backend storage on Vercel, set `DATABASE_URL` to a Postgres database; local SQLite is not persistent on Vercel.

One-command Windows frontend startup from the repo root:

```powershell
.\start-frontend.ps1
```

### Verification

```bash
python -m compileall backend/app
cd frontend && npm run build
```

## Vercel Deployment

Deploy this repo to Vercel as two separate projects from the same Git repository.

### Frontend project

- Root Directory: `frontend`
- Framework Preset: `Next.js`
- Build Command: default
- Output Directory: default
- Environment variables:
  - `NEXT_PUBLIC_API_BASE_URL=https://your-backend-project.vercel.app`

### Backend project

- Root Directory: `backend`
- Framework Preset: Python / `Other`
- Entry file: `backend/index.py`
- Install Command: default, or `pip install -r requirements.txt`
- Environment variables:
  - `API_ALLOWED_ORIGINS=https://your-frontend-project.vercel.app`
  - `API_ALLOWED_ORIGIN_REGEX=https://.*\\.vercel\\.app`
  - Optional: `KAIROS_DB_PATH=/tmp/kairos.db`

### Backend deployment notes

- The backend now exposes a Vercel entrypoint at `backend/index.py`.
- After the backend project deploys, copy its production URL from Vercel and use that exact value for `NEXT_PUBLIC_API_BASE_URL` in the frontend project.
- On Vercel, the SQLite demo database automatically moves to `/tmp/kairos.db` because the deployed project files are read-only.
- `/tmp` is ephemeral. Uploaded syllabus changes are not durable across cold starts or redeploys. For persistent production data, move the backend off local SQLite and onto Postgres or another external database.
- The backend includes `backend/vercel.json` so `app/schema.sql` is bundled with the function deployment.

## Environment Notes

- The root `requirements.txt` installs the backend Python dependencies so you can run the API from the project root.
- Use `--reload-dir backend/app` for the backend dev server so Uvicorn only watches source files.
- Install frontend dependencies in the same shell you will use to run them. If you use PowerShell, run both `npm install` and `npm run dev` in PowerShell so Windows `next.cmd` shims are present.
- This repo is not a root-level Node workspace. If a root `package-lock.json` appears, remove it.

## Fateweaver Protocol

### 1. Strong product definition
Fateweaver Protocol is KAIROS’s signature mechanism for reclaiming meaningful life moments before they disappear. It detects a high-value social opportunity, checks whether that moment is still realistically attainable, and then actively rewrites the user’s day around it. Instead of showing a passive calendar, KAIROS presents a better version of the day and makes the tradeoff legible: what to move, what to compress, what to do now, and what becomes possible if the user acts.

This is the flagship feature because it turns the product from a tracker into an intervention. It does not merely describe the user’s schedule. It reshapes it around moments that would otherwise be lost.

### 2. Plain-English feature description
Fateweaver Protocol is an intelligent reweaving of the day. It looks at what the user has to do, spots a social window that actually matters, checks what work can move, and proposes a cleaner plan that makes the opportunity possible.

It is not rigid scheduling. It is not calendar perfectionism. It is not formal optimization math. It is a practical product behavior: find the moment worth saving, make a believable plan to save it, and show the user how to get there.

### 3. Core user value
College students do not just lose time. They lose specific nights, specific friendships, specific campus moments, and then they carry the guilt of both unfinished work and missed experiences. That is the emotional hole Fateweaver Protocol addresses.

The feature matters because it resolves four things at once:
- missed experiences: the best social moments are short-lived and easy to miss
- passive idling: the day often collapses into scrolling, dithering, and low-value drift
- productivity guilt: students feel behind even when there is still a recoverable path
- social FOMO: they do not just want free time, they want a reason to actually use it

When KAIROS says, in effect, “If you do these two things differently, you can still make sunset on the Slope with your friends,” that feels emotionally powerful in a way a normal planner never does.

### 4. MVP mechanics
The minimum hackathon version of Fateweaver Protocol should be simple, legible, and convincing.

Inputs:
- current schedule blocks for the day
- assignment list with due times, task type, and estimated effort
- friend availability windows
- a small set of user assumptions such as reading speed and historical productivity
- lightweight context such as weather, time of day, and preferred location

Movable work blocks:
- independent study sessions
- reading blocks
- problem set blocks
- writing or admin blocks without a hard start time

Not movable:
- classes
- meetings
- meals or anchors you want to preserve
- any block marked fixed or high-friction to move

High-value social opportunity:
- at least two friends overlap
- timing is soon enough to feel urgent
- duration is realistic, ideally 30 to 60 minutes
- context is emotionally attractive, such as clear weather or a strong Cornell location
- the opportunity sounds like something a student would actually want to claim

Plausibility check:
- can conflicting work blocks be moved earlier or later without breaking fixed obligations
- can any block be compressed slightly without becoming absurd
- does the plan require only a believable focus boost, not superhero discipline
- does the social window still feel worth the tradeoff after the rewrite

AI-generated optimization strategies:
- generated after the app has identified the target pocket and the conflicting work
- shown as tactics attached to the rewritten plan
- phrased as concrete moves tied to unlocking that specific window
- limited to a few sharp suggestions, not a wall of advice

### 5. AI strategy layer
The AI agent’s job is not to “solve the schedule.” Its job is to make the rewoven plan feel smart, tactical, and personal.

The AI should:
- analyze the workload, block types, deadlines, and time of day
- identify where work can be compressed, moved, batched, or downgraded to a good-enough pass
- generate tactics that are directly tied to the target opportunity
- explain tradeoffs in plain English so the user knows what they gain and what they risk
- make the plan feel tailored to this day, this workload, and this moment

Good AI suggestions sound like this:
- “Do the reading in focused skim mode and extract only discussion-critical points.”
- “Finish the problem set’s easy questions first to secure most of the progress quickly.”
- “Move this writing task to tonight since your historical focus is stronger then.”
- “Batch these two admin tasks together to free up a clean 30-minute block.”
- “Use a 25-minute sprint to unlock this social window.”

Bad AI suggestions sound like generic self-help. If the advice would make sense on any random productivity app, it is not good enough for Fateweaver Protocol.

### 6. User flow
The ideal flow is:
1. KAIROS detects a valuable social opportunity forming.
2. It checks the current day and identifies the work standing in the way.
3. It finds which blocks are movable and whether the tradeoff is plausible.
4. It generates a rewritten version of the day.
5. It attaches a small number of context-aware efficiency tactics.
6. The user sees a before-versus-after view with a clear gain.
7. The user accepts or declines the rewrite.
8. If accepted, the schedule updates visually and the moment feels newly real.

The key is that the product should feel decisive. It should not ask the user to manually negotiate fifteen little calendar edits.

### 7. UX copy
Short definition:
Fateweaver Protocol rewrites your day to save the moments that matter.

Landing-page description:
KAIROS does not just organize your schedule. Fateweaver Protocol detects the social windows worth claiming, rewires flexible work around them, and gives you a sharper, more human version of the day.

In-app explanation:
We found a window worth protecting. Fateweaver Protocol moved flexible work, tightened the low-risk tasks, and built you a believable path to make it.

Notification example:
Fateweaver Protocol found a recoverable night: 45 minutes of focused work now unlocks sunset on Libe Slope with 5 friends.

Before vs after explanation:
Before: your day drifts toward fragmented work and a missed opportunity.
After: one focused sprint, one moved block, and the night opens back up.

### 8. Demo framing
In the demo, the user should first see a day that feels full but salvageable. Then KAIROS surfaces a social opportunity that feels specific and desirable. The moment Fateweaver Protocol activates, the schedule should visibly reweave itself: work blocks slide, the social block appears, and the tradeoff statement sharpens.

What should animate:
- the target opportunity becoming “claimable”
- conflicting work blocks relocating in the day view
- a new social block appearing as the earned outcome
- a strategy panel revealing the exact tactics that make the plan believable

How to explain the magic:
- show the old day first
- name the lost moment
- show the rewoven day
- explain the tradeoff in one sentence
- point to the AI strategies as the reason the plan feels achievable rather than theatrical

Those AI strategies are the believability layer. They make the feature feel less like animation polish and more like intelligence.

### 9. Implementation guidance
Build the MVP with a split between simple rules and selective AI.

What can be mocked:
- friend availability
- weather context
- idle detection
- user productivity profile

What should be rule-based:
- work debt scoring
- social pocket ranking
- movable vs fixed block detection
- plausibility checks for rescheduling
- focus boost limits

Where AI is actually useful:
- generating the tactical work-compression strategies
- rewriting tradeoff explanations in polished, human language
- turning a dry schedule move into a personalized recommendation

How to make it feel intelligent quickly:
- use deterministic rules to choose the opportunity and rewrite the day
- use AI only after the system already knows what it wants the user to do
- keep the suggestions tightly grounded in the chosen pocket, the conflicting blocks, and the user profile
- show only the top two or three tactics so the feature feels sharp, not noisy

For the MVP, the current `shuffle_plan` backend contract can remain in place as the implementation layer. Fateweaver Protocol is the product name and UX framing for that mechanism.

### 10. Naming and positioning
`Dynamic Shuffle` sounds like UI motion. `Fateweaver Protocol` sounds like a proprietary mechanism with judgment, intent, and consequence.

The name is stronger because it implies:
- the day is being actively rewoven, not randomly rearranged
- the feature has a distinct product identity
- the outcome is emotional, not merely operational
- KAIROS is not just helping manage time, it is altering the trajectory of the day

That supports the brand. KAIROS is not a planner. It is a life arbitrage engine, and Fateweaver Protocol sounds like the engine’s crown jewel.

## 1. Thesis
KAIROS can win a hackathon because it attacks a real emotional problem, not just a workflow problem: college students do not need another calendar, they need a system that resolves the tension between academic guilt, social FOMO, and passive idling. The MVP should feel magical by doing one thing extremely well: turning a vague tradeoff into a visible, emotionally charged decision, then proving it with Fateweaver Protocol. If the demo clearly shows coursework being priced, a high-value Cornell social pocket being detected, and the schedule physically reorganizing itself to unlock that moment, judges will understand the product in under 30 seconds and remember it after every other “AI planner” blurs together.

## 2. The Exact Demo Story
1. Open the dashboard already seeded with a believable Cornell day.
2. Start on the hero state: KAIROS shows current Work Debt, Social Readiness, and a live opportunity forming around Libe Slope.
3. Upload a syllabus PDF. The parser responds instantly with extracted assignments and a higher-confidence Work Debt Ledger.
4. Highlight the Work Debt panel: show hours owed, procrastination drag, and urgency multipliers.
5. Move to Social Gravity: KAIROS shows a 45-minute sunset pocket with 5 friends free at Libe Slope.
6. Trigger Idle Intervention: “20 mins of YouTube vs. Sunset at the Slope.”
7. Click `Trigger Fateweaver Protocol` or `Play demo story`.
8. The schedule animates. A work block snaps earlier, the social block appears, and the tradeoff statement updates: `If you focus for the next hour at 1.2x pace, you unlock Sunset at the Slope with 5 friends.`
9. End on the social/readiness framing: KAIROS did not just organize tasks, it created a better life outcome.

### What is real for the demo
- Backend API contract
- Work Debt scoring
- Social pocket detection
- Fateweaver Protocol output, tactics, and animation
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
- Fateweaver Protocol as the centerpiece
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
- Formal mathematical optimization or operations research framing
- Shipping a browser extension during the hackathon

## 4. Product Spec

### Main screens
- `Landing + Hero`: immediately explains the product as a life arbitrage engine, not a task app.
- `Dashboard`: the main demo screen with Work Debt, Social Gravity, Fateweaver Protocol, Idle Intervention, and Social Readiness.
- `Upload flow`: lightweight overlay or button interaction that updates the ledger after syllabus parsing.

### Key user actions
- Upload a syllabus.
- Inspect the Work Debt Ledger.
- Review the best social opportunity.
- Trigger Fateweaver Protocol.
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
- Fateweaver Protocol should feel like the app is making life happen.
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
4. Frontend renders the dashboard and animates Fateweaver Protocol.
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

### Fateweaver Protocol
- Use one vertical day view.
- Render `before_blocks` and `after_blocks` in the same component.
- Animate with `layout` transitions so blocks physically relocate rather than re-rendering in place.
- Pair the animation with a plain-English tradeoff sentence and 2-3 tactical AI strategies.

### Emotional payoff
- The best pocket should sound like something a Cornell student would actually want to do.
- Idle Intervention should feel like KAIROS is rescuing the student from a forgettable evening.

## 10. Code Scaffolding

### Backend
- [main.py](/mnt/c/Kairos/backend/app/main.py#L1): FastAPI routes and overview assembly
- [db.py](/mnt/c/Kairos/backend/app/db.py#L1): seeded SQLite store
- [schemas.py](/mnt/c/Kairos/backend/app/schemas.py#L1): API models
- [scheduler.py](/mnt/c/Kairos/backend/app/services/scheduler.py#L1): Work Debt, Social Gravity, Social Readiness, and Fateweaver Protocol planning logic
- [parser.py](/mnt/c/Kairos/backend/app/services/parser.py#L1): mock parser abstraction

### Frontend
- [App.tsx](/mnt/c/Kairos/frontend/src/App.tsx#L1): main demo surface
- [api.ts](/mnt/c/Kairos/frontend/src/api.ts#L1): frontend API client
- [types.ts](/mnt/c/Kairos/frontend/src/types.ts#L1): response types
- [globals.css](/mnt/c/Kairos/frontend/app/globals.css#L1): visual system and layout

### Local run

Backend:

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --reload-dir backend/app
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
3. Implement Fateweaver Protocol before anything else. This is the demo.
4. Make the rewrite believable with context-aware AI tactics, not generic advice.
5. Add Work Debt scoring and the ledger visualization.
6. Add Social Gravity ranking with emotionally attractive copy.
7. Add the idle intervention and Social Readiness framing.
8. Add syllabus upload last, using a mocked parser if necessary.

### Risky parts
- Overbuilding the backend instead of polishing the one demo path.
- A weak Fateweaver moment that feels like a data refresh instead of a life arbitrage engine.
- Generic UI language that makes the product sound like another student planner.
- AI strategy copy that sounds like generic productivity blogging instead of tactical guidance.

### Perceived sophistication per hour spent
- Highest ROI: strong seeded data, premium UI, motion polish, crisp narrative copy.
- Medium ROI: simple but believable formulas.
- Low ROI during hackathon: real integrations unless they are already trivial.

### Final rule
If a feature is not visible in the 3-5 minute judge demo, it should not outrank polish on Fateweaver Protocol, the idle alert, or the Cornell-specific social pocket.
