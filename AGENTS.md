# AGENTS.md

## Project overview

KAIROS is a hackathon MVP for a Cornell-first "Life Operating System." The repository contains:
- `backend/`: FastAPI service with mock syllabus parsing, work debt scoring, social pocket detection, social readiness scoring, Fateweaver Protocol planning, and a seeded SQLite demo store.
- `frontend/`: Next.js dashboard and landing experience with Framer Motion.

## Working agreements

- Preserve the premium Cornell-focused product voice.
- Keep Fateweaver Protocol as the centerpiece of the product and the UI.
- Prefer mocked adapters over hardcoded UI-only data when adding new demo flows.
- Maintain clean separation between domain logic in `backend/app/services` and presentation logic in `frontend/src`.
- Optimize every change for the 3-5 minute judge demo, not feature completeness.

## Flagship feature

- Product language should refer to the old Dynamic Shuffle experience as `Fateweaver Protocol`.
- Fateweaver Protocol is not formal optimization math. It is the product mechanism that detects a meaningful social opportunity, checks whether it is realistically claimable, rewrites flexible work blocks, and gives the user a better version of the day.
- Treat AI strategy suggestions as part of the mechanism, not garnish. They should be situational, tied to unlocking a specific window, and phrased like tactical advice rather than generic productivity content.
- When product copy and implementation language diverge, keep premium product-facing language in the UI and docs, but it is acceptable for internal code and API names to remain `shuffle`-based during the MVP.

## Primary commands

### Backend
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --reload-dir backend/app
```

Windows PowerShell variant:
```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --reload-dir backend/app
```

Windows shortcut:
```powershell
.\start-backend.ps1
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Windows shortcut:
```powershell
.\start-frontend.ps1
```

Frontend note:
- Install and run the frontend from the same OS shell. If you use PowerShell, run `npm install` and `npm run dev` in PowerShell so Windows-compatible `node_modules` shims are created.

### Verification
```bash
python3 -m compileall backend/app
cd frontend && npm run build
```

### Vercel deployment

- Deploy the frontend and backend as two separate Vercel projects from the same repo.
- Set the frontend Root Directory to `frontend`.
- Set the backend Root Directory to `backend`.
- The backend Vercel entrypoint is `backend/index.py`.
- The frontend should use `NEXT_PUBLIC_API_BASE_URL` to point at the deployed backend URL.
- The backend should use `API_ALLOWED_ORIGINS` for the deployed frontend URL and may use `API_ALLOWED_ORIGIN_REGEX` for preview deployments.
- The backend demo SQLite store runs from `/tmp/kairos.db` on Vercel. This is acceptable for demos, but uploaded syllabus state is ephemeral across cold starts and redeploys.

### Environment safety

- Keep the backend virtualenv at the repo root as `venv/`, or otherwise outside the watched `backend/` tree.
- Keep `--reload-dir backend/app` on the backend dev server so Uvicorn only watches source files, not the environment.
- Do not run `npm install` from WSL and then try to use the resulting `node_modules` from PowerShell. Reinstall in the shell you plan to use.
- This repo is not a root-level Node workspace. Do not create a root `package-lock.json`.
- Do not rely on Vercel-hosted SQLite state for anything beyond the live demo. If persistent state matters, move the backend to a real external database.

## Backend conventions

- Extend API contracts in `backend/app/schemas.py`.
- Keep the demo data layer in `backend/app/db.py` and `backend/app/schema.sql`.
- Keep deterministic demo data in `backend/app/mock_data.py`.
- Put scoring and scheduling logic in `backend/app/services/scheduler.py`.
- Keep syllabus parsing behind `backend/app/services/parser.py` so a real LLM provider can replace the mock later.

## Frontend conventions

- Keep the current visual language: warm neutrals, Cornell red accents, fluid motion.
- Use Framer Motion for meaningful transitions, especially the visible “rewoven day” moment in Fateweaver Protocol.
- Prefer typed API helpers in `frontend/src/api.ts`.
- Keep component state simple and local unless a cross-page need emerges.
- Preserve the story rail and judge-mode sequence unless there is a better demo narrative.

## Next upgrades

- Replace the mock parser with OpenAI file parsing.
- Add SQLite or Postgres persistence behind the current schema.
- Swap mocked friend availability for Google Calendar integration.
- Add a lightweight Chrome extension or event simulator for idle detection.
