# Trip AI — Product

## Summary

Trip AI is a trip-planning agent that replaces a travel agency. The user picks a
region, and the agent researches that region and returns a complete, bookable
trip plan: flights, travel necessities, places to go, and a day-by-day schedule.

## Problem

Planning a trip today means one of two things:

- **Use a travel agency.** It is convenient, but it is slow, costs a fee, and
  offers a fixed set of packages.
- **Plan it yourself.** It is flexible, but you must search across many sites
  (airlines, visa rules, maps, blogs, weather) and combine the results by hand.

Trip AI gives the convenience of an agency with the flexibility of planning it
yourself.

## Target user

A traveller who wants a complete plan for a trip without doing the research
across many sites themselves.

## Core feature: the region-scoped trip agent

### 1. Region selection

The user selects a region before the agent starts. The region sets the scope of
the agent's research, so the agent only gathers information inside that area.

- A region can be a country, a group of countries, or a city.
- The user also gives the trip inputs: origin city, dates or trip length,
  number of travellers, and budget.

### 2. Information the agent gathers

Inside the selected region, the agent gathers:

| Area | What the agent finds |
|------|----------------------|
| Plane tickets | Flight options from the origin into the region and between cities in it: price, times, stops, airline. |
| Necessities | Visa and entry rules, currency and payment, power plugs, SIM or eSIM, weather for the dates, a packing list, travel insurance, safety notes. |
| Locations | Places to visit, areas to stay in, and food, ranked against the user's interests. |
| Schedule | A day-by-day itinerary that orders the locations, the transport between them, and the flights. |

### 3. Trip plan output

The agent returns one trip plan that the user can:

- Read as a day-by-day schedule.
- Edit with a follow-up message, for example "make day 3 slower" or "find a
  cheaper flight".
- Use to book, through links to the flight and accommodation providers.

## Architecture

Trip AI is a monolith: one repository, one Python process in production.

| Part | Responsibility |
|------|----------------|
| Frontend | React 19 + Vite, Astryx design system (neutral theme), in `src/`. Region selection, trip inputs, the agent conversation, and the trip plan view. Vite builds it to `dist/`. |
| Backend + agent | [CowAgent](https://github.com/zhayujie/CowAgent) (MIT, Python) in `agent/`. CowAgent is the agent harness: planning, tool loop, skills, memory, web search and browser. We do not build our own harness. Our backend is a CowAgent channel, `trip`, in `agent/channel/trip/`. |

### The `trip` channel

CowAgent receives messages through channels (WeChat, Slack, its web console and
others). Trip AI adds its own channel, `trip`, and runs no other channel. The
`trip` channel is the only listener in the process:

- `/api/*`: the Trip AI API. Today only `GET /api/health`.
- Every other path: the built frontend from `dist/`, with a fallback to
  `index.html` for client-side routes. Paths outside `dist/` are never served.
- Bind address: `trip_host` (default `127.0.0.1`; set `0.0.0.0` in production)
  and `trip_port` (default `8080`) in `agent/config.json`.

Request flow (to build):

1. The frontend sends the region, trip inputs and user message to
   `POST /api/trips/...`.
2. The `trip` channel puts the region scope and trip inputs in the agent's
   context, keys the conversation by trip ID, and hands the message to the
   CowAgent core in the same process, the same way the other channels do.
3. The channel streams the agent's answer back to the frontend.

Model API keys live in `agent/config.json`, which is gitignored, and never
reach the browser.

### CowAgent: lite copy

- **Source:** CowAgent's Python source lives in this repository under
  `agent/`, added with `git subtree` (squashed) at release `2.2.2`. We may edit
  any file in it. To take an upstream release, run
  `git subtree pull --prefix=agent https://github.com/zhayujie/CowAgent.git <tag> --squash`.
  Prefer skills, MCP servers and our own `trip` channel over edits to
  CowAgent's core, because each core edit can conflict with the next upstream
  pull. Core edits are marked with a `trip-ai:` comment.
- **Removed from the copy:**
  - `desktop/`: the Electron desktop client.
  - `channel/web/`: the web console and its admin API, including the
    OpenAI-compatible Chat API. With no admin listener, no admin routes can be
    reached.
  - `tests/`: upstream's test suite. Most of it imported the web console.
- **Core edits** (`trip-ai:` comments): `channel/channel_factory.py` and
  `app.py` register `trip` in place of `web`, and `config.py` turns the web
  console off by default.
- **Operations without a console:** models and keys in `agent/config.json`,
  skills as folders in the workspace, logs on stdout.
- **Travel abilities:** flights, places, weather and visa rules come from
  CowAgent skills or MCP servers that wrap the chosen data sources. A
  dedicated agent for trips keeps its prompt, skills and model apart.
- **Tool lockdown (required):** CowAgent's built-in tools include the
  terminal, file I/O and browser control on the host it runs on. Trip AI users
  are untrusted, so the trip agent must have the terminal and file-write tools
  turned off, and only the travel skills and web search turned on. This must be
  in place before the chat routes go public.

### Running it

- **Once:** `npm install`, then `npm run setup:agent` (creates
  `agent/.venv` and installs CowAgent's Python packages). Create
  `agent/config.json` with `"channel_type": "trip"`, `"web_console": false` and
  the model keys.
- **Development:** `npm run dev` starts CowAgent (the `trip` channel on
  `8080`) and the Vite dev server. Vite proxies `/api` to `8080`.
- **Production:** `npm run build`, then `npm start`. One Python process serves
  `/api` and the built frontend.

## Out of scope for v1

- Booking and payment inside Trip AI. The plan links out to providers.
- Group trips that several users plan together.
- Live rebooking during a trip.

## Open questions

- **LLM provider and model** for the agent. CowAgent supports Claude, GPT,
  Gemini, DeepSeek and others, and the model is set per agent.
- **CowAgent per-user state:** CowAgent's memory and self-evolution are built
  for one personal user. With many Trip AI users on one agent, do memory and
  knowledge need to be turned off or kept per user?
- **Data sources:** which flight API (for example Amadeus, Duffel or
  Skyscanner), which places API, and where the visa and entry rules come from.
- **Accounts:** does v1 need sign-in and saved trips, or does a single
  session without sign-in come first?
- **Region model:** a fixed list of regions, a map selection, or free text?
