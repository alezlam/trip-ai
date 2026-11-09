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

Trip AI is a monolith: one repository holds the frontend and the backend, and
they deploy together.

| Part | Responsibility |
|------|----------------|
| Frontend | React 19 + Vite, Astryx design system (neutral theme). Region selection, trip inputs, the agent conversation, and the trip plan view. |
| Backend | Node 24 + Hono in `server/`. The trip agent (LLM plus tools), calls to external data sources (flights, places, weather, visa rules), saved trips, and API keys. API keys stay on the backend and never reach the browser. |

Routes under `/api` belong to the backend.

- **Development:** `npm run dev` starts the Hono server on port 3001 and the
  Vite dev server. Vite proxies `/api` to the Hono server.
- **Production:** `npm run build`, then `npm start`. One Node process serves
  `/api` and the built frontend from `dist/`, with a fallback to `index.html`
  for client-side routes.

## Out of scope for v1

- Booking and payment inside Trip AI. The plan links out to providers.
- Group trips that several users plan together.
- Live rebooking during a trip.

## Open questions

- **LLM provider and model** for the agent.
- **Data sources:** which flight API (for example Amadeus, Duffel or
  Skyscanner), which places API, and where the visa and entry rules come from.
- **Accounts:** does v1 need sign-in and saved trips, or does a single
  session without sign-in come first?
- **Region model:** a fixed list of regions, a map selection, or free text?
