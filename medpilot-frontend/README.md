# MedPilot Frontend

Next.js 14 · TypeScript · Tailwind CSS · Zustand

AI-powered dermatology platform with role-based access for doctors and patients.

---

## Project Structure
`medpilot/fe/`
```
fe/
├── .env.example                   # All environment variables documented
├── eslint.config.mjs
├── next.config.ts                 # Rewrite /api/* → BACKEND_URL
├── postcss.config.mjs
├── tailwind.config.ts
├── tsconfig.json
│
└── src/
    ├── middleware.ts              # Edge route-guard (role-based redirects)
    │
    ├── app/                       # Next.js App Router
    │   ├── layout.tsx             # Root HTML shell
    │   ├── page.tsx               # / → /auth/login
    │   ├── error.tsx              # Global error boundary
    │   ├── not-found.tsx          # 404 page
    │   ├── globals.css
    │   │
    │   ├── auth/login/page.tsx    # Role selector + cookie setter
    │   │
    │   ├── doctor/
    │   │   ├── layout.tsx         # AppHeader + DoctorSidebar shell
    │   │   ├── page.tsx           # → /doctor/scribe
    │   │   ├── scribe/
    │   │   │   ├── page.tsx       # Feature 1: Medical Scribe
    │   │   │   └── loading.tsx    # Suspense skeleton
    │   │   └── reminder/
    │   │       ├── page.tsx       # Feature 2: Clinical Reminder
    │   │       └── loading.tsx
    │   │
    │   ├── patient/
    │   │   ├── layout.tsx         # AppHeader full-height shell
    │   │   ├── page.tsx           # → /patient/chat
    │   │   └── chat/
    │   │       ├── page.tsx       # Feature 3: QnA Chatbot
    │   │       └── loading.tsx
    │   │
    │   └── api/                   # BFF proxy — forward to BACKEND_URL or mock
    │       ├── scribe/route.ts    # POST /api/scribe
    │       ├── reminder/route.ts  # POST /api/reminder
    │       └── chat/route.ts      # POST /api/chat
    │
    ├── components/
    │   ├── ui/                    # Primitive design-system components
    │   │   ├── Badge.tsx
    │   │   ├── Button.tsx
    │   │   ├── Card.tsx           # + SectionLabel
    │   │   ├── ConfidenceBar.tsx
    │   │   ├── AlertBanner.tsx
    │   │   └── index.ts
    │   ├── shared/                # Cross-role layout components
    │   │   ├── AppHeader.tsx
    │   │   ├── DoctorSidebar.tsx
    │   │   └── index.ts
    │   ├── doctor/                # Doctor-specific feature components
    │   │   ├── RecordingControls.tsx
    │   │   ├── ScribeSummary.tsx
    │   │   ├── ReminderPanel.tsx
    │   │   └── index.ts
    │   └── patient/               # Patient-specific feature components
    │       ├── ChatBubble.tsx
    │       ├── ChatInput.tsx
    │       ├── ChatWindow.tsx
    │       └── index.ts
    │
    ├── hooks/                     # Business-logic hooks
    │   ├── useScribe.ts           # Timer + recording state machine
    │   ├── useReminder.ts         # Reads scribe result, triggers reminder
    │   └── useChat.ts             # Multi-turn chat + AbortController
    │
    ├── services/                  # Data-fetching layer (swap mock ↔ real)
    │   ├── scribe.service.ts
    │   ├── reminder.service.ts
    │   ├── chat.service.ts
    │   └── mock/
    │       ├── scribe.mock.ts
    │       ├── reminder.mock.ts
    │       └── chat.mock.ts
    │
    ├── stores/                    # Zustand slices
    │   ├── auth.store.ts          # Persisted user session
    │   ├── scribe.store.ts
    │   ├── reminder.store.ts
    │   └── chat.store.ts
    │
    ├── types/
    │   └── index.ts               # Single contract file for all JSON schemas
    │
    ├── lib/
    │   ├── api/client.ts          # Typed fetch wrapper + ApiError class
    │   └── utils/
    │       ├── cn.ts              # Tailwind class merger
    │       ├── format.ts          # formatDuration, confidenceLabel, generateRequestId
    │       ├── session.ts         # Cookie encode/set/clear
    │       └── index.ts           # Barrel
    │
    └── config/
        └── index.ts               # All env vars — components never touch process.env
```

---

## Getting Started

```bash
cp .env.example .env
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Connecting to the AI Backend

### 1. Set the backend URL

```env
# .env
BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_MOCK_API=false
```

### 2. Expected endpoints

The AI service must expose three endpoints:

| Endpoint | Method | Request type | Response type |
|---|---|---|---|
| `/api/scribe` | POST | `ScribeRequest` | `ScribeResponse` |
| `/api/reminder` | POST | `ReminderRequest` | `ReminderResponse` |
| `/api/chat` | POST | `ChatRequest` | `ChatResponse` |

All types are defined in `src/types/index.ts` and mirror the JSON schemas in the project spec.

### 3. Development flow (mock mode)

When `NEXT_PUBLIC_MOCK_API=true` (default), all service calls return mock
data from `src/services/mock/`. The Next.js API routes in `src/app/api/`
also fall back to mock data when `BACKEND_URL` is unset.

This means the frontend team can develop and demo the full UI without a
running backend.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **Services layer** (`src/services/`) | Single swap point — change `MOCK_API` to `false` and point `BACKEND_URL` at the real service. No component changes needed. |
| **API route stubs** (`src/app/api/`) | Act as a BFF proxy. Forward to `BACKEND_URL` in production; return mock data in dev. Also allows adding auth headers, rate-limiting, or response transformation without touching the AI service. |
| **Zustand stores** | Lightweight, no boilerplate. Scribe result flows naturally from `scribe.store` → `reminder.store` without prop drilling. |
| **Types in one file** | `src/types/index.ts` is the single contract document between frontend, backend, and AI engineer. Any schema change is made here first. |
| **Feature-scoped components** | `components/doctor/` and `components/patient/` can evolve independently. |

---

## Adding Audio (STT) Support

When the AI engineer wires up real speech-to-text:

1. In `useScribe.ts`, use the browser `MediaRecorder` API to capture audio.
2. Base64-encode the blob and pass it as `audio_base64` in `ScribeRequest`.
3. Set `input_type: "audio"` in `scribe.service.ts`.
4. The backend handles STT → transcript → extraction pipeline.

---

## Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start dev server on :3000 |
| `npm run build` | Production build |
| `npm run type-check` | TypeScript check without emitting |
| `npm run lint` | ESLint |
