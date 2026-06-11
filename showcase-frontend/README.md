# SmartKUET Sentinel — Showcase Frontend

An optional premium React/Vite showcase frontend for competition presentation.
**The existing `dashboard/` HTML pages and FastAPI backend are completely untouched.**

## Architecture

```
FastAPI backend  (port 8002) ─── real AI engine, tracking, rules, DB
Vite/React frontend (port 5173) ─── showcase presentation layer
Existing dashboard/ ────────────── plain HTML fallback (always works)
```

## Prerequisites

- Node.js 18+ (verified: v22.17.0)
- npm 8+

## Run (Development)

```powershell
# Terminal 1: start the backend (optional but recommended for live data)
cd F:\Skill_WORK\CODE\SMART_KUET_Innovative
.venv\Scripts\python -m uvicorn api.main:app --host 127.0.0.1 --port 8002

# Terminal 2: start the React showcase
cd F:\Skill_WORK\CODE\SMART_KUET_Innovative\showcase-frontend
npm install
npm run dev
```

Open: http://localhost:5173

## Pages

| Route | Description |
|---|---|
| `#/` | Landing — hero, features, architecture, privacy |
| `#/security` | Security Control Room — live feed + tracking + events |
| `#/guard` | Guard Decision Assistant — gate actions |
| `#/exam` | Examiner View — mock invigilation concept |

## API Connections

The frontend connects to these FastAPI endpoints via Vite dev proxy:

| Endpoint | Used by |
|---|---|
| `GET /api/runtime/status` | Landing status bar |
| `GET /api/security/status` | Security Room, Guard View |
| `GET /api/tracking/latest` | Security Room tracking panel |
| `http://127.0.0.1:8002/api/video_feed` | MJPEG live feed |

If the backend is offline, all pages fall back to polished demo placeholder data — no crashes.

## Build (Production)

```powershell
npm run build
```

Output goes to `showcase-frontend/dist/` which is in `.gitignore`.

## Git Rules

The following are in `.gitignore` and must never be committed:

```
showcase-frontend/node_modules/
showcase-frontend/dist/
showcase-frontend/.vite/
```

## Tech Stack

- Vite 6 + React 19
- Vanilla CSS design system (dark mode, glassmorphism)
- Google Fonts: Inter + JetBrains Mono
- No TailwindCSS, no external UI libraries
- Zero cloud dependencies
