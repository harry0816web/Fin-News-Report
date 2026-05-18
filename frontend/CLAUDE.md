@AGENTS.md

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical: Next.js version

Next.js is pinned to **16.2.6** with React **19.2.4**. APIs, conventions, and file layout differ from older Next.js versions in training data. Before writing any Next.js code (routing, fonts, metadata, server components, etc.), consult `node_modules/next/dist/docs/` — start at `index.md` and follow into `01-app/` for App Router topics. Heed any deprecation notices you encounter.

## Commands

```bash
npm run dev         # next dev — local server at http://localhost:3000
npm run build       # next build
npm run start       # serve production build
npm run lint        # eslint (flat config in eslint.config.mjs)
npm run test        # vitest run (one-shot, jsdom)
npx vitest          # vitest watch mode
npx vitest path/to/file.test.tsx   # single test file
```

Tailwind CSS v4 is wired through `@tailwindcss/postcss` (see `postcss.config.mjs`); there is no `tailwind.config.js`.

## Architecture

This is the frontend for **台灣財經日報** — a daily Traditional Chinese (zh-Hant) Taiwan finance news digest. The Next.js app is a thin client that renders data fetched from a separate backend (Python Azure Functions under `../backend/`, not part of this directory).

- **API surface (`lib/api.ts`)** — three endpoints consumed:
  - `GET /api/news[?date=YYYY-MM-DD]` → `DailyDigest | null` (404 → null, used to mean "no digest for that date")
  - `GET /api/news/dates` → `{ dates: string[] }`
  - `POST /api/subscribe` → `{ message | error }`
  - Base URL comes from `NEXT_PUBLIC_API_BASE_URL` (defaults to `""`, i.e. same origin). Set this in `.env.local` for local dev pointing at the backend.
- **Data model (`types/news.ts`)** — `DailyDigest` contains an array of `AnalyzedArticle`, each tagged with one of four fixed `Category` strings and a `Sentiment`. Pages group articles by category using a hardcoded `CATEGORY_ORDER` (`科技股市`, `總體經濟`, `上市公司公告`, `國際財經`); keep this list in sync across `app/page.tsx` and `app/history/page.tsx` if it ever changes.
- **Routes (App Router)** — `app/page.tsx` (today's digest), `app/history/page.tsx` (date-picker over `fetchAvailableDates`), `app/subscribe/page.tsx`. `app/layout.tsx` provides the shared header/footer and is the only place `<html lang="zh-Hant">` is set.
- **Client vs server** — pages that fetch are `"use client"` (state + `useEffect`); `app/subscribe/page.tsx` is a server component that just renders the form. Don't convert client pages to server components without rewiring data fetching.
- **Path alias** — `@/*` maps to the frontend root (`tsconfig.json` and `vitest.config.ts` both declare it). Use `@/components/...`, `@/lib/...`, `@/types/...`.

## Tests

Vitest 4 + Testing Library + jsdom. `vitest.setup.ts` imports `@testing-library/jest-dom` globally (so matchers like `toBeInTheDocument` work without per-file imports). Tests live in colocated `__tests__/` folders next to the code they cover (`app/__tests__/`, `app/history/__tests__/`, `app/subscribe/__tests__/`, `components/__tests__/`). `globals: true` is set, so `describe`/`it`/`expect` are available without imports.
